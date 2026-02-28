from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.usuario import Usuario
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    # Registrar un nuevo usuario
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Faltan campos requeridos'}), 400

    if Usuario.query.filter_by(username=username).first() or Usuario.query.filter_by(email=email).first():
        return jsonify({'message': 'El nombre de usuario o correo electrónico ya existe'}), 400

    new_user = Usuario(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    # Iniciar sesión y generar un token JWT
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Faltan campos requeridos'}), 400

    user = Usuario.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24))
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Credenciales inválidas'}), 401
    
@auth_bp.route('/profile', methods=['GET'])
@jwt_required() # Este decorador asegura que el usuario esté autenticado para acceder a esta ruta
def profile():
    # Obtener el perfil del usuario autenticado
    user_id = get_jwt_identity() # Obtener el ID del usuario desde el token JWT
    user = Usuario.query.get(user_id)

    if user:
        return jsonify({
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'active': user.active
        }), 200
    else:
        return jsonify({'message': 'Usuario no encontrado'}), 404