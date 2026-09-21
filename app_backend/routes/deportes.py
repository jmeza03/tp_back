from flask import Blueprint, jsonify
from db import query_all


deportes_bp = Blueprint("deportes", __name__)


@deportes_bp.route("/deportes", methods=["GET"])
def obtener_deportes():
    deportes = query_all("SELECT * FROM deportes ORDER BY id")

    return jsonify({
        "deportes": deportes
    }), 200