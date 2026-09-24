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
    