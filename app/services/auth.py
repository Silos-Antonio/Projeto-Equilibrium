from app.services.db import get_db_connection

import bcrypt


from app.services.db import get_db_connection
import bcrypt

def verificar_credenciais(email, senha):
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT id, nome, senha, perfil, situacao
        FROM usuarios
        WHERE email = %s
    """

    cursor.execute(query, (email,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if not usuario:
        return None

    # Valida a senha com bcrypt
    senha_valida = bcrypt.checkpw(
        senha.encode('utf-8'),
        usuario['senha'].encode('utf-8')
    )

    if not senha_valida:
        return None

    # Retorna o dicionário completo do usuário se tudo estiver correto
    return usuario