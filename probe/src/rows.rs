//! Raw rows and the operational log, in the format of schema/raw-format.json (plan,
//! section 8). Every row is checked against the schema before it is written, the same
//! file Python validates with, so the two sides cannot drift apart.

use serde_json::{Map, Value};
use std::fs::{File, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

const SCHEMA_TEXT: &str = include_str!("../../schema/raw-format.json");

fn schema() -> &'static Value {
    static S: OnceLock<Value> = OnceLock::new();
    S.get_or_init(|| serde_json::from_str(SCHEMA_TEXT).expect("schema/raw-format.json is JSON"))
}

pub fn schema_version() -> u64 {
    schema()["version"].as_u64().expect("schema version")
}

/// Problems of one row against the schema; empty when valid.
pub fn validate(row: &Value) -> Vec<String> {
    let s = schema();
    let mut out = vec![];
    let Some(obj) = row.as_object() else { return vec!["row is not an object".into()] };
    if obj.get("v").and_then(Value::as_u64) != Some(schema_version()) {
        out.push("v: wrong schema version".into());
    }
    let kind = obj.get("kind").and_then(Value::as_str).unwrap_or("");
    let Some(fields) = s["kinds"][kind]["fields"].as_object() else {
        out.push(format!("kind: unknown {kind:?}"));
        return out;
    };
    for name in obj.keys() {
        if name != "v" && name != "kind" && !fields.contains_key(name) {
            out.push(format!("{name}: unknown field"));
        }
    }
    for (name, spec) in fields {
        match obj.get(name) {
            None => out.push(format!("{name}: missing")),
            Some(v) => out.extend(check_value(spec, v).into_iter().map(|w| format!("{name}: {w}"))),
        }
    }
    out
}

fn check_value(spec: &Value, v: &Value) -> Vec<String> {
    let ty = spec["type"].as_str().unwrap_or("");
    let (ty, nullable) = match ty.strip_suffix('?') {
        Some(t) => (t, true),
        None => (ty, false),
    };
    if v.is_null() {
        return if nullable { vec![] } else { vec!["null not allowed".into()] };
    }
    let mut out = vec![];
    if let Some(inner) = ty.strip_prefix("list<").and_then(|t| t.strip_suffix('>')) {
        let Some(items) = v.as_array() else { return vec!["expected list".into()] };
        let mut item_spec = spec.clone();
        item_spec["type"] = Value::String(inner.to_string());
        for it in items {
            out.extend(check_value(&item_spec, it));
        }
        return out;
    }
    let ok = match ty {
        "str" => v.is_string(),
        "int" => v.is_i64() || v.is_u64(),
        "num" => v.is_number(),
        "bool" => v.is_boolean(),
        "obj" => v.is_object(),
        t if t.starts_with("enum:") => t[5..].split('|').any(|e| v.as_str() == Some(e)),
        other => {
            out.push(format!("unknown type {other}"));
            true
        }
    };
    if !ok {
        out.push(format!("expected {ty}"));
        return out;
    }
    if let (Some(fmt), Some(text)) = (spec["format"].as_str(), v.as_str()) {
        if !check_format(fmt, text) {
            out.push(format!("bad {fmt}"));
        }
    }
    if let Some(n) = v.as_f64() {
        if spec["min"].as_f64().is_some_and(|m| n < m) {
            out.push("below min".into());
        }
        if spec["max"].as_f64().is_some_and(|m| n > m) {
            out.push("above max".into());
        }
    }
    out
}

fn check_format(fmt: &str, s: &str) -> bool {
    let b58_len = |lo: usize, hi: usize| {
        (lo..=hi).contains(&s.len()) && crate::b58::decode(s).is_ok()
    };
    match fmt {
        "pubkey" | "hash" => b58_len(32, 44),
        "signature" => b58_len(64, 88),
        "sha256" => s.len() == 64 && s.bytes().all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c)),
        "utc" => s.len() >= 17 && s.ends_with('Z') && s.as_bytes().get(10) == Some(&b'T'),
        "endpoint" => endpoint_ok(s),
        _ => true,
    }
}

fn endpoint_ok(s: &str) -> bool {
    let Some((scheme, rest)) = s.split_once("://") else { return false };
    let rest = rest.strip_suffix('/').unwrap_or(rest);
    matches!(scheme, "http" | "https" | "ws" | "wss")
        && !rest.is_empty()
        && rest.chars().all(|c| c.is_ascii_alphanumeric() || c == '.' || c == '-' || c == ':')
}

/// scheme://host[:port] of a URL: paid RPC URLs carry API keys in the path or query,
/// and raw data is published.
pub fn origin(url: &str) -> String {
    let Some((scheme, rest)) = url.split_once("://") else { return url.to_string() };
    let host = rest.split(['/', '?', '#']).next().unwrap_or("");
    let host = host.rsplit('@').next().unwrap_or(host);
    format!("{scheme}://{host}")
}

