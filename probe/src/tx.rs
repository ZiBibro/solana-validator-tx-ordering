//! Version 1 transactions (plan, section 4): the priority fee is an absolute amount in
//! the message config, and the CU and loaded-data limits must be set explicitly.
//!
//! Layout as built by research/probe-layout/probe-sim.mjs, whose unsigned messages a
//! mainnet node priced and simulated on 2026-10-25 (research/probe-layout/probe-sim-out.txt):
//!   0x81, num_signatures, readonly_signed, readonly_unsigned, config_mask u32 LE,
//!   blockhash, num_instructions u8, num_keys u8, keys, config values in mask-bit order,
//!   per instruction (program index u8, num_accounts u8, data_len u16 LE),
//!   per instruction (account indices, data);
//! the wire form is the message followed by the signatures.
//!
//! The pre-registration anchor (section 10) is a legacy transaction with one Memo v2
//! instruction: header, compact-u16 key count, keys, blockhash, compact-u16 instruction
//! count, instructions with compact-u16 lengths; its wire form puts the compact-u16
//! signature count and the signatures before the message.

use crate::keys::Signer;

pub const SYSTEM_PROGRAM: [u8; 32] = [0u8; 32];
pub const LAMPORTS_PER_SIGNATURE: u64 = 5000;
/// SPL Memo v2, the program of the pre-registration anchor (section 10).
pub const MEMO_PROGRAM: &str = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr";
const VERSION_1: u8 = 0x81;
const TRANSFER_TAG: u32 = 2;
const MASK_PRIORITY_FEE: u32 = 0b11;
const MASK_CU_LIMIT: u32 = 0b100;
const MASK_LOADED_DATA: u32 = 0b1000;
/// Probe limits from the measured successful variant (section 4).
pub const PROBE_CU_LIMIT: u32 = 1000;
pub const PROBE_LOADED_DATA: u32 = 32_768;
/// Send ranks per burst slot in the transfer amount (section 4).
pub const RANKS_PER_BURST: u64 = 16;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Config {
    pub priority_fee: u64,
    pub cu_limit: u32,
    pub loaded_data_limit: u32,
}

pub struct AccountMeta {
    pub key: [u8; 32],
    pub signer: bool,
    pub writable: bool,
}

pub struct Instruction {
    pub program: [u8; 32],
    pub accounts: Vec<AccountMeta>,
    pub data: Vec<u8>,
}

pub fn transfer(from: [u8; 32], to: [u8; 32], lamports: u64) -> Instruction {
    let mut data = TRANSFER_TAG.to_le_bytes().to_vec();
    data.extend_from_slice(&lamports.to_le_bytes());
    Instruction {
        program: SYSTEM_PROGRAM,
        accounts: vec![
            AccountMeta { key: from, signer: true, writable: true },
            AccountMeta { key: to, signer: false, writable: true },
        ],
        data,
    }
}

/// Memo v2 with no accounts: the fee payer's signature is the only one the memo needs.
pub fn memo(text: &str) -> Result<Instruction, String> {
    Ok(Instruction { program: crate::b58::decode32(MEMO_PROGRAM)?, accounts: vec![], data: text.as_bytes().to_vec() })
}

pub struct Message {
    pub bytes: Vec<u8>,
    /// Required signers in key order; the first is the fee payer.
    pub signers: Vec<[u8; 32]>,
    pub write_accounts: Vec<[u8; 32]>,
}

pub fn message_v1(
    payer: [u8; 32],
    instructions: &[Instruction],
    blockhash: [u8; 32],
    config: Config,
) -> Result<Message, String> {
    let keys = ordered_keys(payer, instructions)?;
    let index = |key: &[u8; 32]| keys.iter().position(|k| &k.key == key).unwrap() as u8;
    let signers: Vec<[u8; 32]> = keys.iter().filter(|k| k.signer).map(|k| k.key).collect();
    let readonly_signed = keys.iter().filter(|k| k.signer && !k.writable).count();
    let readonly_unsigned = keys.iter().filter(|k| !k.signer && !k.writable).count();

    let mut m = vec![
        VERSION_1,
        signers.len() as u8,
        readonly_signed as u8,
        readonly_unsigned as u8,
    ];
    m.extend_from_slice(&(MASK_PRIORITY_FEE | MASK_CU_LIMIT | MASK_LOADED_DATA).to_le_bytes());
    m.extend_from_slice(&blockhash);
    m.push(instructions.len() as u8);
    m.push(keys.len() as u8);
    for k in &keys {
        m.extend_from_slice(&k.key);
    }
    m.extend_from_slice(&config.priority_fee.to_le_bytes());
    m.extend_from_slice(&config.cu_limit.to_le_bytes());
    m.extend_from_slice(&config.loaded_data_limit.to_le_bytes());
    for ix in instructions {
        if ix.accounts.len() > 255 || ix.data.len() > u16::MAX as usize {
            return Err("instruction too large".into());
        }
        m.push(index(&ix.program));
        m.push(ix.accounts.len() as u8);
        m.extend_from_slice(&(ix.data.len() as u16).to_le_bytes());
    }
    for ix in instructions {
        m.extend(ix.accounts.iter().map(|a| index(&a.key)));
        m.extend_from_slice(&ix.data);
    }
    let write_accounts = keys.iter().filter(|k| k.writable).map(|k| k.key).collect();
    Ok(Message { bytes: m, signers, write_accounts })
}

