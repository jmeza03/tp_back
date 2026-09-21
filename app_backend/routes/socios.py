import re
from flask import Blueprint,request, jsonify
from db import execute, query_all, query_one

socios_bp = Blueprint("socios", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def  _error(estado, mensaje):
    return jsonify({ "error": mensaje}), estado

def _fila_a_json(fila):
    return {
        "id": fila["id"],
        "nombre": fila["nombre"],
        "email": fila["email"],
        "activo": bool(fila["activo"])
    }


# GET /socios
@socios_bp.get("/socios")
def listar():
    try:
        limite = int(request.args.get("_limit", 10))
        desplazamiento = int(request.args.get("_offset", 0))
    except ValueError:
        return _error(400, "Los parámetros '_limit' y '_offset' deben ser enteros.")
    if not (1 <= limite <= 100):
        return _error(400, "El parámetro '_limit' debe estar entre 1 y 100.")
    if desplazamiento < 0:
        return _error(400, "El parámetro '_offset' no puede ser negativo.")

    filtros,parametros = [], []
    nombre = request.args.get("nombre")
    if nombre:
        filtros.append("nombre LIKE %s")
        parametros.append(f"%{nombre}%")

    activo = request.args.get("activo")
    if activo is not None:
        if activo not in ("true", "false"):
            return _error(400, "El parámetro 'activo' debe ser 'true' o 'false'.")
        filtros.append("activo = %s")
        parametros.append(1 if activo == "true" else 0)

    clausula_where = f"WHERE {' AND '.join(filtros)}" if filtros else ""

    total = query_one(
        f"SELECT COUNT(*) as total FROM socios {clausula_where}", parametros
    )["total"]
    
    filas = query_all(
        f"SELECT id, nombre, email, activo FROM socios {clausula_where} "
        f"ORDER BY id ASC LIMIT %s OFFSET %s",
        parametros + [limite, desplazamiento]
    )

    socios = [_fila_a_json(fila) for fila in filas]

    url_base = request.base_url

    def _link(nuevo_desplazamiento):
        consulta = dict(request.args.to_dict())
        consulta["_limit"] = limite
        consulta["_offset"] = nuevo_desplazamiento
        return f"{url_base}?" + "&".join(f"{k}={v}" for k, v in consulta.items())

    ultimo_desplazamiento = (
        max(0,((total - 1) // limite )* limite) if total > 0 else 0
    )

    enlaces = {
        "_first": _link(0),
        "_prev": _link(max(0, desplazamiento - limite)) if desplazamiento > 0 else None,
        "_next": _link(desplazamiento + limite) if desplazamiento + limite < total else None,
        "_last": _link(ultimo_desplazamiento) 
    }
    return jsonify({"total": total, "socios": socios, "_links": enlaces}), 200


# POST /socios
@socios_bp.post("/socios")
def crear():
    datos = request.get_json(silent=True)
    if not datos or not isinstance(datos, dict):
        return _error(400, "El cuerpo de la solicitud debe ser un JSON válido.")
    if set(datos.keys()) - {"nombre", "email"}:
        return _error(400, "El cuerpo contiene campos no permitidos. Solo se permiten 'nombre' y 'email'.")

    if "nombre" not in datos:
        return _error(400, "El campo 'nombre' es obligatorio.")
    nombre = datos["nombre"]
    if not isinstance(nombre, str) or not nombre.strip():
        return _error(400, "El campo 'nombre' debe ser una cadena no vacía.")
    nombre = nombre.strip()

    if "email" not in datos:
        return _error(400, "El campo 'email' es obligatorio.")
    email = datos["email"]
    if not isinstance(email, str):
        return _error(400, "El campo 'email' debe ser texto.")
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        return _error(400, "El campo 'email' no es válido.")
    if query_one("SELECT id FROM socios WHERE email = %s", [email]):
        return _error(409, "El correo electrónico ya está registrado.")

    nuevo_id = execute(
        "INSERT INTO socios (nombre, email, activo) VALUES (%s, %s, 1)",
        [nombre, email]
    )


    socio_creado = query_one(
        "SELECT id, nombre, email, activo FROM socios WHERE id = %s", [nuevo_id]
    )
    return jsonify(_fila_a_json(socio_creado)), 201


# GET /socios/<id>
@socios_bp.get("/socios/<int:id>")
def obtener(id):
    fila = query_one(
        "SELECT id, nombre, email, activo FROM socios WHERE id = %s", [id]
    )
    if not fila:
        return _error(404, "Socio no encontrado.")
    return jsonify(_fila_a_json(fila)), 200


# PATCH /socios/<id>
@socios_bp.patch("/socios/<int:id>")
def actualizar(id):
    if not query_one("SELECT id FROM socios WHERE id = %s", [id]):
        return _error(404, "Socio no encontrado.")

    datos = request.get_json(silent=True)
    if not datos or not isinstance(datos, dict):
        return _error(400, "El cuerpo de la solicitud debe ser un JSON válido.")
    if set(datos.keys()) - {"nombre", "email", "activo"}:
        return _error(400, "El cuerpo de la solicitud contiene campos no permitidos.")

    campos, valores = [], []

    if "nombre" in datos:
        if not isinstance(datos["nombre"], str) or not datos["nombre"].strip():
            return _error(400, "El campo 'nombre' debe ser una cadena no vacía.")
        campos.append("nombre = %s")
        valores.append(datos["nombre"].strip())

    if "email" in datos:
        if not isinstance(datos["email"],str):
            return _error(400, "El campo 'email' debe ser una cadena no vacía.")
        email = datos["email"].strip().lower()
        if not EMAIL_RE.match(email):
            return _error(400, "El campo 'email' debe ser un correo electrónico válido.")
        if query_one(
            "SELECT id FROM socios WHERE email = %s AND id != %s", [email, id]
        ):
            return _error(409, "El correo electrónico ya está registrado por otro socio.")
        campos.append("email = %s")
        valores.append(email)

    if "activo" in datos:
        if not isinstance(datos["activo"], bool):
            return _error(400, "El campo 'activo' debe ser un valor booleano.")
        campos.append("activo = %s")
        valores.append(datos["activo"])

    if not campos:
        return _error(400, "No se proporcionaron campos para actualizar.")

    execute(
        f"UPDATE socios SET {', '.join(campos)} WHERE id = %s", 
        valores + [id]
    )

    actualizado = query_one(
        "SELECT id, nombre, email, activo FROM socios WHERE id = %s", [id]
    )
    return jsonify(_fila_a_json(actualizado)), 200
