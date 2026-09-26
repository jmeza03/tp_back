from flask import Blueprint, request, jsonify
from services.estados import cambiar_estado_reserva

estados_bp = Blueprint("estados", __name__)


def responder_error(codigo, mensaje, descripcion, estado_http):
    return jsonify({
        "errors": [
            {
            "code": codigo,
            "message": mensaje,
            "level": "error",
            "description": descripcion
            }
        ]
    }), estado_http

@estados_bp.route(
    "/reservas/<int:id_reserva>/estado",
    methods=["PUT"]
)
def actualizar_estado(id_reserva):

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or set(datos) != {"estado"}:
        return responder_error(
            "ERROR_VALIDACION",
            "Solicitud inválida",
            "Debes enviar unicamente el campo estado",
            400
        )
    
    estado_nuevo = datos["estado"]
    resultado = cambiar_estado_reserva(id_reserva, estado_nuevo)
    
    if "error" in resultado:
        if resultado["error"] == "El estado solicitado NO es válido":
            return responder_error(
                        "ERROR_VALIDACION",
                        "Estado inválida",
                        "EL estado solicitado no es valido",
                        400
            )

        if resultado["error"] == "Reserva NO encontrada":
            return responder_error(
                        "ERROR_NO_ENCONTRADO",
                        "Reserva no encontrada",
                        "La reserva solicitada no existe",
                        404
                    )

        return responder_error(
                    "ERROR_CONFLICTO",
                    "Conflicto en la solicitud",
                    "No se puede actualizar el estado de la reserva",
                    409
                )
    return "", 204