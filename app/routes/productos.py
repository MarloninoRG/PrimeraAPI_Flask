from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.producto import Producto

productos_bp = Blueprint('productos', __name__, url_prefix='/productos')

@productos_bp.route('/', methods=['GET'])
def get_productos():
    productos = Producto.query.all()
    return jsonify([p.to_dict() for p in productos]), 200

@productos_bp.route('/<int:id>', methods=['GET'])
def get_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify(producto.to_dict()), 200

@productos_bp.route('/', methods=['POST'])
def create_producto():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    campos_requeridos = ['sku', 'nombre', 'precio']
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({'error': f'El campo {campo} es requerido'}), 400

    if Producto.query.filter_by(sku=data['sku']).first():
        return jsonify({'error': 'Ya existe un producto con ese SKU'}), 409

    nuevo_producto = Producto(
        sku=data['sku'],
        nombre=data['nombre'],
        description=data.get('description'),
        precio=data['precio'],
        stock=data.get('stock', 0),
        categoria_id=data.get('categoria_id'),
        activo=data.get('activo', True)
    )

    db.session.add(nuevo_producto)
    db.session.commit()

    return jsonify(nuevo_producto.to_dict()), 201

@productos_bp.route('/<int:id>', methods=['PUT'])
def update_producto(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    if 'sku' in data:
        existente = Producto.query.filter_by(sku=data['sku']).first()
        if existente and existente.id != id:
            return jsonify({'error': 'Ya existe un producto con ese SKU'}), 409
        producto.sku = data['sku']

    for campo in ['nombre', 'description', 'precio', 'stock', 'categoria_id', 'activo']:
        if campo in data:
            setattr(producto, campo, data[campo])

    db.session.commit()
    return jsonify(producto.to_dict()), 200

@productos_bp.route('/<int:id>', methods=['DELETE'])
def delete_producto(id):
    producto = Producto.query.get_or_404(id)
    producto.activo = False
    db.session.commit()
    return jsonify({'message': f'Producto "{producto.nombre}" desactivado correctamente'}), 200