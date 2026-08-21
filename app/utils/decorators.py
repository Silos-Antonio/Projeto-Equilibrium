from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """
    Decorador que verifica se o usuário está logado.
    Se não estiver, bloqueia o acesso e manda de volta pro login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se o 'terapeuta_id' NÃO está no cookie de sessão
        if 'terapeuta_id' not in session:
            flash('Acesso negado. Por favor, faça login.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function