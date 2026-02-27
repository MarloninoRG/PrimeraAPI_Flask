from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.calificacion import Calificacion
from app.models.estudiante import Estudiante
from sqlalchemy import func

cal_bp = Blueprint('calificaciones', __name__, url_prefix='/cal')

@cal_bp.route('/estudiantes/<int:estudiante_id>/kardex', methods=['GET'])
def obtener_kardex(estudiante_id):
    """
    Obtiene el kardez completo de un estudiante
    Incluye todas las calificaciones, materias, periodos y fechas de evaluación
    """
    estudiante = Estudiante.query.get(estudiante_id)
    if not estudiante:
        return jsonify({'error': 'Estudiante no encontrado'}), 404
    
    calificaciones = Calificacion.query.filter_by(estudiante_id=estudiante_id).all()
    
    if not calificaciones:
        return jsonify({'error': 'No se encontraron calificaciones para este estudiante'}), 404
    
    # Calcular estadisticas 
    valores = [float(cal.calificacion) for cal in calificaciones]
    promedio = sum(valores) / len(valores) if valores else 0
    materias_aprobadas = sum(1 for cal in calificaciones if float(cal.calificacion) >= 60)
    
    kardex = []
    for cal in calificaciones:
        materia_info = {
            'materia_id': cal.materia_id,
            'calificacion': float(cal.calificacion),
            'periodo': cal.periodo,
            'fecha_evaluacion': cal.fecha_evaluacion.isoformat()
        }
        kardex.append(materia_info)
    
    return jsonify({
        'estudiante_id': estudiante_id,
        'nombre_estudiante': estudiante.nombre,
        'kardex': kardex,
        'promedio': promedio,
        'materias_aprobadas': materias_aprobadas
    })

@cal_bp.route('/', methods=['POST'])
def registrar_calificacion():
    """
    Registra una nueva calificación para un estudiante en una materia específica.
    Espera un JSON con los campos: estudiante_id, materia_id, calificacion, periodo, fecha_evaluacion
    """
    data = request.get_json()
    
    # Validar que se haya recibido un JSON válido
    if not data:
        return jsonify({'error': 'No se proporcionaron datos.'}), 400
    
    # Validar que se hayan proporcionado los campos necesarios
    required_fields = ['estudiante_id', 'materia_id', 'calificacion', 'periodo']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es obligatorio.'}), 400
    
    # Verificar que el estudiante exista
    estudiante = Estudiante.query.get(data['estudiante_id'])
    if not estudiante:
        return jsonify({'error': 'Estudiante no encontrado.'}), 404
    
    # Crear un nuevo objeto Calificacion con los datos proporcionados
    nueva_calificacion = Calificacion(
        estudiante_id=data['estudiante_id'],
        materia_id=data['materia_id'],
        calificacion=data['calificacion'],
        periodo=data['periodo'],
        fecha_evaluacion=data.get('fecha_evaluacion')  # Opcional, si no se proporciona se usará la fecha actual
    )
    
    # Agregar la nueva calificación a la sesión de la base de datos y guardar los cambios
    db.session.add(nueva_calificacion)
    db.session.commit()
    
    # Devolver una respuesta JSON con los datos de la nueva calificación y un código de estado 201 (Creado)
    return jsonify(nueva_calificacion.to_dict()), 201