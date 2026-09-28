# Sistema de Reservas de Club Deportivo

API REST desarrollada con Flask para consultar deportes, administrar socios, consultar disponibilidad y gestionar reservas del Club Deportivo Encuentro. La API utiliza MySQL para persistir la información y JSON para intercambiar datos.

## Tecnologías

- Python 3
- Flask 3.1.3
- MySQL Connector/Python 26.7.0
- MySQL

Las dependencias están declaradas en `app_backend/requirements.txt`.

## Contrato OpenAPI

El contrato de la API está en `app_backend/docs/swagger.yaml`.

## Configuración y ejecución

### Requisitos previos

- Python 3 instalado.
- Un servidor MySQL accesible desde la computadora.

### Instalar dependencias

Desde la carpeta del proyecto:

```bash
cd app_backend
python -m venv .venv
```

Activar el entorno virtual:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Instalar los paquetes:

```bash
pip install -r requirements.txt
```

### Configurar MySQL

Copiar `app_backend/.env.example` a `app_backend/.env` y reemplazar los valores de ejemplo por los datos de conexión locales:

```dotenv
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=club_deportivo
```

El nombre de base esperado por la aplicación es `club_deportivo`. El archivo `.env` contiene configuración local y no debe compartirse con credenciales reales.

Desde la carpeta `app_backend`, inicializar el esquema y los deportes:

```bash
python init_db.py
```

### Iniciar la API

Desde `app_backend`, con el entorno virtual activo:

```bash
python app.py
```

La API queda disponible en `http://localhost:5000`.

## Endpoints

### Deportes

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/deportes` | Devuelve los deportes precargados, ordenados por identificador. |

Ejemplo:

```bash
curl http://localhost:5000/deportes
```

Respuesta `200`:

```json
{
  "deportes": [
    {"id": 1, "nombre": "Fútbol"},
    {"id": 2, "nombre": "Tenis"},
    {"id": 3, "nombre": "Pádel"}
  ]
}
```

### Canchas

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/canchas` | Lista canchas con filtros y paginación. |
| POST | `/canchas` | Crea una cancha. |
| GET | `/canchas/{id}` | Consulta una cancha por identificador. |
| PATCH | `/canchas/{id}` | Actualiza parcialmente una cancha. |
| DELETE | `/canchas/{id}` | Elimina una cancha sin reservas asociadas. |
| GET | `/canchas/disponibles` | Busca canchas activas libres en un intervalo. |

#### GET `/canchas`

Parámetros:

| Parámetro | Descripción |
|---|---|
| `id_deporte` | Identificador positivo de un deporte. |
| `nombre` | Búsqueda parcial sin distinguir mayúsculas y minúsculas. |
| `techada` | Filtro booleano: `true` o `false`. |
| `activa` | Filtro booleano: `true` o `false`. |
| `_limit` | Cantidad de resultados; predeterminado `10`, máximo `100`. |
| `_offset` | Cantidad de resultados a omitir; predeterminado `0`. |

Los filtros se combinan. La lista se ordena por `id` ascendente e incluye enlaces de paginación `_first`, `_prev`, `_next` y `_last`.

```bash
curl "http://localhost:5000/canchas?nombre=futbol&activa=true&_limit=10&_offset=0"
```

#### POST `/canchas`

Los campos `nombre`, `id_deporte` y `precio_hora` son obligatorios. `id_deporte` debe corresponder a un deporte existente y `precio_hora` debe ser un entero positivo. Los campos opcionales son `techada` (predeterminado `false`) y `activa` (predeterminado `true`).

```bash
curl -X POST http://localhost:5000/canchas \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Cancha 1","id_deporte":1,"precio_hora":1000000,"techada":false,"activa":true}'
```

La respuesta `201` contiene la cancha creada con `id`, `nombre`, `id_deporte`, `precio_hora`, `techada` y `activa`.

#### GET `/canchas/{id}`

Devuelve los datos de la cancha. Responde `404` si no existe.

```bash
curl http://localhost:5000/canchas/1
```

#### PATCH `/canchas/{id}`

Permite actualizar `nombre`, `precio_hora`, `techada` o `activa`. Los campos omitidos conservan su valor. `id_deporte` no se puede modificar mediante este endpoint.

```bash
curl -X PATCH http://localhost:5000/canchas/1 \
  -H "Content-Type: application/json" \
  -d '{"precio_hora":1200000,"activa":true}'
```

La respuesta `200` contiene la cancha actualizada.

#### DELETE `/canchas/{id}`

Elimina una cancha si no tiene reservas asociadas. Si existen reservas, responde `409`; si la elimina, responde `204 No Content`.

#### GET `/canchas/disponibles`

