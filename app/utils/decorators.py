from functools import wraps

from flask import session, redirect, url_for, flash


def login_required(f):
    """
    Decorador que verifica se o usuário está logado.

    Se não estiver, bloqueia o acesso e manda de volta para o login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'usuario_id' not in session:
            flash('Acesso negado. Por favor, faça login.', 'error')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorador que verifica se o usuário possui perfil de administrador.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Primeiro verifica se existe um usuário autenticado
        if 'usuario_id' not in session:
            flash('Acesso negado. Por favor, faça login.', 'error')
            return redirect(url_for('auth.login'))

        # Depois verifica se o usuário é administrador
        if session.get('perfil') != 'ADMIN':
            flash('Você não tem permissão para acessar esta área.', 'error')
            return redirect(url_for('dashboard.index'))

        return f(*args, **kwargs)

    return decorated_function