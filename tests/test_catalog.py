# tests/test_catalogo.py
"""
Suite 6: Pruebas de los CRUDs de Catálogo.
Cubre: categorias, clientes, materias y productos.
Objetivo: llevar la cobertura total por encima del 80%.
"""
import pytest
import uuid


class TestCategorias:

    def test_crear_y_listar_categoria(self, client):
        uid = uuid.uuid4().hex[:8]
        resp = client.post("/categorias/", json={
            "nombre": f"Cat_{uid}", "description": "Test"
        })
        assert resp.status_code == 201
        assert resp.get_json()["nombre"] == f"Cat_{uid}"

        lista = client.get("/categorias/").get_json()
        assert isinstance(lista, list)

    def test_obtener_categoria_por_id(self, client):
        uid = uuid.uuid4().hex[:8]
        id_cat = client.post("/categorias/", json={"nombre": f"Cat2_{uid}"}) \
                       .get_json()["id"]
        resp = client.get(f"/categorias/{id_cat}")
        assert resp.status_code == 200

    def test_actualizar_categoria(self, client):
        uid = uuid.uuid4().hex[:8]
        id_cat = client.post("/categorias/", json={"nombre": f"Cat3_{uid}"}) \
                       .get_json()["id"]
        resp = client.put(f"/categorias/{id_cat}", json={"nombre": f"Cat3u_{uid}"})
        assert resp.status_code == 200

    def test_eliminar_categoria(self, client):
        uid = uuid.uuid4().hex[:8]
        id_cat = client.post("/categorias/", json={"nombre": f"Cat4_{uid}"}) \
                       .get_json()["id"]
        resp = client.delete(f"/categorias/{id_cat}")
        assert resp.status_code == 200

    def test_nombre_duplicado_retorna_409(self, client):
        uid = uuid.uuid4().hex[:8]
        client.post("/categorias/", json={"nombre": f"Dup_{uid}"})
        resp = client.post("/categorias/", json={"nombre": f"Dup_{uid}"})
        assert resp.status_code == 409


class TestClientes:

    def test_crear_y_listar_cliente(self, client):
        uid = uuid.uuid4().hex[:8]
        resp = client.post("/clientes/", json={
            "nombre": "Juan Test", "email": f"juan_{uid}@test.mx"
        })
        assert resp.status_code == 201
        lista = client.get("/clientes/").get_json()
        assert isinstance(lista, list)

    def test_obtener_cliente_por_id(self, client):
        uid = uuid.uuid4().hex[:8]
        id_cli = client.post("/clientes/", json={
            "nombre": "Ana", "email": f"ana_{uid}@test.mx"
        }).get_json()["id"]
        resp = client.get(f"/clientes/{id_cli}")
        assert resp.status_code == 200

    def test_actualizar_cliente(self, client):
        uid = uuid.uuid4().hex[:8]
        id_cli = client.post("/clientes/", json={
            "nombre": "Pedro", "email": f"pedro_{uid}@test.mx"
        }).get_json()["id"]
        resp = client.put(f"/clientes/{id_cli}", json={"nombre": "Pedro Actualizado"})
        assert resp.status_code == 200

    def test_eliminar_cliente(self, client):
        uid = uuid.uuid4().hex[:8]
        id_cli = client.post("/clientes/", json={
            "nombre": "Luis", "email": f"luis_{uid}@test.mx"
        }).get_json()["id"]
        resp = client.delete(f"/clientes/{id_cli}")
        assert resp.status_code == 200


class TestMaterias:

    def test_crear_y_listar_materia(self, client):
        uid = uuid.uuid4().hex[:8]
        resp = client.post("/materias/", json={
            "clave": f"MAT_{uid}", "nombre": "Álgebra",
            "creditos": 4, "docente": "Dr. X"
        })
        assert resp.status_code == 201
        lista = client.get("/materias/").get_json()
        assert isinstance(lista, list)

    def test_obtener_materia_por_id(self, client):
        uid = uuid.uuid4().hex[:8]
        id_mat = client.post("/materias/", json={
            "clave": f"FIS_{uid}", "nombre": "Física",
            "creditos": 5, "docente": "Dr. Y"
        }).get_json()["id"]
        resp = client.get(f"/materias/{id_mat}")
        assert resp.status_code == 200

    def test_actualizar_materia(self, client):
        uid = uuid.uuid4().hex[:8]
        id_mat = client.post("/materias/", json={
            "clave": f"QUI_{uid}", "nombre": "Química",
            "creditos": 3, "docente": "Dr. Z"
        }).get_json()["id"]
        resp = client.put(f"/materias/{id_mat}", json={"creditos": 6})
        assert resp.status_code == 200

    def test_eliminar_materia(self, client):
        uid = uuid.uuid4().hex[:8]
        id_mat = client.post("/materias/", json={
            "clave": f"BIO_{uid}", "nombre": "Biología",
            "creditos": 3, "docente": "Dr. W"
        }).get_json()["id"]
        resp = client.delete(f"/materias/{id_mat}")
        assert resp.status_code == 200


class TestProductos:

    def test_crear_y_listar_producto(self, client):
        uid = uuid.uuid4().hex[:8]
        resp = client.post("/productos/", json={
            "sku": f"SKU_{uid}", "nombre": "Teclado",
            "precio": 299.00, "stock": 20
        })
        assert resp.status_code == 201
        lista = client.get("/productos/").get_json()
        assert isinstance(lista, list)

    def test_obtener_producto_por_id(self, client):
        uid = uuid.uuid4().hex[:8]
        id_prod = client.post("/productos/", json={
            "sku": f"MON_{uid}", "nombre": "Monitor",
            "precio": 3500.00
        }).get_json()["id"]
        resp = client.get(f"/productos/{id_prod}")
        assert resp.status_code == 200

    def test_actualizar_producto(self, client):
        uid = uuid.uuid4().hex[:8]
        id_prod = client.post("/productos/", json={
            "sku": f"CAM_{uid}", "nombre": "Cámara",
            "precio": 1200.00
        }).get_json()["id"]
        resp = client.put(f"/productos/{id_prod}", json={"precio": 999.00})
        assert resp.status_code == 200

    def test_desactivar_producto(self, client):
        uid = uuid.uuid4().hex[:8]
        id_prod = client.post("/productos/", json={
            "sku": f"AUD_{uid}", "nombre": "Audífonos",
            "precio": 450.00
        }).get_json()["id"]
        resp = client.delete(f"/productos/{id_prod}")
        assert resp.status_code == 200
        assert resp.get_json()["message"] is not None

    def test_sku_duplicado_retorna_409(self, client):
        uid = uuid.uuid4().hex[:8]
        client.post("/productos/", json={
            "sku": f"DUP_{uid}", "nombre": "Prod A", "precio": 100
        })
        resp = client.post("/productos/", json={
            "sku": f"DUP_{uid}", "nombre": "Prod B", "precio": 200
        })
        assert resp.status_code == 409