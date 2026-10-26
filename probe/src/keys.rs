//! Wallet key and the twelve payers derived from it (plan, section 11).
//!
//! The key arrives only as a Compose secret (file or environment variable) mounted
//! read-only. Nothing here formats key bytes: Signer has no Debug, and errors name the
//! problem without the content.

use ed25519_dalek::{Signer as _, SigningKey};
use hmac::{Hmac, Mac};
use sha2::{Digest, Sha256, Sha512};
use std::path::Path;

pub const PAYERS: usize = 12;

pub struct Signer {
    key: SigningKey,
}

impl Signer {
    pub fn from_seed(seed: &[u8; 32]) -> Self {
        Signer { key: SigningKey::from_bytes(seed) }
    }

    pub fn pubkey(&self) -> [u8; 32] {
        self.key.verifying_key().to_bytes()
    }

    pub fn address(&self) -> String {
        crate::b58::encode(&self.pubkey())
    }

    pub fn sign(&self, message: &[u8]) -> [u8; 64] {
        self.key.sign(message).to_bytes()
    }

    fn seed(&self) -> [u8; 32] {
        self.key.to_bytes()
    }
}

/// Read the wallet key. Ok(None) means "no key": the path is missing, or it is the
/// empty directory Docker mounts in place of a missing secret file (stage 1 finding).
pub fn load_wallet(path: &Path) -> Result<Option<Signer>, String> {
    let meta = match std::fs::metadata(path) {
        Ok(m) => m,
        Err(_) => return Ok(None),
    };
    if meta.is_dir() {
        return Ok(None);
    }
    let text = std::fs::read_to_string(path)
        .map_err(|e| format!("wallet key at {}: cannot read ({})", path.display(), e.kind()))?;
    parse_keypair_json(&text).map(Some)
}

/// solana-keygen format: a JSON array of 64 numbers, secret seed then public key.
fn parse_keypair_json(text: &str) -> Result<Signer, String> {
    let bytes: Vec<u8> = serde_json::from_str(text.trim())
        .map_err(|_| "wallet key: not a JSON array of 64 bytes (solana-keygen format)".to_string())?;
    if bytes.len() != 64 {
        return Err(format!("wallet key: {} bytes, expected 64", bytes.len()));
    }
    let seed: [u8; 32] = bytes[..32].try_into().unwrap();
    let signer = Signer::from_seed(&seed);
    if signer.pubkey()[..] != bytes[32..] {
        return Err("wallet key: public half does not match the secret half".into());
    }
    Ok(signer)
}

/// Payer n (1..=12): HMAC-SHA512 keyed with the wallet seed over "itb-payer-<n>"; the
/// first 32 bytes are the ed25519 seed. Deterministic, so payers need no storage and
/// their addresses are always known for the chain reconciliation and for closing.
pub fn derive_payer(wallet: &Signer, n: usize) -> Signer {
    let mut mac = Hmac::<Sha512>::new_from_slice(&wallet.seed()).expect("any key length");
    mac.update(format!("itb-payer-{n}").as_bytes());
    let out = mac.finalize().into_bytes();
    Signer::from_seed(&out[..32].try_into().unwrap())
}

pub fn derive_payers(wallet: &Signer) -> Vec<Signer> {
    (1..=PAYERS).map(|n| derive_payer(wallet, n)).collect()
}

/// Dry-run wallet: a public seed, so dry-run rows carry real-looking signatures and
/// addresses that hold no funds. No secret is involved.
pub fn dry_run_wallet() -> Signer {
    let seed: [u8; 32] = Sha256::digest(b"itb-dry-run-wallet").into();
    Signer::from_seed(&seed)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_wallet(byte: u8) -> Signer {
        Signer::from_seed(&[byte; 32])
    }

    #[test]
    fn same_wallet_gives_same_payers() {
        let a: Vec<String> = derive_payers(&test_wallet(7)).iter().map(|s| s.address()).collect();
        let b: Vec<String> = derive_payers(&test_wallet(7)).iter().map(|s| s.address()).collect();
        let c: Vec<String> = derive_payers(&test_wallet(8)).iter().map(|s| s.address()).collect();
        assert_eq!(a, b);
        assert_eq!(a.len(), PAYERS);
        assert!(a.iter().zip(&c).all(|(x, y)| x != y));
        let mut uniq = a.clone();
        uniq.sort();
        uniq.dedup();
        assert_eq!(uniq.len(), PAYERS);
    }

    #[test]
    fn derivation_is_pinned() {
        // Pinned once from this code: a change of the derivation would strand the rent
        // of payers created by an earlier build, so it must fail a test first.
        let p1 = derive_payer(&test_wallet(1), 1).address();
        assert_eq!(p1, PINNED_PAYER_1);
    }

    const PINNED_PAYER_1: &str = "Ep8UTre7oDJXXUzxNYdcK8WpeMjp3Cy1cACiLABbQyqQ";

    #[test]
    fn keypair_file_forms() {
        let w = test_wallet(3);
        let mut bytes = w.seed().to_vec();
        bytes.extend_from_slice(&w.pubkey());
        let json = serde_json::to_string(&bytes).unwrap();
        assert_eq!(parse_keypair_json(&json).unwrap().address(), w.address());
        bytes[40] ^= 1;
        let bad = serde_json::to_string(&bytes).unwrap();
        let err = parse_keypair_json(&bad).err().unwrap();
        assert_eq!(err, "wallet key: public half does not match the secret half");
        assert!(parse_keypair_json("[1,2,3]").is_err());
    }

    #[test]
    fn directory_in_place_of_the_key_means_no_key() {
        let dir = std::env::temp_dir().join(format!("itb-key-dir-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        assert!(load_wallet(&dir).unwrap().is_none());
        assert!(load_wallet(&dir.join("absent.json")).unwrap().is_none());
        std::fs::remove_dir_all(&dir).unwrap();
    }
}
