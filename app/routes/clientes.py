from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.cliente import Cliente

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/', methods=['GET'])
def get_clientes():
    clientes = Cliente.query.all()
    return jsonify([c.to_dict() for c in clientes]), 200

@clientes_bp.route('/<int:id>', methods=['GET'])
def get_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    return jsonify(cliente.to_dict()), 200

@clientes_bp.route('/', methods=['POST'])
def create_cliente():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    campos_requeridos = ['nombre', 'email']
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({'error': f'El campo {campo} es requerido'}), 400

    if Cliente.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Ya existe un cliente con ese email'}), 409

    nuevo_cliente = Cliente(
        nombre=data['nombre'],
        email=data['email'],
        telefono=data.get('telefono'),
        direccion=data.get('direccion')
    )

    db.session.add(nuevo_cliente)
    db.session.commit()

    return jsonify(nuevo_cliente.to_dict()), 201

@clientes_bp.route('/<int:id>', methods=['PUT'])
def update_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    if 'email' in data:
        existente = Cliente.query.filter_by(email=data['email']).first()
        if existente and existente.id != id:
            return jsonify({'error': 'Ya existe un cliente con ese email'}), 409
        cliente.email = data['email']

    for campo in ['nombre', 'telefono', 'direccion']:
        if campo in data:
            setattr(cliente, campo, data[campo])

    db.session.commit()
    return jsonify(cliente.to_dict()), 200

@clientes_bp.route('/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    return jsonify({'message': f'Cliente "{cliente.nombre}" eliminado correctamente'}), 200