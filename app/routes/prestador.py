from flask import Blueprint, render_template

bp = Blueprint('prestador', __name__)

@bp.route('/')
def dashboard():
    return render_template('prestador/dashboard.html')

@bp.route('/login')
def login():
    return "<h1>Login Prestador</h1><p>Formulario de login para prestadores</p>"

@bp.route('/visitas')
def visitas():
    return "<h1>Mis Visitas</h1><p>Lista de todas mis visitas confirmadas</p>"

@bp.route('/perfil')
def perfil():
    return "<h1>Mi Perfil</h1><p>Actualizar datos personales</p>"

@bp.route('/exportar')
def exportar():
    return "<h1>Exportar Datos</h1><p>Descargar mis visitas en PDF/Excel</p>"