from app.services.db import get_db_connection

import bcrypt


def verificar_credenciais(email, senha):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT id, senha, perfil, situacao
        FROM usuarios
        WHERE email = %s
    """

    cursor.execute(query, (email,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if not usuario:
        return None

    senha_valida = bcrypt.checkpw(
        senha.encode('utf-8'),
        usuario['senha'].encode('utf-8')
    )

    if not senha_valida:
        return None

    if usuario['situacao'] != 'ATIVO':
        return None

    return {
        'id': usuario['id'],
        'perfil': usuario['perfil']
    }