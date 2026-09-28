from flask import Blueprint, request, jsonify
from db import query_all, query_one, execute
from datetime import datetime
from urllib.parse import urlencode

canchas_bp = Blueprint('canchas', __name__)


@canchas_bp.route('/canchas', methods=['GET'])
def listar_canchas():
    try:
        limit = int(request.args.get('_limit', 10)) #De a cuantos va mostrando
        offset = int(request.args.get('_offset', 0)) #De a cuanto va saltando
    except ValueError:
        return jsonify({"error": "Los parametros de paginacion deben ser enteros"}), 400

    if limit < 1 or limit > 100 or offset < 0: #Condiciones
        return jsonify({"error": "Parametros de paginacion invalidos"}), 400

    parametros_permitidos = {'_limit', '_offset', 'id_deporte', 'nombre', 'techada', 'activa'}
    if set(request.args.keys()) - parametros_permitidos:
        return jsonify({"error": "Se enviaron parametros no permitidos"}), 400

    #Pido al usuario
    id_deporte = request.args.get('id_deporte')
    nombre = request.args.get('nombre')
    techada = request.args.get('techada')
    activa = request.args.get('activa')

    #Selecciono de la db
    sql = "SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas WHERE 1=1"
    params = []

    #Verifico y le voy sumando filtros
    if id_deporte is not None:
        try:
            id_deporte = int(id_deporte)
        except ValueError:
            return jsonify({"error": "El id_deporte debe ser un entero"}), 400

        if id_deporte <= 0:
            return jsonify({"error": "El id_deporte debe ser positivo"}), 400

        sql += " AND id_deporte = %s"
        params.append(id_deporte)

    if nombre is not None:
        sql += " AND LOWER(nombre) LIKE LOWER(%s)"
        params.append(f"%{nombre}%")

    #Son booleanos
    if techada is not None:
        if techada not in ('true', 'false'):
            return jsonify({"error": "El parametro techada debe ser 'true' o 'false'"}), 400
        sql += " AND techada = %s"
        params.append(techada == 'true')

    if activa is not None:
        if activa not in ('true', 'false'):
            return jsonify({"error": "El parametro activa debe ser 'true' o 'false'"}), 400
        sql += " AND activa = %s"
        params.append(activa == 'true')

    total = query_one(
        sql.replace(
            "SELECT id, nombre, id_deporte, precio_hora, techada, activa",
            "SELECT COUNT(*) as total"
        ),
        params
    )["total"]

    sql += " ORDER BY id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset]) #.extend: sumo lista

    canchas_obtenidas = query_all(sql, params)
    ultimo_offset = max(0, ((total - 1) // limit) * limit) if total > 0 else 0

    def link(nuevo_offset):
        consulta = request.args.to_dict()
        consulta['_limit'] = limit
        consulta['_offset'] = nuevo_offset
        return f"{request.base_url}?{urlencode(consulta)}"

    #Canchas: muestra las canchas que filtrò, links: lista de la pagina
    respuesta = {
        "canchas": canchas_obtenidas,
        "_links": {
            "_first": {"href": link(0)},
            "_prev": {"href": link(max(0, offset - limit))} if offset > 0 else None,
            "_next": {"href": link(offset + limit)} if offset + limit < total else None,
            "_last": {"href": link(ultimo_offset)}
        }
    }
    return jsonify(respuesta), 200


@canchas_bp.route('/canchas', methods=['POST']) #Crear canchas
def crear_cancha():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la solicitud debe ser un JSON valido"}), 400

    campos_permitidos = {'nombre', 'id_deporte', 'precio_hora', 'techada', 'activa'}
    if set(data.keys()) - campos_permitidos:
        return jsonify({"error": "El cuerpo contiene campos no permitidos"}), 400

    #Toma recibido json y traduce en diccionario pyhton
    nombre = data.get('nombre')
    id_deporte = data.get('id_deporte')
    precio_hora = data.get('precio_hora')

    #Evalua condiciones
    if nombre is None or id_deporte is None or precio_hora is None:
        return jsonify({"error": "Los campos nombre, id_deporte y precio_hora son obligatorios"}), 400

    if not isinstance(nombre, str):
        return jsonify({"error": "El nombre debe ser texto"}), 400

    nombre_limpio = nombre.strip()
    if not nombre_limpio:
        return jsonify({"error": "El nombre no puede estar vacío"}), 400

    if not isinstance(id_deporte, int) or isinstance(id_deporte, bool) or id_deporte <= 0:
        return jsonify({"error": "El id_deporte debe ser un entero positivo"}), 400

    if not isinstance(precio_hora, int) or isinstance(precio_hora, bool) or precio_hora <= 0:
        return jsonify({"error": "El precio por hora debe ser un número entero positivo"}), 400

    deporte_existente = query_one("SELECT id FROM deportes WHERE id = %s", [id_deporte])
    if not deporte_existente:
        return jsonify({"error": "El deporte especificado no existe"}), 404

    #Valores predeterminados
    techada = data.get('techada', False)
    activa = data.get('activa', True)

    if not isinstance(techada, bool):
        return jsonify({"error": "El campo techada debe ser booleano"}), 400

    if not isinstance(activa, bool):
        return jsonify({"error": "El campo activa debe ser booleano"}), 400

    #Comando para consultar tabla
    sql = """
        INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
        VALUES (%s, %s, %s, %s, %s)
    """

    params = [nombre_limpio, id_deporte, precio_hora, techada, activa]

    cancha_id = execute(sql, params) #Se realiza la consulta

    nueva_cancha = query_one("SELECT * FROM canchas WHERE id = %s", [cancha_id])

    return jsonify(nueva_cancha), 201


@canchas_bp.route('/canchas/<int:cancha_id>', methods=['GET'])
def obtener_cancha_por_id(cancha_id):
    if cancha_id <= 0:
        return jsonify({"error": "La cancha solicitada no existe"}), 404

    #Recibe y consulta tabla
    sql = "SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas WHERE id = %s"
    cancha = query_one(sql, [cancha_id])

    #Si no existe, error
    if not cancha:
        return jsonify({"error": "La cancha solicitada no existe"}), 404

    return jsonify(cancha), 200


@canchas_bp.route('/canchas/<int:cancha_id>', methods=['PATCH'])
def actualizar_cancha(cancha_id):
    #Recibe id
    if cancha_id <= 0:
        return jsonify({"error": "La cancha solicitada no existe"}), 404

    cancha_existente = query_one("SELECT * FROM canchas WHERE id = %s", [cancha_id])
    if not cancha_existente:
        return jsonify({"error": "La cancha solicitada no existe"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la solicitud debe ser un JSON valido"}), 400

    if not data:
        return jsonify({"error": "No se enviaron campos para actualizar"}), 400

    campos_permitidos = {'nombre', 'precio_hora', 'techada', 'activa'}
    if set(data.keys()) - campos_permitidos:
        return jsonify({"error": "El cuerpo contiene campos no permitidos. id_deporte no puede modificarse"}), 400

    campos_a_actualizar = [] #guarda fragmento de SQL
    params = [] #Guarda los valores para la consulta

    #Verifica nombre no vacio
    if 'nombre' in data:
        if not isinstance(data['nombre'], str):
            return jsonify({"error": "El nombre debe ser texto"}), 400

        nombre_limpio = data['nombre'].strip()

        if not nombre_limpio:
            return jsonify({"error": "El nombre no puede estar vacío"}), 400

        campos_a_actualizar.append("nombre = %s")
        params.append(nombre_limpio)

    if 'precio_hora' in data:
        precio_hora = data['precio_hora']

        if not isinstance(precio_hora, int) or isinstance(precio_hora, bool) or precio_hora <= 0:
            return jsonify({"error": "El precio debe ser un número entero positivo"}), 400

        campos_a_actualizar.append("precio_hora = %s")
        params.append(precio_hora)

    if 'techada' in data:
        if not isinstance(data['techada'], bool):
            return jsonify({"error": "El campo techada debe ser booleano"}), 400

        campos_a_actualizar.append("techada = %s")
        params.append(data['techada'])

    if 'activa' in data:
        if not isinstance(data['activa'], bool):
            return jsonify({"error": "El campo activa debe ser booleano"}), 400

        campos_a_actualizar.append("activa = %s")
        params.append(data['activa'])

    sql = f"UPDATE canchas SET {', '.join(campos_a_actualizar)} WHERE id = %s"
    params.append(cancha_id)

    execute(sql, params) #Ejecuto actualizacion

    cancha_actualizada = query_one("SELECT * FROM canchas WHERE id = %s", [cancha_id])

    return jsonify(cancha_actualizada), 200


@canchas_bp.route('/canchas/<int:cancha_id>', methods=['DELETE'])
def eliminar_cancha(cancha_id):
    #Recibe id
    if cancha_id <= 0:
        return jsonify({"error": "La cancha solicitada no existe"}), 404

    cancha = query_one("SELECT id FROM canchas WHERE id = %s", [cancha_id])

    #Si no existe cancha
    if not cancha:
        return jsonify({"error": "La cancha solicitada no existe"}), 404

    #Verifica si esta reservado
    reserva_existente = query_one(
        "SELECT id FROM reservas WHERE id_cancha = %s LIMIT 1",
        [cancha_id]
    )

    if reserva_existente:
        return jsonify({"error": "No se puede eliminar la cancha porque tiene reservas asociadas. Podra desactivarse mediante PATCH."}), 409

    #Si no esta reservada y existe cancha
    execute("DELETE FROM canchas WHERE id = %s", [cancha_id])

    return '', 204


@canchas_bp.route('/canchas/disponibles', methods=['GET'])
def obtener_canchas_disponibles():
    try:
        limit = int(request.args.get('_limit', 10))
        offset = int(request.args.get('_offset', 0))
    except ValueError:
        return jsonify({"error": "Los parametros de paginacion deben ser enteros"}), 400

    if limit < 1 or limit > 100 or offset < 0:
        return jsonify({"error": "Parametros de paginacion invalidos"}), 400

    parametros_permitidos = {
        '_limit', '_offset', 'fecha', 'hora_inicio',
        'hora_fin', 'id_deporte', 'techada'
    }

    if set(request.args.keys()) - parametros_permitidos:
        return jsonify({"error": "Se enviaron parametros no permitidos"}), 400

    fecha = request.args.get('fecha')
    hora_inicio = request.args.get('hora_inicio')
    hora_fin = request.args.get('hora_fin')
    id_deporte = request.args.get('id_deporte')
    techada = request.args.get('techada')

    if not fecha or not hora_inicio or not hora_fin:
        return jsonify({"error": "Debe proporcionar 'fecha', 'hora_inicio' y 'hora_fin'"}), 400

    try:
        dt_inicio = datetime.strptime(
            f"{fecha} {hora_inicio}",
            "%Y-%m-%d %H:%M"
        )
        dt_fin = datetime.strptime(
            f"{fecha} {hora_fin}",
            "%Y-%m-%d %H:%M"
        )

        if dt_inicio >= dt_fin:
            return jsonify({"error": "'hora_inicio' debe ser menor a 'hora_fin'"}), 400

    except ValueError:
        return jsonify({"error": "Formato de fecha u hora inválido"}), 400

    if id_deporte is not None:
        try:
            id_deporte = int(id_deporte)
        except ValueError:
            return jsonify({"error": "El id_deporte debe ser un entero"}), 400

        if id_deporte <= 0:
            return jsonify({"error": "El id_deporte debe ser positivo"}), 400

    if techada is not None and techada not in ('true', 'false'):
        return jsonify({"error": "El parametro techada debe ser 'true' o 'false'"}), 400

    #Comando SQL
    sql = """
        SELECT c.id, c.nombre, c.id_deporte, c.precio_hora, c.techada, c.activa
        FROM canchas c
        WHERE c.activa = TRUE
          AND NOT EXISTS (
              SELECT 1
              FROM reservas r
              WHERE r.id_cancha = c.id
                AND r.estado = 'confirmada'
                AND r.fecha_hora_inicio < %s
                AND r.fecha_hora_fin > %s
          )
    """

    params = [dt_fin, dt_inicio]

    if id_deporte is not None:
        sql += " AND c.id_deporte = %s"
        params.append(id_deporte)

    if techada is not None:
        sql += " AND c.techada = %s"
        params.append(techada == 'true')

    sql += " ORDER BY c.id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    canchas_libres = query_all(sql, params)

    total_sql = """
        SELECT COUNT(*) AS total
        FROM canchas c
        WHERE c.activa = TRUE
          AND NOT EXISTS (
              SELECT 1
              FROM reservas r
              WHERE r.id_cancha = c.id
                AND r.estado = 'confirmada'
                AND r.fecha_hora_inicio < %s
                AND r.fecha_hora_fin > %s
          )
    """

    total_params = [dt_fin, dt_inicio]

    if id_deporte is not None:
        total_sql += " AND c.id_deporte = %s"
        total_params.append(id_deporte)

    if techada is not None:
        total_sql += " AND c.techada = %s"
        total_params.append(techada == 'true')

    total = query_one(total_sql, total_params)["total"]
    ultimo_offset = max(0, ((total - 1) // limit) * limit) if total > 0 else 0

    def link(nuevo_offset):
        consulta = request.args.to_dict()
        consulta['_limit'] = limit
        consulta['_offset'] = nuevo_offset
        return f"{request.base_url}?{urlencode(consulta)}"

    respuesta = {
        "canchas": canchas_libres,
        "_links": {
            "_first": {"href": link(0)},
            "_prev": {"href": link(max(0, offset - limit))} if offset > 0 else None,
            "_next": {"href": link(offset + limit)} if offset + limit < total else None,
            "_last": {"href": link(ultimo_offset)}
        }
    }

    return jsonify(respuesta), 200