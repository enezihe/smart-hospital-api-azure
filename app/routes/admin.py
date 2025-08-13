import os
from flask import Blueprint, request, current_app
from ..extensions import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.get("/db-path")
def db_path():
    db_file = db.engine.url.database
    abs_path = os.path.abspath(db_file) if db_file else None
    return {"database_uri": str(db.engine.url), "db_file": db_file, "absolute_path": abs_path}, 200

@admin_bp.route("/init-db", methods=["POST", "GET"])
def init_db():
    if request.method == "GET" and request.args.get("confirm") != "yes":
        return {"message": "Use POST or /admin/init-db?confirm=yes (local only)"}, 200
    db.create_all()
    print("SQLite file:", os.path.abspath(db.engine.url.database))
    return {"status": "initialized"}, 201

@admin_bp.get("/routes")
def list_routes():
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({"rule": str(rule), "methods": sorted(list(rule.methods))})
    return {"routes": routes}, 200
