"""Module 13 -- Write decision + reason + transaction to immutable ledger.
Every decision (including BLOCKs and ESCALATEs) is appended here, hash-chained
to the previous entry so any retroactive tampering is detectable.
"""

from datetime import datetime

from utils.hashing import compute_entry_hash


def write_ledger_entry(conn, txn_id: str, entry_dict: dict) -> str:
    last = conn.execute(
        "SELECT entry_hash FROM audit_log ORDER BY log_id DESC LIMIT 1"
    ).fetchone()
    prev_hash = last["entry_hash"] if last else None

    entry_hash = compute_entry_hash(prev_hash, entry_dict)

    import json
    conn.execute(
        """INSERT INTO audit_log (txn_id, entry_json, prev_hash, entry_hash, created_at)
           VALUES (?,?,?,?,?)""",
        (txn_id, json.dumps(entry_dict, default=str), prev_hash, entry_hash, datetime.utcnow().isoformat()),
    )
    conn.commit()
    return entry_hash


def verify_chain(conn) -> bool:
    """Recomputes the hash chain from scratch and confirms nothing was altered."""
    import json
    rows = conn.execute("SELECT * FROM audit_log ORDER BY log_id ASC").fetchall()
    prev_hash = None
    for row in rows:
        if row["prev_hash"] != prev_hash:
            return False
        expected = compute_entry_hash(prev_hash, json.loads(row["entry_json"]))
        if expected != row["entry_hash"]:
            return False
        prev_hash = row["entry_hash"]
    return True
