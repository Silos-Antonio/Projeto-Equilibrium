import bcrypt
from app.services.db import get_db_connection

def criar_terapeuta_teste():
    conn = get_db_connection()
    if not conn:
        print("Erro: Não foi possível se conectar ao banco de dados")
        return
    
    cursor = conn.cursor()

    #  Senha padrão de teste
    senha_plana = "123456" 

    #  Gerar hash seguro com salt automático
    senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'), bcrypt.gensalt())

    try:
        query = """
                INSERT INTO usuarios (nome, email, telefone, senha)
                VALUES (%s, %s, %s, %s)
                """
        valores = ('Terapeuta Equilibrium 2', 'admin2@equilibrium.com', '12999999999', senha_hash)

        cursor.execute(query, valores)
        conn.commit()
        print(f"Sucesso! Usuário 'admin@equilibrium' foi criado com senha {senha_plana}")

    except Exception as e:
        print(f"Erro ao cadastrar usuário: {e}")
    finally: 
        cursor.close()
        conn.close()

if __name__ == "__main__":
    criar_terapeuta_teste()
