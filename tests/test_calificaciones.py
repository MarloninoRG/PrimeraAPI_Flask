# tests/test_calificaciones.py
"""
Suite 4: Pruebas de calificaciones y kardex.
Rutas reales:
  POST /cal/                         → 201, retorna calificacion.to_dict()
  GET  /cal/estudiantes/<id>/kardex  → 200 {estudiante_id, nombre_estudiante,
                                           kardex[], promedio, materias_aprobadas}
                                     → 404 si no hay calificaciones

Notas:
  - POST /materias/ requiere campo "docente" (obligatorio)
  - La aprobación usa >= 60
  - El kardex retorna 404 si no hay calificaciones (no 200)
"""
import pytest
import uuid


def make_estudiante(uid):
    return {
        "matricula": f"CAL{uid}",
        "nombre": "Carlos",
        "apellido": "Ramírez",
        "email": f"cal{uid}@test.edu.mx",
        "carrera": "ITIC",
        "semestre": 5
    }


class TestRegistroCalificaciones:

    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Crea estudiante y materia únicos antes de cada prueba."""
        uid = uuid.uuid4().hex[:8]
        self.uid = uid
        self.client = client

        # Crear estudiante único
        resp_est = client.post("/estudiantes/", json=make_estudiante(uid))
        assert resp_est.status_code == 201, \
            f"Error creando estudiante: {resp_est.get_json()}"
        self.id_estudiante = resp_est.get_json()["id"]

        # Crear materia única (docente es obligatorio)
        resp_mat = client.post("/materias/", json={
            "clave": f"MAT{uid}", "nombre": f"Materia {uid}",
            "creditos": 5, "docente": "Dr. Test"
        })
        assert resp_mat.status_code == 201, \
            f"Error creando materia: {resp_mat.get_json()}"
        self.id_materia = resp_mat.get_json()["id"]

    def test_registrar_calificacion_valida(self):
        """Registrar calificación válida → 201 con datos guardados."""
        resp = self.client.post("/cal/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": 87.5,
            "periodo": "2024-1"
        })
        assert resp.status_code == 201
        datos = resp.get_json()
        assert float(datos["calificacion"]) == 87.5
        assert datos["estudiante_id"] == self.id_estudiante

    def test_campos_requeridos_calificacion(self):
        """Omitir campo requerido → 400."""
        resp = self.client.post("/cal/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            # "calificacion" omitida
            "periodo": "2024-1"
        })
        assert resp.status_code == 400

    def test_estudiante_inexistente_retorna_404(self):
        """Calificación para estudiante inexistente → 404."""
        resp = self.client.post("/cal/", json={
            "estudiante_id": 99999,
            "materia_id": self.id_materia,
            "calificacion": 80,
            "periodo": "2024-1"
        })
        assert resp.status_code == 404

    def test_calificacion_exactamente_cero(self):
        """Caso borde: 0 es calificación válida (reprobado)."""
        resp = self.client.post("/cal/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": 0,
            "periodo": "2024-1"
        })
        assert resp.status_code == 201

    def test_calificacion_exactamente_cien(self):
        """Caso borde: 100 es calificación válida (perfecta)."""
        resp = self.client.post("/cal/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": 100,
            "periodo": "2024-1"
        })
        assert resp.status_code == 201


class TestKardex:

    def test_kardex_calcula_promedio_correctamente(self, client):
        """Con calificaciones 80, 90, 70 → promedio 80.0, 3 aprobadas."""
        uid = uuid.uuid4().hex[:8]
        id_est = client.post("/estudiantes/", json=make_estudiante(uid)) \
                       .get_json()["id"]

        for i, (nombre, cal) in enumerate([
            ("Matemáticas", 80),
            ("Física", 90),
            ("Química", 70),
        ]):
            mat = client.post("/materias/", json={
                "clave": f"M{i}{uid}", "nombre": nombre,
                "creditos": 4, "docente": "Dr. Test"
            }).get_json()

            client.post("/cal/", json={
                "estudiante_id": id_est,
                "materia_id": mat["id"],
                "calificacion": cal,
                "periodo": "2024-1"
            })

        resp = client.get(f"/cal/estudiantes/{id_est}/kardex")
        assert resp.status_code == 200
        kardex = resp.get_json()

        assert kardex["promedio"] == 80.0
        assert len(kardex["kardex"]) == 3
        assert kardex["materias_aprobadas"] == 3
        assert kardex["nombre_estudiante"] == "Carlos"

    def test_kardex_detecta_materia_reprobada(self, client):
        """Calificación < 60 cuenta como reprobada."""
        uid = uuid.uuid4().hex[:8]
        id_est = client.post("/estudiantes/", json=make_estudiante(uid)) \
                       .get_json()["id"]

        mat = client.post("/materias/", json={
            "clave": f"REP{uid}", "nombre": "Reprobada",
            "creditos": 3, "docente": "Dr. Test"
        }).get_json()

        client.post("/cal/", json={
            "estudiante_id": id_est,
            "materia_id": mat["id"],
            "calificacion": 50,
            "periodo": "2024-1"
        })

        kardex = client.get(f"/cal/estudiantes/{id_est}/kardex").get_json()
        assert kardex["materias_aprobadas"] == 0

    def test_kardex_sin_calificaciones_retorna_404(self, client):
        """Estudiante sin calificaciones → 404 (la API no retorna 200 vacío)."""
        uid = uuid.uuid4().hex[:8]
        id_est = client.post("/estudiantes/", json=make_estudiante(uid)) \
                       .get_json()["id"]
        resp = client.get(f"/cal/estudiantes/{id_est}/kardex")
        assert resp.status_code == 404

    def test_kardex_estudiante_inexistente_retorna_404(self, client):
        """ID de estudiante que no existe → 404."""
        resp = client.get("/cal/estudiantes/99999/kardex")
        assert resp.status_code == 404