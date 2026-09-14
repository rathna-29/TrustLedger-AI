"""Application factory for TrustLedger-AI.

create_app() builds a configured Flask instance and registers the three
blueprints. Putting construction in a factory (instead of module import-time
side effects in app.py) makes the app trivial to test and to run under any
WSGI server (gunicorn/waitress) while keeping a thin ``app.py`` entrypoint.

The factory lives one level below the project root, so template and static
folders are resolved explicitly against the repository root instead of relying
on Flask's default ``<package>/templates`` behaviour (this is what keeps the
dashboard renderable even though ``create_app`` is defined inside the
``application`` package).
"""
import os

from flask import Flask, jsonify, redirect

from config.settings import settings
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from routes.agent_routes import agent_bp
from routes.dashboard_routes import dashboard_bp
from routes.review_routes import review_bp
from utils.scenarios import SCENARIOS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
    )
    app.config["SECRET_KEY"] = settings.jwt_secret
    app.config["JSON_SORT_KEYS"] = False

    app.register_blueprint(agent_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(review_bp)

    @app.route("/")
    def index():
        return redirect("/dashboard")

    @app.route("/api/scenarios")
    def api_scenarios():
        """Lets the dashboard fire pre-built demo scenarios with one click."""
        return jsonify(SCENARIOS)

    @app.route("/healthz")
    def healthz():
        return jsonify({"status": "ok", "service": "TrustLedger-AI"})

    return app
