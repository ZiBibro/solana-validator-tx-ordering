//! Blocking JSON-RPC client. Every getTransaction carries maxSupportedTransactionVersion 1
//! as an integer, without which the node refuses a v1 transaction (stage 3 finding).

use base64::Engine as _;
use serde_json::{json, Value};
use std::time::Duration;

pub const MAX_TX_VERSION: u64 = 1;
const STATUS_BATCH: usize = 256;
const SIGNATURE_PAGE: u64 = 1000;
/// JSON-RPC errors the node asks to retry. In Agave's custom_error.rs only -32019,
/// LongTermStorageUnreachable, says "please try again", and only reads of long-term
/// storage return it, so a retry never repeats a send. A public node returned it to
/// getSignaturesForAddress on 2026-10-29 and failed a campaign run at its start.
const TRANSIENT_CODES: &[i64] = &[-32019];

pub struct Rpc {
    agent: ureq::Agent,
    url: String,
    pub calls: u64,
}

#[derive(Debug)]
pub struct RpcError {
    pub method: String,
    pub code: Option<i64>,
    pub message: String,
}

impl std::fmt::Display for RpcError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self.code {
            Some(c) => write!(f, "{}: error {c}: {}", self.method, self.message),
            None => write!(f, "{}: {}", self.method, self.message),
        }
    }
}

impl From<RpcError> for String {
    fn from(e: RpcError) -> String {
        e.to_string()
    }
}

pub type R<T> = Result<T, RpcError>;

impl Rpc {
    pub fn new(url: &str) -> Rpc {
        let agent = ureq::AgentBuilder::new()
            .timeout(Duration::from_secs(60))
            .user_agent(concat!("itb-probe/", env!("CARGO_PKG_VERSION")))
            .build();
        Rpc { agent, url: url.to_string(), calls: 0 }
    }

    pub fn call(&mut self, method: &str, params: Value) -> R<Value> {
        let body = json!({"jsonrpc": "2.0", "id": 1, "method": method, "params": params});
        let err = |code: Option<i64>, message: String| RpcError { method: method.into(), code, message };
        let mut wait = Duration::from_millis(500);
        for attempt in 0..6 {
            self.calls += 1;
            match self.agent.post(&self.url).send_json(&body) {
                Ok(resp) => {
                    let v: Value = resp.into_json().map_err(|e| err(None, format!("bad JSON: {e}")))?;
                    let Some(e) = v.get("error") else {
                        return Ok(v["result"].clone());
                    };
                    let code = e["code"].as_i64();
                    if attempt == 5 || !code.is_some_and(|c| TRANSIENT_CODES.contains(&c)) {
                        return Err(err(code, e["message"].as_str().unwrap_or("").to_string()));
                    }
                    std::thread::sleep(wait);
                }
                Err(ureq::Error::Status(code, resp)) if code == 429 || code >= 500 => {
                    let after = resp
                        .header("retry-after")
                        .and_then(|s| s.parse::<u64>().ok())
                        .map(Duration::from_secs);
                    if attempt == 5 {
                        return Err(err(Some(code as i64), format!("HTTP {code}")));
                    }
                    std::thread::sleep(after.unwrap_or(wait));
                }
                Err(ureq::Error::Status(code, _)) => return Err(err(Some(code as i64), format!("HTTP {code}"))),
                Err(ureq::Error::Transport(t)) => {
                    if attempt == 5 {
                        // Kind and message only: Display of a transport error carries the
                        // full URL, and paid RPC URLs carry API keys.
                        let msg = t.message().unwrap_or("").replace(&self.url, &crate::rows::origin(&self.url));
                        return Err(err(None, format!("{} {msg}", t.kind())));
                    }
                    std::thread::sleep(wait);
                }
            }
            wait = (wait * 2).min(Duration::from_secs(8));
        }
        unreachable!()
    }

    /// (blockhash, lastValidBlockHeight, context slot).
    pub fn latest_blockhash(&mut self, commitment: &str) -> R<(String, u64, u64)> {
        let v = self.call("getLatestBlockhash", json!([{"commitment": commitment}]))?;
        Ok((
            v["value"]["blockhash"].as_str().unwrap_or("").to_string(),
            v["value"]["lastValidBlockHeight"].as_u64().unwrap_or(0),
            v["context"]["slot"].as_u64().unwrap_or(0),
        ))
    }

