from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.solicitud_visita import SolicitudVisita
from app import db
from app.models.prestador import Prestador
from datetime import datetime

bp = Blueprint('admin', __name__)

@bp.route('/')
def dashboard():
    """Dashboard principal del administrador"""
    # Estadísticas básicas
    total_solicitudes = SolicitudVisita.query.count()
    pendientes = SolicitudVisita.query.filter_by(estado='PENDIENTE').count()
    aprobadas = SolicitudVisita.query.filter_by(estado='APROBADA').count()
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
    return render_template('admin/solicitudes.html', solicitudes=solicitudes)

@bp.route('/solicitud/<int:id>')
def ver_solicitud(id):
    """Ver detalles de una solicitud específica"""
    solicitud = SolicitudVisita.query.get_or_404(id)
    return render_template('admin/solicitud_detalle.html', solicitud=solicitud)

@bp.route('/solicitud/<int:id>/aprobar', methods=['POST'])
def aprobar_solicitud(id):
    """Aprobar una solicitud"""
    try:
        solicitud = SolicitudVisita.query.get_or_404(id)
        solicitud.estado = 'APROBADA'
        solicitud.fecha_respuesta = datetime.now()
        db.session.commit()
        flash('✅ Solicitud aprobada correctamente', 'success')
    except Exception as e:
        flash(f'❌ Error al aprobar solicitud: {str(e)}', 'error')
        db.session.rollback()
    
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
    """Formulario para asignar horarios a una solicitud específica"""
    solicitud = SolicitudVisita.query.get_or_404(id)
    return render_template('admin/asignar_horarios.html', solicitud=solicitud)

@bp.route('/solicitudes/<int:id>/horarios', methods=['POST'])
def guardar_horarios(id):
    """Guardar horarios asignados a una solicitud"""
    try:
        solicitud = SolicitudVisita.query.get_or_404(id)
        
        # Aquí procesarías los horarios del formulario
        horario_inicio = request.form.get('horario_inicio')
        horario_fin = request.form.get('horario_fin')
        prestadores_asignados = request.form.getlist('prestadores')
        
        # Actualizar solicitud con horarios (esto depende de tu modelo)
        solicitud.horario_preferido = f"{horario_inicio} - {horario_fin}"
        solicitud.estado = 'CONFIRMADA'
        
        db.session.commit()
        flash('⏰ Horarios asignados correctamente', 'success')
        
    except Exception as e:
        flash(f'❌ Error al asignar horarios: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.ver_solicitud', id=id))

@bp.route('/solicitud/<int:id>/eliminar', methods=['POST'])
def eliminar_solicitud(id):
    """Eliminar una solicitud (solo administradores)"""
    try:
        solicitud = SolicitudVisita.query.get_or_404(id)
        
        # Guardar datos para el mensaje de confirmación
        nombre_institucion = solicitud.nombre_institucion
        solicitud_id = solicitud.id
        
        # Eliminar de la base de datos
        db.session.delete(solicitud)
        db.session.commit()
        
        flash(f'🗑️ Solicitud #{solicitud_id} de "{nombre_institucion}" eliminada correctamente', 'success')
        
    except Exception as e:
        flash(f'❌ Error al eliminar solicitud: {str(e)}', 'error')
        db.session.rollback()
    
    # Redirigir a la lista de solicitudes
    return redirect(url_for('admin.solicitudes'))

@bp.route('/prestadores')
def prestadores():
    """Lista todos los prestadores de servicios turísticos"""
    prestadores = Prestador.query.filter_by(activo=True).order_by(Prestador.razon_social).all()
    return render_template('admin/prestadores.html', prestadores=prestadores)

@bp.route('/prestadores/nuevo')
def nuevo_prestador():
    """Formulario para crear un nuevo prestador"""
    return render_template('admin/prestador_form.html', prestador=None, accion='Crear')

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

@bp.route('/prestadores/<int:id>/editar')
def editar_prestador(id):
    """Formulario para editar un prestador"""
    prestador = Prestador.query.get_or_404(id)
    return render_template('admin/prestador_form.html', prestador=prestador, accion='Editar')

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