from app.services.db import get_db_connection

def listar_pacientes_do_terapeuta(terapeuta_id):
    """
    Busca os pacientes através do relacionamento entre as tabelas (INNER JOIN).
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    cursor = conn.cursor(dictionary=True)
    
    # Fazemos a junção (JOIN) entre a tabela pacientes e a tabela associativa
    query = """
        SELECT p.id, p.nome, p.email, p.telefone, p.observacoes, p.criado_em 
        FROM pacientes p
        INNER JOIN terapeuta_paciente tp ON p.id = tp.paciente_id
        WHERE tp.terapeuta_id = %s
        ORDER BY p.nome ASC
    """
    
    cursor.execute(query, (terapeuta_id,))
    pacientes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return pacientes

def criar_paciente(terapeuta_id, nome, email, telefone="", observacoes=""):
    """
    Salva o paciente e cria o vínculo relacional com o terapeuta usando uma Transação.
    """
    conn = get_db_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        # 1. Inserimos o paciente na tabela isolada de pacientes
        query_paciente = """
            INSERT INTO pacientes (nome, email, telefone, observacoes) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_paciente, (nome, email, telefone, observacoes))
        
        # O MySQL nos devolve qual foi o ID gerado para esse novo paciente
        paciente_id = cursor.lastrowid
        
        # 2. Criamos o vínculo do terapeuta com este paciente
        query_vinculo = "INSERT INTO terapeuta_paciente (terapeuta_id, paciente_id) VALUES (%s, %s)"
        cursor.execute(query_vinculo, (terapeuta_id, paciente_id))
        
        # 3. Confirmamos as duas operações no banco simultaneamente (Transação)
        conn.commit()
        sucesso = True
        
    except Exception as e:
        # Se der erro no vínculo, ele desfaz a criação do paciente (Rollback)
        conn.rollback()
        print(f"Erro ao inserir paciente: {e}")
        sucesso = False
        
    finally:
        cursor.close()
        conn.close()
        
    return sucesso