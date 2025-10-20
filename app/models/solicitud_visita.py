from app import db
import json
from datetime import datetime

class SolicitudVisita(db.Model):
    """Solicitudes de visitas enviadas por instituciones educativas"""
    
    id = db.Column(db.Integer, primary_key=True)
    
    # DATOS DE LA INSTITUCIÓN
    nombre_institucion = db.Column(db.String(150), nullable=False)
    tipo_institucion = db.Column(db.String(50))
    direccion = db.Column(db.String(200))
    localidad = db.Column(db.String(100))
    
    # CONTACTO RESPONSABLE
    responsable_nombre = db.Column(db.String(100), nullable=False)
    responsable_cargo = db.Column(db.String(100))
    responsable_email = db.Column(db.String(120), nullable=False)
    responsable_telefono = db.Column(db.String(30), nullable=False)
    
    # DETALLES DE LA VISITA SOLICITADA
    prestadores_solicitados = db.Column(db.Text)  # JSON con lista de prestadores seleccionados
    
    # FILTROS / METADATOS
    origen_institucion = db.Column(db.String(20), nullable=False)
    nivel_solicitud = db.Column(db.String(20), nullable=False)
    
    fecha_solicitada = db.Column(db.Date, nullable=False)
    horario_preferido = db.Column(db.String(50))
    
    cantidad_alumnos = db.Column(db.Integer, nullable=False)
    cantidad_docentes = db.Column(db.Integer, default=0)
    edad_promedio = db.Column(db.String(50))
    nivel_educativo = db.Column(db.String(50))
    
    observaciones = db.Column(db.Text)
    necesidades_especiales = db.Column(db.Text)
    
    estado = db.Column(db.String(20), default='PENDIENTE')
    fecha_respuesta = db.Column(db.DateTime)
    motivo_rechazo = db.Column(db.Text)
    
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    ip_origen = db.Column(db.String(45))
    
    def __repr__(self):
        return f'<SolicitudVisita {self.nombre_institucion} - {self.fecha_solicitud}>'
    
    # MÉTODOS PARA MANEJAR JSON DE PRESTADORES
    def get_prestadores_seleccionados(self):
        try:
            return json.loads(self.prestadores_solicitados) if self.prestadores_solicitados else []
        except Exception:
            return []
    
    def set_prestadores_seleccionados(self, lista_prestadores):
        self.prestadores_solicitados = json.dumps(lista_prestadores)
    
    def get_total_visitantes(self):
        return self.cantidad_alumnos + (self.cantidad_docentes or 0)
    
    def get_estado_color(self):
        colores = {
            'PENDIENTE': 'warning',
            'CONFIRMADA': 'success', 
            'RECHAZADA': 'danger',
            'FINALIZADA': 'secondary'
        }
        return colores.get(self.estado, 'secondary')
    
    def puede_ser_confirmada(self):
        return self.estado == 'PENDIENTE'
    
    def confirmar_con_horarios(self, horarios_prestadores, admin_id=None, confirm=False):
        from app import db
        from app.models.visita_prestador import VisitaPrestador
        from app.models.prestador import Prestador
        from datetime import datetime as _dt

        if confirm and not self.puede_ser_confirmada():
            return False

        if not horarios_prestadores:
            return False

        def _parse_time(t):
            if not t:
                return None
            for fmt in ('%H:%M', '%H:%M:%S'):
                try:
                    return _dt.strptime(t.strip(), fmt).time()
                except Exception:
                    continue
            return None

        try:
            if confirm:
                self.estado = 'CONFIRMADA'
                self.fecha_respuesta = _dt.utcnow()
                db.session.add(self)

            for h in horarios_prestadores:
                nombre = h.get('prestador_nombre')
                if not nombre:
                    continue

                prestador = Prestador.query.filter_by(razon_social=nombre).first()
                if not prestador:
                    continue

                hora_inicio = _parse_time(h.get('hora_inicio'))
                hora_fin = _parse_time(h.get('hora_fin'))

                if not hora_inicio:
                    continue

                existente = VisitaPrestador.query.filter_by(solicitud_id=self.id, prestador_id=prestador.id).first()
                if existente:
                    existente.hora_inicio = hora_inicio
                    existente.hora_fin = hora_fin
                    existente.observaciones_prestador = h.get('observaciones')
                    existente.asignado_por_admin_id = admin_id
                    db.session.add(existente)
                else:
                    visita = VisitaPrestador(
                        solicitud_id=self.id,
                        prestador_id=prestador.id,
                        fecha_confirmada=(self.fecha_solicitada if getattr(self,'fecha_solicitada',None) else _dt.utcnow().date()),
                        hora_inicio=hora_inicio,
                        hora_fin=hora_fin,
                        observaciones_prestador=h.get('observaciones'),
                        asignado_por_admin_id=admin_id
                    )
                    db.session.add(visita)

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    def rechazar(self, motivo, admin_id=None):
        """Rechaza la solicitud con motivo"""
        if self.puede_ser_confirmada():
            self.estado = 'RECHAZADA'
            self.motivo_rechazo = motivo
            self.fecha_respuesta = datetime.utcnow()
            return True
        return False
    
    @staticmethod
    def get_solicitudes_por_filtro(origen=None, nivel=None, estado=None):
        """Filtra solicitudes para el panel admin"""
        query = SolicitudVisita.query
        if origen:
            query = query.filter_by(origen_institucion=origen)
        if nivel:
            query = query.filter_by(nivel_solicitud=nivel)
        if estado:
            query = query.filter_by(estado=estado)
        return query.order_by(SolicitudVisita.fecha_solicitud.desc()).all()