from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user
from app.models.prestador import Prestador
from werkzeug.security import check_password_hash
from app.models.visita_prestador import VisitaPrestador

bp = Blueprint('prestador', __name__)

@bp.route('/')
def dashboard():
    return render_template('prestador/dashboard.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        prestador = Prestador.query.filter_by(email=email).first()
        if prestador and check_password_hash(prestador.password_hash, password):
            login_user(prestador)
            flash('Ingreso exitoso', 'success')
            return redirect(url_for('prestador.mis_visitas'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    return render_template('prestador/login.html')

@bp.route('/mis-visitas')
@login_required
def mis_visitas():
    visitas = VisitaPrestador.query.filter_by(prestador_id=current_user.id).all()
    return render_template('prestador/mis_visitas.html', visitas=visitas)

@bp.route('/perfil')
def perfil():
    return "<h1>Mi Perfil</h1><p>Actualizar datos personales</p>"

@bp.route('/exportar')
def exportar():
    return "<h1>Exportar Datos</h1><p>Descargar mis visitas en PDF/Excel</p>"