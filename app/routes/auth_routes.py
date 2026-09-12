from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.auth import verificar_credenciais
from app.services.user_service import criar_terapeuta
from app.extensions import limiter
from app.utils.decorators import admin_required

# Cria o Blueprint chamado 'auth'. Isso agrupa todas as rotas de autenticação.
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=["POST"])
def login():

    if 'usuario_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':

        email = request.form.get('email')
        senha = request.form.get('senha')

        usuario = verificar_credenciais(email, senha)

        if usuario:
            session['usuario_id'] = usuario['id']
            session['perfil'] = usuario['perfil']
            nome_completo = usuario.get('nome', '')
            session['nome'] = nome_completo.split()[0] if nome_completo else 'Terapeuta'

            return redirect(url_for('dashboard.index'))

        flash('E-mail ou senha incorretos.', 'error')

    return render_template('login.html')

@auth_bp.route('/cadastro-terapeuta', methods=['GET', 'POST'])
@admin_required
@limiter.limit("5 per minute", methods=["POST"])
def cadastro_terapeuta():

    if request.method == 'POST':

        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        senha = request.form.get('senha', '')

        # Validação básica
        if not nome or not email or not telefone or not senha:
            flash(
                'Preencha todos os campos obrigatórios.',
                'error'
            )
            return render_template('cadastro_terapeuta.html')

        sucesso, mensagem = criar_terapeuta(
            nome=nome,
            email=email,
            telefone=telefone,
            senha=senha
        )

        if sucesso:
            flash(mensagem, 'success')
            return redirect(
                url_for('auth.cadastro_terapeuta')
            )

        flash(mensagem, 'error')

    return render_template('cadastro_terapeuta.html')
    

@auth_bp.route('/logout')
def logout():
    # Segurança: Limpa o cookie e encerra a sessão
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/termos-de-uso')
def termos_de_uso():
    return render_template('termos_de_uso.html')

@auth_bp.route('/politica_de_privacidade.html')
def politica_de_privacidade():
    return render_template('politica_de_privacidade.html')