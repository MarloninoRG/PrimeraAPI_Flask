# tests/conftest.py
import pytest
from app import create_app, db as _db
from app.config import TestingConfig


# ─── Fixture: Aplicación de prueba ───────────────────────────────────
@pytest.fixture(scope="session")
def app():
    """
    Crea la aplicación Flask en modo de pruebas UNA VEZ por sesión.
    """
    app = create_app(TestingConfig)
    yield app


# ─── Fixture: Base de datos ──────────────────────────────────────────
@pytest.fixture(scope="session")
def db(app):
    """
    Crea TODAS las tablas en SQLite en memoria al inicio de la sesión.
    Las destruye al final. Nunca toca PostgreSQL.
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


# ─── Fixture: Transacción limpia por prueba ──────────────────────────
@pytest.fixture(scope="function")
def session(db):
    """
    Cada prueba corre en una transacción que se revierte al final.
    Garantiza independencia entre pruebas (patrón Rollback).
    """
    connection = db.engine.connect()
    transaction = connection.begin()
    db.session.bind = connection
    yield db.session
    db.session.remove()
    transaction.rollback()
    connection.close()


# ─── Fixture: Cliente HTTP de prueba ─────────────────────────────────
@pytest.fixture(scope="function")
def client(app, db):
    """
    Cliente HTTP para simular peticiones a la API.
    Depende de 'db' para garantizar que las tablas existan antes
    de cualquier petición, incluyendo test_tienda.py.
    """
    return app.test_client()


# ─── Fixture: Datos de estudiante ────────────────────────────────────
@pytest.fixture
def estudiante_data():
    """Datos válidos reutilizables para crear un estudiante."""
    return {
        "matricula": "TEST001",
        "nombre": "Carlos",
        "apellido": "Ramírez",
        "email": "carlos@test.edu.mx",
        "carrera": "ITIC",
        "semestre": 5
    }


# ─── Fixture: Headers JWT de prueba ──────────────────────────────────
@pytest.fixture
def auth_headers(client):
    """
    Registra un usuario, hace login y retorna los headers JWT listos.
    Usa las rutas reales: /auth/register y /auth/login.
    """
    client.post("/auth/register", json={
        "username": "docente_test",
        "email": "doc@test.mx",
        "password": "Password123!"
    })
    resp = client.post("/auth/login", json={
        "username": "docente_test",
        "password": "Password123!"
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}