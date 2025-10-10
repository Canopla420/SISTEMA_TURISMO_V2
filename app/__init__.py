from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

# USER LOADER TEMPORAL - Ahora fuera de create_app
@login_manager.user_loader
def load_user(user_id):
    # TODO: Implementar en Commit 2 con modelos reales
    return None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Configurar Flask-Login
    login_manager.login_view = 'main.index'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    # Registrar blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.routes.prestador import bp as prestador_bp
    app.register_blueprint(prestador_bp, url_prefix='/prestador')
    
    return app

# Importar modelos para que Flask-Migrate los reconozca
from app import models