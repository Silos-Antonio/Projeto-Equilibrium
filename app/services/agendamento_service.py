from datetime import timedelta
import secrets

from app.services.db import get_db_connection
from app.services.sessao_service import encerrar_sessoes_expiradas


def listar_agendamentos_do_terapeuta(terapeuta_id):
    encerrar_sessoes_expiradas(terapeuta_id)
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)
    try:
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
            """,
            (terapeuta_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def criar_agendamento(terapeuta_id, paciente_id, data_hora_inicio, duracao_minutos, observacoes=""):
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
            INSERT INTO sessoes (agendamento_id, duracao_minutos, token_acesso)
            VALUES (%s, %s, %s)
            """,
            (agendamento_id, duracao_minutos, token),
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