/// Legacy message (section 10): the anchor memo goes out in this form, which a mainnet
/// node priced at 5000 lamports on 2026-10-25 (research/probe-layout/probe-sim-out.txt).
pub fn legacy_message(payer: [u8; 32], instructions: &[Instruction], blockhash: [u8; 32]) -> Result<Message, String> {
    let keys = ordered_keys(payer, instructions)?;
    let index = |key: &[u8; 32]| keys.iter().position(|k| &k.key == key).unwrap() as u8;
    let signers: Vec<[u8; 32]> = keys.iter().filter(|k| k.signer).map(|k| k.key).collect();
    let mut m = vec![
        signers.len() as u8,
        keys.iter().filter(|k| k.signer && !k.writable).count() as u8,
        keys.iter().filter(|k| !k.signer && !k.writable).count() as u8,
    ];
    short_vec(&mut m, keys.len());
    for k in &keys {
        m.extend_from_slice(&k.key);
    }
    m.extend_from_slice(&blockhash);
    short_vec(&mut m, instructions.len());
    for ix in instructions {
        m.push(index(&ix.program));
        short_vec(&mut m, ix.accounts.len());
        m.extend(ix.accounts.iter().map(|a| index(&a.key)));
        short_vec(&mut m, ix.data.len());
        m.extend_from_slice(&ix.data);
    }
    let write_accounts = keys.iter().filter(|k| k.writable).map(|k| k.key).collect();
    Ok(Message { bytes: m, signers, write_accounts })
}

/// Compact-u16 length: seven bits per byte, the high bit marks a following byte.
fn short_vec(out: &mut Vec<u8>, mut n: usize) {
    loop {
        let low = (n & 0x7f) as u8;
        n >>= 7;
        if n == 0 {
            out.push(low);
            return;
        }
        out.push(low | 0x80);
    }
}

/// Keys of a message, ordered as both forms need them; the payer is a writable signer.
fn ordered_keys(payer: [u8; 32], instructions: &[Instruction]) -> Result<Vec<AccountMeta>, String> {
    // Keys in first-seen order with merged flags; the payer is a writable signer.
    let mut keys: Vec<AccountMeta> = vec![AccountMeta { key: payer, signer: true, writable: true }];
    let mut add = |key: [u8; 32], signer: bool, writable: bool| {
        if let Some(k) = keys.iter_mut().find(|k| k.key == key) {
            k.signer |= signer;
            k.writable |= writable;
        } else {
            keys.push(AccountMeta { key, signer, writable });
        }
    };
    for ix in instructions {
        for a in &ix.accounts {
            add(a.key, a.signer, a.writable);
        }
        add(ix.program, false, false);
    }
    // Stable partition: writable signers, readonly signers, writable others, readonly others.
    let group = |k: &AccountMeta| match (k.signer, k.writable) {
        (true, true) => 0,
        (true, false) => 1,
        (false, true) => 2,
        (false, false) => 3,
    };
    keys.sort_by_key(group);
    if keys.len() > 255 || instructions.len() > 255 {
        return Err("message has more than 255 keys or instructions".into());
    }
    Ok(keys)
}

pub struct Signed {
    pub wire: Vec<u8>,
    /// First signature, the transaction id.
    pub signature: [u8; 64],
}

