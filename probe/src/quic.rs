//! Direct QUIC to the leader's tpuQuic (plan, section 5.1).
//!
//! The client config repeats create_client_config of Agave v4.3.2
//! (tpu-client-next/src/quic_networking.rs, lines 36-47 and 63): a client certificate
//! from solana-tls-utils, which the TPU server requires, ALPN solana-tpu, keep-alive and
//! idle timeout as there, and send_fairness(false), so the streams of one connection
//! leave in the order they were opened. The certificate comes from a throwaway keypair
//! (QuicClientCertificate::new(None)), so no wallet key is involved.

use crate::clock::mono_ns;
use quinn::crypto::rustls::QuicClientConfig;
use quinn::{ClientConfig, Connection, ConnectionError, Endpoint, IdleTimeout, StoppedError, TransportConfig, VarInt};
use solana_tls_utils::{tls_client_config_builder, QuicClientCertificate};
use std::net::SocketAddr;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Duration;

pub const ALPN_TPU: &[u8] = b"solana-tpu";
const QUIC_MAX_TIMEOUT: Duration = Duration::from_secs(10);
const QUIC_KEEP_ALIVE: Duration = Duration::from_secs(1);
pub const STOPPED_TIMEOUT: Duration = Duration::from_secs(2);
const CONNECT_TIMEOUT: Duration = Duration::from_secs(5);

pub fn client_config() -> ClientConfig {
    let cert = QuicClientCertificate::new(None);
    let mut crypto = tls_client_config_builder()
        .with_client_auth_cert(vec![cert.certificate.clone()], cert.key.clone_key())
        .expect("client certificate");
    crypto.enable_early_data = true;
    crypto.alpn_protocols = vec![ALPN_TPU.to_vec()];
    let mut transport = TransportConfig::default();
    transport.max_idle_timeout(Some(IdleTimeout::try_from(QUIC_MAX_TIMEOUT).unwrap()));
    transport.keep_alive_interval(Some(QUIC_KEEP_ALIVE));
    transport.datagram_receive_buffer_size(None);
    transport.send_fairness(false);
    let mut config = ClientConfig::new(Arc::new(QuicClientConfig::try_from(crypto).expect("QUIC TLS config")));
    config.transport_config(Arc::new(transport));
    config
}

pub struct Transport {
    endpoint: Endpoint,
    /// Every stream the probe opens passes through open_stream and is counted here, so
    /// a dry-run can prove it opened none (section 11).
    streams_opened: Arc<AtomicU64>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum StreamResult {
    /// The peer acknowledged all data of the stream.
    Finished,
    /// The peer stopped the stream with a code.
    Stopped(u64),
    ConnectionClosed(Option<u64>),
    Timeout,
}

impl StreamResult {
    pub fn name(&self) -> &'static str {
        match self {
            StreamResult::Finished => "finished",
            StreamResult::Stopped(_) => "stopped",
            StreamResult::ConnectionClosed(_) => "connection_closed",
            StreamResult::Timeout => "timeout",
        }
    }

    pub fn code(&self) -> Option<u64> {
        match self {
            StreamResult::Stopped(c) => Some(*c),
            StreamResult::ConnectionClosed(c) => *c,
            _ => None,
        }
    }
}

#[derive(Clone, Debug)]
pub struct SendOutcome {
    pub send_end_ns: Option<i64>,
    pub stopped_ns: Option<i64>,
    pub result: StreamResult,
    pub error: Option<String>,
}

pub fn close_code(e: &ConnectionError) -> Option<u64> {
    match e {
        ConnectionError::ApplicationClosed(a) => Some(a.error_code.into_inner()),
        ConnectionError::ConnectionClosed(c) => Some(u64::from(c.error_code)),
        _ => None,
    }
}

impl Transport {
    pub fn new() -> Result<Transport, String> {
        let mut endpoint = Endpoint::client("0.0.0.0:0".parse().unwrap()).map_err(|e| format!("QUIC endpoint: {e}"))?;
        endpoint.set_default_client_config(client_config());
        Ok(Transport { endpoint, streams_opened: Arc::new(AtomicU64::new(0)) })
    }

    pub fn streams_opened(&self) -> u64 {
        self.streams_opened.load(Ordering::SeqCst)
    }

    pub async fn connect(&self, addr: SocketAddr) -> Result<Connection, String> {
        let connecting = self.endpoint.connect(addr, "connect").map_err(|e| format!("connect {addr}: {e}"))?;
        match tokio::time::timeout(CONNECT_TIMEOUT, connecting).await {
            Ok(Ok(c)) => Ok(c),
            Ok(Err(e)) => Err(format!("handshake {addr}: {e}")),
            Err(_) => Err(format!("handshake {addr}: no answer in {} s", CONNECT_TIMEOUT.as_secs())),
        }
    }

