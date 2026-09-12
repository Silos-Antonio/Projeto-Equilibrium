from datetime import timedelta
import secrets
import math
from app.services.db import get_db_connection
from app.services.sessao_service import encerrar_sessoes_expiradas


def listar_agendamentos_do_terapeuta(terapeuta_id, pagina=1, por_pagina=10):
    encerrar_sessoes_expiradas(terapeuta_id)
    conn = get_db_connection()
    if not conn:
        return {'items': [], 'total_paginas': 1, 'pagina_atual': 1}

    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Contar o total de agendamentos para saber quantas páginas teremos
        cursor.execute(
            "SELECT COUNT(*) as total FROM agendamentos WHERE terapeuta_id = %s",
            (terapeuta_id,)
        )
        total_registros = cursor.fetchone()['total']
        total_paginas = math.ceil(total_registros / por_pagina) if total_registros > 0 else 1

        # 2. Garantir que a página atual seja válida e calcular o OFFSET
        pagina = max(1, min(pagina, total_paginas))
        offset = (pagina - 1) * por_pagina

        # 3. Buscar apenas os agendamentos da página atual com LIMIT e OFFSET
        cursor.execute(
            """
            SELECT a.id, a.data_hora_inicio, a.data_hora_fim, a.status,
                   a.observacoes, p.nome AS paciente_nome, s.token_acesso,
                   s.ativa AS sessao_ativa, s.iniciada_em
            FROM agendamentos a
            INNER JOIN pacientes p ON p.id = a.paciente_id
            INNER JOIN sessoes s ON s.agendamento_id = a.id
            WHERE a.terapeuta_id = %s
            ORDER BY a.data_hora_inicio DESC
            LIMIT %s OFFSET %s
            """,
            (terapeuta_id, por_pagina, offset)
        )
        
        items = cursor.fetchall()
        
        # Retornamos um dicionário com os itens e os metadados da paginação
        return {
            'items': items,
            'total_paginas': total_paginas,
            'pagina_atual': pagina
        }
    finally:
        cursor.close()
        conn.close()


