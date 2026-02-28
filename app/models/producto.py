from app.extensions import db
from datetime import datetime

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    categoria = db.relationship('Categoria', back_populates='productos')
    detalles = db.relationship('DetalleOrden', back_populates='producto')

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'nombre': self.nombre,
            'description': self.description,
            'precio': float(self.precio),
            'stock': self.stock,
            'categoria_id': self.categoria_id,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }

    def __repr__(self):
        return f'<Producto {self.sku} - {self.nombre}>'