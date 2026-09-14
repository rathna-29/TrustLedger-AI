"""TrustLedger-AI -- Risk-Aware Autonomy Layer for Financial AI Agents.

Thin WSGI entrypoint. All construction lives in :func:`application.create_app`
(see application/__init__.py) so the same app can be run by Flask's built-in
server, waitress, or gunicorn without duplicating factory logic.

Run (dev):   python app.py
Run (prod):  waitress-serve --port=5000 --call application:create_app
"""
import os

from application import create_app

app = create_app()

if __name__ == "__main__":
    if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")):
        print("[TrustLedger-AI] No database found -- run `venv/bin/python database/seed_data.py` first!")
        print("                 (this also prints the demo agent tokens you'll use in scenario clicks.)")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)
