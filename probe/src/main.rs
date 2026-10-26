//! itb-probe: sends probe bursts into chosen leader windows over direct QUIC.
//!
//! Dry-run is the default. Real sending needs `--live` together with an explicit
//! `--max-spend-lamports N`, and N can only lower the limit compiled in below
//! (plan-implementation, section 11).
//!
//!   itb-probe run --plan FILE [--close-after] [--live --max-spend-lamports N]
//!   itb-probe close [--live --max-spend-lamports N]
//!   itb-probe status
//!   itb-probe clock [--seconds N] [--connections K]
//!
//! Exit codes: 0 done, 1 refused or failed (the message names why), 64 bad arguments.

mod b58;
mod chain;
mod clock;
mod clockcheck;
mod journal;
mod keys;
mod plan;
mod quic;
mod rows;
mod rpc;
mod session;
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

#[derive(Debug, PartialEq, Eq)]
pub enum Command {
    Run { plan: String, close_after: bool, mode: Mode },
    Close { mode: Mode },
    Status,
    Clock { seconds: u64, connections: usize },
}

/// The public node allows 10 subscriptions and each connection of the check takes two.
const MAX_CLOCK_CONNECTIONS: usize = 5;

/// Split the subcommand and its own flags from the mode flags parse_mode reads.
pub fn parse_command(args: &[String]) -> Result<Command, String> {
    let (sub, rest) = args.split_first().ok_or("usage: itb-probe run --plan FILE | close | status | clock")?;
    let mut plan = None;
    let mut close_after = false;
    let mut seconds: u64 = 180;
    let mut connections: usize = 4;
    let mut mode_args = vec![];
    let mut i = 0;
    let number = |flag: &str, v: Option<&String>| -> Result<u64, String> {
        let v = v.ok_or(format!("{flag} needs a value"))?;
        v.parse().map_err(|_| format!("{flag}: not a whole number: {v}"))
    };
    while i < rest.len() {
        match rest[i].as_str() {
            "--plan" if sub == "run" => {
                plan = Some(rest.get(i + 1).ok_or("--plan needs a file")?.clone());
                i += 1;
            }
            "--close-after" if sub == "run" => close_after = true,
            "--seconds" if sub == "clock" => {
                seconds = number("--seconds", rest.get(i + 1))?;
                i += 1;
            }
            "--connections" if sub == "clock" => {
                connections = number("--connections", rest.get(i + 1))? as usize;
                i += 1;
            }
            other => mode_args.push(other.to_string()),
        }
        i += 1;
    }
    match sub.as_str() {
        "run" => Ok(Command::Run { plan: plan.ok_or("run needs --plan FILE")?, close_after, mode: parse_mode(&mode_args)? }),
        "close" => Ok(Command::Close { mode: parse_mode(&mode_args)? }),
        "status" if mode_args.is_empty() => Ok(Command::Status),
        "status" => Err(format!("status takes no arguments: {}", mode_args.join(" "))),
        "clock" if !mode_args.is_empty() => Err(format!("clock takes --seconds and --connections only: {}", mode_args.join(" "))),
        "clock" if seconds == 0 || !(1..=MAX_CLOCK_CONNECTIONS).contains(&connections) => {
            Err(format!("clock needs --seconds above 0 and --connections from 1 to {MAX_CLOCK_CONNECTIONS}"))
        }
        "clock" => Ok(Command::Clock { seconds, connections }),
        other => Err(format!("unknown command {other}; expected run, close, status or clock")),
    }
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let cmd = match parse_command(&args) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("itb-probe: {e}");
            return ExitCode::from(64);
        }
    };
    let settings = session::Settings::from_env();
    let result = match &cmd {
        Command::Run { plan, close_after, mode } => session::run(&settings, mode, std::path::Path::new(plan), *close_after),
        Command::Close { mode } => session::close(&settings, mode),
        Command::Status => session::status(&settings),
        Command::Clock { seconds, connections } => clockcheck::check(&settings, *seconds, *connections),
    };
    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("itb-probe: {e}");
            ExitCode::from(1)
        }
    }
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
    fn commands_parse_with_their_own_flags() {
        assert_eq!(
            parse_command(&args(&["run", "--plan", "p.json"])),
            Ok(Command::Run { plan: "p.json".into(), close_after: false, mode: Mode::DryRun })
        );
        assert_eq!(
            parse_command(&args(&["run", "--live", "--plan", "p.json", "--max-spend-lamports", "9", "--close-after"])),
            Ok(Command::Run { plan: "p.json".into(), close_after: true, mode: Mode::Live { max_spend_lamports: 9 } })
        );
        assert!(parse_command(&args(&["run"])).is_err());
        assert!(parse_command(&args(&["run", "--plan", "p.json", "--live"])).is_err());
        assert_eq!(parse_command(&args(&["close"])), Ok(Command::Close { mode: Mode::DryRun }));
        assert!(parse_command(&args(&["close", "--plan", "p.json"])).is_err());
        assert!(parse_command(&args(&["status", "--live"])).is_err());
        assert!(parse_command(&args(&["send"])).is_err());
        assert!(parse_command(&args(&[])).is_err());
        assert_eq!(parse_command(&args(&["clock"])), Ok(Command::Clock { seconds: 180, connections: 4 }));
        assert_eq!(
            parse_command(&args(&["clock", "--seconds", "60", "--connections", "2"])),
            Ok(Command::Clock { seconds: 60, connections: 2 })
        );
        assert!(parse_command(&args(&["clock", "--connections", "6"])).is_err());
        assert!(parse_command(&args(&["clock", "--seconds", "0"])).is_err());
        assert!(parse_command(&args(&["clock", "--live"])).is_err());
        assert!(parse_command(&args(&["run", "--plan", "p.json", "--seconds", "5"])).is_err());
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
