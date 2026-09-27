
from ..repositories.reservas import obtener_reservas,obtener_reserva_id,agregar_reserva,actualizar_estado,hay_superposicion_reserva
#from ..repositories.socios import obtener_socio_id
#from ..repositories.canchas import obtener_cancha_id
from flask import jsonify

def listar_reservas(limit,offset,canchas_id=None, socio_id=None, estado_arg=None,fecha_desde=None,fecha_hasta=None):
    reservas_dict = {"reservas": []}
    for i in obtener_reservas(limit,offset,canchas_id, socio_id, estado_arg,fecha_desde,fecha_hasta):
        reservas_dict["reservas"].append(i)
    return reservas_dict # sorted(reservas_dict["reservas"], key=lambda x: x["id"]) <-- ordena por id

def listar_reserva_id(reserva_id):
    reserva_dict = obtener_reserva_id(reserva_id)
    if not reserva_dict: #ver si existe reserva con esa id
        return None
    return reserva_dict

def registar_reserva(datos_reserva):
    # en caso de que socio y cancha no existan
  # socio_id =  obtener_socio_id(datos_reserva["id_socio"]) --> repositories/socios 
  # cancha_id = obtener_cancha_id(datos_reserva["id_cancha"]) --> repositories/canchas
 
    superposicion = hay_superposicion_reserva(datos_reserva)
    if superposicion:
        return jsonify({"error": "Ya existe reserva entre esas horas"}),409 
    agregar_reserva(datos_reserva) 
    return '',201


def actualizar_estado_reserva(id: int,estado):
    reserva_id = obtener_reserva_id(id)
    if reserva_id is None:
        return jsonify({"error": f"reserva de id {id} no existe"}),404
    actualizar_estado(id, estado)
    return '',204
