
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services.agendamento_service import criar_agendamento, listar_agendamentos_do_terapeuta, cancelar_agendamento
from app.services.paciente_service import listar_pacientes_do_terapeuta
from app.utils.decorators import login_required
from app.services.sessao_service import encerrar_sessoes_expiradas

agendamento_bp = Blueprint('agendamento', __name__)


@agendamento_bp.route('/agendamentos', methods=['GET', 'POST'])
@login_required
def gerir_agendamentos():
    terapeuta_id = session['usuario_id']

    if request.method == 'POST':
        try:
            paciente_id = int(request.form.get('paciente_id', ''))
            duracao_minutos = int(request.form.get('duracao_minutos', ''))
            inicio = datetime.strptime(request.form.get('data_hora', ''), '%Y-%m-%dT%H:%M')
            if not 5 <= duracao_minutos <= 240:
                raise ValueError
        except ValueError:
            flash('Informe paciente, data/hora e duração válida (de 5 a 240 minutos).', 'error')
        else:
            sucesso, resultado = criar_agendamento(
                terapeuta_id, paciente_id, inicio, duracao_minutos, request.form.get('observacoes', '')
            )
            if sucesso:
                flash(f'Agendamento criado. Link da sessão: {url_for("sessao.acessar_sessao", token=resultado, _external=True)}', 'success')
            else:
                flash(resultado, 'error')
        return redirect(url_for('agendamento.gerir_agendamentos'))

    encerrar_sessoes_expiradas(terapeuta_id)

    return render_template(
        'agendamentos.html',
        pacientes=listar_pacientes_do_terapeuta(terapeuta_id),
        agendamentos=listar_agendamentos_do_terapeuta(terapeuta_id),
    )

@agendamento_bp.route(
    '/agendamentos/<int:agendamento_id>/cancelar',
    methods=['POST']
)
@login_required
def cancelar(agendamento_id):

    terapeuta_id = session['usuario_id']

    sucesso, mensagem = cancelar_agendamento(
        terapeuta_id,
        agendamento_id,
    )

    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')

    return redirect(
        url_for('agendamento.gerir_agendamentos')
    )