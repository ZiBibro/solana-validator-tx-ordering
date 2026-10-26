//! Blocking JSON-RPC client. Every getTransaction carries maxSupportedTransactionVersion 1
//! as an integer, without which the node refuses a v1 transaction (stage 3 finding).

use base64::Engine as _;
use serde_json::{json, Value};
use std::time::Duration;

pub const MAX_TX_VERSION: u64 = 1;
const STATUS_BATCH: usize = 256;
const SIGNATURE_PAGE: u64 = 1000;

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
                    if let Some(e) = v.get("error") {
                        return Err(err(e["code"].as_i64(), e["message"].as_str().unwrap_or("").to_string()));
                    }
                    return Ok(v["result"].clone());
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

    /// Every signature of an address, newest first, paging with `before`.
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
            before = page.last().and_then(|e| e["signature"].as_str()).map(String::from);
            out.extend(page);
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
