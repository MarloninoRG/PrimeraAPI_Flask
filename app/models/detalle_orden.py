from app.extensions import db

class DetalleOrden(db.Model):
    __tablename__ = 'detalle_ordenes'

    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('ordenes.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    # Relaciones
    orden = db.relationship('Orden', back_populates='detalles')
    producto = db.relationship('Producto', back_populates='detalles')

    def to_dict(self):
        return {
            'id': self.id,
            'orden_id': self.orden_id,
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario)
        }

    def __repr__(self):
        return f'<DetalleOrden orden={self.orden_id} producto={self.producto_id}>'