// The expected bytes of the probe tests in probe/src/tx.rs, rebuilt with the message
// builder of probe-sim.mjs.
//
// probe-sim.mjs builds unsigned version 1 and legacy messages by hand and asks a public
// mainnet node to price and simulate them with signature checks off; probe-sim-out.txt
// is its run of 2026-10-25, where the version 1 self-transfer simulated without error for
// 5000 lamports and the memo variants show how the priority fee and the loaded-data limit
// act. The Rust builder follows the same layout. This script takes the builder functions
// from probe-sim.mjs as they stand, builds the two probes the Rust tests build, and
// compares the bytes with the hex strings in tx.rs. Nothing is fetched, signed or sent.
//
//     node research/probe-layout/vector.mjs
//
// Exit status 0 when both strings match.
import { readFileSync } from 'node:fs';

const here = new URL('.', import.meta.url);
const source = readFileSync(new URL('probe-sim.mjs', here), 'utf8');
// Everything before the cases, less the one line that asks the node for a blockhash.
const defs = source.slice(0, source.indexOf('const P = '))
  .split('\n').filter(line => !line.startsWith('const bh = ')).join('\n');
const { v1Message, transferData, SYS } = new Function(defs + '\nreturn { v1Message, transferData, SYS };')();

const A = 'BAPwtQzaPZYJQYeJjQbTiPXx55Gja9gX85qv8i9Jk6u9';
const B = 'tickUcsEQegChaAuo9VYQQztB4ZGApY6ZT4FkULWY6N';
const BH = 'EkSnNWid2cvwEVnVx9aBqawnmiCNiDgp3gUdkDPTKN1N';
const P = { k: A, signer: true, writable: true };
// The transfer amount names the probe: burst_seq * 16 + send_rank + 1.
const amount = (burstSeq, sendRank) => burstSeq * 16 + sendRank + 1;

const built = [
  // Independent arm: burst 1, rank 0, priority fee 100 lamports, 1000 CU.
  v1Message([P, { k: SYS }], [{ prog: 1, accts: [0, 0], data: transferData(amount(1, 0)) }], BH,
    { priorityFeeLamports: 100, cuLimit: 1000, loadedBytes: 32768 }),
  // Shared arm: burst 1, rank 1, no priority fee, 20 000 CU, a 0-lamport transfer to the shared account.
  v1Message([P, { k: B, writable: true }, { k: SYS }],
    [{ prog: 2, accts: [0, 0], data: transferData(amount(1, 1)) }, { prog: 2, accts: [0, 1], data: transferData(0) }], BH,
    { priorityFeeLamports: 0, cuLimit: 20000, loadedBytes: 32768 }),
].map(m => Buffer.from(m.msg).toString('hex'));

const tests = readFileSync(new URL('../../probe/src/tx.rs', here), 'utf8');
const expected = [...tests.matchAll(/assert_eq!\(hex\(&m\.bytes\), "([0-9a-f]+)"\)/g)].map(m => m[1]);
if (expected.length !== built.length) {
  console.error(`tx.rs holds ${expected.length} expected strings, this script builds ${built.length}`);
  process.exit(1);
}
let bad = 0;
for (const [i, name] of ['independent', 'shared'].entries()) {
  const same = built[i] === expected[i];
  bad += same ? 0 : 1;
  console.log(`${name}: ${same ? 'matches tx.rs' : 'DIFFERS from tx.rs'} (${built[i].length / 2} bytes)`);
  if (!same) console.log(`  built    ${built[i]}\n  expected ${expected[i]}`);
}
process.exit(bad ? 1 : 0);
