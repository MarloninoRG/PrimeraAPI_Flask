from flask import Flask
from flask_cors import CORS
from .config import DevelopmentConfig
from .routes import main_bp
from .routes.estudiantes import estudiantes_bp
from .routes.materia import materia_bp
from .routes.calificaciones import cal_bp
from .routes.auth import auth_bp
from .extensions import db, jwt
from flasgger import Swagger

def create_app(config_class=DevelopmentConfig):
    """Función de fábrica para crear la aplicación Flask"""
    
    # Crear la instancia de Flask
    app = Flask(__name__)
    
    # Cargar la configuración desde la clase proporcionada
    app.config.from_object(config_class)
    
    # Inicializar la extensión SQLAlchemy con la aplicación
    db.init_app(app)
    
    # Habilitar CORS para permitir solicitudes desde otros dominios
    CORS(app)
    
    # Inicializar JWTManager para manejar la autenticación con JWT
    jwt.init_app(app)
    
    # Configurar Swagger para la documentación de la API
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,  # Incluir todas las rutas
                "model_filter": lambda tag: True,  # Incluir todos los modelos
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
    
    # Importar y registrar los blueprints (rutas) de la aplicación
    app.register_blueprint(main_bp)
    app.register_blueprint(estudiantes_bp)
    app.register_blueprint(materia_bp)
    app.register_blueprint(cal_bp)
    app.register_blueprint(auth_bp)
            
    return app