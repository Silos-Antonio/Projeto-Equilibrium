from flask import Blueprint, render_template, session
from app.utils.decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)

# Uso do @login_required logo abaixo do @dashboard_bp.route!
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Aqui, no futuro, buscará os pacientes e agendamentos do banco de dados
    return render_template('dashboard.html', terapeuta_id=session.get('terapeuta_id'))