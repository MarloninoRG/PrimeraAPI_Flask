from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.usuario import Usuario
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registrar un nuevo usuario
    ---
    tags:
      - Autenticación
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: "juan123"
            email:
              type: string
              example: "juan@gmail.com"
            password:
              type: string
              example: "segura123"
    responses:
      201:
        description: Usuario registrado exitosamente
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Usuario registrado exitosamente"
      400:
        description: Faltan campos requeridos o el usuario ya existe
    """
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
    """
    Iniciar sesión y obtener token JWT
    ---
    tags:
      - Autenticación
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "juan123"
            password:
              type: string
              example: "segura123"
    responses:
      200:
        description: Login exitoso, retorna token JWT
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      400:
        description: Faltan campos requeridos
      401:
        description: Credenciales inválidas
    """
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
@jwt_required()
def profile():
    """
    Obtener perfil del usuario autenticado
    ---
    tags:
      - Autenticación
    security:
      - Bearer: []
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Token JWT en formato "Bearer <token>"
        example: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      200:
        description: Perfil del usuario obtenido exitosamente
        schema:
          type: object
          properties:
            username:
              type: string
              example: "juan123"
            email:
              type: string
              example: "juan@gmail.com"
            role:
              type: string
              example: "user"
            active:
              type: boolean
              example: true
      401:
        description: Token inválido o no proporcionado
      404:
        description: Usuario no encontrado
    """
    user_id = get_jwt_identity()
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