Requiere los parámetros `fecha` (`YYYY-MM-DD`), `hora_inicio` (`HH:MM`) y `hora_fin` (`HH:MM`). Acepta además `_limit`, `_offset`, `id_deporte` y `techada` como filtros opcionales.

```bash
curl "http://localhost:5000/canchas/disponibles?fecha=2026-10-15&hora_inicio=18:00&hora_fin=20:00&_limit=10&_offset=0"
```

La consulta devuelve canchas activas que no tienen una reserva confirmada superpuesta con el intervalo indicado, junto con sus enlaces de paginación. La consulta es informativa y no retiene el horario.

### Socios

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/socios` | Lista socios con paginación y filtros opcionales. |
| POST | `/socios` | Registra un socio. |
| GET | `/socios/{id}` | Consulta un socio por identificador. |
| PATCH | `/socios/{id}` | Actualiza parcialmente un socio. |

#### GET `/socios`

Parámetros:

| Parámetro | Descripción |
|---|---|
| `nombre` | Busca coincidencias parciales sin distinguir mayúsculas y minúsculas. |
| `activo` | Filtra por `true` o `false`. |
| `_limit` | Cantidad de resultados; predeterminado `10`, máximo `100`. |
| `_offset` | Cantidad de resultados a omitir; predeterminado `0`. |

Los filtros se pueden combinar. La lista se ordena por `id` ascendente y la respuesta incluye enlaces `_first`, `_prev`, `_next` y `_last`.

```bash
curl "http://localhost:5000/socios?nombre=ana&activo=true&_limit=10&_offset=0"
```

#### POST `/socios`

El body requiere `nombre` y `email`. El servidor elimina espacios al inicio y al final, almacena el email en minúsculas y asigna `activo: true`.

```bash
curl -X POST http://localhost:5000/socios \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana Pérez","email":"ana@example.com"}'
```

Respuesta `201`:

```json
{
  "id": 1,
  "nombre": "Ana Pérez",
  "email": "ana@example.com",
  "activo": true
}
```

Un email ya registrado responde `409`.

#### GET `/socios/{id}`

Devuelve `id`, `nombre`, `email` y `activo`. Responde `404` cuando no existe un socio con ese identificador.

```bash
curl http://localhost:5000/socios/1
```

#### PATCH `/socios/{id}`

Permite actualizar uno o más campos: `nombre`, `email` y `activo`. Los campos omitidos conservan su valor.

```bash
curl -X PATCH http://localhost:5000/socios/1 \
  -H "Content-Type: application/json" \
  -d '{"activo":false}'
```

La respuesta contiene el socio actualizado. Se utiliza `400` para datos inválidos, `404` si el socio no existe y `409` si el email ya pertenece a otro socio.

### Reservas

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/reservas` | Lista reservas con paginación y filtros opcionales. |
| POST | `/reservas` | Crea una reserva. |
| GET | `/reservas/{id}` | Consulta todos los campos de una reserva. |
| PUT | `/reservas/{id}/estado` | Actualiza el estado de una reserva. |

#### GET `/reservas`

Parámetros:

| Parámetro | Descripción |
|---|---|
| `id_cancha` | Filtra por cancha. |
| `id_socio` | Filtra por socio. |
| `estado` | Filtra por `confirmada`, `cancelada` o `finalizada`. |
| `fecha_desde` | Fecha mínima de uso, formato `YYYY-MM-DD`, inclusiva. |
| `fecha_hasta` | Fecha máxima de uso, formato `YYYY-MM-DD`, inclusiva. |
| `_limit` | Cantidad de resultados; predeterminado `10`, máximo `100`. |
| `_offset` | Cantidad de resultados a omitir; predeterminado `0`. |

El rango se aplica al día de utilización de la cancha, con ambos extremos incluidos. Se puede enviar un solo extremo. Si se envían ambos, debe cumplirse `fecha_desde <= fecha_hasta`. Se permiten consultas de reservas pasadas.

```bash
curl "http://localhost:5000/reservas?id_socio=1&fecha_desde=2026-10-01&fecha_hasta=2026-10-31&_limit=10&_offset=0"
```

Respuesta `200`:

```json
{
  "reservas": [
    {
      "id": 1,
      "id_cancha": 2,
      "id_socio": 1,
      "fecha_hora_inicio": "2026-10-15T18:00:00.000000-03:00",
      "fecha_hora_fin": "2026-10-15T20:00:00.000000-03:00",
      "estado": "confirmada",
      "tarifa_hora": 1000000,
      "total": 2000000
    }
  ],
  "_links": {
    "_first": { "href": "http://localhost:5000/reservas?_limit=10&_offset=0" },
    "_prev": null,
    "_next": null,
    "_last": { "href": "http://localhost:5000/reservas?_limit=10&_offset=0" }
  }
}
```

