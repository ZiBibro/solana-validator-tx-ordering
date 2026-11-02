"""Known answers of the campaign data: python -m unittest discover -s tests

Burst 194 of campaign-mainnet-20261028T055501Z (JitoLabs HEL1USMZ, denominator
arm, slot 2) met a connection the leader closed: all 12 of its sends read
connection_closed, "closed by peer: dropped (code 1)". None of its probes was
delivered or landed, and the analysis counts it so. The payers of the campaign
were closed outside a run, and the spend table counts those transactions."""

import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from itb import analyze, report  # noqa: E402

RUN = "campaign-mainnet-20261028T055501Z"
BURST = 194


class Burst194(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = analyze.load_run(os.path.join(REPO, "data", "runs", RUN))
        cls.sigs = [s for s, p in cls.raw.probes.items() if p["burst_seq"] == BURST]

    def test_every_send_met_a_closed_connection(self):
        self.assertEqual(len(self.sigs), 12)
        self.assertEqual({self.raw.sends[s]["result"] for s in self.sigs}, {"connection_closed"})

    def test_no_probe_landed(self):
        self.assertEqual({self.raw.inclusions[s]["status"] for s in self.sigs}, {"expired"})

    def test_inclusion_leaves_it_out_of_the_delivered(self):
        # 672 probes of the run less the 12 of burst 194; the other 660 sends finished.
        delivered = sum(row["delivered"] for row in analyze.inclusion_shares([self.raw]))
        self.assertEqual(delivered, 660)
        self.assertNotIn("connection_closed", analyze.DELIVERED)

    def test_order_tests_leave_it_out(self):
        unit = [u for u in analyze.units_of(self.raw) if u.burst_seq == BURST]
        self.assertEqual(len(unit), 1)
        self.assertEqual(unit[0].blocks, [])
        self.assertIn("fewer-than-two-in-a-block", unit[0].reasons)


class Closing(unittest.TestCase):
    def test_the_close_after_the_campaign_counts_twelve_fees(self):
        rows = report._closings(os.path.join(REPO, "logs"))
        self.assertIn(("close-mainnet-20261102T055032Z", "2026-11-02 05:50:32", 12), rows)
        self.assertIn("| `close-mainnet-20261102T055032Z` | 2026-11-02 05:50:32 | 12 closing transactions"
                      " | - | 60000 | 60000 | - | - |",
                      report.spend_block([], [], os.path.join(REPO, "logs")))


if __name__ == "__main__":
    unittest.main()
