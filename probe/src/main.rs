//! itb-probe: sends probe bursts into chosen leader windows over direct QUIC.
//!
//! Dry-run is the default. Real sending needs `--live` together with an explicit
//! `--max-spend-lamports N`, and N can only lower the limit compiled in below
//! (plan-implementation, section 11).

mod b58;
mod clock;
mod journal;
mod keys;
mod quic;
mod rows;
mod rpc;
mod slots;
mod tls;
mod tx;

use std::process::ExitCode;

/// Fee spend limit compiled into the binary: 0.05 SOL. A flag may lower it, never raise it.
pub const SPEND_LIMIT_LAMPORTS: u64 = 50_000_000;

#[derive(Debug, PartialEq, Eq)]
pub enum Mode {
    DryRun,
    Live { max_spend_lamports: u64 },
}

/// Parse the command line into a mode. Errors are messages for the operator.
pub fn parse_mode(args: &[String]) -> Result<Mode, String> {
    let mut live = false;
    let mut max_spend: Option<u64> = None;
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--live" => live = true,
            "--max-spend-lamports" => {
                let v = args
                    .get(i + 1)
                    .ok_or("--max-spend-lamports needs a value")?;
                let n: u64 = v
                    .parse()
                    .map_err(|_| format!("--max-spend-lamports: not a whole number of lamports: {v}"))?;
                if n > SPEND_LIMIT_LAMPORTS {
                    return Err(format!(
                        "--max-spend-lamports {n} exceeds the compiled limit {SPEND_LIMIT_LAMPORTS}; the flag can only lower it"
                    ));
                }
                max_spend = Some(n);
                i += 1;
            }
            other => return Err(format!("unknown argument: {other}")),
        }
        i += 1;
    }
    match (live, max_spend) {
        (false, _) => Ok(Mode::DryRun),
        (true, Some(n)) => Ok(Mode::Live { max_spend_lamports: n }),
        (true, None) => Err("--live needs an explicit --max-spend-lamports N".into()),
    }
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mode = match parse_mode(&args) {
        Ok(m) => m,
        Err(e) => {
            eprintln!("itb-probe: {e}");
            return ExitCode::from(64);
        }
    };
    println!("itb-probe: mode {mode:?}, compiled limit {SPEND_LIMIT_LAMPORTS} lamports");
    eprintln!("itb-probe: sending is not implemented yet (build stage 4 of plan-implementation)");
    ExitCode::from(2)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn args(list: &[&str]) -> Vec<String> {
        list.iter().map(|s| s.to_string()).collect()
    }

    #[test]
    fn limit_is_five_hundredths_of_a_sol() {
        assert_eq!(SPEND_LIMIT_LAMPORTS, 50_000_000);
    }

    #[test]
    fn dry_run_is_the_default() {
        assert_eq!(parse_mode(&args(&[])), Ok(Mode::DryRun));
        assert_eq!(parse_mode(&args(&["--max-spend-lamports", "10"])), Ok(Mode::DryRun));
    }

    #[test]
    fn live_needs_an_explicit_amount() {
        assert!(parse_mode(&args(&["--live"])).is_err());
        assert_eq!(
            parse_mode(&args(&["--live", "--max-spend-lamports", "4300000"])),
            Ok(Mode::Live { max_spend_lamports: 4_300_000 })
        );
    }

    #[test]
    fn flag_cannot_raise_the_limit() {
        let at = SPEND_LIMIT_LAMPORTS.to_string();
        let over = (SPEND_LIMIT_LAMPORTS + 1).to_string();
        assert!(parse_mode(&args(&["--live", "--max-spend-lamports", &at])).is_ok());
        assert!(parse_mode(&args(&["--live", "--max-spend-lamports", &over])).is_err());
    }

    #[test]
    fn raw_format_schema_is_reachable() {
        // The probe writes rows in the format of schema/raw-format.json; the build
        // context carries it so later row tests can check field names against it.
        let schema = include_str!("../../schema/raw-format.json");
        for kind in ["\"run\"", "\"burst\"", "\"probe\"", "\"send\"", "\"burst_end\""] {
            assert!(schema.contains(kind), "schema lacks kind {kind}");
        }
    }
}
