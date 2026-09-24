from flask import Blueprint, request, jsonify
from db import fetch_all, fetch_one, execute_query
from datetime import datetime

canchas_bp = Blueprint('canchas', __name__)

@canchas_bp.route('/canchas', methods=['GET'])
def listar_canchas():
    limit = int(request.args.get('_limit', 10)) #De a cuantos va mostrando
    offset = int(request.args.get('_offset', 0)) #De a cuanto va saltando

    if limit < 1 or limit >100 or offset < 0: #Condiciones
        return jsonify({"error": "Parametros de paginacion incalidos"}), 400

    #Pido al usuario
    id_deporte = request.args.get('id_deporte')
    nombre = request.args.get('nombre')
    techada = request.args.get('techada')
    activa = request.args.get('activa')

    #Selecciono de la db
    sql = "SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas WHERE 1=1"
    params = []

    #Verifico y le voy sumando filtros
    if id_deporte:
        sql += " AND id_deporte = %s "
        params.append(id_deporte)

    if nombre:
        sql += " AND LOWER(nombre) LIKE LOWER(%s)"
        params.append(f"%{nombre}%")

    #Son booleanos
    if techada is not None:
        sql += " AND techada = %s"
        params.append(techada.lower() == 'true' )

    if activa is not None:
        sql += " AND activa = %s"
        params.append(activa.lower() == 'true')

    sql += " ORDER BY id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset]) #.extend: sumo lista 

    canchas_obtenidas = fetch_all(sql, params)
    prev_offset = max(0, offset - limit)
    #Canchas: muestra las canchas que filtrò, links: lista de la pagina
    respuesta = {
        "canchas": canchas_obtenidas,
        "_links": {
            "_first": f"/canchas?_limit={limit}&_offset=0",
            "_prev": f"/canchas?_limit={limit}&_offset={prev_offset}",
            "_next": f"/canchas?_limit={limit}&_offset={offset + limit}"
        }
    }
    return jsonify(respuesta), 200

@canchas_bp.route('/canchas', methods=['POST']) #Crear canchas
def crear_cancha():

    data=request.get_json() or {} 

    #Toma recibido json y traduce en diccionario pyhton o con el {} hace que quede como none
    nombre = data.get('nombre')
    id_deporte = data.get('id_deporte')
    precio_hora = data.get('precio_hora')

    #Evalua condiciones
    if nombre is None or id_deporte is None or precio_hora is None:
        return jsonify({"error": "Los campos nombre, id_deporte y precio_hora son obligatorios"}), 400

    nombre_limpio = str(nombre).strip()
    if not nombre_limpio:
        return jsonify({"error": "El nombre no puede estar vacío"}), 400

    if not isinstance(precio_hora, int) or precio_hora <= 0:
        return jsonify({"error": "El precio por hora debe ser un número entero positivo"}), 400

    deporte_existente = fetch_one("SELECT id FROM deportes WHERE id = %s", [id_deporte])
    if not deporte_existente:
        return jsonify({"error": "El deporte especificado no existe"}), 400

    #Valores predeterminados
    techada = data.get('techada', False)
    activa = data.get('activa', True)
    #Comando para consultar tabla
    sql = """
        INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
        VALUES (%s, %s, %s, %s, %s)
    """
    #Valores %s
    params = [nombre_limpio, id_deporte, precio_hora, techada, activa]

    cancha_id = execute_query(sql, params) #Se realiza la consulta

    nueva_cancha = fetch_one("SELECT * FROM canchas WHERE id = %s", [cancha_id])

    return jsonify(nueva_cancha), 201


@canchas_bp.route('/canchas/<int:cancha_id>', methods=['GET'])
def obtener_cancha_por_id(cancha_id):
    #Recibe y consulta tabla
    sql = "SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas WHERE id = %s"
    cancha = fetch_one(sql, [cancha_id])

    #Si no existe, error
    if not cancha:
        return jsonify({"error": "La cancha solicitada no existe"}), 404

    
    return jsonify(cancha), 200

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['PATCH'])
def actualizar_cancha(cancha_id):
    #Recibe id

    cancha_existente = fetch_one("SELECT * FROM canchas WHERE id = %s", [cancha_id])
    if not cancha_existente:
        return jsonify({"error": "La cancha solicitada no existe"}), 404

    
    data = request.get_json() or {}

    campos_a_actualizar = [] #guarda fragmento de SQL
    params = [] #Guarda los valores para la consulta

    #Verifica nombre no vacio
    if 'nombre' in data:
        nombre_limpio = str(data['nombre']).strip()
        if not nombre_limpio:
            return jsonify({"error": "El nombre no puede estar vacío"}), 400
        campos_a_actualizar.append("nombre = %s")
        params.append(nombre_limpio)

    if 'precio_hora' in data:
        precio_hora = data['precio_hora']
        if not isinstance(precio_hora, int) or precio_hora <= 0:
            return jsonify({"error": "El precio debe ser un número entero positivo"}), 400
        campos_a_actualizar.append("precio_hora = %s")
        params.append(precio_hora)

    if 'techada' in data:
        campos_a_actualizar.append("techada = %s")
        params.append(bool(data['techada']))

    if 'activa' in data:
        campos_a_actualizar.append("activa = %s")
        params.append(bool(data['activa']))

   
    if not campos_a_actualizar:
        return jsonify({"error": "No se enviaron campos válidos para actualizar"}), 400

    
    sql = f"UPDATE canchas SET {', '.join(campos_a_actualizar)} WHERE id = %s"
    params.append(cancha_id)

   
    execute_query(sql, params) #Ejecuto actualizacion

    cancha_actualizada = fetch_one("SELECT * FROM canchas WHERE id = %s", [cancha_id])

    return jsonify(cancha_actualizada), 200


