from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('instituciones/index.html')

@bp.route('/test')
def test():
    return "<h1>Sistema de Turismo V2</h1><p>Página de prueba funcionando!</p>"