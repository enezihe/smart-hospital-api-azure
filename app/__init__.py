from flask import Flask, request
from dotenv import load_dotenv
from .extensions import db, cors
from .config import Config

def create_app(config_class: type = Config) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    cors.init_app(app)

    @app.before_request
    def _log_req():
        print("REQ:", request.method, request.path,
              "| CT:", request.headers.get("Content-Type"),
              "| X-API-Key:", bool(request.headers.get("X-API-Key")),
              "| Idem:", request.headers.get("Idempotency-Key"))

    @app.get("/health")
    def health():
        return {"status": "OK"}, 200

    # register blueprints
    from .routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from .routes.api_v1 import api_v1_bp
    app.register_blueprint(api_v1_bp)

    return app
