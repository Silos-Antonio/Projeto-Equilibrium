from unittest.mock import MagicMock

from app import cli


def test_create_admin_com_sucesso(
    app,
    monkeypatch
):
    monkeypatch.setattr(
        cli,
        'existe_admin',
        lambda: False
    )

    criar_admin_mock = MagicMock(
        return_value=(True, None)
    )

    monkeypatch.setattr(
        cli,
        'criar_admin',
        criar_admin_mock
    )

    runner = app.test_cli_runner()

    result = runner.invoke(
        args=['create-admin'],
        input=(
            'Admin Teste\n'
            'admin@teste.com\n'
            '18999999999\n'
            'senha-segura\n'
            'senha-segura\n'
        )
    )

    assert result.exit_code == 0

    assert (
        'Administrador criado com sucesso.'
        in result.output
    )

    criar_admin_mock.assert_called_once_with(
        nome='Admin Teste',
        email='admin@teste.com',
        telefone='18999999999',
        senha='senha-segura',
    )

def test_create_admin_recusa_quando_admin_ja_existe(
    app,
    monkeypatch
):
    monkeypatch.setattr(
        cli,
        'existe_admin',
        lambda: True
    )

    criar_admin_mock = MagicMock()

    monkeypatch.setattr(
        cli,
        'criar_admin',
        criar_admin_mock
    )

    runner = app.test_cli_runner()

    result = runner.invoke(
        args=['create-admin']
    )

    assert result.exit_code == 0

    assert (
        'Já existe um administrador cadastrado.'
        in result.output
    )

    criar_admin_mock.assert_not_called()

def test_create_admin_recusa_senha_curta(
    app,
    monkeypatch
):
    monkeypatch.setattr(
        cli,
        'existe_admin',
        lambda: False
    )

    criar_admin_mock = MagicMock()

    monkeypatch.setattr(
        cli,
        'criar_admin',
        criar_admin_mock
    )

    runner = app.test_cli_runner()

    result = runner.invoke(
        args=['create-admin'],
        input=(
            'Admin Teste\n'
            'admin@teste.com\n'
            '18999999999\n'
            '1234567\n'
            '1234567\n'
        )
    )

    assert result.exit_code != 0

    assert (
        'A senha deve possuir pelo menos 8 caracteres.'
        in result.output
    )

    criar_admin_mock.assert_not_called()

def test_create_admin_exibe_erro_do_service(
    app,
    monkeypatch
):
    monkeypatch.setattr(
        cli,
        'existe_admin',
        lambda: False
    )

    monkeypatch.setattr(
        cli,
        'criar_admin',
        lambda **kwargs: (
            False,
            'E-mail ou telefone já cadastrado.'
        )
    )

    runner = app.test_cli_runner()

    result = runner.invoke(
        args=['create-admin'],
        input=(
            'Admin Teste\n'
            'admin@teste.com\n'
            '18999999999\n'
            'senha-segura\n'
            'senha-segura\n'
        )
    )

    assert result.exit_code != 0

    assert (
        'E-mail ou telefone já cadastrado.'
        in result.output
    )