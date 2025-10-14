from flask import Blueprint, render_template

bp = Blueprint('admin', __name__)

@bp.route('/')
def dashboard():
    return "<h1>Panel Administrativo</h1><p>Dashboard de la Dirección de Turismo</p>"

@bp.route('/login')
def login():
    return "<h1>Login Admin</h1><p>Formulario de login para administradores</p>"

@bp.route('/solicitudes')
def solicitudes():
    return render_template('admin/solicitudes.html') 

@bp.route('/solicitudes/<int:id>/horarios')
def asignar_horarios(id):
    """Formulario para asignar horarios a una solicitud específica"""
    # Por ahora usamos datos fijos, después conectamos con la base de datos
    return render_template('admin/asignar_horarios.html')

@bp.route('/prestadores')
def prestadores():
    return "<h1>Gestión Prestadores</h1><p>CRUD de prestadores y empresas</p>"