/// Sign the message bytes with each required signer, in key order.
pub fn sign(message: &Message, signers: &[&Signer]) -> Result<Signed, String> {
    let mut wire = message.bytes.clone();
    let mut first = None;
    for key in &message.signers {
        let s = signers
            .iter()
            .find(|s| &s.pubkey() == key)
            .ok_or_else(|| format!("no signer for {}", crate::b58::encode(key)))?;
        let sig = s.sign(&message.bytes);
        first.get_or_insert(sig);
        wire.extend_from_slice(&sig);
    }
    Ok(Signed { wire, signature: first.ok_or("message without signers")? })
}

/// Legacy wire form: compact-u16 signature count, the signatures in key order, the message.
pub fn sign_legacy(message: &Message, signers: &[&Signer]) -> Result<Signed, String> {
    let mut wire = vec![];
    short_vec(&mut wire, message.signers.len());
    let mut first = None;
    for key in &message.signers {
        let s = signers
            .iter()
            .find(|s| &s.pubkey() == key)
            .ok_or_else(|| format!("no signer for {}", crate::b58::encode(key)))?;
        let sig = s.sign(&message.bytes);
        first.get_or_insert(sig);
        wire.extend_from_slice(&sig);
    }
    wire.extend_from_slice(&message.bytes);
    Ok(Signed { wire, signature: first.ok_or("message without signers")? })
}

/// The legacy wire with zeroed signatures, for simulateTransaction with sigVerify off.
pub fn unsigned_legacy_wire(message: &Message) -> Vec<u8> {
    let mut wire = vec![];
    short_vec(&mut wire, message.signers.len());
    wire.extend(std::iter::repeat_n(0u8, 64 * message.signers.len()));
    wire.extend_from_slice(&message.bytes);
    wire
}

/// Amount of the self-transfer that names the probe: burst_seq*16 + send_rank + 1.
pub fn probe_amount(burst_seq: u64, send_rank: u8) -> u64 {
    burst_seq * RANKS_PER_BURST + send_rank as u64 + 1
}

/// A probe: the self-transfer that names it, plus in the shared arm a 0-lamport
/// transfer to the shared account (section 6).
pub fn probe_message(
    payer: [u8; 32],
    shared_with: Option<[u8; 32]>,
    burst_seq: u64,
    send_rank: u8,
    config: Config,
    blockhash: [u8; 32],
) -> Result<Message, String> {
    let mut ixs = vec![transfer(payer, payer, probe_amount(burst_seq, send_rank))];
    if let Some(other) = shared_with {
        ixs.push(transfer(payer, other, 0));
    }
    message_v1(payer, &ixs, blockhash, config)
}

