import logging

from mysql.connector import Error

from app.services.db import get_db_connection

logger = logging.getLogger(__name__)

CHAKRAS = (
    'CORONARIO', 'FRONTAL', 'LARINGEO', 'CARDIACO',
    'PLEXO_SOLAR', 'SACRAL', 'BASICO',
)


def validar_niveis(niveis):
    if not isinstance(niveis, dict) or set(niveis) != set(CHAKRAS):
        raise ValueError('Informe os sete níveis de equilíbrio.')
    valores = {}
    for chakra in CHAKRAS:
        valor = niveis[chakra]
        if isinstance(valor, bool) or not isinstance(valor, int) or not 0 <= valor <= 100:
            raise ValueError('Cada nível deve ser um número inteiro entre 0 e 100.')
        valores[chakra] = valor
    return valores


def criar_avaliacao(terapeuta_id, paciente_id, niveis, observacoes=None):
    valores = validar_niveis(niveis)
    conn = get_db_connection()
    if not conn:
        raise RuntimeError('Não foi possível conectar ao banco de dados.')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO avaliacoes_chakras (terapeuta_id, paciente_id, observacoes) VALUES (%s, %s, %s)',
            (terapeuta_id, paciente_id, (observacoes or '').strip() or None),
        )
        avaliacao_id = cursor.lastrowid
        cursor.executemany(
            'INSERT INTO avaliacao_chakra_itens (avaliacao_id, chakra, nivel_equilibrio) VALUES (%s, %s, %s)',
            [(avaliacao_id, chakra, valores[chakra]) for chakra in CHAKRAS],
        )
        conn.commit()
        return avaliacao_id
    except Error:
        conn.rollback()
        logger.exception('Erro ao criar avaliação de chakras.')
        raise
    finally:
        cursor.close()
        conn.close()


def listar_avaliacoes(terapeuta_id, paciente_id):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            '''SELECT id, paciente_id, observacoes, criado_em
               FROM avaliacoes_chakras
               WHERE terapeuta_id = %s AND paciente_id = %s
               ORDER BY criado_em DESC, id DESC''',
            (terapeuta_id, paciente_id),
        )
        avaliacoes = cursor.fetchall()
        for avaliacao in avaliacoes:
            cursor.execute(
                'SELECT chakra, nivel_equilibrio FROM avaliacao_chakra_itens WHERE avaliacao_id = %s',
                (avaliacao['id'],),
            )
            avaliacao['itens'] = {row['chakra']: row['nivel_equilibrio'] for row in cursor.fetchall()}
        return avaliacoes
    except Error:
        logger.exception('Erro ao consultar avaliações de chakras.')
        return []
    finally:
        cursor.close()
        conn.close()


def buscar_avaliacao(terapeuta_id, paciente_id, avaliacao_id):
    return next((item for item in listar_avaliacoes(terapeuta_id, paciente_id)
                 if item['id'] == avaliacao_id), None)
