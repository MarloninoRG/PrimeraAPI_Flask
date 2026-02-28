import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Config:
    """Clase de configuración básica para Flask"""
    
    # Clave secreta para sesiones y seguridad
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    
    # Desactivar el seguimiento de modificaciones de objetos para ahorrar recursos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mostrar las consultas SQL en la consola para depuración
    SQLALCHEMY_ECHO = True
    
    # Configuración de JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_jwt_secret_key")
    
class DevelopmentConfig(Config):
    """Configuración específica para el entorno de desarrollo"""
    
    # Habilitar el modo de depuración
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuración específica para el entorno de producción"""
    
    # Deshabilitar el modo de depuración
    DEBUG = False
    SQLALCHEMY_ECHO = False  # No mostrar consultas SQL en producción