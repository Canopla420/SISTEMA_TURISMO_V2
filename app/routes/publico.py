from flask import Blueprint, render_template

bp = Blueprint('publico', __name__)

@bp.route('/')
@bp.route('/solicitar-visita')
def solicitar_visita():
    """Formulario público para solicitar visitas"""
    return render_template('publico/solicitar_visita.html')

@bp.route('/gracias')
def gracias():
    """Página de confirmación"""
    return """
    <div class="container mt-5">
        <div class="alert alert-success text-center">
            <h2>✅ Solicitud Enviada</h2>
            <p>Su solicitud fue recibida correctamente. Recibirá confirmación en 48-72 horas.</p>
            <a href="/publico/solicitar-visita" class="btn btn-primary">Nueva Solicitud</a>
        </div>
    </div>
    """

@bp.route('/info')
def informacion():
    """Información sobre prestadores disponibles"""
    return "<h1>ℹ️ Información Turística</h1><p>Aquí iría información sobre los lugares disponibles para visitar</p>"