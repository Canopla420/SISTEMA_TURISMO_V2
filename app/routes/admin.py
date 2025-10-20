from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.models.solicitud_visita import SolicitudVisita
from app import db
from app.models.prestador import Prestador
from app.models.visita_prestador import VisitaPrestador
from datetime import datetime
from werkzeug.security import generate_password_hash
import json


bp = Blueprint('admin', __name__)

@bp.route('/')
def dashboard():
    """Dashboard principal del administrador"""
    # Estadísticas básicas
    total_solicitudes = SolicitudVisita.query.count()
    pendientes = SolicitudVisita.query.filter_by(estado='PENDIENTE').count()
    aprobadas = SolicitudVisita.query.filter_by(estado='CONFIRMADA').count()
    rechazadas = SolicitudVisita.query.filter_by(estado='RECHAZADA').count()
    
    return render_template('admin/dashboard.html', 
                         total=total_solicitudes,
                         pendientes=pendientes,
                         aprobadas=aprobadas,
                         rechazadas=rechazadas)



@bp.route('/login')
def login():
    """Página de login para administradores"""
    return "<h1>Login Admin</h1><p>Formulario de login para administradores</p>"



@bp.route('/solicitudes')
def solicitudes():
    """Lista todas las solicitudes de visitas"""
    solicitudes = SolicitudVisita.query.order_by(SolicitudVisita.fecha_solicitud.desc()).all()
    for solicitud in solicitudes:
        solicitud.lugares = json.loads(solicitud.prestadores_solicitados) if solicitud.prestadores_solicitados else []
    return render_template('admin/solicitudes.html', solicitudes=solicitudes)



@bp.route('/solicitud/<int:id>')
def ver_solicitud(id):
    solicitud = SolicitudVisita.query.get_or_404(id)
    # obtener lista de prestadores (intenta método del modelo o parsear JSON)
    try:
        seleccionados = solicitud.get_prestadores_seleccionados()
    except Exception:
        seleccionados = json.loads(solicitud.prestadores_solicitados or '[]')
    visitas = VisitaPrestador.query.filter_by(solicitud_id=id).order_by(VisitaPrestador.hora_inicio).all()
    return render_template('admin/solicitud_detalle.html',
                           solicitud=solicitud,
                           seleccionados=seleccionados,
                           visitas=visitas)


@bp.route('/solicitud/<int:id>/aprobar', methods=['POST'])
def aprobar_solicitud(id):
    """Marcar solicitud como CONFIRMADA (no crear visitas)"""
    try:
        solicitud = SolicitudVisita.query.get_or_404(id)
        solicitud.estado = 'CONFIRMADA'
        solicitud.fecha_respuesta = datetime.utcnow()
        db.session.add(solicitud)
        db.session.commit()
        flash('✅ Solicitud marcada como CONFIRMADA', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al aprobar solicitud: {e}', 'danger')
    return redirect(url_for('admin.ver_solicitud', id=id))


@bp.route('/solicitud/<int:id>/rechazar', methods=['POST'])
def rechazar_solicitud(id):
    """Rechazar una solicitud"""
    try:
        solicitud = SolicitudVisita.query.get_or_404(id)
        motivo = request.form.get('motivo', '').strip()
        
        if not motivo:
            flash('❌ Debe indicar un motivo para rechazar la solicitud', 'error')
            return redirect(url_for('admin.ver_solicitud', id=id))
        
        solicitud.estado = 'RECHAZADA'
        solicitud.fecha_respuesta = datetime.now()
        solicitud.motivo_rechazo = motivo
        db.session.commit()
        flash('⚠️ Solicitud rechazada', 'warning')
    except Exception as e:
        flash(f'❌ Error al rechazar solicitud: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.ver_solicitud', id=id))



