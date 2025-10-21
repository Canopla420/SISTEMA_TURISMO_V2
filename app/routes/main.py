from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/test')
def test():
    return render_template('test.html')  # ← CAMBIAR A TEMPLATE

@bp.route('/simple')
def simple():
    return "<h1>Sistema de Turismo V2</h1><p>Página de prueba funcionando!</p>"