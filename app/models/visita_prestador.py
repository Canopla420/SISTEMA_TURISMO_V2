from app import db
from datetime import datetime

class VisitaPrestador(db.Model):
    """Visitas confirmadas y asignadas a prestadores con horarios específicos"""
    
    id = db.Column(db.Integer, primary_key=True)
    
    # RELACIONES
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitud_visita.id'), nullable=False)
    solicitud = db.relationship('SolicitudVisita', backref=db.backref('visitas_asignadas', lazy=True))
    
    prestador_id = db.Column(db.Integer, db.ForeignKey('prestador.id'), nullable=False)
    prestador = db.relationship('Prestador', backref=db.backref('visitas_confirmadas', lazy=True))
    
    # HORARIOS ESPECÍFICOS (asignados por admin)
    fecha_confirmada = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time)
    grupo = db.Column(db.Integer, default=1)  # Grupo 1 o Grupo 2 (del formulario)
    duracion_estimada = db.Column(db.Integer)  # En minutos
    
    # DETALLES ESPECÍFICOS DE LA VISITA
    guia_asignado = db.Column(db.String(100))  # Nombre del guía específico
    observaciones_prestador = db.Column(db.Text)  # Notas internas del prestador
    sala_o_area = db.Column(db.String(100))  # "Sala principal", "Área externa"
    
    # ESTADO DE LA VISITA CONFIRMADA
    estado_visita = db.Column(db.String(20), default='PROGRAMADA')  # PROGRAMADA, EN_CURSO, COMPLETADA, CANCELADA
    
    # METADATOS
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    asignado_por_admin_id = db.Column(db.Integer, db.ForeignKey('usuario_admin.id'))
    asignado_por = db.relationship('UsuarioAdmin', backref='visitas_asignadas')
    
    # REGISTRO POST-VISITA
    fecha_realizacion = db.Column(db.DateTime)
    visitantes_reales = db.Column(db.Integer)  # Por si vinieron menos/más alumnos
    calificacion = db.Column(db.Integer)  # 1-5 estrellas (opcional)
    comentarios_finales = db.Column(db.Text)
    
    def __repr__(self):
        return f'<VisitaPrestador {self.solicitud.nombre_institucion} - {self.prestador.razon_social} - {self.fecha_confirmada}>'
    
    def get_horario_completo(self):
        """Retorna horario formateado: '10:00 - 11:30'"""
        if self.hora_fin:
            return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"
        return self.hora_inicio.strftime('%H:%M')
    
    def get_duracion_texto(self):
        """Retorna duración legible: '1 hora 30 minutos'"""
        if self.duracion_estimada:
            horas = self.duracion_estimada // 60
            minutos = self.duracion_estimada % 60
            if horas > 0:
                return f"{horas}h {minutos}min" if minutos > 0 else f"{horas}h"
            return f"{minutos}min"
        return "No especificada"
    
    def puede_ser_modificada(self):
        """Verifica si la visita puede ser reprogramada"""
        return self.estado_visita in ['PROGRAMADA']
    
    def marcar_completada(self, visitantes_reales=None, comentarios=None):
        """Marca la visita como completada"""
        self.estado_visita = 'COMPLETADA'
        self.fecha_realizacion = datetime.utcnow()
        if visitantes_reales:
            self.visitantes_reales = visitantes_reales
        if comentarios:
            self.comentarios_finales = comentarios
        
        # También actualizar la solicitud original si todas las visitas terminaron
        todas_completadas = all(
            v.estado_visita == 'COMPLETADA' 
            for v in self.solicitud.visitas_asignadas
        )
        if todas_completadas:
            self.solicitud.estado = 'FINALIZADA'
    
    def get_info_completa(self):
        """Retorna información completa para mostrar en panel prestador"""
        return {
            'fecha': self.fecha_confirmada,
            'horario': self.get_horario_completo(),
            'institucion': self.solicitud.nombre_institucion,
            'localidad': self.solicitud.localidad,
            'cantidad_alumnos': self.solicitud.cantidad_alumnos,
            'nivel': self.solicitud.nivel_educativo,
            'edad': self.solicitud.edad_promedio,  # ✅ AGREGAR ESTE
            'grupo': self.grupo,
            'contacto': self.solicitud.responsable_nombre,
            'telefono': self.solicitud.responsable_telefono,
            'estado': self.estado_visita,
            'observaciones': self.observaciones_prestador,
            'necesidades_especiales': self.solicitud.necesidades_especiales
        }
    
    def get_estado_color(self):
        """Retorna color CSS según el estado"""
        colores = {
            'PROGRAMADA': 'primary',
            'EN_CURSO': 'warning',
            'COMPLETADA': 'success',
            'CANCELADA': 'danger'
        }
        return colores.get(self.estado_visita, 'secondary')
    
    @staticmethod
    def get_visitas_por_prestador(prestador_id, fecha_desde=None, fecha_hasta=None):
        """Obtiene visitas de un prestador específico con filtros de fecha"""
        query = VisitaPrestador.query.filter_by(prestador_id=prestador_id)
        
        if fecha_desde:
            query = query.filter(VisitaPrestador.fecha_confirmada >= fecha_desde)
        if fecha_hasta:
            query = query.filter(VisitaPrestador.fecha_confirmada <= fecha_hasta)
            
        return query.order_by(VisitaPrestador.fecha_confirmada.asc(), VisitaPrestador.hora_inicio.asc()).all()
    
    @staticmethod
    def get_visitas_hoy(prestador_id):
        """Obtiene visitas de hoy para un prestador"""
        from datetime import date
        return VisitaPrestador.query.filter_by(
            prestador_id=prestador_id,
            fecha_confirmada=date.today()
        ).order_by(VisitaPrestador.hora_inicio.asc()).all()