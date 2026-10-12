# API RESTful de Cursos — Django REST Framework

API REST para gestionar un catálogo de cursos, construida con **Django 6.1** y
**Django REST Framework 3.18** (Unidad 3 – Aplicación API RESTful).

- Recurso expuesto: **Curso** (`nombre`, `descripcion`, `profesor`, `fecha_inicio`).
- Respuestas y peticiones **solo en JSON**.
- **Lectura pública**; crear, modificar y eliminar requieren **autenticación por token**.
- Medidas de seguridad: limitación de peticiones, secretos por variables de entorno,
  token revocable y validación de datos (ver [Seguridad](#seguridad)).
- Uso de IA y su validación documentados en [`EVIDENCIA_IA.md`](EVIDENCIA_IA.md).

## Requisitos

- Python 3.10 o superior.

## Instalación

```bash
git clone <URL-del-repositorio>
cd api_cursos

python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # crea el usuario con el que se obtiene el token
```

## Configuración

Por defecto funciona en desarrollo local sin configurar nada. Para otros entornos se
usan variables de entorno:

| Variable | Por defecto | Descripción |
|---|---|---|
| `DJANGO_SECRET_KEY` | clave de desarrollo | Clave secreta de Django. **Obligatoria si `DJANGO_DEBUG=0`**. |
| `DJANGO_DEBUG` | `1` | `0` desactiva el modo debug. |
| `DJANGO_ALLOWED_HOSTS` | vacío | Hosts permitidos, separados por coma. |

Si `DJANGO_DEBUG=0` y no se define `DJANGO_SECRET_KEY`, el proyecto se niega a arrancar.

## Ejecución

```bash
python manage.py runserver
```

La API queda en `http://127.0.0.1:8000/api/`.

## Pruebas

```bash
python manage.py test
```

Ejecuta 18 pruebas automáticas de los endpoints (lectura pública, autenticación,
CRUD, validaciones, códigos de respuesta, revocación de token y límite de intentos
de login).

## Endpoints

Base: `/api/`

| Método | Ruta | Auth | Descripción | Respuestas |
|---|---|---|---|---|
| POST | `/api/token/` | No | Obtiene el token con `username` y `password` | 200, 400, 429 |
| DELETE | `/api/token/revoke/` | Token | Revoca el token usado en la petición | 204, 401 |
| GET | `/api/cursos/` | No | Lista paginada de cursos (10 por página, `?page=2`) | 200 |
| POST | `/api/cursos/` | Token | Crea un curso | 201, 400, 401 |
| GET | `/api/cursos/{id}/` | No | Detalle de un curso | 200, 404 |
| PUT | `/api/cursos/{id}/` | Token | Reemplaza un curso (todos los campos) | 200, 400, 401, 404 |
| PATCH | `/api/cursos/{id}/` | Token | Modifica campos de un curso | 200, 400, 401, 404 |
| DELETE | `/api/cursos/{id}/` | Token | Elimina un curso | 204, 401, 404 |

Cualquier petición puede responder además `429` si se supera el límite de peticiones.

## Autenticación

1. Obtener el token con las credenciales del usuario creado con `createsuperuser`:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "TU_USUARIO", "password": "TU_CONTRASEÑA"}'
# {"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
```

2. Enviarlo en la cabecera `Authorization` de las peticiones protegidas:

```bash
curl -X POST http://127.0.0.1:8000/api/cursos/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Python Avanzado", "descripcion": "Decoradores", "profesor": "Ana Pérez", "fecha_inicio": "2026-03-01"}'
```

3. Cerrar la sesión de la API (revocar el token):

```bash
curl -X DELETE http://127.0.0.1:8000/api/token/revoke/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

## Ejemplos de respuestas JSON

Lista (`GET /api/cursos/`):

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nombre": "Python Avanzado",
      "descripcion": "Decoradores",
      "profesor": "Ana Pérez",
      "fecha_inicio": "2026-03-01"
    }
  ]
}
```

Error de validación (`400`), con un mensaje por campo:

```json
{
  "nombre": ["El nombre debe tener al menos 3 caracteres."],
  "fecha_inicio": ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD."]
}
```

Sin token (`401`): `{"detail": "Authentication credentials were not provided."}`

Token inválido o revocado (`401`): `{"detail": "Invalid token."}`

Curso inexistente (`404`): `{"detail": "No Curso matches the given query."}`

## Seguridad

- **Autenticación por token** (`TokenAuthentication`): las rutas de escritura devuelven
  `401` sin un token válido. La lectura de cursos es pública a propósito.
- **Límite de peticiones** (throttling): 60/min anónimos, 120/min autenticados y
  **5/min en `/api/token/`** para dificultar ataques de fuerza bruta (responde `429`).
- **Token revocable**: `DELETE /api/token/revoke/` invalida el token.
- **Secretos fuera del código**: `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` se leen del
  entorno; con `DEBUG=0` es obligatorio definir la clave.
- **Solo JSON**: se desactivan los demás parsers y renderers de DRF, reduciendo la
  superficie de ataque.
- **Validación de entrada** en el serializer (nombre mínimo de 3 caracteres, profesor
  no vacío, formato de fecha) con errores por campo.
- **La contraseña nunca se devuelve**: el login solo responde el token.

Limitaciones conocidas: el token de DRF **no expira por tiempo** (solo se invalida al
revocarlo) y debe viajar siempre por **HTTPS** en un despliegue real. Para tokens con
expiración se podría usar JWT (`djangorestframework-simplejwt`).

## Estructura

```
api_cursos/
├── manage.py
├── requirements.txt
├── mysite/             # configuración (settings.py con DRF, urls.py)
└── cursos/
    ├── models.py         # modelo Curso
    ├── serializers.py     # CursoSerializer con validaciones
    ├── views.py            # CursoViewSet, LoginTokenView, RevokeTokenView
    ├── urls.py              # router de DRF y rutas del token
    ├── admin.py              # Curso registrado en el admin
    └── tests.py               # 18 pruebas de los endpoints
```
