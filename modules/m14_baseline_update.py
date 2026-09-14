"""Module 14 -- Update behaviour profile and risk baselines.
Recomputes rolling mean/std for the agent AFTER a completed (non-blocked)
transaction. Blocked attempts deliberately do NOT update the baseline --
otherwise a slow drift/manipulation attack could gradually redefine "normal".
"""

from datetime import datetime


def update_baseline(conn, agent_id: str):
    rows = conn.execute(
        """SELECT t.amount
           FROM transactions t
           JOIN decisions d ON t.txn_id = d.txn_id
           WHERE t.agent_id = ? AND d.decision IN ('EXECUTE', 'CONSTRAIN')
           ORDER BY t.created_at DESC LIMIT 50""",
        (agent_id,),
    ).fetchall()
    amounts = [r["amount"] for r in rows]

    if not amounts:
        return

    mean_amount = sum(amounts) / len(amounts)
    variance = sum((a - mean_amount) ** 2 for a in amounts) / max(len(amounts), 1)
    std_amount = max(variance ** 0.5, 1.0)

    conn.execute(
        """UPDATE behaviour_profiles
           SET mean_amount = ?, std_amount = ?, sample_count = ?, last_updated = ?
           WHERE agent_id = ?""",
        (mean_amount, std_amount, len(amounts), datetime.utcnow().isoformat(), agent_id),
    )
    conn.commit()
