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
    return "<h1>Solicitudes Pendientes</h1><p>Lista de solicitudes por confirmar</p>"

@bp.route('/prestadores')
def prestadores():
    return "<h1>Gestión Prestadores</h1><p>CRUD de prestadores y empresas</p>"