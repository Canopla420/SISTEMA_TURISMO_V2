from app import db
from datetime import datetime
import json
from flask_login import UserMixin

class Prestador(db.Model, UserMixin):
    """Prestadores turísticos con datos completos para validación de solicitudes"""
    
    id = db.Column(db.Integer, primary_key=True)
    
    # DATOS BÁSICOS
    razon_social = db.Column(db.String(150), nullable=False)
    cuit = db.Column(db.String(13), unique=True)
    titular_nombre = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    contacto_responsable = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120))
    
    #Hash contraseña
    password_hash = db.Column(db.String(128))

    # DESCRIPCIÓN DEL SERVICIO
    descripcion_visita = db.Column(db.Text)
    tiene_material_digital = db.Column(db.Boolean, default=False)
    
    # DISPONIBILIDAD (para validar solicitudes)
    meses_disponibles = db.Column(db.String(200))  # ["Enero", "Febrero", ...]
    dias_disponibles = db.Column(db.String(100))   # ["Lunes", "Martes", ...]
    horarios_sugeridos = db.Column(db.String(50))  # mañana/tarde/ambos
    detalle_horarios = db.Column(db.Text)
    duracion_visita = db.Column(db.String(50))
    
    # CAPACIDADES (para validar cantidad de alumnos)
    visitantes_maximo = db.Column(db.Integer)
    recorridos_por_turno = db.Column(db.Integer, default=1)
    
    # RESTRICCIONES (para validar solicitudes)
    edades_recomendadas = db.Column(db.String(200))  # ["inicial", "primaria", ...]
    acceso_movilidad_reducida = db.Column(db.String(20))
    afectado_por_lluvia = db.Column(db.String(50))
    
    # SERVICIOS
    tiene_personal = db.Column(db.Boolean, default=True)
    tipo_reserva = db.Column(db.String(50))
    costo_referencia = db.Column(db.Text)
    
    # METADATOS
    activo = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), nullable=False, default='prestador')  # 'prestador' | 'admin'
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Prestador {self.razon_social}>'
    
    def puede_recibir_solicitud(self, solicitud):
        """Valida si el prestador puede atender una solicitud"""
        # TODO: Implementar validaciones en Commit 3
        return True
    
    def get_meses_disponibles(self):
        try:
            return json.loads(self.meses_disponibles) if self.meses_disponibles else []
        except:
            return []
    
    def get_edades_recomendadas(self):
        try:
            return json.loads(self.edades_recomendadas) if self.edades_recomendadas else []
        except:
            return []

    def is_admin(self):
        return (self.role or '') == 'admin'

    def is_prestador(self):
        return (self.role or '') == 'prestador'