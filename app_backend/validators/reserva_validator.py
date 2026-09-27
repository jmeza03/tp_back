from datetime import datetime
# constantes de negocio definidas constants.py
# Usa las reglas generales de reservas definidas en constants.py
from constants import (
    ZONA_HORARIA_CLUB,
    HORA_APERTURA_CLUB,
    HORA_CIERRE_CLUB,
    DURACION_MINIMA_RESERVA_HORAS,
    DURACION_MAXIMA_RESERVA_HORAS
)

def validar_nueva_reserva(fecha_hora_inicio: datetime, fecha_hora_fin: datetime):

    ahora = datetime.now(ZONA_HORARIA_CLUB)

    # forzar que las fechas recibidas tengan asignada la zona GMT-3
    if fecha_hora_inicio.tzinfo is None:
        fecha_hora_inicio = fecha_hora_inicio.replace(tzinfo=ZONA_HORARIA_CLUB)
    if fecha_hora_fin.tzinfo is None:
        fecha_hora_fin = fecha_hora_fin.replace(tzinfo=ZONA_HORARIA_CLUB)

    # solo se podron crear reservas cuyo inicio sea posterior al momento actual 
    if fecha_hora_inicio <= ahora:
        return False, "La fecha y hora de inicio debe ser posterior al momento actual."

    #  validacion logica cronologica
    if fecha_hora_inicio >= fecha_hora_fin:
        return False, "La fecha de inicio debe ser menor que la fecha de finalizacion."

    #  comenzaron y terminaron en horas en punto 
    if fecha_hora_inicio.minute != 0 or fecha_hora_inicio.second != 0 or fecha_hora_inicio.microsecond != 0:
        return False, "El horario de inicio debe ser una hora en punto (ej. 14:00)."
    if fecha_hora_fin.minute != 0 or fecha_hora_fin.second != 0 or fecha_hora_fin.microsecond != 0:
        return False, "El horario de finalizacion debe ser una hora en punto."

    # el intervalo completo debe quedar dentro del horario del club (08:00 a 23:00)
    if fecha_hora_inicio.hour < HORA_APERTURA_CLUB or fecha_hora_inicio.hour > HORA_CIERRE_CLUB:
        return False, f"El horario de inicio debe estar dentro del rango del club ({HORA_APERTURA_CLUB}:00 a {HORA_CIERRE_CLUB}:00)."
    if fecha_hora_fin.hour < HORA_APERTURA_CLUB or fecha_hora_fin.hour > HORA_CIERRE_CLUB:
        return False, f"El horario de fin debe estar dentro del rango del club ({HORA_APERTURA_CLUB}:00 a {HORA_CIERRE_CLUB}:00)."

    # no podron atravesar la medianoche
    if fecha_hora_inicio.date() != fecha_hora_fin.date():
        return False, "La reserva no puede atravesar la medianoche."

    # las reservas duraron entre una y tres horas completas 
    duracion = (fecha_hora_fin - fecha_hora_inicio).total_seconds() / 3600
    if duracion < DURACION_MINIMA_RESERVA_HORAS or duracion > DURACION_MAXIMA_RESERVA_HORAS:
        return False, f"La reserva debe durar obligatoriamente entre {int(DURACION_MINIMA_RESERVA_HORAS)} y {int(DURACION_MAXIMA_RESERVA_HORAS)} horas completas."

    return True, ""
