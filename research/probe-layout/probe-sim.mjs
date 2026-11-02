// Build unsigned probe transactions (zero signatures) and evaluate them read-only:
// getFeeForMessage + simulateTransaction(sigVerify:false, replaceRecentBlockhash:true).
// Nothing is signed, nothing is sent. Usage: node probe-sim.mjs <feePayerBase58> [rpcUrl]
const ALPH = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
function b58dec(s) {
  let n = 0n; for (const c of s) { const i = ALPH.indexOf(c); if (i < 0) throw new Error('bad b58'); n = n * 58n + BigInt(i); }
  const out = []; while (n > 0n) { out.unshift(Number(n % 256n)); n /= 256n; }
  for (const c of s) { if (c === '1') out.unshift(0); else break; }
  return Uint8Array.from(out);
}
function pk(s) { const b = b58dec(s); if (b.length !== 32) throw new Error('pubkey len ' + b.length + ' for ' + s); return b; }
function cu16(n) { const o = []; for (;;) { let e = n & 0x7f; n >>= 7; if (n === 0) { o.push(e); return o; } o.push(e | 0x80); } }
function u32le(n) { const b = Buffer.alloc(4); b.writeUInt32LE(n); return [...b]; }
function u64le(n) { const b = Buffer.alloc(8); b.writeBigUInt64LE(BigInt(n)); return [...b]; }

const url = process.argv[3] || 'https://api.mainnet-beta.solana.com';
const PAYER = process.argv[2];
const SYS = '11111111111111111111111111111111';
const MEMO2 = 'MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr';
const CB = 'ComputeBudget111111111111111111111111111111';

async function rpc(method, params) {
  const r = await fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }) });
  return r.json();
}

// keys: [{k, signer, writable}] ordered as legacy layout requires; ixs: [{prog, accts:[idx], data:[bytes]}]
function legacyMessage(keys, ixs, blockhash) {
  const nSig = keys.filter(k => k.signer).length;
  const roSigned = keys.filter(k => k.signer && !k.writable).length;
  const roUnsigned = keys.filter(k => !k.signer && !k.writable).length;
  const m = [nSig, roSigned, roUnsigned, ...cu16(keys.length)];
  for (const k of keys) m.push(...pk(k.k));
  m.push(...pk(blockhash));
  m.push(...cu16(ixs.length));
  for (const ix of ixs) { m.push(ix.prog, ...cu16(ix.accts.length), ...ix.accts, ...cu16(ix.data.length), ...ix.data); }
  return { msg: Uint8Array.from(m), nSig };
}
function v1Message(keys, ixs, blockhash, cfg) {
  const nSig = keys.filter(k => k.signer).length;
  const roSigned = keys.filter(k => k.signer && !k.writable).length;
  const roUnsigned = keys.filter(k => !k.signer && !k.writable).length;
  let mask = 0; const vals = [];
  if (cfg.priorityFeeLamports !== undefined) { mask |= 0b11; vals.push(...u64le(cfg.priorityFeeLamports)); }
  if (cfg.cuLimit !== undefined) { mask |= 0b100; vals.push(...u32le(cfg.cuLimit)); }
  if (cfg.loadedBytes !== undefined) { mask |= 0b1000; vals.push(...u32le(cfg.loadedBytes)); }
  const m = [129, nSig, roSigned, roUnsigned, ...u32le(mask), ...pk(blockhash), ixs.length, keys.length];
  for (const k of keys) m.push(...pk(k.k));
  m.push(...vals);
  for (const ix of ixs) { const l = Buffer.alloc(2); l.writeUInt16LE(ix.data.length); m.push(ix.prog, ix.accts.length, ...l); }
  for (const ix of ixs) m.push(...ix.accts, ...ix.data);
  return { msg: Uint8Array.from(m), nSig, v1: true };
}
function wireLegacy({ msg, nSig }) { return Buffer.from([...cu16(nSig), ...new Array(64 * nSig).fill(0), ...msg]); }
function wireV1({ msg, nSig }) { return Buffer.from([...msg, ...new Array(64 * nSig).fill(0)]); }

const bh = (await rpc('getLatestBlockhash', [{ commitment: 'finalized' }])).result.value.blockhash;
const memoData = [...Buffer.from('probe-000001')];
const transferData = (lamports) => [...u32le(2), ...u64le(lamports)];
const cuLimitIx = (idx, units) => ({ prog: idx, accts: [], data: [2, ...u32le(units)] });
const cuPriceIx = (idx, micro) => ({ prog: idx, accts: [], data: [3, ...u64le(micro)] });
const loadedIx = (idx, bytes) => ({ prog: idx, accts: [], data: [4, ...u32le(bytes)] });

const P = { k: PAYER, signer: true, writable: true };
const cases = {
  empty_no_instructions: legacyMessage([P], [], bh),
  self_transfer_1_lamport: legacyMessage([P, { k: SYS }], [{ prog: 1, accts: [0, 0], data: transferData(1) }], bh),
  self_transfer_0_lamport: legacyMessage([P, { k: SYS }], [{ prog: 1, accts: [0, 0], data: transferData(0) }], bh),
  memo_v2_12_bytes: legacyMessage([P, { k: MEMO2 }], [{ prog: 1, accts: [], data: memoData }], bh),
  cb_only_limit_price: legacyMessage([P, { k: CB }], [cuLimitIx(1, 1000), cuPriceIx(1, 1000)], bh),
  memo_v2_with_cb_limit_price_loaded: legacyMessage([P, { k: MEMO2 }, { k: CB }], [cuLimitIx(2, 20000), cuPriceIx(2, 10000), loadedIx(2, 32768), { prog: 1, accts: [], data: memoData }], bh),
  self_transfer_with_cb_limit_price: legacyMessage([P, { k: SYS }, { k: CB }], [cuLimitIx(2, 1000), cuPriceIx(2, 100000), { prog: 1, accts: [0, 0], data: transferData(1) }], bh),
  v1_memo_v2_prio_1000_lamports: v1Message([P, { k: MEMO2 }], [{ prog: 1, accts: [], data: memoData }], bh, { priorityFeeLamports: 1000, cuLimit: 20000, loadedBytes: 32768 }),
  v1_self_transfer_no_prio: v1Message([P, { k: SYS }], [{ prog: 1, accts: [0, 0], data: transferData(1) }], bh, { cuLimit: 1000, loadedBytes: 32768 }),
  v1_empty_config_memo: v1Message([P, { k: MEMO2 }], [{ prog: 1, accts: [], data: memoData }], bh, {}),
};
console.log('blockhash', bh, 'payer', PAYER, 'rpc', url, 'at', new Date().toISOString());
for (const [name, m] of Object.entries(cases)) {
  const wire = m.v1 ? wireV1(m) : wireLegacy(m);
  const fee = await rpc('getFeeForMessage', [Buffer.from(m.msg).toString('base64'), { commitment: 'processed' }]);
  const sim = await rpc('simulateTransaction', [wire.toString('base64'), { encoding: 'base64', sigVerify: false, replaceRecentBlockhash: true, commitment: 'processed' }]);
  const v = sim.result?.value;
  console.log(JSON.stringify({ name, wireBytes: wire.length, feeForMessage: fee.result?.value ?? fee.error, simErr: v ? v.err : sim.error, unitsConsumed: v?.unitsConsumed, fee: v?.fee, loadedAccountsDataSize: v?.loadedAccountsDataSize, logs: v?.logs?.slice(0, 6) }));
  await new Promise(r => setTimeout(r, 300));
}
