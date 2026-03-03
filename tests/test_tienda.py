# tests/test_tienda.py
"""
Suite 5: Prueba End-to-End del flujo completo de la TechStore API.
"""
import pytest
import uuid


class TestFlujoCOmpleto:
    """Prueba el flujo completo de compra en la tienda."""

    @pytest.fixture(autouse=True)
    def setup_tienda(self, client):
        """Prepara el estado inicial para cada prueba."""
        self.client = client
        self.token_admin = None
        self.token_cliente = None
        self.productos_creados = {}
        # Sufijo único por prueba para evitar conflictos de datos duplicados
        self.uid = uuid.uuid4().hex[:8]

    # ─── Helper: registrar usuario y obtener token ────────────────────
    def _login(self, username, email, password):
        """Registra un usuario y retorna su access_token."""
        self.client.post("/auth/register", json={
            "username": username, "email": email, "password": password
        })
        resp = self.client.post("/auth/login", json={
            "username": username, "password": password
        })
        return resp.get_json()["access_token"]

    # ─── Helper: crear categorías y productos ────────────────────────
    def _crear_productos(self):
        """Crea categorías únicas y los productos del catálogo."""
        # Nombres únicos por prueba para evitar conflicto 409
        cat1 = self.client.post("/categorias/", json={
            "nombre": f"Laptops_{self.uid}",
            "description": "Computadoras portátiles"
        }).get_json()

        cat2 = self.client.post("/categorias/", json={
            "nombre": f"Accesorios_{self.uid}",
            "description": "Periféricos"
        }).get_json()

        productos = [
            {"sku": f"LAP_{self.uid}", "nombre": "Laptop Gamer 15",
             "precio": 18999.00, "stock": 10, "categoria_id": cat1["id"]},
            {"sku": f"MOU_{self.uid}", "nombre": "Mouse Inalambrico",
             "precio": 349.00, "stock": 50, "categoria_id": cat2["id"]},
            {"sku": f"USB_{self.uid}", "nombre": "USB Hub 7 puertos",
             "precio": 199.00, "stock": 30, "categoria_id": cat2["id"]},
        ]
        for prod in productos:
            resp = self.client.post("/productos/", json=prod)
            assert resp.status_code == 201, \
                f"Error creando producto {prod['sku']}: {resp.get_json()}"
            self.productos_creados[prod["sku"]] = resp.get_json()

    # ─── Helper: crear cliente en la tabla clientes ───────────────────
    def _crear_cliente_db(self, sufijo=""):
        """Crea un registro en la tabla clientes (requerido por órdenes)."""
        resp = self.client.post("/clientes/", json={
            "nombre": "Cliente Test",
            "email": f"clientetest{self.uid}{sufijo}@gmail.com",
            "telefono": "5551234567"
        })
        return resp.get_json()["id"]

    def test_flujo_completo_compra(self):
        """
        PRUEBA MAESTRA: Flujo completo de principio a fin.
        Registro → Login → Productos → Orden → Verificar stock → Reporte
        """
        # ── PASO 1: Admin se registra y crea productos ──
        self.token_admin = self._login(
            f"admin_{self.uid}", f"admin_{self.uid}@techstore.mx", "Admin123!"
        )
        self._crear_productos()
        assert len(self.productos_creados) == 3, "Deben crearse 3 productos"

        # ── PASO 2: Cliente se registra ──
        self.token_cliente = self._login(
            f"cliente_{self.uid}", f"cliente_{self.uid}@gmail.com", "Cliente123!"
        )
        assert self.token_cliente is not None

        # ── PASO 3: Ver catálogo ──
        resp_productos = self.client.get("/productos/")
        assert resp_productos.status_code == 200
        assert isinstance(resp_productos.get_json(), list)

        # ── PASO 4: Procesar orden ──
        id_cliente_db = self._crear_cliente_db()
        headers_cliente = {"Authorization": f"Bearer {self.token_cliente}"}

        sku_laptop = f"LAP_{self.uid}"
        sku_mouse = f"MOU_{self.uid}"
        id_laptop = self.productos_creados[sku_laptop]["id"]
        id_mouse = self.productos_creados[sku_mouse]["id"]
        stock_inicial_laptop = self.productos_creados[sku_laptop]["stock"]

        resp_orden = self.client.post("/api/ordenes/", json={
            "cliente_id": id_cliente_db,
            "productos": [
                {"producto_id": id_laptop, "cantidad": 2},
                {"producto_id": id_mouse, "cantidad": 5}
            ]
        }, headers=headers_cliente)

        assert resp_orden.status_code == 201, \
            f"Error en orden: {resp_orden.get_json()}"
        orden = resp_orden.get_json()
        assert orden["productos_comprados"] == 2
        assert orden["total"] > 0
        assert "orden_id" in orden

        # ── PASO 5: Verificar que el stock se redujo ──
        stock_actual = self.client.get(f"/productos/{id_laptop}").get_json()["stock"]
        assert stock_actual == stock_inicial_laptop - 2, \
            f"Stock debería ser {stock_inicial_laptop - 2}, es {stock_actual}"

        # ── PASO 6: Reporte de ventas ──
        headers_admin = {"Authorization": f"Bearer {self.token_admin}"}
        resp_reporte = self.client.get("/api/reportes/ventas", headers=headers_admin)
        assert resp_reporte.status_code == 200
        reporte = resp_reporte.get_json()
        assert reporte["resumen"]["total_ordenes"] >= 1
        assert reporte["resumen"]["ingresos"] > 0
        assert isinstance(reporte["top_productos"], list)

    def test_orden_con_stock_insuficiente_falla(self):
        """
        CASO NEGATIVO CRÍTICO: Pedir más stock del disponible.
        La orden completa se rechaza y el stock NO se modifica.
        """
        self.token_admin = self._login(
            f"admin2_{self.uid}", f"admin2_{self.uid}@techstore.mx", "Admin123!"
        )
        self._crear_productos()

        self.token_cliente = self._login(
            f"cliente2_{self.uid}", f"cliente2_{self.uid}@gmail.com", "Cliente123!"
        )
        headers_cliente = {"Authorization": f"Bearer {self.token_cliente}"}
        id_cliente_db = self._crear_cliente_db("_2")

        sku_usb = f"USB_{self.uid}"
        id_usb = self.productos_creados[sku_usb]["id"]

        # Hay 30 en stock, pedimos 999
        resp = self.client.post("/api/ordenes/", json={
            "cliente_id": id_cliente_db,
            "productos": [{"producto_id": id_usb, "cantidad": 999}]
        }, headers=headers_cliente)

        assert resp.status_code == 400
        assert "error" in resp.get_json()

        # CRÍTICO: El stock no debe haberse modificado
        stock_usb = self.client.get(f"/productos/{id_usb}").get_json()["stock"]
        assert stock_usb == 30, "El stock no debe cambiar si la orden falla"

    def test_reporte_requiere_autenticacion(self):
        """Sin JWT → 401 en el reporte de ventas."""
        resp = self.client.get("/api/reportes/ventas")
        assert resp.status_code == 401

    def test_orden_requiere_autenticacion(self):
        """Sin JWT → 401 al intentar crear una orden."""
        resp = self.client.post("/api/ordenes/", json={
            "cliente_id": 1,
            "productos": [{"producto_id": 1, "cantidad": 1}]
        })
        assert resp.status_code == 401