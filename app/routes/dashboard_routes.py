from flask import Blueprint, render_template, session
from app.utils.decorators import login_required
from app.services.dashboard_service import buscar_dados_dashboard

dashboard_bp = Blueprint('dashboard', __name__)

# Uso do @login_required logo abaixo do @dashboard_bp.route!
@dashboard_bp.route('/dashboard')
@login_required
def index():
    terapeuta_id = session.get('terapeuta_id')
    return render_template('dashboard.html', terapeuta_id=terapeuta_id, dados=buscar_dados_dashboard(terapeuta_id))
