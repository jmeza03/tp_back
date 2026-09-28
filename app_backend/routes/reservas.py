from flask import Blueprint,jsonify, request
# Importa la logica de reservas desde los modulos locales
from services.reservas import registrar_reserva, listar_reservas, listar_reserva_id
from repositories.reservas import contador_reservas
from validators.reserva_validator import validar_datos_reserva_nueva,validar_id,construir_error
from constants import (
    PAGINACION_LIMIT_POR_DEFECTO,
    PAGINACION_LIMIT_MAXIMO,
    PAGINACION_OFFSET_POR_DEFECTO,
    )
reservas_bp=Blueprint('reservas',__name__)

@reservas_bp.route('/reservas', methods=['GET'])
def lista_reservas():
    canchas_id = request.args.get("id_cancha")
    socio_id = request.args.get("id_socio")
    estado_arg = request.args.get("estado")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    

    limit = request.args.get("_limit",PAGINACION_LIMIT_POR_DEFECTO, type=int)
    offset = request.args.get("_offset",PAGINACION_OFFSET_POR_DEFECTO,type=int)
    if limit < 1 or limit > PAGINACION_LIMIT_MAXIMO:
        return jsonify({
            "error": "_limit debe estar entre 1 y 100"
        }), 400

    if offset < 0:
        return jsonify({
            "error": "_offset no puede ser negativo"
        }), 400

    total = contador_reservas()[0]["total"]
    offset_prev = max(0, offset - limit)
    offset_next = offset + limit
    offset_last = ((total - 1) // limit) * limit
    links = {
    "_first": {
      "href": f"http://localhost:5000/reservas?_offset=0&_limit={limit}"
    },
    "_prev": {
      "href": f"http://localhost:5000/reservas?_offset={offset_prev}&_limit={limit}"
    },
    "_next": {
      "href": f"http://localhost:5000/reservas?_offset={offset_next}&_limit={limit}"
    },
    "_last": {
      "href": f"http://localhost:5000/reservas?_offset={offset_last}&_limit={limit}"
    }
  }
   
    reserva = listar_reservas(limit,offset,canchas_id, socio_id, estado_arg,fecha_desde,fecha_hasta)
    resultado = {"reservas": reserva, "links": links}
    return jsonify(resultado), 200





@reservas_bp.route('/reservas/<id>', methods=['GET'])
def listar_reservas_id(id):
    resultado = validar_id(id)
    if resultado:
        return jsonify(resultado),400
    reserva = listar_reserva_id(id)
    if not reserva:
        mensaje = construir_error(
            code="ERROR_NO_ENCONTRADO",
            mesagge="EL CUERPO DE LA SOLICITUD NO EXISTE",
            description=f"No existe una reserva con id : {id}"
        )
        return jsonify(mensaje),404
    return jsonify(reserva),200




@reservas_bp.route('/reservas/', methods=['POST'])
def agregar_reserva():
    datos_reserva = request.get_json(silent=True)
    if not isinstance(datos_reserva, dict):
          return jsonify({"error": "El cuerpo de la solicitud debe ser un JSON valido"}), 400
    # Validar que los datos sean correctos (Campos obligatorios, int, formato y que no este vacio)
    mensaje = validar_datos_reserva_nueva(datos_reserva)
    if mensaje:
        return jsonify(mensaje),400
    # Validar la existencia de canchas, socios, ademas de que no haya superposicion
    resultado = registrar_reserva(datos_reserva)
    if resultado:
        return jsonify(resultado),409
    return '',201