@canchas_bp.route('/canchas/<int:cancha_id>', methods=['DELETE'])
def eliminar_cancha(cancha_id):
   #Recibe id

    cancha = fetch_one("SELECT id FROM canchas WHERE id = %s", [cancha_id])

    #Si cancha no existe
    if not cancha:
        return jsonify({"error": "La cancha solicitada no existe"}), 404

    #Verifica si esta reservado
    reserva_existente = fetch_one("SELECT id FROM reservas WHERE id_cancha = %s", [cancha_id])
    
    if reserva_existente:
        return jsonify({"error": "No se puede eliminar la cancha porque tiene reservas asociadas. Podra desactivarse mediante PATCH."}), 409
    
    #Si no esta reservada y existe cancha
    execute_query("DELETE FROM canchas WHERE id = %s", [cancha_id])
    
    return '', 204


@canchas_bp.route('/canchas/disponibles', methods=['GET'])
def obtener_canchas_disponibles():
    limit = int(request.args.get('_limit', 10))
    offset = int(request.args.get('_offset', 0))
    
    if limit < 1 or limit > 100 or offset < 0:
        return jsonify({"error": "Parametros de paginacion invalidos"}), 400

    fecha_inicio = request.args.get('fecha_hora_inicio')
    fecha_fin = request.args.get('fecha_hora_fin')
    id_deporte = request.args.get('id_deporte')
    techada = request.args.get('techada')

    if not fecha_inicio or not fecha_fin:
        return jsonify({"error": "Debe proporcionar 'fecha_hora_inicio' y 'fecha_hora_fin'"}), 400

    #si dentro del try ocurre error, salta a except
    try:
        #fromisoformat: corversor de str a fecha python
        dt_inicio = datetime.fromisoformat(fecha_inicio)
        dt_fin = datetime.fromisoformat(fecha_fin)
        if dt_inicio >= dt_fin:
            return jsonify({"error": "'fecha_hora_inicio' debe ser menor a 'fecha_hora_fin'"}), 400
    except ValueError:
        return jsonify({"error": "Formato de fecha/hora inválido. Use formato YYYY-MM-DDTHH:MM:SS"}), 400

    #Comando SQL
    sql = """
        SELECT id, nombre, id_deporte, precio_hora, techada, activa
        FROM canchas 
        WHERE activa = TRUE
          AND id NOT IN (
              SELECT id_cancha 
              FROM reservas r 
              WHERE estado != 'cancelada'
                AND fecha_hora_inicio < %s 
                AND fecha_hora_fin > %s
          )
    """
    #Variables %s
    params = [dt_fin, dt_inicio]

    
    if id_deporte:
        sql += " AND id_deporte = %s"
        params.append(id_deporte)

    if techada is not None:
        sql += " AND techada = %s"
        params.append(techada.lower() == 'true')

    sql += " ORDER BY id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    canchas_libres = fetch_all(sql, params)
    prev_offset = max(0, offset - limit)

    respuesta = {
        "canchas": canchas_libres,
        "_links": {
            "_first": f"/canchas/disponibles?fecha_hora_inicio={fecha_inicio}&fecha_hora_fin={fecha_fin}&_limit={limit}&_offset=0",
            "_prev": f"/canchas/disponibles?fecha_hora_inicio={fecha_inicio}&fecha_hora_fin={fecha_fin}&_limit={limit}&_offset={prev_offset}",
            "_next": f"/canchas/disponibles?fecha_hora_inicio={fecha_inicio}&fecha_hora_fin={fecha_fin}&_limit={limit}&_offset={offset + limit}"
        }
    }
    return jsonify(respuesta), 200