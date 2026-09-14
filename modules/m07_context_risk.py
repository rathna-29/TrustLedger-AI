"""Module 7 -- Evaluate counterparty, protocol, market and liquidity context.
For the hackathon prototype these signals are simulated via a small lookup
table rather than a live chain explorer / KYC provider / market-data feed
(see PROJECT_DOCUMENTATION.md Part 11). The integration point is clearly
marked below for a production swap-in.

Market/liquidity risk is derived deterministically from the destination id,
so identical requests always yield identical risk scores.
"""

COUNTERPARTY_RISK_TIERS = {
    "whitelisted_known": 10,
    "known_new_pattern": 35,
    "unknown_unverified": 70,
    "flagged_blacklisted": 100,
}

PROTOCOL_RISK_TIERS = {
    "audited_established": 10,
    "audited_new": 40,
    "unaudited": 80,
    None: 20,  # no protocol involved (plain transfer)
}


def _stable_market_risk(destination_id: str) -> float:
    """Deterministic pseudo-volatility in [5, 25] from the destination id."""
    if not destination_id:
        return 5.0
    seed = sum(ord(c) for c in destination_id)
    return round(5 + (seed % 21), 1)


def evaluate_context(conn, destination_id: str) -> dict:
    row = conn.execute(
        "SELECT * FROM counterparties WHERE counterparty_id = ?", (destination_id,)
    ).fetchone()

    if row is None:
        # Never-seen destination -> treat as unverified by default
        counterparty_risk = COUNTERPARTY_RISK_TIERS["unknown_unverified"]
        protocol_risk = PROTOCOL_RISK_TIERS[None]
        blacklisted = False
        tier = "unknown_unverified"
    else:
        tier = row["risk_tier"]
        counterparty_risk = COUNTERPARTY_RISK_TIERS.get(tier, 70)
        protocol_risk = PROTOCOL_RISK_TIERS.get(row["protocol_risk_tier"], 20)
        blacklisted = tier == "flagged_blacklisted"

    # --- Deterministic simulated market/liquidity risk -----------------------
    # PRODUCTION INTEGRATION POINT: replace with a real market-data /
    # liquidity feed. Stable per-destination so the demo is reproducible.
    market_risk = _stable_market_risk(destination_id)

    return {
        "counterparty_tier": tier,
        "counterparty_risk": counterparty_risk,
        "protocol_risk": protocol_risk,
        "market_risk": market_risk,
        "blacklisted": blacklisted,
    }
