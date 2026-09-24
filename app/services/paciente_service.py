import mysql.connector

from app.services.db import get_db_connection

import logging

from mysql.connector import Error, IntegrityError

from app.services.db import get_db_connection

from app.utils.normalizer import normalizar_telefone


logger = logging.getLogger(__name__)

def listar_pacientes_do_terapeuta(terapeuta_id, limite=20, deslocamento=0):
    """
    Lista os pacientes cadastrados pelo terapeuta autenticado com paginação.
    Retorna a lista de pacientes e o número total de pacientes.
    """
    conn = get_db_connection()
    if not conn:
        return [], 0
        
    cursor = conn.cursor(dictionary=True)
    
    # Conta o total de pacientes para a paginação
    cursor.execute("SELECT COUNT(*) as total FROM pacientes WHERE terapeuta_id = %s", (terapeuta_id,))
    total_pacientes = cursor.fetchone()['total']
    
    # Busca apenas os pacientes da página atual
    query = """
        SELECT p.id, p.nome, p.email, p.telefone, p.observacoes, p.criado_em 
        FROM pacientes p
        WHERE p.terapeuta_id = %s
        ORDER BY p.nome ASC
        LIMIT %s OFFSET %s
    """
    
    cursor.execute(query, (terapeuta_id, limite, deslocamento))
    pacientes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return pacientes, total_pacientes

def criar_paciente(
    terapeuta_id,
    nome,
    email,
    telefone,
    observacoes
):
    conn = get_db_connection()

    if not conn:
        return (
            False,
            'Não foi possível conectar ao banco de dados.'
        )

    cursor = conn.cursor()
    telefone = normalizar_telefone(telefone)

    try:
        cursor.execute(
            """
            INSERT INTO pacientes (
                terapeuta_id,
                nome,
                email,
                telefone,
                observacoes
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                terapeuta_id,
                nome,
                email or None,
                telefone or None,
                observacoes or None,
            )
        )

        conn.commit()

        return True, None

    except IntegrityError as error:
        conn.rollback()

        if (
            error.errno == 1062
            and 'uq_pacientes_terapeuta_telefone'
            in str(error)
        ):
            return (
                False,
                'Este telefone já está cadastrado '
                'para outro paciente deste terapeuta.'
            )

        logger.exception(
            'Erro de integridade ao cadastrar paciente.'
        )

        return (
            False,
            'Não foi possível cadastrar o paciente.'
        )

    except Error:
        conn.rollback()

        logger.exception(
            'Erro ao cadastrar paciente.'
        )

        return (
            False,
            'Não foi possível cadastrar o paciente.'
        )

    finally:
        cursor.close()
        conn.close()

def buscar_paciente_do_terapeuta(terapeuta_id, paciente_id):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT id, nome, email, telefone, observacoes FROM pacientes WHERE id = %s AND terapeuta_id = %s', (paciente_id, terapeuta_id))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def atualizar_paciente(terapeuta_id, paciente_id, nome, email, telefone, observacoes):
    conn = get_db_connection()
    if not conn:
        return False, 'Não foi possível conectar ao banco de dados.'
    
    cursor = conn.cursor()
    telefone = normalizar_telefone(telefone)
    
    try:
        cursor.execute('UPDATE pacientes SET nome = %s, email = %s, telefone = %s, observacoes = %s WHERE id = %s AND terapeuta_id = %s', (nome, email or None, telefone or None, observacoes or None, paciente_id, terapeuta_id))
        if cursor.rowcount != 1:
            conn.rollback()
            return False, 'Paciente não encontrado.'
        conn.commit()
        return True, 'Dados do paciente atualizados com sucesso.'
    except mysql.connector.Error as error:
        conn.rollback()
        if error.errno == 1062:
            return False, 'Este telefone já está cadastrado para outro paciente deste terapeuta.'
        return False, 'Não foi possível atualizar o paciente.'
    finally:
        cursor.close()
        conn.close()
