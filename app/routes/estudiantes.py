from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.estudiante import Estudiante

estudiantes_bp = Blueprint('estudiantes', __name__, url_prefix='/estudiantes')

@estudiantes_bp.route('/', methods=['POST'])
def crear_estudiante():
    """
    Crear un nuevo estudiante
    ---
    tags:
      - Estudiantes
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - matricula
            - nombre
            - apellido
            - email
            - carrera
            - semestre
          properties:
            matricula:
              type: string
              example: "2023001"
            nombre:
              type: string
              example: "Juan"
            apellido:
              type: string
              example: "Pérez"
            email:
              type: string
              example: "juan@gmail.com"
            carrera:
              type: string
              example: "Ingeniería en Sistemas"
            semestre:
              type: integer
              example: 3
    responses:
      201:
        description: Estudiante creado exitosamente
      400:
        description: Datos inválidos o faltantes
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos.'}), 400

    required_fields = ['matricula', 'nombre', 'apellido', 'email', 'carrera', 'semestre']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es obligatorio.'}), 400

    if Estudiante.query.filter_by(matricula=data['matricula']).first():
        return jsonify({'error': 'La matrícula ya existe.'}), 400
    if Estudiante.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El correo electrónico ya existe.'}), 400

    nuevo_estudiante = Estudiante(
        matricula=data['matricula'],
        nombre=data['nombre'],
        apellido=data['apellido'],
        email=data['email'],
        carrera=data['carrera'],
        semestre=data['semestre']
    )

    db.session.add(nuevo_estudiante)
    db.session.commit()

    return jsonify(nuevo_estudiante.to_dict()), 201


@estudiantes_bp.route('/', methods=['GET'])
def obtener_estudiantes():
    """
    Obtener lista de estudiantes
    ---
    tags:
      - Estudiantes
    parameters:
      - in: query
        name: carrera
        type: string
        required: false
        description: Filtrar por carrera
        example: "Ingeniería en Sistemas"
      - in: query
        name: pagina
        type: integer
        required: false
        default: 1
      - in: query
        name: per_page
        type: integer
        required: false
        default: 10
    responses:
      200:
        description: Lista de estudiantes obtenida exitosamente
    """
    carrera = request.args.get('carrera')
    pagina = request.args.get('pagina', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)

    estudiantes = Estudiante.query
    if carrera:
        estudiantes = estudiantes.filter_by(carrera=carrera)

    estudiantes = estudiantes.paginate(page=pagina, per_page=per_page, error_out=False)

    estudiantes_list = [estudiante.to_dict() for estudiante in estudiantes.items]
    return jsonify({
        'estudiantes': estudiantes_list,
        'pagina': pagina,
        'total_paginas': estudiantes.pages,
        'total_estudiantes': estudiantes.total
    }), 200


@estudiantes_bp.route('/<int:id>', methods=['GET'])
def obtener_estudiante(id):
    """
    Obtener un estudiante por ID
    ---
    tags:
      - Estudiantes
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID del estudiante
        example: 1
    responses:
      200:
        description: Estudiante encontrado
      404:
        description: Estudiante no encontrado
    """
    estudiante = Estudiante.query.get_or_404(id, description='Estudiante no encontrado.')
    return jsonify(estudiante.to_dict()), 200


@estudiantes_bp.route('/<int:id>', methods=['PUT'])
def actualizar_estudiante(id):
    """
    Actualizar un estudiante por ID
    ---
    tags:
      - Estudiantes
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID del estudiante
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nombre:
              type: string
              example: "Juan Carlos"
            apellido:
              type: string
              example: "Pérez López"
            email:
              type: string
              example: "juancarlos@gmail.com"
            carrera:
              type: string
              example: "Ingeniería en Sistemas"
            semestre:
              type: integer
              example: 4
    responses:
      200:
        description: Estudiante actualizado exitosamente
      404:
        description: Estudiante no encontrado
    """
    estudiante = Estudiante.query.get_or_404(id, description='Estudiante no encontrado.')
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos.'}), 400

    for key in ['matricula', 'nombre', 'apellido', 'email', 'carrera', 'semestre']:
        if key in data:
            setattr(estudiante, key, data[key])

    db.session.commit()
    return jsonify(estudiante.to_dict()), 200


@estudiantes_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_estudiante(id):
    """
    Eliminar un estudiante por ID
    ---
    tags:
      - Estudiantes
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID del estudiante
        example: 1
    responses:
      200:
        description: Estudiante eliminado exitosamente
      404:
        description: Estudiante no encontrado
    """
    estudiante = Estudiante.query.get_or_404(id, description='Estudiante no encontrado.')
    estudiante.activo = False
    db.session.commit()

    return jsonify({'message': f'Estudiante {estudiante.matricula} eliminado exitosamente.'}), 200