from app.extensions import db
from datetime import datetime

class Orden(db.Model):
    __tablename__ = 'ordenes'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    cliente = db.relationship('Cliente', back_populates='ordenes')
    detalles = db.relationship('DetalleOrden', back_populates='orden')

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'total': float(self.total),
            'estado': self.estado,
            'fecha': self.fecha.isoformat()
        }

    def __repr__(self):
        return f'<Orden {self.id} - {self.estado}>'