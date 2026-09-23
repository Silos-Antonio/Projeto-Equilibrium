import bcrypt
import pytest

from unittest.mock import MagicMock

from app.services import auth


@pytest.fixture
def banco_mock(monkeypatch):
    cursor = MagicMock()
    conn = MagicMock()

    conn.cursor.return_value = cursor

    monkeypatch.setattr(
        auth,
        'get_db_connection',
        lambda: conn
    )

    return conn, cursor


def criar_usuario_mock(
    situacao='ATIVO',
    senha='senha-segura'
):
    senha_hash = bcrypt.hashpw(
        senha.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    return {
        'id': 1,
        'nome': 'Usuário Teste',
        'email': 'teste@equilibrium.com',
        'senha': senha_hash,
        'perfil': 'TERAPEUTA',
        'situacao': situacao,
    }


def test_usuario_ativo_com_senha_correta_autentica(banco_mock):
    conn, cursor = banco_mock

    cursor.fetchone.return_value = criar_usuario_mock()

    usuario = auth.verificar_credenciais(
        'teste@equilibrium.com',
        'senha-segura'
    )

    assert usuario is not None
    assert usuario['id'] == 1
    assert usuario['situacao'] == 'ATIVO'

    conn.close.assert_called_once()


def test_usuario_inativo_nao_autentica(banco_mock):
    _, cursor = banco_mock

    cursor.fetchone.return_value = criar_usuario_mock(
        situacao='INATIVO'
    )

    usuario = auth.verificar_credenciais(
        'teste@equilibrium.com',
        'senha-segura'
    )

    assert usuario is None

def test_senha_incorreta_nao_autentica(banco_mock):
    _, cursor = banco_mock

    cursor.fetchone.return_value = criar_usuario_mock()

    usuario = auth.verificar_credenciais(
        'teste@equilibrium.com',
        'senha-errada'
    )

    assert usuario is None


def test_usuario_inexistente_nao_autentica(banco_mock):
    _, cursor = banco_mock

    cursor.fetchone.return_value = None

    usuario = auth.verificar_credenciais(
        'naoexiste@equilibrium.com',
        'qualquer-senha'
    )

    assert usuario is None


def test_falha_de_conexao_nao_autentica(monkeypatch):
    monkeypatch.setattr(
        auth,
        'get_db_connection',
        lambda: None
    )

    usuario = auth.verificar_credenciais(
        'teste@equilibrium.com',
        'senha-segura'
    )

    assert usuario is None