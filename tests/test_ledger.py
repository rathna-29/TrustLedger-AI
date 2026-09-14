"""Ledger contract: untouched chain verifies; one tampered row is caught."""

import os
import tempfile
import unittest

import database.db as dbm
import database.seed_data as sd
from modules.m13_ledger import verify_chain
from modules.pipeline import run_pipeline
from utils.scenarios import SCENARIOS


class LedgerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._t = tempfile.TemporaryDirectory()
        cls._tdb = os.path.join(cls._t.name, "tl_ledger.db")
        cls._o = dbm.DB_PATH
        dbm.DB_PATH = cls._tdb
        dbm.init_db()
        sd.seed()
        sc = SCENARIOS["scenario_1_normal"]
        run_pipeline(sc["payload"], sc["token"])

    @classmethod
    def tearDownClass(cls):
        dbm.DB_PATH = cls._o
        cls._t.cleanup()

    def _conn(self):
        c = dbm.get_db()
        self.addCleanup(c.close)
        return c

    # (identical contract as the probe: untouched -> True, then tamper -> False)
    def test_chain_contract_in_ordered_sequence(self):
        # 1) untouched chain MUST verify (hash chain recomputed from whole DB)
        self.assertTrue(verify_chain(self._conn()))

        # 2) tamper the LATEST row, then the SAME verifier MUST reject
        conn = self._conn()
        conn.execute(
            "UPDATE audit_log SET entry_json='{}' "
            "WHERE log_id=(SELECT MAX(log_id) FROM audit_log)"
        )
        conn.commit()
        self.assertFalse(verify_chain(conn))


if __name__ == "__main__":
    unittest.main()
