# Evidencia del uso de IA y validación de sus recomendaciones

Herramienta usada: **Claude Code** (asistente de IA de Anthropic), como apoyo en la
configuración de Django REST Framework, la autenticación, la seguridad y las pruebas.
La rúbrica de la Unidad 3 pide analizar, validar y adaptar lo que la IA recomienda; este
documento deja constancia de qué se pidió, qué se recomendó y cómo se verificó.

## Qué se le pidió a la IA

> Construir, a partir del proyecto de cursos de la Evaluación 2, una API RESTful con
> Django REST Framework que cumpla la rúbrica de la Unidad 3: DRF configurado, un
> recurso (Curso) expuesto con endpoints CRUD, respuestas JSON, autenticación por
> token, medidas básicas de seguridad, pruebas de los endpoints y un README.

Decisiones tomadas por el estudiante antes de generar el código:

- Hacer el trabajo sobre **una copia nueva** del proyecto, para no modificar lo ya
  entregado en la Evaluación 2.
- Usar **autenticación por Token de DRF** (y no JWT ni sesión), por simplicidad.

## Recomendaciones de la IA, decisión y validación

| # | Recomendación | Decisión | Cómo se validó |
|---|---|---|---|
| 1 | Usar `TokenAuthentication` con `IsAuthenticatedOrReadOnly` como permiso por defecto | Aceptada | Pruebas: sin token → `401`, token falso → `401`, con token → `201`; lectura pública → `200` |
| 2 | Limitar el endpoint de login (`ScopedRateThrottle`, 5/min) contra fuerza bruta | Aceptada | Prueba automática: el 6.º intento seguido responde `429` |
| 3 | Mover `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` a variables de entorno y negarse a arrancar con `DEBUG=0` sin clave | Aceptada y adaptada: se dejó una clave de desarrollo por defecto para poder ejecutar sin configurar | Se revisó `settings.py`; con `DEBUG=0` sin clave lanza `ImproperlyConfigured` |
| 4 | Endpoint para revocar el token, porque el token de DRF no expira | Aceptada | Prueba: tras `DELETE /api/token/revoke/`, el mismo token responde `401` |
| 5 | Dejar solo `JSONRenderer` y `JSONParser` | Aceptada | Respuestas verificadas con `curl` (`Content-Type: application/json`) |
| 6 | Paginación (10 por página) | Aceptada | Prueba: la lista devuelve `count`, `next`, `previous` y `results` |
| 7 | Validar `nombre` y `profesor` en el serializer | Aceptada | Prueba: datos inválidos → `400` con un mensaje por campo |
| 8 | Usar JWT con expiración en lugar de token simple | **No aplicada** (se eligió Token); el riesgo de que no expire se mitiga con la revocación y se documenta como limitación | Documentado en el README |
| 9 | Restringir la escritura con `DjangoModelPermissions` (mínimo privilegio) | **No aplicada**: se consideró excesiva para el alcance; cualquier usuario autenticado puede escribir | Documentado aquí como riesgo conocido |

## Riesgos identificados

- El token no caduca por tiempo: si se filtra, sirve hasta que se revoque.
- Sin HTTPS el token viaja en claro; en producción debe usarse siempre HTTPS.
- Cualquier usuario autenticado puede crear, modificar y borrar cursos (sin roles).

## Verificación realizada

- **18 pruebas automáticas** (`python manage.py test`), todas aprobadas.
- **Prueba manual con `curl`** sobre el servidor en ejecución, cubriendo: lectura
  pública, escritura sin token (`401`), login, creación (`201`), validación (`400`),
  `PATCH` (`200`), `DELETE` (`204`), recurso borrado (`404`) y reutilización de un
  token revocado (`401`).
- `python manage.py check` y `makemigrations --check` sin observaciones.
