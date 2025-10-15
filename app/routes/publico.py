from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.solicitud_visita import SolicitudVisita
from app import db
from datetime import datetime

bp = Blueprint('publico', __name__)

@bp.route('/')
@bp.route('/solicitar-visita', methods=['GET', 'POST'])
def solicitar_visita():
    """Formulario público para solicitar visitas"""
    
    if request.method == 'POST':
        print("FORMULARIO RECIBIDO")  
        # Procesar formulario de solicitud de visita
        try:
            print("CREANDO SOLICITUD")  
            # Obtener datos del formulario
            solicitud = SolicitudVisita(
                # Datos institución
                nombre_institucion=request.form['nombre_institucion'],
                localidad=request.form['localidad'],
                responsable_nombre=request.form['director'],
                responsable_email=request.form.get('email_director'),
                responsable_telefono=request.form.get('telefono_director'),
                
                # CAMPOS REQUERIDOS QUE FALTABAN:
                origen_institucion='EXTERNA',
                nivel_solicitud='PRIMARIA',
                
                # Datos grupo
                nivel_educativo=request.form['nivel'],
                cantidad_alumnos=int(request.form['cantidad']),
                edad_promedio=request.form.get('edad'),
                
                # Discapacidad
                necesidades_especiales=request.form.get('detalle_discapacidad'),
                
                # Fecha
                fecha_solicitada=datetime.strptime(request.form['fecha_visita'], '%Y-%m-%d').date(),
                
                # Prestadores (NOMBRE CORRECTO)
                prestadores_solicitados=','.join(request.form.getlist('lugares')),
                
                # Observaciones
                observaciones=request.form.get('observaciones', ''),
                
                # Estado inicial
                estado='PENDIENTE',
                fecha_solicitud=datetime.now()
            )
            
            # Guardar en base de datos
            db.session.add(solicitud)
            db.session.commit()
            
            print("GUARDADO OK - REDIRIGIENDO")
            
            return redirect(url_for('publico.gracias'))
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            flash(f'Error al procesar solicitud: {str(e)}', 'error')
            return redirect(url_for('publico.solicitar_visita'))
    
    # Si es GET, mostrar formulario
    return render_template('publico/solicitar_visita.html')

@bp.route('/gracias')
def gracias():
    """Página de confirmación"""
    return render_template('publico/gracias.html')

@bp.route('/info')
def informacion():
    """Información sobre prestadores disponibles"""
    return "<h1>ℹ️ Información Turística</h1><p>Aquí iría información sobre los lugares disponibles para visitar</p>"