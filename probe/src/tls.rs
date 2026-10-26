//! Who issued the RPC node's certificate, as this container sees it (plan, section 11).
//!
//! The campaign machine runs Avast, whose Web Shield re-signs HTTPS with its own root:
//! on 2026-10-26 a container saw "Avast Web/Mail Shield Root" for crates.io and
//! github.com and the genuine ZeroSSL issuer for api.mainnet-beta.solana.com. The check
//! records the end-entity certificate inside a verifier that delegates every decision
//! to the standard WebPKI verifier, so verification is never relaxed; on a rejected
//! chain the recorded certificate still names who signed it.

use rustls::client::danger::{HandshakeSignatureValid, ServerCertVerified, ServerCertVerifier};
use rustls::client::WebPkiServerVerifier;
use rustls::pki_types::{CertificateDer, ServerName, UnixTime};
use rustls::{ClientConfig, ClientConnection, DigitallySignedStruct, RootCertStore, SignatureScheme};
use std::io::Write;
use std::net::TcpStream;
use std::sync::{Arc, Mutex};
use std::time::Duration;

#[derive(Debug)]
struct Recording {
    inner: Arc<WebPkiServerVerifier>,
    seen: Mutex<Option<Vec<u8>>>,
}

impl ServerCertVerifier for Recording {
    fn verify_server_cert(
        &self,
        end_entity: &CertificateDer<'_>,
        intermediates: &[CertificateDer<'_>],
        server_name: &ServerName<'_>,
        ocsp: &[u8],
        now: UnixTime,
    ) -> Result<ServerCertVerified, rustls::Error> {
        *self.seen.lock().unwrap() = Some(end_entity.to_vec());
        self.inner.verify_server_cert(end_entity, intermediates, server_name, ocsp, now)
    }

    fn verify_tls12_signature(
        &self,
        message: &[u8],
        cert: &CertificateDer<'_>,
        dss: &DigitallySignedStruct,
    ) -> Result<HandshakeSignatureValid, rustls::Error> {
        self.inner.verify_tls12_signature(message, cert, dss)
    }

    fn verify_tls13_signature(
        &self,
        message: &[u8],
        cert: &CertificateDer<'_>,
        dss: &DigitallySignedStruct,
    ) -> Result<HandshakeSignatureValid, rustls::Error> {
        self.inner.verify_tls13_signature(message, cert, dss)
    }

    fn supported_verify_schemes(&self) -> Vec<SignatureScheme> {
        self.inner.supported_verify_schemes()
    }
}

pub struct Issuer {
    pub host: String,
    pub issuer: String,
    pub verified: bool,
    pub error: Option<String>,
}

impl Issuer {
    /// A local antivirus proxy re-signs the traffic: the measurement must not run.
    pub fn intercepted(&self) -> bool {
        let i = self.issuer.to_ascii_lowercase();
        ["avast", "avg ", "kaspersky", "eset", "bitdefender", "for ssl/tls scanning"]
            .iter()
            .any(|m| i.contains(m))
    }
}

pub fn https_issuer(url: &str) -> Result<Issuer, String> {
    let rest = url.split_once("://").map(|x| x.1).unwrap_or(url);
    let hostport = rest.split(['/', '?']).next().unwrap_or("");
    let (host, port) = match hostport.rsplit_once(':') {
        Some((h, p)) if p.chars().all(|c| c.is_ascii_digit()) => (h.to_string(), p.parse().unwrap_or(443)),
        _ => (hostport.to_string(), 443u16),
    };
    let roots = RootCertStore { roots: webpki_roots::TLS_SERVER_ROOTS.to_vec() };
    let provider = Arc::new(rustls::crypto::ring::default_provider());
    let inner = WebPkiServerVerifier::builder_with_provider(Arc::new(roots), provider.clone())
        .build()
        .map_err(|e| format!("verifier: {e}"))?;
    let recording = Arc::new(Recording { inner, seen: Mutex::new(None) });
    let config = ClientConfig::builder_with_provider(provider)
        .with_safe_default_protocol_versions()
        .map_err(|e| e.to_string())?
        .dangerous()
        .with_custom_certificate_verifier(recording.clone())
        .with_no_client_auth();
    let name = ServerName::try_from(host.clone()).map_err(|e| format!("{host}: {e}"))?;
    let mut conn = ClientConnection::new(Arc::new(config), name).map_err(|e| e.to_string())?;
    let mut sock = TcpStream::connect((host.as_str(), port)).map_err(|e| format!("{host}:{port}: {e}"))?;
    sock.set_read_timeout(Some(Duration::from_secs(15))).ok();
    let mut error = None;
    while conn.is_handshaking() {
        if let Err(e) = conn.complete_io(&mut sock) {
            error = Some(e.to_string());
            break;
        }
    }
    conn.send_close_notify();
    let _ = conn.complete_io(&mut sock);
    let _ = sock.flush();
    let der = recording.seen.lock().unwrap().clone();
    let issuer = match der {
        Some(d) => x509_parser::parse_x509_certificate(&d)
            .map(|(_, c)| c.issuer().to_string())
            .unwrap_or_else(|e| format!("unparsed certificate ({e})")),
        None => "no certificate received".into(),
    };
    Ok(Issuer { host, issuer, verified: error.is_none(), error })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn antivirus_issuers_are_flagged() {
        let mk = |s: &str| Issuer { host: "h".into(), issuer: s.into(), verified: false, error: None };
        assert!(mk("OU=generated by Avast Antivirus for SSL/TLS scanning, O=Avast Web/Mail Shield, CN=Avast Web/Mail Shield Root").intercepted());
        assert!(!mk("C=AT, O=ZeroSSL GmbH, CN=ZeroSSL ECC DV SSL CA 2").intercepted());
    }
}