/// Highest fee the probe can be charged: one signature plus its v1 priority fee.
pub fn worst_fee(signatures: usize, config: Config) -> u64 {
    (signatures as u64).saturating_mul(LAMPORTS_PER_SIGNATURE).saturating_add(config.priority_fee)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::b58;

    fn hex(b: &[u8]) -> String {
        b.iter().map(|x| format!("{x:02x}")).collect()
    }

    // Expected bytes come from the JavaScript builder of research/probe-layout/probe-sim.mjs
    // on the same inputs; `node research/probe-layout/vector.mjs` rebuilds and compares them.
    const A: &str = "BAPwtQzaPZYJQYeJjQbTiPXx55Gja9gX85qv8i9Jk6u9";
    const B: &str = "tickUcsEQegChaAuo9VYQQztB4ZGApY6ZT4FkULWY6N";
    const BH: &str = "EkSnNWid2cvwEVnVx9aBqawnmiCNiDgp3gUdkDPTKN1N";

    #[test]
    fn independent_probe_matches_the_simulated_layout() {
        let cfg = Config { priority_fee: 100, cu_limit: 1000, loaded_data_limit: 32768 };
        let m = probe_message(b58::decode32(A).unwrap(), None, 1, 0, cfg, b58::decode32(BH).unwrap()).unwrap();
        assert_eq!(hex(&m.bytes), "810100010f000000cc490e928cd2e3873bb343fc95da33179ca60f4dbf46c2c36e91299d55d4e6b9010296fd0ac2747ea6047a45c1fdb1845943e79431f1dc4ea89e5999a7a8e0dce40c00000000000000000000000000000000000000000000000000000000000000006400000000000000e80300000080000001020c000000020000001100000000000000");
        assert_eq!(m.write_accounts, vec![b58::decode32(A).unwrap()]);
    }

    #[test]
    fn shared_probe_matches_the_simulated_layout() {
        let cfg = Config { priority_fee: 0, cu_limit: 20000, loaded_data_limit: 32768 };
        let m = probe_message(
            b58::decode32(A).unwrap(),
            Some(b58::decode32(B).unwrap()),
            1,
            1,
            cfg,
            b58::decode32(BH).unwrap(),
        )
        .unwrap();
        assert_eq!(hex(&m.bytes), "810100010f000000cc490e928cd2e3873bb343fc95da33179ca60f4dbf46c2c36e91299d55d4e6b9020396fd0ac2747ea6047a45c1fdb1845943e79431f1dc4ea89e5999a7a8e0dce40c0d3fad52d0e9d6e9a8ab550ad5c1036db07f48cb8c8ba29dba161961c8c8cdeb00000000000000000000000000000000000000000000000000000000000000000000000000000000204e00000080000002020c0002020c0000000200000012000000000000000001020000000000000000000000");
        assert_eq!(m.write_accounts.len(), 2);
    }

    #[test]
    fn signature_covers_the_message_and_trails_it() {
        let s = Signer::from_seed(&[9u8; 32]);
        let cfg = Config { priority_fee: 10, cu_limit: PROBE_CU_LIMIT, loaded_data_limit: PROBE_LOADED_DATA };
        let m = probe_message(s.pubkey(), None, 5, 3, cfg, [1u8; 32]).unwrap();
        let signed = sign(&m, &[&s]).unwrap();
        assert_eq!(&signed.wire[..m.bytes.len()], &m.bytes[..]);
        assert_eq!(&signed.wire[m.bytes.len()..], &signed.signature[..]);
        let vk = ed25519_dalek::VerifyingKey::from_bytes(&s.pubkey()).unwrap();
        let sig = ed25519_dalek::Signature::from_bytes(&signed.signature);
        assert!(vk.verify_strict(&m.bytes, &sig).is_ok());
        assert_eq!(worst_fee(1, cfg), 5010);
        assert_eq!(probe_amount(5, 3), 84);
    }

    #[test]
    fn compact_u16_takes_seven_bits_a_byte() {
        for (n, want) in [(0usize, vec![0u8]), (127, vec![0x7f]), (128, vec![0x80, 0x01]), (16384, vec![0x80, 0x80, 0x01])] {
            let mut out = vec![];
            short_vec(&mut out, n);
            assert_eq!(out, want, "{n}");
        }
    }

    #[test]
    fn anchor_memo_is_a_legacy_message_signed_ahead_of_it() {
        let s = Signer::from_seed(&[7u8; 32]);
        let text = format!("itb-prereg {}", "ab".repeat(32));
        let m = legacy_message(s.pubkey(), &[memo(&text).unwrap()], [2u8; 32]).unwrap();
        let program = b58::decode32(MEMO_PROGRAM).unwrap();
        // Header: one writable signer, no readonly signer, one readonly key (the program).
        assert_eq!(&m.bytes[..4], &[1, 0, 1, 2]);
        assert_eq!(&m.bytes[4..36], &s.pubkey());
        assert_eq!(&m.bytes[36..68], &program);
        assert_eq!(&m.bytes[68..100], &[2u8; 32]);
        // One instruction: program index 1, no accounts, 75 data bytes.
        assert_eq!(&m.bytes[100..104], &[1, 1, 0, 75]);
        assert_eq!(&m.bytes[104..], text.as_bytes());
        assert_eq!(m.write_accounts, vec![s.pubkey()]);
        let signed = sign_legacy(&m, &[&s]).unwrap();
        assert_eq!(signed.wire[0], 1);
        assert_eq!(&signed.wire[1..65], &signed.signature[..]);
        assert_eq!(&signed.wire[65..], &m.bytes[..]);
        let vk = ed25519_dalek::VerifyingKey::from_bytes(&s.pubkey()).unwrap();
        assert!(vk.verify_strict(&m.bytes, &ed25519_dalek::Signature::from_bytes(&signed.signature)).is_ok());
        let blank = unsigned_legacy_wire(&m);
        assert_eq!(blank.len(), signed.wire.len());
        assert!(blank[1..65].iter().all(|b| *b == 0));
        // The v1 form of the same probe keeps its layout after the key ordering moved out.
        let v1 = message_v1(s.pubkey(), &[memo(&text).unwrap()], [2u8; 32], Config { priority_fee: 0, cu_limit: 1, loaded_data_limit: 1 }).unwrap();
        assert_eq!(&v1.bytes[..4], &[VERSION_1, 1, 0, 1]);
    }
}
