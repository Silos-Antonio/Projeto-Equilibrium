from flask import Blueprint, abort, render_template, request, redirect, url_for, session, flash
from app.utils.decorators import login_required
from app.services.paciente_service import atualizar_paciente, buscar_paciente_do_terapeuta, listar_pacientes_do_terapeuta, criar_paciente

paciente_bp = Blueprint('paciente', __name__)

@paciente_bp.route('/pacientes', methods=['GET', 'POST'])
@login_required
def gerir_pacientes():
    terapeuta_id = session.get('terapeuta_id')

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        observacoes = request.form.get('observacoes')

        if not nome:
            flash('O nome do paciente é obrigatório.', 'error')
        elif criar_paciente(terapeuta_id, nome, email, telefone, observacoes):
            flash('Paciente registrado com sucesso!', 'success')
        else:
            flash('Erro ao registrar o paciente.', 'error')
            
        return redirect(url_for('paciente.gerir_pacientes'))

    # CHAMADA DA FUNÇÃO CORRIGIDA AQUI:
    lista_pacientes = listar_pacientes_do_terapeuta(terapeuta_id)
    
    return render_template('pacientes.html', pacientes=lista_pacientes)


@paciente_bp.route('/pacientes/<int:paciente_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_paciente(paciente_id):
    terapeuta_id = session.get('terapeuta_id')
    paciente = buscar_paciente_do_terapeuta(terapeuta_id, paciente_id)
    if not paciente:
        abort(404)
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        observacoes = request.form.get('observacoes', '').strip()
        if not nome:
            flash('O nome do paciente é obrigatório.', 'error')
        else:
            sucesso, mensagem = atualizar_paciente(terapeuta_id, paciente_id, nome, email, telefone, observacoes)
            if sucesso:
                flash(mensagem, 'success')
                return redirect(url_for('paciente.gerir_pacientes'))
            flash(mensagem, 'error')
        paciente.update(nome=nome, email=email, telefone=telefone, observacoes=observacoes)
    return render_template('editar_paciente.html', paciente=paciente)
