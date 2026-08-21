from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.auth import verificar_credenciais

# Cria o Blueprint chamado 'auth'. Isso agrupa todas as rotas de autenticação.
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Segurança: Se já tem sessão ativa, não precisa fazer login novamente
    if 'terapeuta_id' in session:
        return redirect(url_for('health_check')) # Futuramente mudar para o Dashboard

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Chama serviço testado anteriormente!
        terapeuta_id = verificar_credenciais(email, senha)

        if terapeuta_id:
            # SUCESSO: Grava o ID do terapeuta no cookie criptografado (session)
            session['terapeuta_id'] = terapeuta_id
            
            # Redireciona para o health check temporariamente para validar
            return redirect(url_for('dashboard.index')) 
        else:
            # ERRO: Devolve uma mensagem (flash) para a tela
            flash('E-mail ou senha incorretos.', 'error')

    # Se for GET (apenas acessando a URL), mostra a página HTML de login
    return render_template('login.html')

    

@auth_bp.route('/logout')
def logout():
    # Segurança: Limpa o cookie e encerra a sessão
    session.clear()
    return redirect(url_for('auth.login'))