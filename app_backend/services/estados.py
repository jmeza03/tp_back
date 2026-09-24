from db import query_one, execute
from datetime import datetime, timezone, timedelta

ZONA_CLUB = timezone(timedelta(hours=-3))

def validar_transicion(estado_actual, estado_nuevo, inicio, fin, ahora):
    #validar que los estados sean válidos
    estados_validos = ["confirmada", "cancelada", "finalizada"]

    if estado_actual not in estados_validos or estado_nuevo not in estados_validos:
        return False

    if estado_actual == estado_nuevo:
        return True
    # Si el estado actual es "cancelada" o "finalizada", no se permite ninguna transición
    if estado_actual in ["cancelada", "finalizada"]:
        return False
    #solo se puede cancelar antes del inicio
    if estado_nuevo == "cancelada":
        return ahora < inicio
    #solo se puede finalizar cuando llega la hora de finalizacion
    if estado_nuevo == "finalizada":
        return ahora >= fin
    
    return False


def obtener_estado_reserva(id_reserva):
    sql = """
        SELECT id, estado, fecha_hora_inicio, fecha_hora_fin
        FROM reservas
        WHERE id = %s
        """
    #%s es identificador por separa para que MYSQL procese correctamente el parametro
    reserva = query_one(sql,(id_reserva,))
    #se guardan los datos de la reserva en un diccionario, sino devuelve none "flechita hacia arriba"
    return reserva

def cambiar_estado_reserva(id_reserva, estado_nuevo):

    estados_validos = [
        "confirmada",
        "cancelada",
        "finalizada"
    ]

    if estado_nuevo not in estados_validos:
        return {
            "error": "El estado solicitado NO es válido"
        }

    reserva = obtener_estado_reserva(id_reserva)

    if reserva is None:
        return {
            "error": "Reserva NO encontrada"
        }
    
    estado_actual = reserva["estado"]
    inicio = reserva["fecha_hora_inicio"]
    fin = reserva["fecha_hora_fin"]

    inicio = inicio.replace(tzinfo=ZONA_CLUB)
    fin = fin.replace(tzinfo=ZONA_CLUB)

    ahora = datetime.now(ZONA_CLUB)

    permitido = validar_transicion(
        estado_actual,
        estado_nuevo, 
        inicio, 
        fin, 
        ahora
    )
    if not permitido:
        return {
            "error": "la transición de estado no está permitida"
        }

    if estado_actual == estado_nuevo:
        return {
            "mensaje": "la reserva ya tiene ese estado"
        }

    sql = """
        UPDATE reservas
        SET estado = %s
        WHERE id = %s
    """

    execute(sql, (estado_nuevo, id_reserva))

    return {
        "mensaje": f"Estado de reserva actualizado correctamente"
        }