"""Pipeline contract: blocked decisions are deterministic and stab-prone.

Trust: for an EXECUTE, the ledger hash will differ on repeat BY DESIGN -
every run appends its own auditable, timestamped block, so a blocked result
is what must stay byte-stable: decision + risk_score + 15-stage trace.
"""
import os
import tempfile
import unittest

import database.db as dbm
import database.seed_data as sd
from modules.pipeline import run_pipeline
from utils.scenarios import SCENARIOS


class BlockedIsDeterministic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls._tmpdb = os.path.join(cls._tmp.name, "tl_blocked.db")
        cls._orig_path = dbm.DB_PATH
        dbm.DB_PATH = cls._tmpdb
        dbm.init_db()
        sd.seed()

    @classmethod
    def tearDownClass(cls):
        dbm.DB_PATH = cls._orig_path
        cls._tmp.cleanup()

    def _blocked(self):
        sc = SCENARIOS["scenario_3_suspicious_wallet"]
        return run_pipeline(sc["payload"], sc["token"])

    def test_blocked_decision_and_risk_are_stable(self):
        a, b = self._blocked(), self._blocked()
        self.assertEqual(a["decision"], "BLOCK")
        self.assertEqual(a["decision"], b["decision"])
        self.assertEqual(a["risk_score"], b["risk_score"])

    def test_blocked_trace_is_full_15_stages(self):
        r = self._blocked()
        self.assertEqual(len(r["pipeline_stages"]), 15)


if __name__ == "__main__":
    unittest.main()
