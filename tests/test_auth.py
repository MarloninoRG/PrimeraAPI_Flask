# tests/test_auth.py
"""
Suite 3: Pruebas de Autenticación y Autorización JWT.

Rutas reales:
  POST /auth/register  → 201 {message} | 400 {message}
  POST /auth/login     → 200 {access_token} | 401 {message}
  GET  /auth/profile   → 200 {username, email, role, active} (requiere JWT)

Notas:
  - Username duplicado → 400 (no 409)
  - No existe ruta de admin, no se prueba control de roles
  - Token inválido → 401 o 422 según Flask-JWT-Extended
"""
import pytest
import uuid


class TestRegistro:

    def test_registro_exitoso(self, client):
        """Registrar usuario nuevo con datos válidos → 201 con message."""
        uid = uuid.uuid4().hex[:8]
        resp = client.post("/auth/register", json={
            "username": f"docente_{uid}",
            "email": f"doc_{uid}@uni.mx",
            "password": "Segura123!"
        })
        assert resp.status_code == 201
        assert "message" in resp.get_json()

    def test_username_duplicado_retorna_400(self, client):
        """Registrar dos usuarios con el mismo username → 400."""
        uid = uuid.uuid4().hex[:8]
        payload = {
            "username": f"dup_{uid}",
            "email": f"a_{uid}@test.mx",
            "password": "Pass1234!"
        }
        client.post("/auth/register", json=payload)

        # Segundo intento: mismo username, email distinto
        payload["email"] = f"b_{uid}@test.mx"
        resp = client.post("/auth/register", json=payload)
        assert resp.status_code == 400
        assert "message" in resp.get_json()

    def test_faltan_campos_requeridos(self, client):
        """Omitir campos obligatorios → 400."""
        resp = client.post("/auth/register", json={
            "username": "incompleto"
            # falta email y password
        })
        assert resp.status_code == 400


class TestLogin:

    def test_login_exitoso_retorna_token(self, client):
        """Login correcto → 200 con access_token JWT válido."""
        uid = uuid.uuid4().hex[:8]
        client.post("/auth/register", json={
            "username": f"user_{uid}",
            "email": f"user_{uid}@test.mx",
            "password": "LoginPass1!"
        })
        resp = client.post("/auth/login", json={
            "username": f"user_{uid}",
            "password": "LoginPass1!"
        })
        assert resp.status_code == 200
        datos = resp.get_json()
        assert "access_token" in datos
        assert len(datos["access_token"]) > 50, "El token debe ser un JWT válido"

    def test_password_incorrecta_retorna_401(self, client):
        """Contraseña incorrecta → 401 Unauthorized."""
        uid = uuid.uuid4().hex[:8]
        client.post("/auth/register", json={
            "username": f"user401_{uid}",
            "email": f"u401_{uid}@test.mx",
            "password": "CorrectPass1!"
        })
        resp = client.post("/auth/login", json={
            "username": f"user401_{uid}",
            "password": "PasswordIncorrecta!"
        })
        assert resp.status_code == 401
        assert "message" in resp.get_json()

    def test_usuario_inexistente_retorna_401(self, client):
        """Username que no existe → 401 (no 404, por seguridad)."""
        resp = client.post("/auth/login", json={
            "username": "usuario_que_no_existe_xyz",
            "password": "cualquiera"
        })
        assert resp.status_code == 401


class TestRutasProtegidas:

    def test_ruta_protegida_sin_token_retorna_401(self, client):
        """Acceder a /auth/profile SIN token → 401."""
        resp = client.get("/auth/profile")
        assert resp.status_code == 401

    def test_ruta_protegida_con_token_valido(self, client, auth_headers):
        """Con token válido → 200 con datos del usuario."""
        resp = client.get("/auth/profile", headers=auth_headers)
        assert resp.status_code == 200
        datos = resp.get_json()
        assert "username" in datos
        assert "email" in datos
        assert "role" in datos
        assert "active" in datos

    def test_token_manipulado_retorna_error(self, client):
        """Token con firma inválida → 401 o 422."""
        token_falso = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJoYWNrZXIifQ.firma_falsa"
        headers = {"Authorization": f"Bearer {token_falso}"}
        resp = client.get("/auth/profile", headers=headers)
        assert resp.status_code in [401, 422]

    def test_header_sin_bearer_retorna_error(self, client):
        """Authorization sin prefijo 'Bearer' → 401 o 422."""
        headers = {"Authorization": "token_directo_sin_bearer"}
        resp = client.get("/auth/profile", headers=headers)
        assert resp.status_code in [401, 422]