    /// One probe on its own unidirectional stream: open_uni, write_all, finish; the end
    /// of write_all is the send mark. The stopped() wait runs in a task, so the next
    /// probe does not wait for this one's acknowledgement.
    pub async fn send(&self, conn: &Connection, wire: Vec<u8>) -> tokio::task::JoinHandle<SendOutcome> {
        let fail = |result: StreamResult, error: String| {
            tokio::spawn(async move { SendOutcome { send_end_ns: None, stopped_ns: None, result, error: Some(error) } })
        };
        self.streams_opened.fetch_add(1, Ordering::SeqCst);
        let mut stream = match conn.open_uni().await {
            Ok(s) => s,
            Err(e) => return fail(StreamResult::ConnectionClosed(close_code(&e)), format!("open_uni: {e}")),
        };
        if let Err(e) = stream.write_all(&wire).await {
            return fail(StreamResult::ConnectionClosed(None), format!("write_all: {e}"));
        }
        let send_end_ns = mono_ns();
        let _ = stream.finish();
        tokio::spawn(async move {
            let (result, error) = match tokio::time::timeout(STOPPED_TIMEOUT, stream.stopped()).await {
                Ok(Ok(None)) => (StreamResult::Finished, None),
                Ok(Ok(Some(code))) => (StreamResult::Stopped(code.into_inner()), None),
                Ok(Err(StoppedError::ConnectionLost(e))) => (StreamResult::ConnectionClosed(close_code(&e)), Some(e.to_string())),
                Ok(Err(e)) => (StreamResult::ConnectionClosed(None), Some(e.to_string())),
                Err(_) => (StreamResult::Timeout, None),
            };
            SendOutcome { send_end_ns: Some(send_end_ns), stopped_ns: Some(mono_ns()), result, error }
        })
    }
}

pub fn close(conn: &Connection, reason: &[u8]) {
    conn.close(VarInt::from_u32(0), reason);
}

pub fn stats_json(conn: &Connection) -> serde_json::Value {
    let s = conn.stats();
    serde_json::json!({
        "rtt_ns": s.path.rtt.as_nanos() as u64,
        "lost_packets": s.path.lost_packets,
        "sent_packets": s.path.sent_packets,
        "congestion_events": s.path.congestion_events,
        "cwnd": s.path.cwnd,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use quinn::crypto::rustls::QuicServerConfig;
    use solana_tls_utils::tls_server_config_builder;

    /// A local server with the TPU's TLS settings (client certificate required, ALPN
    /// solana-tpu) that counts and reads unidirectional streams in acceptance order.
    async fn tpu_like_server() -> (SocketAddr, tokio::sync::mpsc::UnboundedReceiver<Vec<u8>>, Arc<AtomicU64>) {
        let cert = QuicClientCertificate::new(None);
        let mut crypto = tls_server_config_builder()
            .with_single_cert(vec![cert.certificate.clone()], cert.key.clone_key())
            .unwrap();
        crypto.alpn_protocols = vec![ALPN_TPU.to_vec()];
        let server = quinn::ServerConfig::with_crypto(Arc::new(QuicServerConfig::try_from(crypto).unwrap()));
        let endpoint = Endpoint::server(server, "127.0.0.1:0".parse().unwrap()).unwrap();
        let addr = endpoint.local_addr().unwrap();
        let (tx, rx) = tokio::sync::mpsc::unbounded_channel();
        let accepted = Arc::new(AtomicU64::new(0));
        let counter = accepted.clone();
        tokio::spawn(async move {
            while let Some(incoming) = endpoint.accept().await {
                let Ok(conn) = incoming.await else { continue };
                let tx = tx.clone();
                let counter = counter.clone();
                tokio::spawn(async move {
                    while let Ok(mut s) = conn.accept_uni().await {
                        counter.fetch_add(1, Ordering::SeqCst);
                        if let Ok(data) = s.read_to_end(4096).await {
                            let _ = tx.send(data);
                        }
                    }
                });
            }
        });
        (addr, rx, accepted)
    }

    #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
    async fn dry_run_handshake_opens_no_stream() {
        let (addr, _rx, accepted) = tpu_like_server().await;
        let t = Transport::new().unwrap();
        let conn = t.connect(addr).await.expect("handshake with a TPU-like server");
        assert!(conn.rtt() < Duration::from_secs(1));
        close(&conn, b"dry-run");
        tokio::time::sleep(Duration::from_millis(200)).await;
        assert_eq!(t.streams_opened(), 0);
        assert_eq!(accepted.load(Ordering::SeqCst), 0);
    }

    #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
    async fn streams_arrive_in_send_order_and_are_acknowledged() {
        let (addr, mut rx, accepted) = tpu_like_server().await;
        let t = Transport::new().unwrap();
        let conn = t.connect(addr).await.unwrap();
        let mut handles = vec![];
        for i in 0..5u8 {
            handles.push(t.send(&conn, vec![i; 200]).await);
        }
        let mut got = vec![];
        for _ in 0..5 {
            got.push(rx.recv().await.unwrap()[0]);
        }
        assert_eq!(got, vec![0, 1, 2, 3, 4]);
        for h in handles {
            let o = h.await.unwrap();
            assert_eq!(o.result, StreamResult::Finished, "{o:?}");
            assert!(o.stopped_ns.unwrap() >= o.send_end_ns.unwrap());
        }
        assert_eq!(t.streams_opened(), 5);
        assert_eq!(accepted.load(Ordering::SeqCst), 5);
    }
}
