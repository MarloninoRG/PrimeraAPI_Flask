from app.extensions import db

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.Text)

    # Relación: un cliente tiene muchas órdenes
    ordenes = db.relationship('Orden', back_populates='cliente')

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion
        }

    def __repr__(self):
        return f'<Cliente {self.nombre}>'