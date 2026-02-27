from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import DevelopmentConfig

# Crear la instancia de SQLAlchemy
# ORM convierte las tablas de la base de datos en clases de Python
db = SQLAlchemy()

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
    
    # Importar y registrar los blueprints (rutas) de la aplicación
    from .routes import main_bp
    app.register_blueprint(main_bp)
        
    return app