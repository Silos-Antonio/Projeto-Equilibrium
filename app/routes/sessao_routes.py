# app/routes/sessao_routes.py
from datetime import datetime, timedelta

from pathlib import Path

from flask import Blueprint, flash, jsonify, redirect, render_template, request, send_file, url_for

from app.services.sessao_service import buscar_dados_sessao, encerrar_sessao, iniciar_sessao

sessao_bp = Blueprint('sessao', __name__)

@sessao_bp.route('/sessao/<token>')
def acessar_sessao(token):

    # ==========================================
    # BUSCA A SESSÃO
    # ==========================================

    sessao = buscar_dados_sessao(token)

    if not sessao:

        return render_template(
            'sessao.html',
            sessao=sessao,
            status=status,
            fim_timestamp=fim_timestamp
        )


    # ==========================================
    # DETERMINA O STATUS
    # ==========================================

    agora = datetime.now()

    fim_timestamp = None


    if agora < sessao['data_hora_inicio']:

        status = 'aguardando'


    elif agora > sessao['data_hora_fim'] and not sessao['iniciada_em']:

        status = 'encerrada'


    elif not sessao['iniciada_em']:

        status = 'pronta'


    elif sessao['finalizada_em']:

        status = 'encerrada'


    else:

        fim_real = (
            sessao['iniciada_em']
            + timedelta(minutes=sessao['duracao_minutos'])
        )

        if agora >= fim_real:

            encerrar_sessao(token)
            status = 'encerrada'

        else:

            status = 'ativa'

            fim_timestamp = int(
                fim_real.timestamp() * 1000
            )


    # ==========================================
    # RENDERIZA A PÁGINA
    # ==========================================

    return render_template(
        'sessao.html',
        sessao=sessao,
        status=status,
        fim_timestamp=fim_timestamp
    )

@sessao_bp.route('/sessao/<token>/iniciar', methods=['POST'])
def iniciar(token):
    sucesso, resultado = iniciar_sessao(token)
    if request.accept_mimetypes.best == 'application/json':
        if sucesso:
            return jsonify({'fim_timestamp': int(resultado.timestamp() * 1000)})
        return jsonify({'erro': resultado}), 409

    if not sucesso:
        flash(resultado, 'error')
    return redirect(url_for('sessao.acessar_sessao', token=token))


@sessao_bp.route('/audio/meditacao.mp3')
def audio_meditacao():
    """Entrega o MP3 com requisições condicionais e suporte a retomada do navegador."""
    arquivo = Path(__file__).resolve().parent.parent / 'sound' / '528Hz River.mp3'
    return send_file(arquivo, mimetype='audio/mpeg', conditional=True, max_age=60 * 60 * 24 * 7)