@bp.route('/solicitudes/<int:id>/horarios')
def asignar_horarios(id):
    solicitud = SolicitudVisita.query.get_or_404(id)

    # lista de prestadores seleccionados guardada en la solicitud (JSON)
    try:
        seleccionados = solicitud.get_prestadores_seleccionados()
    except Exception:
        seleccionados = json.loads(solicitud.prestadores_solicitados or '[]')

    # obtener prestadores "disponibles" — intentamos filtrar por tipo de institución si existe el campo
    query = Prestador.query.filter_by(activo=True)
    if getattr(solicitud, 'tipo_institucion', None) and hasattr(Prestador, 'tipo_institucion'):
        query = query.filter_by(tipo_institucion=solicitud.tipo_institucion)
    disponibles = query.order_by(Prestador.razon_social).all()

    return render_template('admin/asignar_horarios.html',
                           solicitud=solicitud,
                           seleccionados=seleccionados,
                           disponibles=disponibles)


@bp.route('/solicitudes/<int:id>/horarios', methods=['POST'])
def guardar_horarios(id):
    solicitud = SolicitudVisita.query.get_or_404(id)

    seleccionados = request.form.getlist('prestadores[]')

    horarios_prestadores = []
    faltantes_confirm = []

    confirm_all = bool(request.form.get('confirm_all'))
    for nombre in seleccionados:
        inicio = request.form.get(f'{nombre}_inicio')
        fin = request.form.get(f'{nombre}_fin')
        grupo = request.form.get(f'{nombre}_grupo') or 1
        obs = request.form.get(f'{nombre}_obs')

        if inicio or fin or obs:
            horarios_prestadores.append({
                'prestador_nombre': nombre,
                'hora_inicio': inicio,
                'hora_fin': fin,
                'grupo': grupo,
                'observaciones': obs
            })

        if confirm_all and (not inicio):
            faltantes_confirm.append(nombre)

    if confirm_all and faltantes_confirm:
        flash('Falta hora de inicio para: ' + ', '.join(faltantes_confirm), 'danger')
        return redirect(url_for('admin.asignar_horarios', id=id))

    if not horarios_prestadores and not seleccionados:
        flash('No se seleccionaron prestadores.', 'warning')
        return redirect(url_for('admin.asignar_horarios', id=id))

    try:
        solicitud.prestadores_solicitados = json.dumps(seleccionados)
        db.session.add(solicitud)
        db.session.commit()

        ok = solicitud.confirmar_con_horarios(horarios_prestadores,
                                             admin_id=(current_user.id if hasattr(current_user,'id') else None),
                                             confirm=confirm_all)
        if ok:
            msg = 'Horarios procesados.'
            if confirm_all:
                msg += ' Solicitud confirmada y visitas creadas.'
            flash(msg, 'success')
        else:
            flash('No se pudieron crear las visitas. Revisa los datos.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al asignar horarios: {e}', 'danger')

    return redirect(url_for('admin.ver_solicitud', id=id))



