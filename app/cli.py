import click
from flask.cli import with_appcontext

from app.services.user_service import criar_admin, existe_admin


@click.command('create-admin')
@with_appcontext
def create_admin_command():
    """Cria o administrador inicial da aplicação."""

    if existe_admin():
        click.echo(
            'Já existe um administrador cadastrado. '
            'Nenhuma alteração foi realizada.'
        )
        return

    click.echo('Criação do administrador inicial')
    click.echo()

    nome = click.prompt('Nome').strip()
    email = click.prompt('E-mail').strip().lower()
    telefone = click.prompt('Telefone').strip()

    senha = click.prompt(
        'Senha',
        hide_input=True,
        confirmation_prompt=True
    )

    if len(senha) < 8:
        raise click.ClickException(
            'A senha deve possuir pelo menos 8 caracteres.'
        )

    sucesso, erro = criar_admin(
        nome=nome,
        email=email,
        telefone=telefone,
        senha=senha,
    )

    if not sucesso:
        raise click.ClickException(erro)

    click.echo()
    click.secho(
        'Administrador criado com sucesso.',
        fg='green'
    )


def register_commands(app):
    app.cli.add_command(create_admin_command)