def criar_agendamento(terapeuta_id, paciente_id, data_hora_inicio, duracao_minutos, observacoes="", musica_selecionada="528Hz River.mp3"):
    """Cria agendamento e sua sessão pública em uma única transação."""
    data_hora_fim = data_hora_inicio + timedelta(minutes=duracao_minutos)
    conn = get_db_connection()
    if not conn:
        return False, 'Não foi possível conectar ao banco de dados.'

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id FROM pacientes WHERE id = %s AND terapeuta_id = %s',
            (paciente_id, terapeuta_id),
        )
        if not cursor.fetchone():
            conn.rollback()
            return False, 'Paciente inválido para este terapeuta.'

        cursor.execute(
            """
            SELECT id FROM agendamentos
            WHERE terapeuta_id = %s
              AND status = 'AGENDADO'
              AND data_hora_inicio < %s
              AND data_hora_fim > %s
            LIMIT 1
            """,
            (terapeuta_id, data_hora_fim, data_hora_inicio),
        )
        if cursor.fetchone():
            conn.rollback()
            return False, 'Já existe um agendamento nesse intervalo de horário.'

        cursor.execute(
            """
            INSERT INTO agendamentos
                (terapeuta_id, paciente_id, data_hora_inicio, data_hora_fim, observacoes)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (terapeuta_id, paciente_id, data_hora_inicio, data_hora_fim, observacoes or None),
        )
        agendamento_id = cursor.lastrowid
        token = secrets.token_urlsafe(32)
        cursor.execute(
            """
            INSERT INTO sessoes (agendamento_id, duracao_minutos, token_acesso, musica_selecionada)
            VALUES (%s, %s, %s, %s)
            """,
            (agendamento_id, duracao_minutos, token, musica_selecionada),
        )
        conn.commit()
        return True, token
    
    except Exception as error:
        conn.rollback()
        print(f'Erro ao criar agendamento: {error}')
        return False, 'Não foi possível salvar o agendamento.'
    finally:
        cursor.close()
        conn.close()

def cancelar_agendamento(terapeuta_id, agendamento_id):
    """
    Cancela um agendamento pertencente ao terapeuta.

    Não permite cancelar sessões que já foram iniciadas.
    """

    conn = get_db_connection()

    if not conn:
        return False, 'Não foi possível conectar ao banco de dados.'

    cursor = conn.cursor(dictionary=True)

    try:
        # Verifica se o agendamento pertence ao terapeuta
        cursor.execute(
            """
            SELECT
                a.id,
                a.status,
                s.iniciada_em
            FROM agendamentos a
            INNER JOIN sessoes s
                ON s.agendamento_id = a.id
            WHERE a.id = %s
              AND a.terapeuta_id = %s
            """,
            (agendamento_id, terapeuta_id),
        )

        agendamento = cursor.fetchone()

        if not agendamento:
            return False, 'Agendamento não encontrado.'

        if agendamento['status'] == 'CANCELADO':
            return False, 'Este agendamento já foi cancelado.'

        if agendamento['iniciada_em']:
            return False, (
                'Não é possível cancelar um agendamento '
                'cuja sessão já foi iniciada.'
            )

        # Cancela o agendamento
        cursor.execute(
            """
            UPDATE agendamentos
            SET status = 'CANCELADO'
            WHERE id = %s
              AND terapeuta_id = %s
            """,
            (agendamento_id, terapeuta_id),
        )

        # Garante que a sessão vinculada não fique ativa
        cursor.execute(
            """
            UPDATE sessoes
            SET ativa = 0
            WHERE agendamento_id = %s
            """,
            (agendamento_id,),
        )

        conn.commit()

        return True, 'Agendamento cancelado com sucesso.'

    except Exception as error:

        conn.rollback()

        print(f'Erro ao cancelar agendamento: {error}')

        return False, 'Não foi possível cancelar o agendamento.'

    finally:

        cursor.close()
        conn.close()

def editar_horario_agendamento(terapeuta_id, agendamento_id, nova_data_hora_inicio, nova_duracao_minutos):
    """
    Atualiza o horário e a duração de um agendamento.
    Garante que não haja choque de horários e que a sessão não tenha iniciado.
    """
    nova_data_hora_fim = nova_data_hora_inicio + timedelta(minutes=nova_duracao_minutos)
    conn = get_db_connection()
    if not conn:
        return False, 'Não foi possível conectar ao banco de dados.'

    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Verifica propriedade e status
        cursor.execute(
            """
            SELECT a.status, s.iniciada_em
            FROM agendamentos a
            LEFT JOIN sessoes s ON s.agendamento_id = a.id
            WHERE a.id = %s AND a.terapeuta_id = %s
            """,
            (agendamento_id, terapeuta_id)
        )
        agendamento = cursor.fetchone()

        if not agendamento:
            return False, 'Agendamento não encontrado.'
        if agendamento['status'] != 'AGENDADO':
            return False, 'Apenas agendamentos ativos podem ser editados.'
        if agendamento['iniciada_em']:
            return False, 'Não é possível editar o horário de uma sessão que já foi iniciada.'

        # 2. Verifica sobreposição de horários (ignorando o próprio agendamento)
        cursor.execute(
            """
            SELECT id FROM agendamentos
            WHERE terapeuta_id = %s
              AND status = 'AGENDADO'
              AND id != %s
              AND data_hora_inicio < %s
              AND data_hora_fim > %s
            LIMIT 1
            """,
            (terapeuta_id, agendamento_id, nova_data_hora_fim, nova_data_hora_inicio)
        )
        if cursor.fetchone():
            return False, 'Você já possui um agendamento neste intervalo de horário.'

        # 3. Atualiza as tabelas agendamentos e sessoes
        cursor.execute(
            "UPDATE agendamentos SET data_hora_inicio = %s, data_hora_fim = %s WHERE id = %s",
            (nova_data_hora_inicio, nova_data_hora_fim, agendamento_id)
        )
        cursor.execute(
            "UPDATE sessoes SET duracao_minutos = %s WHERE agendamento_id = %s",
            (nova_duracao_minutos, agendamento_id)
        )

        conn.commit()
        return True, 'Horário atualizado com sucesso!'
    except Exception as error:
        conn.rollback()
        print(f'Erro ao editar agendamento: {error}')
        return False, 'Não foi possível salvar o novo horário.'
    finally:
        cursor.close()
        conn.close()