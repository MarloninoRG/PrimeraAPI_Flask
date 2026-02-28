from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.categoria import Categoria

categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

@categorias_bp.route('/', methods=['GET'])
def get_categorias():
    categorias = Categoria.query.all()
    return jsonify([c.to_dict() for c in categorias]), 200

@categorias_bp.route('/<int:id>', methods=['GET'])
def get_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    return jsonify(categoria.to_dict()), 200

@categorias_bp.route('/', methods=['POST'])
def create_categoria():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    if 'nombre' not in data:
        return jsonify({'error': 'El campo nombre es requerido'}), 400

    if Categoria.query.filter_by(nombre=data['nombre']).first():
        return jsonify({'error': 'Ya existe una categoría con ese nombre'}), 409

    nueva_categoria = Categoria(
        nombre=data['nombre'],
        description=data.get('description')
    )

    db.session.add(nueva_categoria)
    db.session.commit()

    return jsonify(nueva_categoria.to_dict()), 201

@categorias_bp.route('/<int:id>', methods=['PUT'])
def update_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    if 'nombre' in data:
        existente = Categoria.query.filter_by(nombre=data['nombre']).first()
        if existente and existente.id != id:
            return jsonify({'error': 'Ya existe una categoría con ese nombre'}), 409
        categoria.nombre = data['nombre']

    if 'description' in data:
        categoria.description = data['description']

    db.session.commit()
    return jsonify(categoria.to_dict()), 200

@categorias_bp.route('/<int:id>', methods=['DELETE'])
def delete_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    return jsonify({'message': f'Categoría "{categoria.nombre}" eliminada correctamente'}), 200