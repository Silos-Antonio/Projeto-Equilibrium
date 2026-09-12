
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.services.agendamento_service import criar_agendamento, listar_agendamentos_do_terapeuta, cancelar_agendamento, editar_horario_agendamento
from app.services.paciente_service import listar_pacientes_do_terapeuta
from app.utils.decorators import login_required
from app.services.sessao_service import encerrar_sessoes_expiradas

agendamento_bp = Blueprint('agendamento', __name__)

OPCOES_MUSICA = [
    {'arquivo': '528Hz River.mp3', 'nome': '528Hz - Frequência de cura'},
    {'arquivo': 'Tradicional.mp3', 'nome': 'Tradicional'},
    {'arquivo': 'Nature.mp3', 'nome': 'Natureza'},
    {'arquivo': 'Ocean.mp3', 'nome': 'Oceano'},
    {'arquivo': 'Spirit.mp3', 'nome': 'Espiritual'},
    {'arquivo': 'Cosmic.mp3', 'nome': 'Astral'}
]

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
            musica = request.form.get('musica', '528Hz River.mp3')
            sucesso, resultado = criar_agendamento(
                terapeuta_id, paciente_id, inicio, duracao_minutos, request.form.get('observacoes', ''), musica
            )
            if sucesso:
                flash(f'Agendamento criado. Link da sessão: {url_for("sessao.acessar_sessao", token=resultado, _external=True)}', 'success')
            else:
                flash(resultado, 'error')
        return redirect(url_for('agendamento.gerir_agendamentos'))

    encerrar_sessoes_expiradas(terapeuta_id)

    pagina = request.args.get('page', 1, type=int)
    
    # NOVO: Recebe o dicionário completo da nossa alteração no service
    pagina = request.args.get('page', 1, type=int)
    paginacao = listar_agendamentos_do_terapeuta(terapeuta_id, pagina=pagina)
    
    # 1. Desempacota a tupla, pegando apenas o primeiro elemento (a lista de dicionários) 
    # e ignorando o segundo (total) com o underline "_"
    pacientes_lista, _ = listar_pacientes_do_terapeuta(terapeuta_id)

    return render_template(
        'agendamentos.html',
        pacientes=pacientes_lista,        # 2. Passa a lista limpa para o Jinja
        agendamentos=paginacao['items'], 
        paginacao=paginacao,   
        musicas=OPCOES_MUSICA            
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

@agendamento_bp.route('/agendamentos/<int:agendamento_id>/editar', methods=['POST'])
@login_required
def editar(agendamento_id):
    terapeuta_id = session['usuario_id']
    
    try:
        nova_duracao = int(request.form.get('duracao_minutos', ''))
        nova_inicio = datetime.strptime(request.form.get('data_hora', ''), '%Y-%m-%dT%H:%M')
        if not 5 <= nova_duracao <= 240:
            raise ValueError
    except ValueError:
        flash('Data, hora ou duração inválidas.', 'error')
        return redirect(url_for('agendamento.gerir_agendamentos'))

    sucesso, mensagem = editar_horario_agendamento(
        terapeuta_id, agendamento_id, nova_inicio, nova_duracao
    )

    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')

    return redirect(url_for('agendamento.gerir_agendamentos'))