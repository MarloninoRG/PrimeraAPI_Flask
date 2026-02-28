from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.calificacion import Calificacion
from app.models.estudiante import Estudiante
from sqlalchemy import func

cal_bp = Blueprint('calificaciones', __name__, url_prefix='/cal')


@cal_bp.route('/estudiantes/<int:estudiante_id>/kardex', methods=['GET'])
def obtener_kardex(estudiante_id):
    """
    Obtener el kardex completo de un estudiante
    ---
    tags:
      - Calificaciones
    parameters:
      - in: path
        name: estudiante_id
        type: integer
        required: true
        description: ID del estudiante
        example: 1
    responses:
      200:
        description: Kardex obtenido exitosamente
        schema:
          type: object
          properties:
            estudiante_id:
              type: integer
              example: 1
            nombre_estudiante:
              type: string
              example: "Juan"
            kardex:
              type: array
              items:
                type: object
                properties:
                  materia_id:
                    type: integer
                    example: 1
                  calificacion:
                    type: number
                    example: 85.50
                  periodo:
                    type: string
                    example: "2024-1"
                  fecha_evaluacion:
                    type: string
                    example: "2024-06-15"
            promedio:
              type: number
              example: 85.50
            materias_aprobadas:
              type: integer
              example: 3
      404:
        description: Estudiante no encontrado o sin calificaciones
    """
    estudiante = Estudiante.query.get(estudiante_id)
    if not estudiante:
        return jsonify({'error': 'Estudiante no encontrado'}), 404

    calificaciones = Calificacion.query.filter_by(estudiante_id=estudiante_id).all()

    if not calificaciones:
        return jsonify({'error': 'No se encontraron calificaciones para este estudiante'}), 404

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
    Registrar una nueva calificación
    ---
    tags:
      - Calificaciones
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - estudiante_id
            - materia_id
            - calificacion
            - periodo
          properties:
            estudiante_id:
              type: integer
              example: 1
            materia_id:
              type: integer
              example: 1
            calificacion:
              type: number
              example: 85.50
            periodo:
              type: string
              example: "2024-1"
            fecha_evaluacion:
              type: string
              example: "2024-06-15"
              description: Opcional, si no se proporciona se usará la fecha actual
    responses:
      201:
        description: Calificación registrada exitosamente
      400:
        description: Datos inválidos o faltantes
      404:
        description: Estudiante no encontrado
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos.'}), 400

    required_fields = ['estudiante_id', 'materia_id', 'calificacion', 'periodo']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es obligatorio.'}), 400

    estudiante = Estudiante.query.get(data['estudiante_id'])
    if not estudiante:
        return jsonify({'error': 'Estudiante no encontrado.'}), 404

    nueva_calificacion = Calificacion(
        estudiante_id=data['estudiante_id'],
        materia_id=data['materia_id'],
        calificacion=data['calificacion'],
        periodo=data['periodo'],
        fecha_evaluacion=data.get('fecha_evaluacion')
    )

    db.session.add(nueva_calificacion)
    db.session.commit()

    return jsonify(nueva_calificacion.to_dict()), 201