import bcrypt
import mysql.connector
from app.services.db import get_db_connection

def criar_terapeuta(nome, email, telefone, senha):
    # 1. Gerar hash da senha
    senha_bytes = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_senha = bcrypt.hashpw(senha_bytes, salt)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 2. Inserir no banco
        query = """
            INSERT INTO usuarios (nome, email, telefone, senha) 
            VALUES (%s, %s, %s, %s)
        """
        valores = (nome, email, telefone, hash_senha.decode('utf-8'))
        cursor.execute(query, valores)
        conn.commit()
        return True, "Terapeuta cadastrado com sucesso."
        
    except mysql.connector.Error as err:
        # Verifica se o erro é de restrição UNIQUE (código de erro MySQL 1062)
        if err.errno == 1062:
            return False, "E-mail ou telefone já cadastrados no sistema."
        # Outros erros de banco
        return False, "Erro interno de banco de dados."
    finally:
        cursor.close()
        conn.close()
