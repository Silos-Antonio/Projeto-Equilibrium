from flask import Flask, jsonify
from dotenv import load_dotenv
load_dotenv()

from app.services.db import get_db_connection # Importa o serviço de DB
import os

# Importa rotas de autenticação
from app.routes.auth_routes import auth_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.paciente_routes import paciente_bp
from app.routes.agendamento_routes import agendamento_bp
from app.routes.sessao_routes import sessao_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(paciente_bp)
    app.register_blueprint(agendamento_bp)
    app.register_blueprint(sessao_bp)
    

    @app.route('/health', methods=['GET'])
    def health_check():
        # Testa a conexão com o banco
        conn = get_db_connection()
        db_status = "ok" if conn else "erro"
        if conn:
            conn.close() # Sempre fechamos a conexão após testar!

        return jsonify({
            "status": "sucesso",
            "api": "online",
            "database": db_status
        }), 200
    
    return app
