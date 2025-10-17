from app import db
import json
from datetime import datetime

class SolicitudVisita(db.Model):
    """Solicitudes de visitas enviadas por instituciones educativas"""
    
    id = db.Column(db.Integer, primary_key=True)
    
    # DATOS DE LA INSTITUCIÓN
    nombre_institucion = db.Column(db.String(150), nullable=False)
    tipo_institucion = db.Column(db.String(50))  # "Jardín", "Primaria", "Secundaria", "Universidad"
    direccion = db.Column(db.String(200))
    localidad = db.Column(db.String(100))
    
    # CONTACTO RESPONSABLE
    responsable_nombre = db.Column(db.String(100), nullable=False)
    responsable_cargo = db.Column(db.String(100))  # "Directora", "Maestra", "Coordinador"
    responsable_email = db.Column(db.String(120), nullable=False)
    responsable_telefono = db.Column(db.String(30), nullable=False)
    
    # DETALLES DE LA VISITA SOLICITADA
    prestadores_solicitados = db.Column(db.Text)  # JSON con lista de prestadores seleccionados
    
    # AGREGAR ESTOS CAMPOS PARA FILTROS:
    origen_institucion = db.Column(db.String(20), nullable=False)  # 'ESPERANZA', 'EXTERNA'
    nivel_solicitud = db.Column(db.String(20), nullable=False)     # 'PRIMARIA', 'SECUNDARIA'
    
    fecha_solicitada = db.Column(db.Date, nullable=False)
    horario_preferido = db.Column(db.String(50))  # "Mañana", "Tarde", "9:00-11:00"
    
    # GRUPO DE VISITANTES
    cantidad_alumnos = db.Column(db.Integer, nullable=False)
    cantidad_docentes = db.Column(db.Integer, default=0)
    edad_promedio = db.Column(db.String(50))  # "5-6 años", "12-13 años"
    nivel_educativo = db.Column(db.String(50))  # "Inicial", "Primaria", "Secundaria"
    
    # OBSERVACIONES Y NECESIDADES ESPECIALES
    observaciones = db.Column(db.Text)
    necesidades_especiales = db.Column(db.Text)  # Movilidad reducida, alergias, etc.
    
    # ESTADO DE LA SOLICITUD
    estado = db.Column(db.String(20), default='PENDIENTE')  # PENDIENTE, CONFIRMADA, RECHAZADA, FINALIZADA
    fecha_respuesta = db.Column(db.DateTime)
    motivo_rechazo = db.Column(db.Text)
    
    # METADATOS
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    ip_origen = db.Column(db.String(45))  # Para auditoría
    
    def __repr__(self):
        return f'<SolicitudVisita {self.nombre_institucion} - {self.fecha_solicitud}>'
    
    # MÉTODOS PARA MANEJAR JSON DE PRESTADORES
    def get_prestadores_seleccionados(self):
        """Convierte JSON a lista de prestadores"""
        try:
            return json.loads(self.prestadores_solicitados) if self.prestadores_solicitados else []
        except:
            return []
    
    def set_prestadores_seleccionados(self, lista_prestadores):
        """Convierte lista a JSON para guardar en BD"""
        self.prestadores_solicitados = json.dumps(lista_prestadores)
    
    def get_total_visitantes(self):
        """Retorna total de personas (alumnos + docentes)"""
        return self.cantidad_alumnos + (self.cantidad_docentes or 0)
    
    def get_estado_color(self):
        """Retorna color CSS según el estado"""
        colores = {
            'PENDIENTE': 'warning',
            'CONFIRMADA': 'success', 
            'RECHAZADA': 'danger',
            'FINALIZADA': 'secondary'
        }
        return colores.get(self.estado, 'secondary')
    
    def puede_ser_confirmada(self):
        """Verifica si la solicitud puede ser confirmada"""
        return self.estado == 'PENDIENTE'
    
    def confirmar_con_horarios(self, horarios_prestadores, admin_id=None):
        """Confirma la solicitud Y crea las VisitaPrestador automáticamente"""
        from app.models.visita_prestador import VisitaPrestador
        from app.models.prestador import Prestador

        print("Entrando a confirmar_con_horarios")  # <-- Print 1

        if not self.puede_ser_confirmada():
            print("No puede ser confirmada")        # <-- Print 2
            return False
        
        try:
            print("Dentro del try, creando visitas")  # <-- Print 3

            # 1. Cambiar estado de la solicitud
            self.estado = 'CONFIRMADA'
            self.fecha_respuesta = datetime.utcnow()
            
            # 2. Crear VisitaPrestador para cada prestador con horarios
            for horario_data in horarios_prestadores:
                # horario_data = {
                #     'prestador_nombre': 'Museo de la Colonización',
                #     'hora_inicio': '10:00',
                #     'hora_fin': '11:00',
                #     'grupo': 1
                # }
                print("Creando visita para:", horario_data)

                prestador = Prestador.query.filter_by(
                    razon_social=horario_data['prestador_nombre']
                ).first()
            
        
                if prestador:
                    print("Datos visita:", {
                        "solicitud_id": self.id,
                        "prestador_id": prestador.id,
                        "fecha_confirmada": self.fecha_solicitada,
                        "hora_inicio": horario_data['hora_inicio'],
                        "hora_fin": horario_data.get('hora_fin'),
                        "grupo": horario_data.get('grupo', 1)
                    })
                    visita = VisitaPrestador()
                    visita.solicitud_id = self.id
                    visita.prestador_id = prestador.id
                    visita.fecha_confirmada = self.fecha_solicitada.date() if hasattr(self.fecha_solicitada, "date") else self.fecha_solicitada
                    visita.hora_inicio = datetime.strptime(horario_data['hora_inicio'], '%H:%M').time()
                    if horario_data.get('hora_fin'):
                        visita.hora_fin = datetime.strptime(horario_data['hora_fin'], '%H:%M').time()
                    visita.grupo = horario_data.get('grupo', 1)
                    visita.asignado_por_admin_id = admin_id
                    
                    db.session.add(visita)
            
            # 3. Guardar todo
            db.session.commit()
            print("Solicitud confirmada con horarios y visitas creadas.")
            return True
            
        except Exception as e:
            print("Error al confirmar solicitud con horarios:", e)
            db.session.rollback()
            return False
    
    def confirmar(self, admin_id=None):
        """Confirma la solicitud (método simple sin horarios)"""
        if self.puede_ser_confirmada():
            self.estado = 'CONFIRMADA'
            self.fecha_respuesta = datetime.utcnow()
            return True
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