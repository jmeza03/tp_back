import re

def validar_alta_socio(nombre: str, email: str):

    # El nombre no podra quedar vacio
    if not nombre or not nombre.strip():
        return False, "El nombre del socio es obligatorio y no puede contener solo espacios."
    
    # El correo debera tener un formato valido 
    patron_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(patron_email, email.strip()):
        return False, "El formato del correo electronico es invalido."
        
    return True, ""

def validar_alta_cancha(nombre: str, precio_hora: int):

    # El nombre no podra quedar vacio despues de quitar espacios
    if not nombre or not nombre.strip():
        return False, "El nombre de la cancha es obligatorio."
        
    # El precio debera ser un entero positivo mayor que cero 
    if not isinstance(precio_hora, int) or precio_hora <= 0:
        return False, "La tarifa por hora debe ser un numero entero mayor que cero."
        
    return True, ""
