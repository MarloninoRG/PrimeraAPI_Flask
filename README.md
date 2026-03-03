# 🚀 Primera API con Flask

API REST desarrollada con Flask que integra dos módulos principales: **gestión escolar** (estudiantes, materias y calificaciones) y **tienda en línea** (productos, categorías, clientes y órdenes). Incluye autenticación JWT, documentación Swagger y suite de pruebas con 91% de cobertura.

**Autor:** Marlon Rojas Galindo

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Variables de Entorno](#variables-de-entorno)
- [Ejecutar la API](#ejecutar-la-api)
- [Endpoints](#endpoints)
- [Autenticación JWT](#autenticación-jwt)
- [Pruebas](#pruebas)

---

## 📖 Descripción

Este proyecto es una API REST construida con Flask que combina dos dominios:

- **Módulo Escolar:** Gestión de estudiantes, materias y calificaciones con kardex y cálculo de promedios.
- **Módulo Tienda:** Catálogo de productos, gestión de clientes, procesamiento de órdenes con control de stock y reportes de ventas.

Ambos módulos comparten un sistema de autenticación basado en JWT y una base de datos relacional gestionada con SQLAlchemy.

---

## 🛠 Tecnologías

| Herramienta | Versión | Uso |
|---|---|---|
| Python | 3.14 | Lenguaje base |
| Flask | Latest | Framework web |
| Flask-SQLAlchemy | Latest | ORM |
| Flask-JWT-Extended | Latest | Autenticación JWT |
| Flask-Migrate | Latest | Migraciones de BD |
| Flask-CORS | Latest | Manejo de CORS |
| Flasgger | Latest | Documentación Swagger |
| PostgreSQL | Latest | Base de datos producción |
| SQLite | Built-in | Base de datos pruebas |
| pytest | Latest | Framework de pruebas |
| pytest-cov | Latest | Cobertura de código |

---

## 📁 Estructura del Proyecto

```
API-U3/
├── app/
│   ├── __init__.py          # Factory de la aplicación
│   ├── config.py            # Configuraciones (Dev, Prod, Test)
│   ├── extensions.py        # Instancias de db y jwt
│   ├── models/
│   │   ├── usuario.py       # Modelo de usuario con hash de contraseña
│   │   ├── estudiante.py    # Modelo de estudiante
│   │   ├── materia.py       # Modelo de materia
│   │   ├── calificacion.py  # Modelo de calificación
│   │   ├── categoria.py     # Modelo de categoría
│   │   ├── producto.py      # Modelo de producto
│   │   ├── cliente.py       # Modelo de cliente
│   │   ├── orden.py         # Modelo de orden
│   │   └── detalle_orden.py # Modelo de detalle de orden
│   └── routes/
│       ├── auth.py          # Registro, login y perfil
│       ├── estudiantes.py   # CRUD estudiantes
│       ├── materia.py       # CRUD materias
│       ├── calificaciones.py# Registro y kardex
│       ├── categorias.py    # CRUD categorías
│       ├── productos.py     # CRUD productos
│       ├── clientes.py      # CRUD clientes
│       ├── ordenes.py       # Procesamiento de órdenes
│       └── reportes.py      # Reporte de ventas
├── tests/
│   ├── conftest.py          # Fixtures de pytest
│   ├── test_modelos.py      # Pruebas unitarias de modelos
│   ├── test_auth.py         # Pruebas de autenticación JWT
│   ├── test_estudiantes.py  # Pruebas CRUD estudiantes
│   ├── test_calificaciones.py# Pruebas de calificaciones y kardex
│   ├── test_catalogo.py     # Pruebas de categorías, clientes, materias, productos
│   └── test_tienda.py       # Pruebas E2E del flujo de tienda
├── .env                     # Variables de entorno (no se sube a GitHub)
├── .gitignore
├── pytest.ini               # Configuración de pytest (80% cobertura mínima)
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/primera-api-flask.git
cd primera-api-flask

# 2. Crear y activar el entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## 🔐 Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
SECRET_KEY=tu_clave_secreta_aqui
JWT_SECRET_KEY=tu_clave_jwt_de_al_menos_32_caracteres
DATABASE_URL=postgresql://usuario:password@localhost:5432/nombre_bd
```

---

## ▶️ Ejecutar la API

```bash
# Crear las tablas en la base de datos
flask db init
flask db migrate -m "Tablas iniciales"
flask db upgrade

# Iniciar el servidor de desarrollo
flask run
```

La API estará disponible en `http://localhost:5000`.
La documentación Swagger estará disponible en `http://localhost:5000/docs/`.

---

## 📡 Endpoints

### 🔑 Autenticación — `/auth`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/auth/register` | Registrar nuevo usuario | No |
| POST | `/auth/login` | Iniciar sesión, retorna JWT | No |
| GET | `/auth/profile` | Ver perfil del usuario | ✅ JWT |

### 🎓 Estudiantes — `/estudiantes`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/estudiantes/` | Crear estudiante | No |
| GET | `/estudiantes/` | Listar estudiantes (paginado) | No |
| GET | `/estudiantes/<id>` | Obtener estudiante por ID | No |
| PUT | `/estudiantes/<id>` | Actualizar estudiante | No |
| DELETE | `/estudiantes/<id>` | Borrado lógico (activo=False) | No |

### 📚 Materias — `/materias`

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/materias/` | Crear materia |
| GET | `/materias/` | Listar materias |
| GET | `/materias/<id>` | Obtener materia por ID |
| PUT | `/materias/<id>` | Actualizar materia |
| DELETE | `/materias/<id>` | Eliminar materia |

### 📊 Calificaciones — `/cal`

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/cal/` | Registrar calificación |
| GET | `/cal/estudiantes/<id>/kardex` | Obtener kardex completo |

**Respuesta del kardex:**
```json
{
  "estudiante_id": 1,
  "nombre_estudiante": "Carlos",
  "kardex": [...],
  "promedio": 85.0,
  "materias_aprobadas": 3
}
```

### 🏷️ Categorías — `/categorias`

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/categorias/` | Crear categoría |
| GET | `/categorias/` | Listar categorías |
| GET | `/categorias/<id>` | Obtener categoría |
| PUT | `/categorias/<id>` | Actualizar categoría |
| DELETE | `/categorias/<id>` | Eliminar categoría |

### 📦 Productos — `/productos`

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/productos/` | Crear producto |
| GET | `/productos/` | Listar productos |
| GET | `/productos/<id>` | Obtener producto |
| PUT | `/productos/<id>` | Actualizar producto |
| DELETE | `/productos/<id>` | Desactivar producto |

### 👤 Clientes — `/clientes`

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/clientes/` | Crear cliente |
| GET | `/clientes/` | Listar clientes |
| GET | `/clientes/<id>` | Obtener cliente |
| PUT | `/clientes/<id>` | Actualizar cliente |
| DELETE | `/clientes/<id>` | Eliminar cliente |

### 🛒 Órdenes — `/api/ordenes`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/api/ordenes/` | Procesar orden de compra | ✅ JWT |

**Body esperado:**
```json
{
  "cliente_id": 1,
  "productos": [
    { "producto_id": 5, "cantidad": 2 },
    { "producto_id": 12, "cantidad": 1 }
  ]
}
```

### 📈 Reportes — `/api/reportes`

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| GET | `/api/reportes/ventas` | Reporte de ventas del mes | ✅ JWT |

Parámetros opcionales: `?mes=3&anio=2026`

---

## 🔒 Autenticación JWT

Las rutas protegidas requieren el token en el header:

```
Authorization: Bearer <access_token>
```

**Flujo:**
1. `POST /auth/register` → crear cuenta
2. `POST /auth/login` → obtener `access_token`
3. Incluir token en el header de cada petición protegida

---

## 🧪 Pruebas

El proyecto usa **pytest** con SQLite en memoria para pruebas aisladas y rápidas, sin necesidad de PostgreSQL.

```bash
# Correr todas las pruebas con reporte de cobertura
pytest -v

# Correr un archivo específico
pytest tests/test_auth.py -v

# Ver reporte HTML de cobertura
# (se genera en reports/coverage/)
```

**Resultado actual:**

```
62 passed, 0 failed
Cobertura total: 91.25% ✅ (mínimo requerido: 80%)
```

| Suite | Pruebas | Descripción |
|---|---|---|
| `test_modelos.py` | 8 | Pruebas unitarias de modelos ORM |
| `test_auth.py` | 10 | Registro, login y rutas protegidas |
| `test_estudiantes.py` | 13 | CRUD completo de estudiantes |
| `test_calificaciones.py` | 9 | Registro de calificaciones y kardex |
| `test_catalogo.py` | 17 | CRUD de categorías, clientes, materias y productos |
| `test_tienda.py` | 4 | Flujo E2E completo de la tienda |

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos.
