# tests/test_estudiantes.py
"""
Suite 2: Pruebas de Integración del CRUD de Estudiantes.
Ruta base: /estudiantes/
- POST retorna el estudiante directo (sin wrapper)
- Matrícula/email duplicados retornan 400
- GET lista retorna: {estudiantes[], pagina, total_paginas, total_estudiantes}
- DELETE retorna {message} y marca activo=False
"""
import pytest
import uuid


def make_estudiante(uid):
    """Genera datos únicos de estudiante usando un sufijo uid."""
    return {
        "matricula": f"MAT{uid}",
        "nombre": "Carlos",
        "apellido": "Ramírez",
        "email": f"carlos{uid}@test.edu.mx",
        "carrera": "ITIC",
        "semestre": 5
    }


class TestCrearEstudiante:
    """Pruebas del endpoint POST /estudiantes/"""

    def test_crear_estudiante_exitoso(self, client):
        """CASO POSITIVO: Crear estudiante con datos válidos → 201."""
        uid = uuid.uuid4().hex[:8]
        respuesta = client.post("/estudiantes/", json=make_estudiante(uid))
        datos = respuesta.get_json()

        assert respuesta.status_code == 201, \
            f"Se esperaba 201, llegó {respuesta.status_code}: {datos}"
        assert datos["matricula"] == f"MAT{uid}"
        assert datos["nombre"] == "Carlos"
        assert "id" in datos

    def test_matricula_duplicada_retorna_400(self, client):
        """CASO NEGATIVO: Matrícula duplicada → 400."""
        uid = uuid.uuid4().hex[:8]
        data = make_estudiante(uid)
        client.post("/estudiantes/", json=data)
        respuesta = client.post("/estudiantes/", json=data)

        assert respuesta.status_code == 400
        assert "error" in respuesta.get_json()

    def test_campo_email_requerido(self, client):
        """CASO NEGATIVO: Omitir email → 400 mencionando 'email'."""
        uid = uuid.uuid4().hex[:8]
        datos_incompletos = {
            "matricula": f"INC{uid}",
            "nombre": "Sin Email",
            "apellido": "Test",
            "carrera": "ITIC",
            "semestre": 1
            # "email" omitido a propósito
        }
        respuesta = client.post("/estudiantes/", json=datos_incompletos)
        assert respuesta.status_code == 400
        cuerpo = respuesta.get_json()
        assert "error" in cuerpo
        assert "email" in cuerpo["error"].lower()

    def test_body_vacio_retorna_error(self, client):
        """
        CASO BORDE: Body vacío → error de cliente.
        Flask retorna 415 (Unsupported Media Type) cuando no hay Content-Type JSON,
        lo cual es igualmente válido que 400 para indicar una petición inválida.
        """
        respuesta = client.post("/estudiantes/", data="")
        assert respuesta.status_code in [400, 415], \
            f"Se esperaba 400 o 415, llegó {respuesta.status_code}"


class TestObtenerEstudiante:
    """Pruebas de GET /estudiantes/ y GET /estudiantes/<id>"""

    def test_lista_devuelve_200(self, client):
        """La lista siempre retorna 200 con estructura de paginación."""
        respuesta = client.get("/estudiantes/")
        assert respuesta.status_code == 200
        datos = respuesta.get_json()
        assert "estudiantes" in datos
        assert "total_estudiantes" in datos
        assert "total_paginas" in datos

    def test_lista_vacia_retorna_lista_vacia(self, client):
        """La lista puede estar vacía pero nunca debe retornar 500."""
        respuesta = client.get("/estudiantes/")
        datos = respuesta.get_json()
        assert respuesta.status_code == 200
        assert isinstance(datos["estudiantes"], list)

    def test_obtener_por_id_existente(self, client):
        """Obtener un estudiante existente → 200 con sus datos."""
        uid = uuid.uuid4().hex[:8]
        post_resp = client.post("/estudiantes/", json=make_estudiante(uid))
        id_creado = post_resp.get_json()["id"]

        respuesta = client.get(f"/estudiantes/{id_creado}")
        assert respuesta.status_code == 200
        assert respuesta.get_json()["id"] == id_creado

    def test_id_inexistente_retorna_404(self, client):
        """ID que no existe → 404."""
        respuesta = client.get("/estudiantes/99999")
        assert respuesta.status_code == 404

    @pytest.mark.parametrize("pagina,per_page", [
        (1, 5),
        (2, 5),
        (1, 100),
    ])
    def test_paginacion(self, client, pagina, per_page):
        """PARAMETRIZADO: La paginación responde 200 con distintos valores."""
        respuesta = client.get(f"/estudiantes/?pagina={pagina}&per_page={per_page}")
        assert respuesta.status_code == 200


class TestActualizarEstudiante:

    def test_actualizar_semestre(self, client):
        """PUT actualiza el campo y retorna el objeto actualizado."""
        uid = uuid.uuid4().hex[:8]
        id_est = client.post("/estudiantes/", json=make_estudiante(uid)) \
                       .get_json()["id"]

        resp = client.put(f"/estudiantes/{id_est}", json={"semestre": 8})
        assert resp.status_code == 200
        assert resp.get_json()["semestre"] == 8


class TestEliminarEstudiante:

    def test_borrado_logico(self, client):
        """
        DELETE hace borrado lógico: marca activo=False.
        Se verifica consultando el estudiante directamente por ID
        ya que GET /estudiantes/ no filtra por activo.
        """
        uid = uuid.uuid4().hex[:8]
        id_est = client.post("/estudiantes/", json=make_estudiante(uid)) \
                       .get_json()["id"]

        # Eliminar
        resp_del = client.delete(f"/estudiantes/{id_est}")
        assert resp_del.status_code == 200
        assert "message" in resp_del.get_json()

        # Verificar activo=False consultando directamente por ID
        resp_get = client.get(f"/estudiantes/{id_est}")
        assert resp_get.status_code == 200
        assert resp_get.get_json()["activo"] == False, \
            "El estudiante debe tener activo=False tras el borrado lógico"