//! Time: one monotonic clock for every send mark (plan, section 5.1) and UTC for the logs.

use std::sync::OnceLock;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

static ORIGIN: OnceLock<Instant> = OnceLock::new();

/// Nanoseconds on the monotonic clock of this process (std::time::Instant), so an NTP
/// step in the middle of a run cannot shift the offset bands.
pub fn mono_ns() -> i64 {
    ns_of(Instant::now())
}

pub fn ns_of(t: Instant) -> i64 {
    let origin = *ORIGIN.get_or_init(Instant::now);
    if t >= origin {
        t.duration_since(origin).as_nanos() as i64
    } else {
        -(origin.duration_since(t).as_nanos() as i64)
    }
}

pub fn instant_of(ns: i64) -> Instant {
    let origin = *ORIGIN.get_or_init(Instant::now);
    if ns >= 0 {
        origin + Duration::from_nanos(ns as u64)
    } else {
        origin - Duration::from_nanos(ns.unsigned_abs())
    }
}

/// Sleep until a monotonic mark: coarse sleep, then a short spin for the last 2 ms.
pub fn sleep_until_ns(ns: i64) {
    let target = instant_of(ns);
    loop {
        let now = Instant::now();
        if now >= target {
            return;
        }
        let left = target - now;
        if left > Duration::from_millis(3) {
            std::thread::sleep(left - Duration::from_millis(2));
        } else {
            std::hint::spin_loop();
        }
    }
}

/// ISO 8601 UTC with milliseconds, ending in Z.
pub fn utc_now() -> String {
    let d = SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default();
    utc_of(d.as_secs() as i64, d.subsec_millis())
}

pub fn utc_of(secs: i64, millis: u32) -> String {
    let days = secs.div_euclid(86_400);
    let rem = secs.rem_euclid(86_400);
    let (y, m, d) = civil_from_days(days);
    format!(
        "{y:04}-{m:02}-{d:02}T{:02}:{:02}:{:02}.{millis:03}Z",
        rem / 3600,
        rem % 3600 / 60,
        rem % 60
    )
}

/// Days since 1970-01-01 to a proleptic Gregorian date (H. Hinnant's algorithm).
fn civil_from_days(z: i64) -> (i64, u32, u32) {
    let z = z + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z.rem_euclid(146_097);
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = if mp < 10 { mp + 3 } else { mp - 9 } as u32;
    let y = yoe + era * 400 + if m <= 2 { 1 } else { 0 };
    (y, m, d)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn utc_format() {
        assert_eq!(utc_of(0, 0), "1970-01-01T00:00:00.000Z");
        // 2026-10-26 21:29:56 UTC, the moment of the TLS issuer measurement.
        assert_eq!(utc_of(1_793_050_196, 7), "2026-10-26T21:29:56.007Z");
        assert_eq!(utc_of(951_782_400, 0), "2000-02-29T00:00:00.000Z");
    }

    #[test]
    fn monotonic_marks_round_trip() {
        let a = mono_ns();
        let t = instant_of(a + 5_000_000);
        assert_eq!(ns_of(t), a + 5_000_000);
        sleep_until_ns(a + 3_000_000);
        assert!(mono_ns() >= a + 3_000_000);
    }
}
