# app/services/sessao_service.py

from datetime import datetime, timedelta

from app.services.db import get_db_connection


def buscar_dados_sessao(token_acesso):
    """
    Busca a sessão pelo token e faz um JOIN com agendamentos e pacientes
    para termos todo o contexto necessário para a tela da terapia.
    """
    conn = get_db_connection()

    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            s.token_acesso,
            s.duracao_minutos,
            s.ativa,
            s.iniciada_em,
            s.finalizada_em,
            a.data_hora_inicio,
            a.data_hora_fim,
            a.status AS agendamento_status,
            p.nome AS paciente_nome
        FROM sessoes s
        INNER JOIN agendamentos a ON s.agendamento_id = a.id
        INNER JOIN pacientes p ON a.paciente_id = p.id
        WHERE s.token_acesso = %s
    """

    cursor.execute(query, (token_acesso,))
    sessao = cursor.fetchone()

    cursor.close()
    conn.close()

    return sessao


def iniciar_sessao(token_acesso):
    """
    Marca o início uma única vez e impede reinicializações do cronômetro.
    """
    conn = get_db_connection()

    if not conn:
        return False, 'Não foi possível conectar ao banco de dados.'

    cursor = conn.cursor()

    try:
        inicio = datetime.now()

        cursor.execute(
            """
            UPDATE sessoes s
            INNER JOIN agendamentos a ON a.id = s.agendamento_id
            SET
                s.ativa = TRUE,
                s.iniciada_em = %s
            WHERE s.token_acesso = %s
              AND s.iniciada_em IS NULL
              AND a.status = 'AGENDADO'
              AND NOW() >= a.data_hora_inicio
              AND NOW() <= a.data_hora_fim
            """,
            (inicio, token_acesso),
        )

        if cursor.rowcount != 1:
            conn.rollback()
            return False, 'Esta sessão não pode mais ser iniciada.'

        conn.commit()

        cursor.execute(
            """
            SELECT duracao_minutos
            FROM sessoes
            WHERE token_acesso = %s
            """,
            (token_acesso,),
        )

        resultado = cursor.fetchone()

        if not resultado:
            return False, 'Não foi possível obter a duração da sessão.'

        duracao_minutos = resultado[0]

        fim = inicio + timedelta(minutes=duracao_minutos)

        return True, fim

    except Exception as error:
        conn.rollback()
        print(f'Erro ao iniciar sessão: {error}')
        return False, 'Não foi possível iniciar a sessão.'

    finally:
        cursor.close()
        conn.close()


def encerrar_sessao(token_acesso):
    """
    Registra o encerramento de uma sessão que foi iniciada.
    """
    conn = get_db_connection()

    if not conn:
        return

    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE sessoes s
            INNER JOIN agendamentos a ON a.id = s.agendamento_id
            SET
                s.ativa = FALSE,
                s.finalizada_em = COALESCE(s.finalizada_em, NOW()),
                a.status = 'CONCLUIDO'
            WHERE s.token_acesso = %s
              AND s.ativa = TRUE
            """,
            (token_acesso,),
        )

        conn.commit()

    except Exception as error:
        conn.rollback()
        print(f'Erro ao encerrar sessão: {error}')

    finally:
        cursor.close()
        conn.close()


def encerrar_sessoes_expiradas(terapeuta_id=None):
    """
    Sincroniza sessões que chegaram ao fim.

    Existem dois cenários:

    1. A sessão foi iniciada e seu tempo terminou:
       -> sessão = encerrada
       -> agendamento = CONCLUIDO

    2. A sessão nunca foi iniciada e o horário do agendamento terminou:
       -> sessão permanece inativa
       -> agendamento = NAO_COMPARECEU
    """

    conn = get_db_connection()

    if not conn:
        return

    cursor = conn.cursor()

    try:
        # ---------------------------------------------------------
        # 1. Sessões iniciadas que chegaram ao fim
        # ---------------------------------------------------------

        query_concluidas = """
            UPDATE sessoes s
            INNER JOIN agendamentos a
                ON a.id = s.agendamento_id
            SET
                s.ativa = FALSE,
                s.finalizada_em = COALESCE(s.finalizada_em, NOW()),
                a.status = 'CONCLUIDO'
            WHERE s.ativa = TRUE
              AND s.iniciada_em IS NOT NULL
              AND TIMESTAMPADD(
                    MINUTE,
                    s.duracao_minutos,
                    s.iniciada_em
                  ) <= NOW()
        """

        parametros_concluidas = ()

        if terapeuta_id is not None:
            query_concluidas += """
                AND a.terapeuta_id = %s
            """
            parametros_concluidas = (terapeuta_id,)

        cursor.execute(
            query_concluidas,
            parametros_concluidas
        )

        # ---------------------------------------------------------
        # 2. Sessões que nunca foram iniciadas
        # ---------------------------------------------------------

        query_nao_comparecimento = """
            UPDATE sessoes s
            INNER JOIN agendamentos a
                ON a.id = s.agendamento_id
            SET
                s.finalizada_em = COALESCE(s.finalizada_em, NOW()),
                a.status = 'NAO_COMPARECEU'
            WHERE s.iniciada_em IS NULL
              AND a.status = 'AGENDADO'
              AND a.data_hora_fim <= NOW()
        """

        parametros_nao_comparecimento = ()

        if terapeuta_id is not None:
            query_nao_comparecimento += """
                AND a.terapeuta_id = %s
            """
            parametros_nao_comparecimento = (terapeuta_id,)

        cursor.execute(
            query_nao_comparecimento,
            parametros_nao_comparecimento
        )

        conn.commit()

    except Exception as error:
        conn.rollback()
        print(f'Erro ao sincronizar sessões expiradas: {error}')

    finally:
        cursor.close()
        conn.close()