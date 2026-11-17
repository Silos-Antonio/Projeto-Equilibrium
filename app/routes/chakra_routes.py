from flask import Blueprint, abort, flash, redirect, request, session, url_for
import logging

from app.services.chakra_service import CHAKRAS, criar_avaliacao
from app.utils.decorators import login_required
from app.services.paciente_service import buscar_paciente_do_terapeuta

chakra_bp = Blueprint('chakra', __name__)
logger = logging.getLogger(__name__)


@chakra_bp.route('/pacientes/<int:paciente_id>/avaliacoes-chakras', methods=['POST'])
@login_required
def criar(paciente_id):
    terapeuta_id = session.get('usuario_id')
    if not buscar_paciente_do_terapeuta(terapeuta_id, paciente_id):
        abort(404)
    try:
        niveis = {}
        confirmados = set(request.form.getlist('confirmado'))
        if confirmados != set(CHAKRAS):
            raise ValueError('Ajuste cada um dos sete controles antes de salvar a avaliação.')
        for chakra in CHAKRAS:
            raw = request.form.get(f'nivel_{chakra}')
            if raw is None or not raw.isdecimal():
                raise ValueError('Defina o nível dos sete chakras antes de salvar.')
            niveis[chakra] = int(raw)
        criar_avaliacao(terapeuta_id, paciente_id, niveis, request.form.get('observacoes'))
        flash('Avaliação de chakras salva com sucesso.', 'success')
    except ValueError as error:
        flash(str(error), 'error')
    except Exception:
        logger.exception('Falha ao persistir avaliação de chakras.')
        flash('Não foi possível salvar a avaliação. Tente novamente.', 'error')
    return redirect(url_for('paciente.editar_paciente', paciente_id=paciente_id) + '#avaliacao-chakras')