#### POST `/reservas`

El body requiere `id_socio`, `id_cancha`, `fecha_hora_inicio` y `fecha_hora_fin`.

```bash
curl -X POST http://localhost:5000/reservas \
  -H "Content-Type: application/json" \
  -d '{"id_socio":1,"id_cancha":2,"fecha_hora_inicio":"2026-10-15T18:00:00.000000-03:00","fecha_hora_fin":"2026-10-15T20:00:00.000000-03:00"}'
```

Validaciones:

- El socio y la cancha deben existir y estar activos.
- Las fechas se interpretan en GMT-3 con el formato `YYYY-MM-DDTHH:MM:SS.ffffff-03:00`.
- El intervalo debe comenzar en el futuro, empezar y terminar en horas en punto, durar entre una y tres horas, quedar dentro del horario 08:00–23:00 y no atravesar la medianoche.
- No puede superponerse con otra reserva confirmada de la misma cancha ni del mismo socio. Los intervalos consecutivos sí se permiten.
- El servidor asigna el estado `confirmada`, conserva la tarifa vigente de la cancha y calcula el total como `horas × tarifa_hora`.

Respuesta `201`:

```json
{
  "id": 1,
  "id_cancha": 2,
  "id_socio": 1,
  "fecha_hora_inicio": "2026-10-15T18:00:00.000000-03:00",
  "fecha_hora_fin": "2026-10-15T20:00:00.000000-03:00",
  "estado": "confirmada",
  "tarifa_hora": 1000000,
  "total": 2000000
}
```

Se utiliza `400` para datos inválidos, `404` si el socio o la cancha no existen y `409` si hay superposición o alguna entidad está inactiva.

#### GET `/reservas/{id}`

Devuelve todos los campos de la reserva, incluidos `estado`, `tarifa_hora` y `total`.

```bash
curl http://localhost:5000/reservas/1
```

Responde `404` cuando no existe una reserva con ese identificador.

#### PUT `/reservas/{id}/estado`

El body contiene únicamente el nuevo estado:

```json
{
  "estado": "cancelada"
}
```

Transiciones:

| Estado actual | Estado solicitado | Condición |
|---|---|---|
| `confirmada` | `cancelada` | El horario de inicio todavía no llegó. |
| `confirmada` | `finalizada` | Se alcanzó o superó el horario de finalización. |
| `cancelada` | Otro estado | No permitido. |
| `finalizada` | Otro estado | No permitido. |

Repetir el estado actual devuelve éxito sin modificar la reserva. Una cancelación libera el horario, pero no elimina el registro. No se permite reactivar reservas canceladas.

```bash
curl -X PUT http://localhost:5000/reservas/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado":"cancelada"}'
```

Respuesta exitosa `200`:

```json
{
  "id": 1,
  "id_cancha": 2,
  "id_socio": 1,
  "fecha_hora_inicio": "2026-10-15T18:00:00.000000-03:00",
  "fecha_hora_fin": "2026-10-15T20:00:00.000000-03:00",
  "estado": "cancelada",
  "tarifa_hora": 1000000,
  "total": 2000000
}
```

Se utiliza `400` para un estado desconocido y `409` para una transición no permitida o solicitada fuera del momento permitido.

## Formato de errores

Los errores se devuelven en JSON con una clave `errors`:

```json
{
  "errors": [
    {
      "code": "ERROR_VALIDACION",
      "message": "Descripción breve del error.",
      "level": "error",
      "description": "Descripción del problema."
    }
  ]
}
```

Códigos usados: `400` para solicitudes inválidas, `404` para recursos inexistentes y `409` para conflictos de negocio.

## Pruebas

```bash
python -m pytest app_backend/tests
```

## Supuestos adoptados

- Todos los horarios se interpretan en GMT-3, sin conversión de zona horaria.
- Las reservas conservan la tarifa por hora y el total calculados al momento del alta, aunque el precio de la cancha cambie después.
- Desactivar una cancha o un socio impide crear nuevas reservas asociadas, pero no cancela ni invalida las existentes.
- La consulta de disponibilidad es informativa y no crea ni retiene una reserva.
- No se implementa autenticación ni notificaciones.
- No se administran cuotas sociales, pagos, torneos ni inscripciones a clases.
- Los deportes se cargan mediante `init_db` y no se pueden crear, modificar ni eliminar por API.
- No se modifica la cancha, el socio ni los horarios de una reserva ya creada; para corregirla se debe cancelar, cuando corresponda, y registrar una nueva.
- La eliminación de una cancha solo se permite si no tiene reservas asociadas, en cualquier estado.
- Las extensiones opcionales del enunciado (bloqueos por mantenimiento y reservas recurrentes) no forman parte de la implementación.