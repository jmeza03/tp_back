from flask import Blueprint, request, jsonify
from services.estados import cambiar_estado_reserva

estados_bp = Blueprint("estados", __name__)

@estados_bp.route(
    "/reservas/<int:id_reserva>/estado",
    methods=["PUT"]
)
def actualizar_estado(id_reserva):

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "estado" not in datos:
        return jsonify({
            "error": "Debes enviar un JSON con el campo estado"
        }), 400
    
    estado_nuevo = datos["estado"]
    resultado = cambiar_estado_reserva(id_reserva, estado_nuevo)
    if "error" in resultado:
        if resultado["error"] == "El estado solicitado NO es válido":
            return jsonify(resultado), 400

        if resultado["error"] == "Reserva NO encontrada":
            return jsonify(resultado), 404

        return jsonify(resultado), 409
    return jsonify(resultado), 200