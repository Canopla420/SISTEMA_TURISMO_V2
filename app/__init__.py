from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
migrate = Migrate()
#login = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    #login.init_app(app)
    mail.init_app(app)
    
    # Registrar blueprints - SOLO MAIN por ahora
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    

    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.routes.prestador import bp as prestador_bp
    app.register_blueprint(prestador_bp, url_prefix='/prestador')
    
    from app.routes.publico import bp as publico_bp
    app.register_blueprint(publico_bp, url_prefix='/publico')

    return app

# Importar modelos (al final para evitar imports circulares)
#from app.models import usuario_admin, prestador, usuario_prestador, solicitud_visita, visita_prestador