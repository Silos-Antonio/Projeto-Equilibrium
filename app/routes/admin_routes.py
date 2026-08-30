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
    alterar_situacao_usuario
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

        if not nome or not email or not telefone:
            flash(
                'Preencha todos os campos obrigatórios.',
                'error'
            )

            return render_template(
                'admin/editar_terapeuta.html',
                usuario=usuario
            )

        sucesso, mensagem = atualizar_terapeuta(
            usuario_id,
            nome,
            email,
            telefone
        )

        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('admin.usuarios'))

        flash(mensagem, 'error')

    return render_template(
        'admin/editar_terapeuta.html',
        usuario=usuario
    )