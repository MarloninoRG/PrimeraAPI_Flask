from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.materia import Materia

materia_bp = Blueprint('materias', __name__, url_prefix='/materias')

# GET - Obtener todas las materias
@materia_bp.route('/', methods=['GET'])
def get_materias():
    materias = Materia.query.all()
    return jsonify([m.to_dict() for m in materias]), 200

# GET - Obtener una materia por ID
@materia_bp.route('/<int:id>', methods=['GET'])
def get_materia(id):
    materia = Materia.query.get_or_404(id)
    return jsonify(materia.to_dict()), 200

# POST - Crear una nueva materia
@materia_bp.route('/', methods=['POST'])
def create_materia():
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

# PUT - Actualizar una materia existente
@materia_bp.route('/<int:id>', methods=['PUT'])
def update_materia(id):
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

# DELETE - Eliminar una materia
@materia_bp.route('/<int:id>', methods=['DELETE'])
def delete_materia(id):
    materia = Materia.query.get_or_404(id)

    db.session.delete(materia)
    db.session.commit()

    return jsonify({'message': f'Materia "{materia.nombre}" eliminada correctamente'}), 200