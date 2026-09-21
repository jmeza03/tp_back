from flask import Blueprint, jsonify

socios_bp = Blueprint("socios", __name__)

@socios_bp.get("/socios")
def listar():
    return jsonify([]), 200

@socios_bp.post("/socios")
def crear():
    return jsonify({"mensaje": "pendiente"}), 201

@socios_bp.get("/socios/<int:id>")
def obtener(id):
    return jsonify({"id": id}), 200

@socios_bp.patch("/socios/<int:id>")
def actualizar(id):
    return jsonify({"id": id}), 200
