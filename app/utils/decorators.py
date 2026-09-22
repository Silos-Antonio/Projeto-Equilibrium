from functools import wraps

from flask import flash, redirect, session, url_for

from app.services.auth import buscar_usuario_ativo_por_id


def _buscar_usuario_da_sessao():
    """Valida no banco se o usuário da sessão ainda existe e está ativo."""
    usuario_id = session.get('usuario_id')

    if not usuario_id:
        return None

    usuario = buscar_usuario_ativo_por_id(usuario_id)

    if not usuario:
        session.clear()
        return None

    return usuario

def login_required(f):
    """Exige uma sessão associada a um usuário que continue ativo."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario = _buscar_usuario_da_sessao()

        if not usuario:
            flash(
                'Acesso negado. Por favor, faça login.',
                'error'
            )
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated_function

def admin_required(f):
    """Exige um usuário ativo com perfil de administrador."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario = _buscar_usuario_da_sessao()

        if not usuario:
            flash(
                'Acesso negado. Por favor, faça login.',
                'error'
            )
            return redirect(url_for('auth.login'))

        if usuario['perfil'] != 'ADMIN':
            flash(
                'Você não tem permissão para acessar esta área.',
                'error'
            )
            return redirect(url_for('dashboard.index'))

        return f(*args, **kwargs)

    return decorated_function