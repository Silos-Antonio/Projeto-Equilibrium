from app.services.db import get_db_connection
import mysql.connector


def listar_usuarios():
    """Retorna todos os usuários cadastrados no sistema."""

    conn = get_db_connection()

    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                nome,
                email,
                telefone,
                perfil,
                situacao,
                criado_em
            FROM usuarios
            ORDER BY nome ASC
            """
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def alterar_situacao_usuario(usuario_id):
    """Alterna a situação de um terapeuta entre ATIVO e INATIVO."""

    conn = get_db_connection()

    if not conn:
        return False, 'Não foi possível conectar ao banco de dados.'

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT perfil, situacao
            FROM usuarios
            WHERE id = %s
            """,
            (usuario_id,)
        )

        usuario = cursor.fetchone()

        if not usuario:
            return False, 'Usuário não encontrado.'

        if usuario['perfil'] != 'TERAPEUTA':
            return False, 'A situação deste usuário não pode ser alterada.'

        nova_situacao = (
            'INATIVO'
            if usuario['situacao'] == 'ATIVO'
            else 'ATIVO'
        )

        cursor.execute(
            """
            UPDATE usuarios
            SET situacao = %s
            WHERE id = %s
            """,
            (nova_situacao, usuario_id)
        )

        conn.commit()

        return True, 'Situação do terapeuta atualizada com sucesso.'

    except mysql.connector.Error as error:
        conn.rollback()
        print(f'Erro ao alterar situação: {error}')

        return False, 'Não foi possível alterar a situação do usuário.'

    finally:
        cursor.close()
        conn.close()

def buscar_usuario_por_id(usuario_id):
    """Busca um usuário específico pelo ID."""

    conn = get_db_connection()

    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                nome,
                email,
                telefone,
                perfil,
                situacao,
                criado_em
            FROM usuarios
            WHERE id = %s
            """,
            (usuario_id,)
        )

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

def atualizar_terapeuta(usuario_id, nome, email, telefone):
    """Atualiza os dados de um terapeuta."""

    conn = get_db_connection()

    if not conn:
        return False, 'Não foi possível conectar ao banco de dados.'

    cursor = conn.cursor(dictionary=True)

    try:
        # Confirma que o usuário existe e é um terapeuta
        cursor.execute(
            """
            SELECT id, perfil
            FROM usuarios
            WHERE id = %s
            """,
            (usuario_id,)
        )

        usuario = cursor.fetchone()

        if not usuario:
            return False, 'Usuário não encontrado.'

        if usuario['perfil'] != 'TERAPEUTA':
            return False, 'Apenas terapeutas podem ser editados.'

        # Verifica se e-mail ou telefone pertencem a outro usuário
        cursor.execute(
            """
            SELECT id
            FROM usuarios
            WHERE (email = %s OR telefone = %s)
              AND id <> %s
            LIMIT 1
            """,
            (email, telefone, usuario_id)
        )

        duplicado = cursor.fetchone()

        if duplicado:
            return False, 'E-mail ou telefone já cadastrados no sistema.'

        cursor.execute(
            """
            UPDATE usuarios
            SET nome = %s,
                email = %s,
                telefone = %s
            WHERE id = %s
            """,
            (nome, email, telefone, usuario_id)
        )

        conn.commit()

        return True, 'Dados do terapeuta atualizados com sucesso.'

    except mysql.connector.Error as error:
        conn.rollback()
        print(f'Erro ao atualizar terapeuta: {error}')

        return False, 'Não foi possível atualizar os dados do terapeuta.'

    finally:
        cursor.close()
        conn.close()