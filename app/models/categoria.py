from app.extensions import db

class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    # Relación: una categoría tiene muchos productos
    productos = db.relationship('Producto', back_populates='categoria')

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'description': self.description
        }

    def __repr__(self):
        return f'<Categoria {self.nombre}>'