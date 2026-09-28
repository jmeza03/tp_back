from flask import Blueprint,jsonify, request
# Importa la logica de reservas desde los modulos locales
from services.reservas import registar_reserva, actualizar_estado_reserva, listar_reservas, listar_reserva_id
from repositories.reservas import contador_reservas
reservas_bp=Blueprint('reservas',__name__)

@reservas_bp.route('/reservas', methods=['GET'])
def lista_reservas():
    canchas_id = request.args.get("id_cancha")
    socio_id = request.args.get("id_socio")
    estado_arg = request.args.get("estado")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    
    #falta validaciones de los request

    limit = request.args.get("_limit",10, type=int)
    offset = request.args.get("_offset",0,type=int)


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
    #validar(id) validar que el id sea un int
    reserva = listar_reserva_id(id)
    if reserva is None:
        return jsonify({"error": f"reserva de id {id} no existe"}),404
    return jsonify(reserva),200

@reservas_bp.route('/reservas/', methods=['POST'])
def agregar_reserva():
    datos_reserva = request.get_json()

    #validar_datos_reserva(datos_reserva) --> valida si los datos son correctos
    #validar_campo_oblicatorio(datos_reserva) --> desde validators valida si los campos estan

    return registar_reserva(datos_reserva)

@reservas_bp.route('/reservas/<id>/estado', methods = ['PUT'])
def actualizar_estado(id):
    estado = request.get_json()
    #validar_id(id)
    #validar_estado(estado) --> validaciones

    return actualizar_estado_reserva(id,estado)