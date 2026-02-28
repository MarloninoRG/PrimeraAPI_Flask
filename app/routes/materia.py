from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.materia import Materia

materia_bp = Blueprint('materias', __name__, url_prefix='/materias')

@materia_bp.route('/', methods=['GET'])
def get_materias():
    """
    Obtener todas las materias
    ---
    tags:
      - Materias
    responses:
      200:
        description: Lista de materias obtenida exitosamente
    """
    materias = Materia.query.all()
    return jsonify([m.to_dict() for m in materias]), 200


@materia_bp.route('/<int:id>', methods=['GET'])
def get_materia(id):
    """
    Obtener una materia por ID
    ---
    tags:
      - Materias
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID de la materia
        example: 1
    responses:
      200:
        description: Materia encontrada
      404:
        description: Materia no encontrada
    """
    materia = Materia.query.get_or_404(id)
    return jsonify(materia.to_dict()), 200


@materia_bp.route('/', methods=['POST'])
def create_materia():
    """
    Crear una nueva materia
    ---
    tags:
      - Materias
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - clave
            - nombre
            - creditos
            - docente
          properties:
            clave:
              type: string
              example: "MAT101"
            nombre:
              type: string
              example: "Cálculo Diferencial"
            creditos:
              type: integer
              example: 5
            docente:
              type: string
              example: "Dr. Juan Pérez"
    responses:
      201:
        description: Materia creada exitosamente
      400:
        description: Datos inválidos o faltantes
      409:
        description: Ya existe una materia con esa clave
    """
    data = request.get_json()

    campos_requeridos = ['clave', 'nombre', 'creditos', 'docente']
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({'error': f'El campo "{campo}" es requerido'}), 400

    if Materia.query.filter_by(clave=data['clave']).first():
        return jsonify({'error': 'Ya existe una materia con esa clave'}), 409

    nueva_materia = Materia(
        clave=data['clave'],
        nombre=data['nombre'],
        creditos=data['creditos'],
        docente=data['docente']
    )

    db.session.add(nueva_materia)
    db.session.commit()

    return jsonify(nueva_materia.to_dict()), 201


@materia_bp.route('/<int:id>', methods=['PUT'])
def update_materia(id):
    """
    Actualizar una materia por ID
    ---
    tags:
      - Materias
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID de la materia
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            clave:
              type: string
              example: "MAT102"
            nombre:
              type: string
              example: "Cálculo Integral"
            creditos:
              type: integer
              example: 6
            docente:
              type: string
              example: "Dra. María López"
    responses:
      200:
        description: Materia actualizada exitosamente
      404:
        description: Materia no encontrada
      409:
        description: Ya existe una materia con esa clave
    """
    materia = Materia.query.get_or_404(id)
    data = request.get_json()

    if 'clave' in data:
        existente = Materia.query.filter_by(clave=data['clave']).first()
        if existente and existente.id != id:
            return jsonify({'error': 'Ya existe una materia con esa clave'}), 409
        materia.clave = data['clave']

    if 'nombre' in data:
        materia.nombre = data['nombre']
    if 'creditos' in data:
        materia.creditos = data['creditos']
    if 'docente' in data:
        materia.docente = data['docente']

    db.session.commit()

    return jsonify(materia.to_dict()), 200


@materia_bp.route('/<int:id>', methods=['DELETE'])
def delete_materia(id):
    """
    Eliminar una materia por ID
    ---
    tags:
      - Materias
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID de la materia
        example: 1
    responses:
      200:
        description: Materia eliminada correctamente
      404:
        description: Materia no encontrada
    """
    materia = Materia.query.get_or_404(id)

    db.session.delete(materia)
    db.session.commit()

    return jsonify({'message': f'Materia "{materia.nombre}" eliminada correctamente'}), 200