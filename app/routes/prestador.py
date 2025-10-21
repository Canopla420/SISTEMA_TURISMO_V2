from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, login_required, current_user
from app.models.prestador import Prestador
from werkzeug.security import check_password_hash
from app.models.visita_prestador import VisitaPrestador
from sqlalchemy.orm import joinedload
from app import db
from datetime import datetime
from app.decorators import prestador_required

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

@bp.route('/mis-visitas', methods=['GET'])
@login_required
@prestador_required
def mis_visitas():
    prestador_id = getattr(current_user, 'prestador_id', None) or current_user.id
    visitas = VisitaPrestador.query.options(
        joinedload(VisitaPrestador.solicitud)
    ).filter_by(prestador_id=prestador_id).order_by(VisitaPrestador.fecha_confirmada.desc()).all()
    return render_template('prestador/mis_visitas.html', visitas=visitas)

@bp.route('/visita/<int:id>/realizada', methods=['POST'])
@login_required
def marcar_realizada(id):
    visita = VisitaPrestador.query.get_or_404(id)
    user_prestador_id = getattr(current_user, 'prestador_id', None) or current_user.id
    if visita.prestador_id != user_prestador_id:
        abort(403)
    visita.estado = 'REALIZADA'
    if hasattr(visita, 'fecha_realizada'):
        visita.fecha_realizada = datetime.utcnow()
    db.session.add(visita)
    db.session.commit()
    flash('Visita marcada como realizada.', 'success')
    return redirect(url_for('prestador.mis_visitas'))

@bp.route('/perfil')
def perfil():
    return "<h1>Mi Perfil</h1><p>Actualizar datos personales</p>"

@bp.route('/exportar')
def exportar():
    return "<h1>Exportar Datos</h1><p>Descargar mis visitas en PDF/Excel</p>"