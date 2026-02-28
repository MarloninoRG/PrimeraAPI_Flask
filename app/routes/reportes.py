from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func, extract
from datetime import datetime
from app.extensions import db
from app.models.orden import Orden
from app.models.producto import Producto
from app.models.detalle_orden import DetalleOrden

reportes_bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')

@reportes_bp.route("/ventas", methods=["GET"])
@jwt_required()
def reporte_ventas():
    """Genera un reporte de ventas del mes actual."""
    mes = request.args.get("mes", datetime.now().month, type=int)
    anio = request.args.get("anio", datetime.now().year, type=int)

    # Consulta con agregaciones SQL
    resultado = db.session.query(
        func.count(Orden.id).label("total_ordenes"),
        func.sum(Orden.total).label("ingresos_totales"),
        func.avg(Orden.total).label("ticket_promedio")
    ).filter(
        extract("month", Orden.fecha) == mes,
        extract("year", Orden.fecha) == anio
    ).first()

    # Top 5 productos más vendidos
    top_productos = db.session.query(
        Producto.nombre,
        func.sum(DetalleOrden.cantidad).label("unidades"),
        func.sum(DetalleOrden.cantidad * DetalleOrden.precio_unitario).label("revenue")
    ).join(DetalleOrden).group_by(
        Producto.nombre
    ).order_by(
        func.sum(DetalleOrden.cantidad).desc()
    ).limit(5).all()

    return jsonify({
        "periodo": f"{mes}/{anio}",
        "resumen": {
            "total_ordenes": resultado.total_ordenes or 0,
            "ingresos": float(resultado.ingresos_totales or 0),
            "ticket_promedio": float(resultado.ticket_promedio or 0)
        },
        "top_productos": [
            {
                "producto": p.nombre,
                "unidades": p.unidades,
                "revenue": float(p.revenue)
            }
            for p in top_productos
        ]
    }), 200