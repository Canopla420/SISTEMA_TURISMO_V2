from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class UsuarioPrestador(UserMixin, db.Model):
    """Usuarios que trabajan en prestadores turísticos"""
    
    id = db.Column(db.Integer, primary_key=True)
    
    # DATOS DE LOGIN
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # DATOS PERSONALES
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100))  # "Guía", "Responsable", "Coordinador", etc.
    telefono = db.Column(db.String(30))
    
    # RELACIÓN CON PRESTADOR (CLAVE FORÁNEA)
    prestador_id = db.Column(db.Integer, db.ForeignKey('prestador.id'), nullable=False)
    prestador = db.relationship('Prestador', backref=db.backref('usuarios', lazy=True))
    
    # ESTADO
    activo = db.Column(db.Boolean, default=True)
    
    # METADATOS
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<UsuarioPrestador {self.email}>'
    
    def set_password(self, password):
        """Encripta y guarda la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def get_nombre_completo(self):
        """Retorna nombre y apellido"""
        return f"{self.nombre} {self.apellido}"
    
    def get_prestador_nombre(self):
        """Retorna nombre del prestador al que pertenece"""
        return self.prestador.razon_social if self.prestador else "Sin asignar"
    
    # Métodos requeridos por Flask-Login
    def get_id(self):
        return str(self.id)
    
    @property
    def is_active(self):
        return self.activo
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False