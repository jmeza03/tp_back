from datetime import timezone, timedelta

# zona horaria fija 
ZONA_HORARIA_CLUB = timezone(timedelta(hours=-3))

# restricciones horarias comerciales del club
HORA_APERTURA_CLUB = 8  
HORA_CIERRE_CLUB = 23 

# restricciones de duracion de las reservas 
DURACION_MINIMA_RESERVA_HORAS = 1.0
DURACION_MAXIMA_RESERVA_HORAS = 3.0

# paginacion de listados 
PAGINACION_LIMIT_POR_DEFECTO = 10
PAGINACION_LIMIT_MAXIMO = 100
PAGINACION_OFFSET_POR_DEFECTO = 0

# estados del ciclo de vida de las reservas
ESTADO_CONFIRMADA = "confirmada"
ESTADO_CANCELADA = "cancelada"
ESTADO_FINALIZADA = "finalizada"

# validacion de payloads en endpoints
ESTADOS_RESERVA_VALIDOS = [ESTADO_CONFIRMADA, ESTADO_CANCELADA, ESTADO_FINALIZADA]
