import pytest

from app import create_app
from app.utils.decorators import admin_required, login_required


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv(
        'SECRET_KEY',
        'test-secret-key'
    )

    app = create_app()

    app.config.update(
        TESTING=True,
    )

    @app.route('/__test__/protected')
    @login_required
    def protected_test():
        return 'acesso permitido', 200

    @app.route('/__test__/admin')
    @admin_required
    def admin_test():
        return 'acesso administrativo permitido', 200

    yield app


@pytest.fixture
def client(app):
    return app.test_client()