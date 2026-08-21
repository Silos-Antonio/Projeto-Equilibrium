from app.services.db import get_db_connection
import bcrypt 

def verificar_credenciais(email, senha):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT id, senha FROM usuarios WHERE email = %s"
    cursor.execute(query, (email,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
        return usuario['id']
    return None