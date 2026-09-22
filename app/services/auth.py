import bcrypt

from app.services.db import get_db_connection


def verificar_credenciais(email, senha):
    conn = get_db_connection()

    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT id, nome, senha, perfil, situacao
            FROM usuarios
            WHERE email = %s
        """

        cursor.execute(query, (email,))
        usuario = cursor.fetchone()

    finally:
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

    return usuario


def buscar_usuario_ativo_por_id(usuario_id):
    """Retorna o usuário da sessão somente se ele ainda estiver ativo."""
    conn = get_db_connection()

    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, nome, perfil
            FROM usuarios
            WHERE id = %s
              AND situacao = 'ATIVO'
            """,
            (usuario_id,)
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()