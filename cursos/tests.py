from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Curso

CURSO_VALIDO = {
    "nombre": "Python Avanzado",
    "descripcion": "Decoradores y generadores",
    "profesor": "Ana Pérez",
    "fecha_inicio": "2026-03-01",
}


class ApiBase(APITestCase):
    def setUp(self):
        cache.clear()  # los límites de peticiones usan la caché
        self.usuario = User.objects.create_user("tester", password="Clave-de-prueba-123")
        self.token = Token.objects.create(user=self.usuario)
        self.curso = Curso.objects.create(
            nombre="Django Básico",
            descripcion="Introducción",
            profesor="Luis Soto",
            fecha_inicio="2026-01-15",
        )

    def autenticar(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")


class LecturaPublicaTests(ApiBase):
    def test_listar_es_publico_y_devuelve_json_paginado(self):
        r = self.client.get("/api/cursos/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/json")
        self.assertEqual(r.json()["count"], 1)
        self.assertEqual(r.json()["results"][0]["nombre"], "Django Básico")

    def test_detalle_es_publico(self):
        r = self.client.get(f"/api/cursos/{self.curso.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            set(r.json()), {"id", "nombre", "descripcion", "profesor", "fecha_inicio"}
        )

    def test_detalle_inexistente_devuelve_404_json(self):
        r = self.client.get("/api/cursos/9999/")
        self.assertEqual(r.status_code, 404)
        self.assertIn("detail", r.json())


class EscrituraYAutenticacionTests(ApiBase):
    def test_crear_sin_token_devuelve_401(self):
        r = self.client.post("/api/cursos/", CURSO_VALIDO, format="json")
        self.assertEqual(r.status_code, 401)
        self.assertEqual(Curso.objects.count(), 1)

    def test_token_invalido_devuelve_401(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token clave-falsa")
        r = self.client.post("/api/cursos/", CURSO_VALIDO, format="json")
        self.assertEqual(r.status_code, 401)

    def test_crear_con_token_devuelve_201(self):
        self.autenticar()
        r = self.client.post("/api/cursos/", CURSO_VALIDO, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["nombre"], "Python Avanzado")
        self.assertEqual(Curso.objects.count(), 2)

    def test_crear_con_datos_invalidos_devuelve_400_con_errores_por_campo(self):
        self.autenticar()
        datos = {"nombre": "ab", "profesor": "  ", "fecha_inicio": "no-es-fecha"}
        r = self.client.post("/api/cursos/", datos, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(set(r.json()), {"nombre", "profesor", "fecha_inicio"})

    def test_actualizar_completo_con_put(self):
        self.autenticar()
        r = self.client.put(f"/api/cursos/{self.curso.id}/", CURSO_VALIDO, format="json")
        self.assertEqual(r.status_code, 200)
        self.curso.refresh_from_db()
        self.assertEqual(self.curso.nombre, "Python Avanzado")

    def test_actualizar_parcial_con_patch(self):
        self.autenticar()
        r = self.client.patch(
            f"/api/cursos/{self.curso.id}/", {"profesor": "Marta Díaz"}, format="json"
        )
        self.assertEqual(r.status_code, 200)
        self.curso.refresh_from_db()
        self.assertEqual(self.curso.profesor, "Marta Díaz")
        self.assertEqual(self.curso.nombre, "Django Básico")

    def test_modificar_sin_token_devuelve_401(self):
        r = self.client.patch(
            f"/api/cursos/{self.curso.id}/", {"profesor": "X Y"}, format="json"
        )
        self.assertEqual(r.status_code, 401)

    def test_eliminar_con_token_devuelve_204(self):
        self.autenticar()
        r = self.client.delete(f"/api/cursos/{self.curso.id}/")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Curso.objects.filter(id=self.curso.id).exists())

    def test_eliminar_sin_token_devuelve_401(self):
        r = self.client.delete(f"/api/cursos/{self.curso.id}/")
        self.assertEqual(r.status_code, 401)
        self.assertTrue(Curso.objects.filter(id=self.curso.id).exists())

    def test_metodo_no_permitido_en_la_coleccion(self):
        self.autenticar()
        r = self.client.delete("/api/cursos/")
        self.assertEqual(r.status_code, 405)


class TokenTests(ApiBase):
    def test_login_correcto_devuelve_token(self):
        r = self.client.post(
            "/api/token/",
            {"username": "tester", "password": "Clave-de-prueba-123"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["token"], self.token.key)

    def test_login_con_credenciales_invalidas_devuelve_400(self):
        r = self.client.post(
            "/api/token/", {"username": "tester", "password": "incorrecta"}, format="json"
        )
        self.assertEqual(r.status_code, 400)
        self.assertNotIn("token", r.json())

    def test_login_limitado_a_5_intentos_por_minuto(self):
        datos = {"username": "tester", "password": "incorrecta"}
        for _ in range(5):
            self.assertEqual(self.client.post("/api/token/", datos, format="json").status_code, 400)
        r = self.client.post("/api/token/", datos, format="json")
        self.assertEqual(r.status_code, 429)

    def test_revocar_token_lo_invalida(self):
        self.autenticar()
        r = self.client.delete("/api/token/revoke/")
        self.assertEqual(r.status_code, 204)
        r = self.client.post("/api/cursos/", CURSO_VALIDO, format="json")
        self.assertEqual(r.status_code, 401)

    def test_revocar_sin_token_devuelve_401(self):
        r = self.client.delete("/api/token/revoke/")
        self.assertEqual(r.status_code, 401)
