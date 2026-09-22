import bcrypt
import mysql.connector

from app.services.db import get_db_connection


def criar_usuario(nome, email, telefone, senha, perfil='TERAPEUTA'):
    """Cria um usuário com senha protegida por bcrypt."""

    senha_bytes = senha.encode('utf-8')
    hash_senha = bcrypt.hashpw(
        senha_bytes,
        bcrypt.gensalt()
    )

    conn = get_db_connection()

    if not conn:
        return False, 'Não foi possível conectar ao banco de dados.'

    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO usuarios (
                nome,
                email,
                telefone,
                senha,
                perfil,
                situacao
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        valores = (
            nome,
            email,
            telefone,
            hash_senha.decode('utf-8'),
            perfil,
            'ATIVO'
        )

        cursor.execute(query, valores)
        conn.commit()

        return True, 'Usuário cadastrado com sucesso.'

    except mysql.connector.Error as err:
        conn.rollback()

        if err.errno == 1062:
            return False, 'E-mail ou telefone já cadastrados no sistema.'

        return False, 'Erro interno de banco de dados.'

    finally:
        cursor.close()
        conn.close()


def criar_terapeuta(nome, email, telefone, senha):
    """Cria um usuário com perfil de terapeuta."""

    return criar_usuario(
        nome=nome,
        email=email,
        telefone=telefone,
        senha=senha,
        perfil='TERAPEUTA'
    )


def criar_admin(nome, email, telefone, senha):
    """Cria um usuário com perfil de administrador."""

    return criar_usuario(
        nome=nome,
        email=email,
        telefone=telefone,
        senha=senha,
        perfil='ADMIN'
    )

def existe_admin():
    conn = get_db_connection()

    if not conn:
        return False

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id
            FROM usuarios
            WHERE perfil = 'ADMIN'
            LIMIT 1
            """
        )

        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conn.close()


def criar_admin(nome, email, telefone, senha):
    conn = get_db_connection()

    if not conn:
        return False, 'Não foi possível conectar ao banco de dados.'

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id
            FROM usuarios
            WHERE email = %s
               OR telefone = %s
            LIMIT 1
            """,
            (email, telefone)
        )

        if cursor.fetchone():
            return False, 'E-mail ou telefone já cadastrado.'

        senha_hash = bcrypt.hashpw(
            senha.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        cursor.execute(
            """
            INSERT INTO usuarios (
                nome,
                email,
                telefone,
                senha,
                perfil,
                situacao
            )
            VALUES (%s, %s, %s, %s, 'ADMIN', 'ATIVO')
            """,
            (
                nome,
                email,
                telefone,
                senha_hash,
            )
        )

        conn.commit()

        return True, None

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()