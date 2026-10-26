//! Base58 with the Bitcoin alphabet, the text form of Solana keys, hashes and signatures.

const ALPHABET: &[u8; 58] = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

pub fn encode(bytes: &[u8]) -> String {
    let zeros = bytes.iter().take_while(|&&b| b == 0).count();
    // Base-58 digits, least significant first.
    let mut digits: Vec<u8> = Vec::with_capacity(bytes.len() * 138 / 100 + 1);
    for &b in &bytes[zeros..] {
        let mut carry = b as u32;
        for d in digits.iter_mut() {
            carry += (*d as u32) << 8;
            *d = (carry % 58) as u8;
            carry /= 58;
        }
        while carry > 0 {
            digits.push((carry % 58) as u8);
            carry /= 58;
        }
    }
    let mut out = String::with_capacity(zeros + digits.len());
    out.extend(std::iter::repeat('1').take(zeros));
    out.extend(digits.iter().rev().map(|&d| ALPHABET[d as usize] as char));
    out
}

pub fn decode(s: &str) -> Result<Vec<u8>, String> {
    let zeros = s.bytes().take_while(|&c| c == b'1').count();
    // Bytes, least significant first.
    let mut bytes: Vec<u8> = Vec::with_capacity(s.len());
    for c in s.bytes().skip(zeros) {
        let v = ALPHABET
            .iter()
            .position(|&a| a == c)
            .ok_or_else(|| format!("not base58: {s:?}"))? as u32;
        let mut carry = v;
        for b in bytes.iter_mut() {
            carry += (*b as u32) * 58;
            *b = (carry & 0xff) as u8;
            carry >>= 8;
        }
        while carry > 0 {
            bytes.push((carry & 0xff) as u8);
            carry >>= 8;
        }
    }
    let mut out = vec![0u8; zeros];
    out.extend(bytes.iter().rev());
    Ok(out)
}

pub fn decode32(s: &str) -> Result<[u8; 32], String> {
    let v = decode(s)?;
    v.as_slice()
        .try_into()
        .map_err(|_| format!("expected 32 bytes, got {} from {s:?}", v.len()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trip_and_known_values() {
        assert_eq!(encode(&[0u8; 32]), "11111111111111111111111111111111");
        let sys = decode32("11111111111111111111111111111111").unwrap();
        assert_eq!(sys, [0u8; 32]);
        let tick = "tickUcsEQegChaAuo9VYQQztB4ZGApY6ZT4FkULWY6N";
        assert_eq!(encode(&decode32(tick).unwrap()), tick);
        assert_eq!(encode(b"hello world"), "StV1DL6CwTryKyV");
        assert!(decode("0OIl").is_err());
    }
}
