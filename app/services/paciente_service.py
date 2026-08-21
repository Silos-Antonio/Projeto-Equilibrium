import mysql.connector

from app.services.db import get_db_connection

def listar_pacientes_do_terapeuta(terapeuta_id):
    """
    Lista somente os pacientes cadastrados pelo terapeuta autenticado.
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT p.id, p.nome, p.email, p.telefone, p.observacoes, p.criado_em 
        FROM pacientes p
        WHERE p.terapeuta_id = %s
        ORDER BY p.nome ASC
    """
    
    cursor.execute(query, (terapeuta_id,))
    pacientes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return pacientes

def criar_paciente(terapeuta_id, nome, email, telefone="", observacoes=""):
    """
    Salva um paciente associado ao terapeuta que o cadastrou.
    """
    conn = get_db_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        query_paciente = """
            INSERT INTO pacientes (terapeuta_id, nome, email, telefone, observacoes)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query_paciente, (terapeuta_id, nome, email or None, telefone or None, observacoes or None))

        conn.commit()
        sucesso = True
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir paciente: {e}")
        sucesso = False
        
    finally:
        cursor.close()
        conn.close()
        
    return sucesso


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
            return False, 'Este telefone já está cadastrado para outro paciente.'
        return False, 'Não foi possível atualizar o paciente.'
    finally:
        cursor.close()
        conn.close()