    pub fn block_height(&mut self, commitment: &str) -> R<u64> {
        Ok(self.call("getBlockHeight", json!([{"commitment": commitment}]))?.as_u64().unwrap_or(0))
    }

    pub fn cluster_nodes(&mut self) -> R<Vec<Value>> {
        Ok(self.call("getClusterNodes", json!([]))?.as_array().cloned().unwrap_or_default())
    }

    pub fn epoch_schedule(&mut self) -> R<Value> {
        self.call("getEpochSchedule", json!([]))
    }

    /// Leader schedule of the epoch containing `slot`: identity to slot indices.
    pub fn leader_schedule(&mut self, slot: u64) -> R<Value> {
        self.call("getLeaderSchedule", json!([slot, {"commitment": "finalized"}]))
    }

    pub fn min_rent(&mut self, bytes: u64) -> R<u64> {
        Ok(self.call("getMinimumBalanceForRentExemption", json!([bytes]))?.as_u64().unwrap_or(0))
    }

    /// Lamports of each address; 0 for an account that does not exist.
    pub fn balances(&mut self, addresses: &[String]) -> R<Vec<u64>> {
        let v = self.call(
            "getMultipleAccounts",
            json!([addresses, {"commitment": "finalized", "encoding": "base64", "dataSlice": {"offset": 0, "length": 0}}]),
        )?;
        Ok(v["value"]
            .as_array()
            .map(|a| a.iter().map(|x| x["lamports"].as_u64().unwrap_or(0)).collect())
            .unwrap_or_default())
    }

    /// Statuses with transaction history, in the order of `sigs`.
    pub fn signature_statuses(&mut self, sigs: &[String]) -> R<Vec<Option<Value>>> {
        let mut out = Vec::with_capacity(sigs.len());
        for chunk in sigs.chunks(STATUS_BATCH) {
            let v = self.call("getSignatureStatuses", json!([chunk, {"searchTransactionHistory": true}]))?;
            for s in v["value"].as_array().cloned().unwrap_or_default() {
                out.push(if s.is_null() { None } else { Some(s) });
            }
        }
        Ok(out)
    }

    pub fn transaction(&mut self, sig: &str) -> R<Option<Value>> {
        let v = self.call(
            "getTransaction",
            json!([sig, {"encoding": "json", "commitment": "finalized", "maxSupportedTransactionVersion": MAX_TX_VERSION}]),
        )?;
        Ok(if v.is_null() { None } else { Some(v) })
    }

    /// Every signature of an address, newest first, paging with `before`. A page shorter
    /// than the limit is the last: the node fills a page from its own ledger and then from
    /// long-term storage, and a failure of that storage comes back as -32019, not as a
    /// short page (Agave rpc.rs, get_signatures_for_address).
    pub fn signatures_for_address(&mut self, address: &str) -> R<Vec<Value>> {
        let mut out = vec![];
        let mut before: Option<String> = None;
        loop {
            let mut opts = json!({"limit": SIGNATURE_PAGE, "commitment": "finalized"});
            if let Some(b) = &before {
                opts["before"] = json!(b);
            }
            let page = self.call("getSignaturesForAddress", json!([address, opts]))?;
            let page = page.as_array().cloned().unwrap_or_default();
            if page.is_empty() {
                return Ok(out);
            }
            let last = (page.len() as u64) < SIGNATURE_PAGE;
            before = page.last().and_then(|e| e["signature"].as_str()).map(String::from);
            out.extend(page);
            if last {
                return Ok(out);
            }
        }
    }

    /// sendTransaction; `max_retries` None lets the node rebroadcast until expiry.
    pub fn send(&mut self, wire: &[u8], skip_preflight: bool, max_retries: Option<u64>) -> R<String> {
        let b64 = base64::engine::general_purpose::STANDARD.encode(wire);
        let mut opts = json!({"encoding": "base64", "skipPreflight": skip_preflight, "preflightCommitment": "confirmed"});
        if let Some(n) = max_retries {
            opts["maxRetries"] = json!(n);
        }
        let v = self.call("sendTransaction", json!([b64, opts]))?;
        Ok(v.as_str().unwrap_or("").to_string())
    }

