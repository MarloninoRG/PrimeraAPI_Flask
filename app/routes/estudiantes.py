from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.estudiante import Estudiante

estudiantes_bp = Blueprint('estudiantes', __name__, url_prefix='/estudiantes')

# =======================================================
# CREATE: POST
# =======================================================

@estudiantes_bp.route('/', methods=['POST'])
def crear_estudiante():
    """
    Ruta para crear un nuevo estudiante.
    Espera un JSON con los datos del estudiante en el cuerpo de la solicitud.
    """
    data = request.get_json()
    
    # Validar que se haya recibido un JSON válido
    if not data:
        return jsonify({'error': 'No se proporcionaron datos.'}), 400
    
    # Validar que se hayan proporcionado los campos necesarios
    required_fields = ['matricula', 'nombre', 'apellido', 'email', 'carrera', 'semestre']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es obligatorio.'}), 400
    
    # Verificar que la matrícula y el email sean únicos
    if Estudiante.query.filter_by(matricula=data['matricula']).first():
        return jsonify({'error': 'La matrícula ya existe.'}), 400
    if Estudiante.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El correo electrónico ya existe.'}), 400
    
    # Crear un nuevo objeto Estudiante con los datos proporcionados
    nuevo_estudiante = Estudiante(
        matricula=data['matricula'],
        nombre=data['nombre'],
        apellido=data['apellido'],
        email=data['email'],
        carrera=data['carrera'],
        semestre=data['semestre']
    )
    
    # Agregar el nuevo estudiante a la sesión de la base de datos y guardar los cambios
    db.session.add(nuevo_estudiante)
    db.session.commit()
    
    # Devolver una respuesta JSON con los datos del nuevo estudiante y un código de estado 201 (Creado)
    return jsonify(nuevo_estudiante.to_dict()), 201

# =======================================================
# READ: GET
# =======================================================

@estudiantes_bp.route('/', methods=['GET'])
def obtener_estudiantes():
    """
    Ruta para obtener la lista de todos los estudiantes.
    Devuelve un JSON con una lista de estudiantes.
    """
    # Parametros de consulta para filtrar por carrera o semestre (opcionales)
    carrera = request.args.get('carrera')
    pagina = request.args.get('pagina', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    
    # Construir la consulta para obtener los estudiantes, aplicando filtros si se proporcionan
    estudiantes = Estudiante.query
    if carrera:
        estudiantes = estudiantes.filter_by(carrera=carrera)
    
    # Paginar los resultados para evitar devolver demasiados estudiantes en una sola respuesta
    estudiantes = estudiantes.paginate(page=pagina, per_page=per_page, error_out=False)
    
    estudiantes_list = [estudiante.to_dict() for estudiante in estudiantes.items]
    return jsonify({
        'estudiantes': estudiantes_list,
        'pagina': pagina,
        'total_paginas': estudiantes.pages,
        'total_estudiantes': estudiantes.total
    }), 200
    
# =======================================================
# READ: GET by ID
# =======================================================
@estudiantes_bp.route('/<int:id>', methods=['GET'])
def obtener_estudiante(id):
    """
    Ruta para obtener los detalles de un estudiante específico por su ID.
    Devuelve un JSON con los datos del estudiante o un error si no se encuentra.
    """
    # get_or_404 es una función de Flask-SQLAlchemy que devuelve el objeto si se encuentra o un error 404 si no se encuentra
    estudiante = Estudiante.query.get_or_404(id, description='Estudiante no encontrado.')
    return jsonify(estudiante.to_dict()), 200

# =======================================================
# UPDATE: PUT
# =======================================================
@estudiantes_bp.route('/<int:id>', methods=['PUT'])
def actualizar_estudiante(id):
    """
    Ruta para actualizar los datos de un estudiante específico por su ID.
    Espera un JSON con los campos a actualizar en el cuerpo de la solicitud.
    Devuelve un JSON con los datos actualizados del estudiante o un error si no se encuentra.
    """
    estudiante = Estudiante.query.get_or_404(id, description='Estudiante no encontrado.')
    data = request.get_json()
    
    # Validar que se haya recibido un JSON válido
    if not data:
        return jsonify({'error': 'No se proporcionaron datos.'}), 400
    
    # Actualizar los campos del estudiante con los datos proporcionados
    for key in ['matricula', 'nombre', 'apellido', 'email', 'carrera', 'semestre']:
        if key in data:
            setattr(estudiante, key, data[key])
    
    # Guardar los cambios en la base de datos
    db.session.commit()
    
    return jsonify(estudiante.to_dict()), 200

# =======================================================
# DELETE: DELETE
# =======================================================
@estudiantes_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_estudiante(id):
    """
    Ruta para eliminar un estudiante específico por su ID.
    Devuelve un mensaje de éxito o un error si no se encuentra el estudiante.
    """
    estudiante = Estudiante.query.get_or_404(id, description='Estudiante no encontrado.')
    estudiante.activo = False  # Marcar el estudiante como inactivo en lugar de eliminarlo físicamente
    
    # Eliminar el estudiante de la base de datos
    db.session.commit()
    
    return jsonify({'message': f'Estudiante {estudiante.matricula} eliminado exitosamente.'}), 200