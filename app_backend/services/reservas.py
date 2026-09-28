from validators.reserva_validator import construir_error
from routes.canchas import obtener_cancha_por_id
from routes.socios import obtener
# Importa las consultas de reservas desde repositories
from repositories.reservas import obtener_reservas, obtener_reserva_id, insertar_reserva, hay_superposicion_reserva,entidad_activa

def listar_reservas(limit,offset,canchas_id=None, socio_id=None, estado_arg=None,fecha_desde=None,fecha_hasta=None):
    reservas_dict = {"reservas": []}
    for i in obtener_reservas(limit,offset,canchas_id, socio_id, estado_arg,fecha_desde,fecha_hasta):
        reservas_dict["reservas"].append(i)
    return reservas_dict 

def listar_reserva_id(reserva_id):
    reserva_dict = obtener_reserva_id(reserva_id)
    if not reserva_dict: #ver si existe reserva con esa id
        return None
    return reserva_dict

def registrar_reserva(datos_reserva):


    # Verifica que la cancha exista
    cancha,code = obtener_cancha_por_id(datos_reserva["id_cancha"])
    if code == 404:
        return construir_error(
                    code="ERROR_NO_ENCONTRADO",
                    mesagge="Recurso no encontrado",
                    description= f"La cancha de id '{datos_reserva["id_cancha"]}' no existe "
        )

    
    # Verifca que el socio exista
    mensaje_socio,estado = obtener(datos_reserva["id_socio"])
    if estado == 404:
        return construir_error(
                code="ERROR_NO_ENCONTRADO",
                mesagge="Recurso no encontrado",
                description= f"El socio de id '{datos_reserva["id_socio"]}' no existe "
        )
    socio_activo = entidad_activa("socios",datos_reserva["id_socio"],"activo")
    if not socio_activo:
        return construir_error(
            code="ERROR_CONFLICTO",
            mesagge="Conflicto en la reserva",
            description=f"El socio de id '{datos_reserva["id_socio"]}' se encuentra inactivo"
        )

    
    # Verifica que la cancha se encuentre disponible
    cancha_activa = entidad_activa("canchas",datos_reserva["id_cancha"],"activa")
    if not cancha_activa:
        return construir_error(
            code="ERROR_CONFLICTO",
            mesagge="Conflicto en la reserva",
            description=f"La cancha de id '{datos_reserva["id_cancha"]}' se encuentra inactiva"
        )

    superposicion = hay_superposicion_reserva(datos_reserva)


    # Verifica que no exista otra reserva en el mismo horario
    if superposicion:
        return construir_error(
                    code="ERROR_CONFLICTO",
                    mesagge="Conflicto en la reserva",
                    description=f"Ya hay una reserva entre el intervalo de las horas"
        )
    # Si todo sale bien, registra la reserva en la base de datos
    insertar_reserva(datos_reserva)
