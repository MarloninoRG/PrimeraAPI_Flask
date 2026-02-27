from app.extensions import db
from datetime import datetime

class Estudiante(db.Model):
    """
    Modelo para representar a un estudiante en la base de datos.
    SQLAlchemy se encargará de mapear esta clase a una tabla en la base de datos.
    """
    # Nombre de la tabla en la base de datos
    __tablename__ = 'estudiantes'
    
    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)  # ID del estudiante, clave primaria
    matricula = db.Column(db.String(20), unique=True, nullable=False)  # Matrícula del estudiante
    nombre = db.Column(db.String(100), nullable=False)  # Nombre del estudiante
    apellido = db.Column(db.String(100), nullable=False)  # Apellido del estudiante
    email = db.Column(db.String(120), unique=True, nullable=False)  # Correo electrónico del estudiante
    carrera = db.Column(db.String(100), nullable=False)  # Carrera del estudiante
    semestre = db.Column(db.Integer, nullable=False, default=1)  # Semestre del estudiante
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de registro del estudiante
    activo = db.Column(db.Boolean, default=True)  # Indica si el estudiante está activo
    
    def to_dict(self):
        """
        Método para convertir el objeto Estudiante a un diccionario.
        Esto es útil para serializar el objeto a JSON.
        """
        return {
            'id': self.id,
            'matricula': self.matricula,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'nombre_completo': f"{self.nombre} {self.apellido}",
            'email': self.email,
            'carrera': self.carrera,
            'semestre': self.semestre,
            'fecha_registro': self.fecha_registro.isoformat(),
            'activo': self.activo
        }
    
    def __repr__(self):
        """
        Método para representar el objeto Estudiante como una cadena.
        Esto es útil para depuración y logging.
        """
        return f"<Estudiante {self.matricula} - {self.nombre} {self.apellido}>"