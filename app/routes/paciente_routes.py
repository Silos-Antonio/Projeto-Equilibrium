from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.decorators import login_required
# IMPORTAÇÃO CORRIGIDA AQUI:
from app.services.paciente_service import listar_pacientes_do_terapeuta, criar_paciente

paciente_bp = Blueprint('paciente', __name__)

@paciente_bp.route('/pacientes', methods=['GET', 'POST'])
@login_required
def gerir_pacientes():
    terapeuta_id = session.get('terapeuta_id')

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        
        # Como atualizamos a regra de negócio, podemos passar telefone e observacoes vazios por enquanto
        if criar_paciente(terapeuta_id, nome, email, telefone="", observacoes=""):
            flash('Paciente registrado com sucesso!', 'success')
        else:
            flash('Erro ao registrar o paciente.', 'error')
            
        return redirect(url_for('paciente.gerir_pacientes'))

    # CHAMADA DA FUNÇÃO CORRIGIDA AQUI:
    lista_pacientes = listar_pacientes_do_terapeuta(terapeuta_id)
    
    return render_template('pacientes.html', pacientes=lista_pacientes)