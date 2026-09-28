# Usa las funciones de acceso a la base de datos definidas en db.py
from db import query_one, query_all, execute
from datetime import datetime
def obtener_reservas(limit,offset,canchas_id, socio_id, estado_arg,fecha_desde,fecha_hasta):
    sql = "SELECT * FROM reservas WHERE 1=1 "
    parametros = []
    sql = comparador(sql, parametros, "id_cancha = ", canchas_id)
    sql = comparador(sql, parametros, "id_socio = ",socio_id)
    sql = comparador(sql, parametros, "estado = ", estado_arg)

    if (fecha_desde is not None) and fecha_hasta is None:
        sql += "AND fecha_hora_inicio >= %s"
        parametros.append(fecha_desde)
    if (fecha_hasta is not None) and fecha_desde is None:
        sql += "AND fecha_hora_inicio <= %s"
        parametros.append(fecha_hasta)
    if (fecha_hasta is not None) and (fecha_desde is not None):
        sql += "AND fecha_hora_inicio <= %s AND fecha_hora_inicio >= %s"
        parametros.append(fecha_hasta)
        parametros.append(fecha_desde)
    #paginado
    sql+= " ORDER BY id ASC LIMIT %s OFFSET %s"
    parametros.append(limit)
    parametros.append(offset)
    reservas = query_all(sql,parametros)

    
    return reservas

#cantidad de reservas en la base
def contador_reservas():
    sql = "SELECT COUNT(*) AS total FROM reservas"
    return query_all(sql)

def obtener_reserva_id(reserva_id):
    sql = "SELECT * FROM reservas WHERE id = %s"
    parametros = [reserva_id]
    return query_one(sql, parametros)

#solo es un if 
def comparador(sql, parametros, condicion, valor):
    if valor is not None:
        sql += f"AND {condicion} %s"
        parametros.append(valor)
    return sql


def agregar_reserva(datos):
    # Inserta la reserva usando los nombres de columnas actuales de la base.
    # Luego habrá que ajustar estos campos si el contrato exige otros nombres o formato.
    sql = """
        INSERT INTO reservas
        (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, tarifa_hora, total)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    precio_hora = precio_hora_cancha(datos["id_cancha"])
    precio_total = precio_hora * precio_xhora(
        datos["fecha_hora_inicio"],
        datos["fecha_hora_fin"]
    )

    parametros = [
        datos["id_socio"],
        datos["id_cancha"],
        datos["fecha_hora_inicio"],
        datos["fecha_hora_fin"],
        precio_hora,
        precio_total
    ]

    execute(sql, parametros)

def precio_hora_cancha(id_cancha): #conseguir el precio x hora de la cancha por el id
    sql = "SELECT precio_hora FROM canchas WHERE id = %s"
    parametros = [id_cancha]
    resultado = query_one(sql, parametros)
    return resultado["precio_hora"]

def precio_xhora(fecha_hora_in,fecha_hora_fin): #calcular cantidad horas de la nueva reserva
    return (datetime.fromisoformat(fecha_hora_fin) - datetime.fromisoformat(fecha_hora_in)).total_seconds() / 3600

def actualizar_estado(id_reserva, estado):
    sql = "UPDATE reservas SET estado = %s WHERE id = %s"
    parametros = [estado["estado"], id_reserva]
    return execute(sql,parametros)

def hay_superposicion_reserva(datos): #ver si hay una reserva en las horas dadas
    sql = "SELECT EXISTS ( SELECT 1 FROM reservas WHERE id_cancha = %s AND fecha_hora_inicio < %s AND fecha_hora_fin > %s) AS existe_superposicion"
    parametros = [datos["id_cancha"],datos["fecha_hora_fin"],datos["fecha_hora_inicio"]]
    return bool(query_one(sql,parametros)["existe_superposicion"])