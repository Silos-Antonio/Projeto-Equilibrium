from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.services.admin_service import (
    listar_usuarios,
    buscar_usuario_por_id,
    alterar_situacao_usuario,
    atualizar_terapeuta
)

from app.utils.decorators import admin_required

from app.services.admin_service import (
    listar_usuarios,
    alterar_situacao_usuario,
    redefinir_senha_terapeuta
)

from app.extensions import limiter


admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin'
)


@admin_bp.route('/usuarios')
@admin_required
def usuarios():

    usuarios = listar_usuarios()

    return render_template(
        'admin/usuarios.html',
        usuarios=usuarios
    )


@admin_bp.route('/usuarios/<int:usuario_id>/situacao', methods=['POST'])
@admin_required
def alterar_situacao(usuario_id):

    sucesso, mensagem = alterar_situacao_usuario(usuario_id)

    flash(
        mensagem,
        'success' if sucesso else 'error'
    )

    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@admin_required
@limiter.limit("10 per minute", methods=["POST"])
def editar_usuario(usuario_id):

    usuario = buscar_usuario_por_id(usuario_id)

    if not usuario:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('admin.usuarios'))

    if usuario['perfil'] != 'TERAPEUTA':
        flash('Apenas terapeutas podem ser editados.', 'error')
        return redirect(url_for('admin.usuarios'))

    if request.method == 'POST':

        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        nova_senha = request.form.get('nova_senha', '').strip() # <-- Captura a nova senha opcional

        if not nome or not email or not telefone:
            flash(
                'Preencha todos os campos obrigatórios.',
                'error'
            )
            return render_template(
                'admin/editar_terapeuta.html',
                usuario=usuario
            )

        # Atualiza os dados cadastrais básicos
        sucesso, mensagem = atualizar_terapeuta(
            usuario_id,
            nome,
            email,
            telefone
        )

        if not sucesso:
            flash(mensagem, 'error')
            return render_template('admin/editar_terapeuta.html', usuario=usuario)

        # Se o admin digitou uma nova senha, faz a redefinição separadamente
        if nova_senha:
            if len(nova_senha) < 6: # Validação opcional de tamanho mínimo
                flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
                return render_template('admin/editar_terapeuta.html', usuario=usuario)
                
            sucesso_senha, msg_senha = redefinir_senha_terapeuta(usuario_id, nova_senha)
            if not sucesso_senha:
                flash(msg_senha, 'error')
                return render_template('admin/editar_terapeuta.html', usuario=usuario)
            
            flash('Dados e nova senha atualizados com sucesso!', 'success')
        else:
            flash('Dados do terapeuta atualizados com sucesso!', 'success')

        return redirect(url_for('admin.usuarios'))

    return render_template(
        'admin/editar_terapeuta.html',
        usuario=usuario
    )