    pub fn simulate(&mut self, wire: &[u8], sig_verify: bool) -> R<Value> {
        let b64 = base64::engine::general_purpose::STANDARD.encode(wire);
        let v = self.call(
            "simulateTransaction",
            json!([b64, {"encoding": "base64", "sigVerify": sig_verify, "replaceRecentBlockhash": !sig_verify, "commitment": "confirmed"}]),
        )?;
        Ok(v["value"].clone())
    }
}

#[cfg(test)]
pub(crate) mod tests {
    use super::*;
    use std::io::{BufRead, BufReader, Read, Write};
    use std::net::TcpListener;
    use std::sync::{Arc, Mutex};

    /// A local HTTP server that answers request n with replies[n] and closes the
    /// connection; it records each JSON-RPC request body it reads.
    pub(crate) fn serve(replies: Vec<Value>) -> (Rpc, Arc<Mutex<Vec<Value>>>) {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let url = format!("http://{}", listener.local_addr().unwrap());
        let seen = Arc::new(Mutex::new(vec![]));
        let log = seen.clone();
        std::thread::spawn(move || {
            for reply in replies {
                let Ok((stream, _)) = listener.accept() else { return };
                let mut reader = BufReader::new(stream);
                let mut len = 0;
                loop {
                    let mut line = String::new();
                    if reader.read_line(&mut line).unwrap_or(0) == 0 {
                        return;
                    }
                    let line = line.trim_end();
                    if line.is_empty() {
                        break;
                    }
                    if let Some((k, v)) = line.split_once(':') {
                        if k.eq_ignore_ascii_case("content-length") {
                            len = v.trim().parse().unwrap_or(0);
                        }
                    }
                }
                let mut body = vec![0; len];
                reader.read_exact(&mut body).unwrap();
                log.lock().unwrap().push(serde_json::from_slice(&body).unwrap_or(Value::Null));
                let text = reply.to_string();
                let mut stream = reader.into_inner();
                let _ = write!(
                    stream,
                    "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{text}",
                    text.len()
                );
            }
        });
        (Rpc::new(&url), seen)
    }

    fn rpc_error(code: i64, message: &str) -> Value {
        json!({"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": 1})
    }

    fn page(from: usize, n: usize) -> Value {
        let entries: Vec<Value> = (from..from + n).map(|i| json!({"signature": format!("sig{i}"), "slot": i})).collect();
        json!({"jsonrpc": "2.0", "result": entries, "id": 1})
    }

    #[test]
    fn long_term_storage_error_is_retried() {
        let (mut rpc, seen) = serve(vec![
            rpc_error(-32019, "Failed to query long-term storage; please try again"),
            json!({"jsonrpc": "2.0", "result": 7, "id": 1}),
        ]);
        assert_eq!(rpc.block_height("finalized").unwrap(), 7);
        assert_eq!(seen.lock().unwrap().len(), 2);
    }

    #[test]
    fn other_rpc_errors_are_not_retried() {
        let preflight = rpc_error(-32002, "Transaction simulation failed");
        let (mut rpc, seen) = serve(vec![preflight; 6]);
        let e = rpc.call("sendTransaction", json!([])).unwrap_err();
        assert_eq!(e.code, Some(-32002));
        assert_eq!(seen.lock().unwrap().len(), 1);
    }

    #[test]
    fn signature_listing_stops_at_a_short_page() {
        let full = SIGNATURE_PAGE as usize;
        let (mut rpc, seen) = serve(vec![page(0, full), page(full, 3), page(full + 3, 1)]);
        let sigs = rpc.signatures_for_address("addr").unwrap();
        assert_eq!(sigs.len(), full + 3);
        let seen = seen.lock().unwrap();
        assert_eq!(seen.len(), 2);
        assert_eq!(seen[1]["params"][1]["before"], json!(format!("sig{}", full - 1)));
    }
}