@bp.route('/solicitud/<int:id>/eliminar', methods=['POST'])
def eliminar_solicitud(id):
    """Eliminar una solicitud y sus visitas asociadas (asegurarse permisos/CSRF desde plantilla)"""
    # opcional: control de permisos (ej. current_user.is_admin)
    # if not getattr(current_user, 'is_admin', False):
    #     flash('No autorizado', 'danger')
    #     return redirect(url_for('admin.ver_solicitud', id=id))

    solicitud = SolicitudVisita.query.get_or_404(id)
    nombre_institucion = solicitud.nombre_institucion
    try:
        # borrado en bloque de las visitas asociadas (más eficiente)
        VisitaPrestador.query.filter_by(solicitud_id=id).delete(synchronize_session=False)
        db.session.delete(solicitud)
        db.session.commit()
        flash(f'🗑️ Solicitud #{id} de \"{nombre_institucion}\" eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        # loguear el error si querés: app.logger.exception(e)
        flash(f'❌ Error al eliminar solicitud: {e}', 'danger')
    return redirect(url_for('admin.solicitudes'))


@bp.route('/visita/<int:id>/eliminar', methods=['POST'])
def eliminar_visita(id):
    """Eliminar una VisitaPrestador y volver al detalle de la solicitud"""
    visita = VisitaPrestador.query.get_or_404(id)
    try:
        solicitud_id = visita.solicitud_id
        db.session.delete(visita)
        db.session.commit()
        flash('Visita eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar visita: {e}', 'danger')
        print('Error eliminar_visita:', e)
    return redirect(request.referrer or url_for('admin.ver_solicitud', id=solicitud_id))


@bp.route('/visita/<int:id>/editar', methods=['POST'])
def editar_visita(id):
    visita = VisitaPrestador.query.get_or_404(id)
    hora_inicio = request.form.get('hora_inicio')
    hora_fin = request.form.get('hora_fin')
    obs = request.form.get('obs')

    try:
        visita.hora_inicio = datetime.strptime(hora_inicio, '%H:%M').time() if hora_inicio else None
        visita.hora_fin = datetime.strptime(hora_fin, '%H:%M').time() if hora_fin else None
    except ValueError:
        flash('Formato de hora inválido. Usa HH:MM.', 'danger')
        return redirect(url_for('admin.ver_solicitud', id=visita.solicitud_id))

    visita.observaciones_prestador = obs
    try:
        db.session.add(visita)
        db.session.commit()
        flash('Horario de la visita actualizado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar visita: {e}', 'danger')

    return redirect(url_for('admin.ver_solicitud', id=visita.solicitud_id))


@bp.route('/prestadores')
def prestadores():
    """Lista todos los prestadores de servicios turísticos"""
    prestadores = Prestador.query.filter_by(activo=True).order_by(Prestador.razon_social).all()
    return render_template('admin/prestadores.html', prestadores=prestadores)



@bp.route('/prestadores/nuevo')
def nuevo_prestador():
    """Formulario para crear un nuevo prestador"""
    return render_template('admin/prestador_form.html', prestador=None, accion='Crear')


@bp.route('/solicitudes/<int:id>/prestador/asignar', methods=['POST'])
def asignar_prestador(id):
    solicitud = SolicitudVisita.query.get_or_404(id)
    prestador_nombre = request.form.get('prestador_nombre')
    hora_inicio = request.form.get('hora_inicio')
    hora_fin = request.form.get('hora_fin')
    obs = request.form.get('obs')

    if not (prestador_nombre and hora_inicio and hora_fin):
        flash('Faltan datos para asignar este prestador.', 'danger')
        return redirect(url_for('admin.asignar_horarios', id=id))

    prestador = Prestador.query.filter_by(razon_social=prestador_nombre).first()
    if not prestador:
        flash('Prestador no encontrado.', 'danger')
        return redirect(url_for('admin.asignar_horarios', id=id))

    try:
        existente = VisitaPrestador.query.filter_by(solicitud_id=solicitud.id, prestador_id=prestador.id).first()
        if existente:
            existente.hora_inicio = hora_inicio
            existente.hora_fin = hora_fin
            existente.observaciones_prestador = obs
            db.session.add(existente)
        else:
            visita = VisitaPrestador(
                solicitud_id=solicitud.id,
                prestador_id=prestador.id,
                fecha_confirmada=(solicitud.fecha_solicitada if getattr(solicitud,'fecha_solicitada',None) else datetime.utcnow().date()),
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                observaciones_prestador=obs,
                asignado_por_admin_id=(current_user.id if hasattr(current_user,'id') else None)
            )
            db.session.add(visita)
        db.session.commit()
        flash(f'Horario asignado a {prestador_nombre}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al asignar prestador: {e}', 'danger')

    return redirect(url_for('admin.asignar_horarios', id=id))


@bp.route('/prestadores/crear', methods=['POST'])
def crear_prestador():
    """Crear un nuevo prestador"""
    try:
        prestador = Prestador(
            razon_social=request.form.get('razon_social'),
            cuit=request.form.get('cuit'),
            titular_nombre=request.form.get('titular_nombre'),
            direccion=request.form.get('direccion'),
            contacto_responsable=request.form.get('contacto_responsable'),
            telefono=request.form.get('telefono'),
            email=request.form.get('email'),
            password_hash=generate_password_hash(request.form.get('password')),
            descripcion_visita=request.form.get('descripcion_visita'),
            tiene_material_digital=bool(request.form.get('tiene_material_digital')),
            meses_disponibles=request.form.get('meses_disponibles'),
            dias_disponibles=request.form.get('dias_disponibles'),
            horarios_sugeridos=request.form.get('horarios_sugeridos'),
            duracion_visita=request.form.get('duracion_visita'),
            visitantes_maximo=int(request.form.get('visitantes_maximo', 0)) or None,
            edades_recomendadas=request.form.get('edades_recomendadas'),
            acceso_movilidad_reducida=request.form.get('acceso_movilidad_reducida'),
            tipo_reserva=request.form.get('tipo_reserva'),
            costo_referencia=request.form.get('costo_referencia')
        )
        
        db.session.add(prestador)
        db.session.commit()
        
        flash(f'✅ Prestador "{prestador.razon_social}" creado correctamente', 'success')
        return redirect(url_for('admin.prestadores'))
        
    except Exception as e:
        flash(f'❌ Error al crear prestador: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('admin.nuevo_prestador'))



@bp.route('/prestadores/<int:id>')
def ver_prestador(id):
    """Ver detalles de un prestador"""
    prestador = Prestador.query.get_or_404(id)
    return render_template('admin/prestador_detalle.html', prestador=prestador)



@bp.route('/prestadores/<int:id>/editar', methods=['GET','POST'])
def editar_prestador(id):
    from app.models.prestador import Prestador
    prestador = Prestador.query.get_or_404(id)
    if request.method == 'POST':
        prestador.razon_social = request.form.get('razon_social')
        prestador.contacto_responsable = request.form.get('contacto_responsable')
        prestador.telefono = request.form.get('telefono')
        prestador.email = request.form.get('email')
        prestador.direccion = request.form.get('direccion')
        db.session.add(prestador)
        db.session.commit()
        flash('Prestador actualizado.', 'success')
        return redirect(url_for('admin.prestadores'))
    return render_template('admin/prestador_form.html', prestador=prestador, action_url=url_for('admin.editar_prestador', id=prestador.id))



@bp.route('/prestadores/<int:id>/actualizar', methods=['POST'])
def actualizar_prestador(id):
    """Actualizar un prestador existente"""
    try:
        prestador = Prestador.query.get_or_404(id)
        
        prestador.razon_social = request.form.get('razon_social')
        prestador.cuit = request.form.get('cuit')
        prestador.titular_nombre = request.form.get('titular_nombre')
        prestador.direccion = request.form.get('direccion')
        prestador.contacto_responsable = request.form.get('contacto_responsable')
        prestador.telefono = request.form.get('telefono')
        prestador.email = request.form.get('email')
        prestador.descripcion_visita = request.form.get('descripcion_visita')
        prestador.tiene_material_digital = bool(request.form.get('tiene_material_digital'))
        prestador.meses_disponibles = request.form.get('meses_disponibles')
        prestador.dias_disponibles = request.form.get('dias_disponibles')
        prestador.horarios_sugeridos = request.form.get('horarios_sugeridos')
        prestador.duracion_visita = request.form.get('duracion_visita')
        prestador.visitantes_maximo = int(request.form.get('visitantes_maximo', 0)) or None
        prestador.edades_recomendadas = request.form.get('edades_recomendadas')
        prestador.acceso_movilidad_reducida = request.form.get('acceso_movilidad_reducida')
        prestador.tipo_reserva = request.form.get('tipo_reserva')
        prestador.costo_referencia = request.form.get('costo_referencia')
        
        db.session.commit()
        flash(f'✅ Prestador "{prestador.razon_social}" actualizado correctamente', 'success')
        return redirect(url_for('admin.ver_prestador', id=id))
        
    except Exception as e:
        flash(f'❌ Error al actualizar prestador: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('admin.editar_prestador', id=id))



@bp.route('/prestadores/<int:id>/eliminar', methods=['POST'])
def eliminar_prestador(id):
    """Eliminar (desactivar) un prestador"""
    try:
        prestador = Prestador.query.get_or_404(id)
        prestador.activo = False
        db.session.commit()
        
        flash(f'🗑️ Prestador "{prestador.razon_social}" eliminado correctamente', 'success')
        
    except Exception as e:
        flash(f'❌ Error al eliminar prestador: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.prestadores'))



@bp.route('/reportes')
def reportes():
    """Reportes y estadísticas"""
    return "<h1>📊 Reportes</h1><p>Estadísticas y reportes del sistema</p>"



@bp.route('/configuracion')
def configuracion():
    """Configuración del sistema"""
    return "<h1>⚙️ Configuración</h1><p>Configuración del sistema de turismo</p>"