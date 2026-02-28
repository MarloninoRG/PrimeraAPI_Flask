from flask import Flask
from flask_cors import CORS
from .config import DevelopmentConfig
from .routes import main_bp
from .routes.estudiantes import estudiantes_bp
from .routes.materia import materia_bp
from .routes.calificaciones import cal_bp
from .routes.auth import auth_bp
from .routes.categorias import categorias_bp
from .routes.productos import productos_bp
from .routes.clientes import clientes_bp
from .extensions import db, jwt
from flasgger import Swagger


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # ✅ Importar todos los modelos aquí en orden
    from .models.usuario import Usuario
    from .models.estudiante import Estudiante
    from .models.materia import Materia
    from .models.calificacion import Calificacion
    from .models.categoria import Categoria
    from .models.producto import Producto
    from .models.cliente import Cliente
    from .models.orden import Orden
    from .models.detalle_orden import DetalleOrden

    CORS(app)
    jwt.init_app(app)

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }

    swagger_template = {
        "info": {
            "title": "API de Gestión de Estudiantes",
            "description": "API para gestionar estudiantes, materias y calificaciones",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header"
            }
        }
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    app.register_blueprint(main_bp)
    app.register_blueprint(estudiantes_bp)
    app.register_blueprint(materia_bp)
    app.register_blueprint(cal_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(clientes_bp)

    return app