pub fn row(kind: &str, fields: Value) -> Value {
    let mut m = Map::new();
    m.insert("v".into(), Value::from(schema_version()));
    m.insert("kind".into(), Value::from(kind));
    if let Value::Object(f) = fields {
        m.extend(f);
    }
    Value::Object(m)
}

/// probes.jsonl of one run. Probe rows are fsynced before the transaction is sent.
pub struct RowFile {
    path: PathBuf,
    file: File,
    pub schema_problems: Vec<String>,
}

impl RowFile {
    pub fn create_new(path: &Path) -> Result<RowFile, String> {
        if let Some(dir) = path.parent() {
            std::fs::create_dir_all(dir).map_err(|e| format!("{}: {e}", dir.display()))?;
        }
        let file = OpenOptions::new()
            .create_new(true)
            .append(true)
            .open(path)
            .map_err(|e| format!("{}: {e} (a run id is used once)", path.display()))?;
        Ok(RowFile { path: path.to_path_buf(), file, schema_problems: vec![] })
    }

    pub fn write(&mut self, kind: &str, fields: Value) -> Result<(), String> {
        let r = row(kind, fields);
        for p in validate(&r) {
            self.schema_problems.push(format!("{kind}: {p}"));
        }
        self.file
            .write_all(format!("{r}\n").as_bytes())
            .map_err(|e| format!("{}: {e}", self.path.display()))
    }

    pub fn sync(&mut self) -> Result<(), String> {
        self.file.sync_data().map_err(|e| format!("{}: fsync: {e}", self.path.display()))
    }
}

#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Debug)]
pub enum Level {
    Debug,
    Info,
    Warn,
    Error,
}

impl Level {
    pub fn parse(s: &str) -> Level {
        match s {
            "debug" => Level::Debug,
            "warn" => Level::Warn,
            "error" => Level::Error,
            _ => Level::Info,
        }
    }

    fn name(self) -> &'static str {
        match self {
            Level::Debug => "debug",
            Level::Info => "info",
            Level::Warn => "warn",
            Level::Error => "error",
        }
    }
}

/// Operational log, logs/<run_id>.jsonl (section 12): one row per event. Key material
/// never reaches it; the localnet pipeline test searches it for the test key bytes.
pub struct Log {
    file: Option<File>,
    level: Level,
    run_id: Option<String>,
}

impl Log {
    pub fn stderr_only(level: Level) -> Log {
        Log { file: None, level, run_id: None }
    }

    pub fn open(path: &Path, level: Level, run_id: &str) -> Result<Log, String> {
        if let Some(dir) = path.parent() {
            std::fs::create_dir_all(dir).map_err(|e| format!("{}: {e}", dir.display()))?;
        }
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)
            .map_err(|e| format!("{}: {e}", path.display()))?;
        Ok(Log { file: Some(file), level, run_id: Some(run_id.to_string()) })
    }

    pub fn event(&mut self, level: Level, event: &str, burst_seq: Option<u64>, data: Value) {
        if level < self.level {
            return;
        }
        let data = if data.is_null() { Value::Null } else { data };
        eprintln!("itb-probe {} {event} {}", level.name(), if data.is_null() { String::new() } else { data.to_string() });
        let r = row(
            "log",
            serde_json::json!({
                "ts": crate::clock::utc_now(), "level": level.name(), "service": "probe",
                "run_id": self.run_id, "burst_seq": burst_seq, "event": event, "data": data,
            }),
        );
        if let Some(f) = self.file.as_mut() {
            let _ = f.write_all(format!("{r}\n").as_bytes());
        }
    }

    pub fn info(&mut self, event: &str, burst_seq: Option<u64>, data: Value) {
        self.event(Level::Info, event, burst_seq, data)
    }

    pub fn warn(&mut self, event: &str, burst_seq: Option<u64>, data: Value) {
        self.event(Level::Warn, event, burst_seq, data)
    }

    pub fn error(&mut self, event: &str, burst_seq: Option<u64>, data: Value) {
        self.event(Level::Error, event, burst_seq, data)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn schema_check_catches_drift() {
        let good = row(
            "log",
            json!({"ts": "2026-10-26T21:00:00.000Z", "level": "info", "service": "probe",
                   "run_id": null, "burst_seq": null, "event": "start", "data": null}),
        );
        assert!(validate(&good).is_empty(), "{:?}", validate(&good));
        let mut extra = good.clone();
        extra["surprise"] = json!(1);
        assert_eq!(validate(&extra), vec!["surprise: unknown field".to_string()]);
        let mut wrong = good.clone();
        wrong["level"] = json!("loud");
        assert_eq!(validate(&wrong).len(), 1);
        let mut missing = good;
        missing.as_object_mut().unwrap().remove("event");
        assert_eq!(validate(&missing), vec!["event: missing".to_string()]);
    }

    #[test]
    fn origin_strips_paths_and_keys() {
        assert_eq!(origin("https://rpc.example.com/v2/SECRET?api-key=x"), "https://rpc.example.com");
        assert_eq!(origin("wss://user:pw@node.example:8900/"), "wss://node.example:8900");
        assert!(endpoint_ok(&origin("https://api.mainnet-beta.solana.com")));
    }
}
