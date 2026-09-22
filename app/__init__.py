import os

from dotenv import load_dotenv
from flask import Flask, jsonify

from app.extensions import csrf, limiter
from app.routes.admin_routes import admin_bp
from app.routes.agendamento_routes import agendamento_bp
from app.routes.auth_routes import auth_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.paciente_routes import paciente_bp
from app.routes.sessao_routes import sessao_bp
from app.services.db import get_db_connection
from app.cli import register_commands


load_dotenv()


def create_app():
    app = Flask(__name__)

    secret_key = os.getenv('SECRET_KEY')

    if not secret_key:
        raise RuntimeError('SECRET_KEY não configurada.')

    app.config['SECRET_KEY'] = secret_key

    limiter.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(paciente_bp)
    app.register_blueprint(agendamento_bp)
    app.register_blueprint(sessao_bp)
    app.register_blueprint(admin_bp)
    
    register_commands(app)

    @app.route('/health', methods=['GET'])
    def health_check():
        conn = get_db_connection()

        if not conn:
            return jsonify({
                'status': 'error',
                'api': 'online',
                'database': 'unavailable',
            }), 503

        conn.close()

        return jsonify({
            'status': 'ok',
            'api': 'online',
            'database': 'online',
        }), 200

    return app