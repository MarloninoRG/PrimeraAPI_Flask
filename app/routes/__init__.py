from flask import Blueprint, jsonify
from datetime import datetime

# Blueprint para las rutas principales
main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    """Ruta raiz que devuelve un mensaje de bienvenida y algunos datos adicionales"""
    return jsonify({
        "message": "Bienvenido a mi primera API con Flask",
        "version": "1.0",
        "tecnologias": ["Flask", "SQLAlchemy", "PostgreSQL"]
    })

@main_bp.route('/health', methods=['GET'])
def health_check():
    """Ruta para verificar el estado de la API"""
    return jsonify({
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "base_de_datos": "Conectada"
    }), 200
    
