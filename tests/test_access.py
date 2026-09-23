from app.utils import decorators


def test_rota_protegida_recusa_usuario_sem_sessao(client):
    response = client.get('/__test__/protected')

    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_usuario_ativo_acessa_rota_protegida(
    client,
    monkeypatch
):
    monkeypatch.setattr(
        decorators,
        'buscar_usuario_ativo_por_id',
        lambda usuario_id: {
            'id': usuario_id,
            'nome': 'Usuário Teste',
            'perfil': 'TERAPEUTA',
        }
    )

    with client.session_transaction() as sessao:
        sessao['usuario_id'] = 1

    response = client.get('/__test__/protected')

    assert response.status_code == 200
    assert 'acesso permitido' in response.get_data(
        as_text=True
    )

def test_usuario_inativado_tem_sessao_encerrada(
    client,
    monkeypatch
):
    monkeypatch.setattr(
        decorators,
        'buscar_usuario_ativo_por_id',
        lambda usuario_id: None
    )

    with client.session_transaction() as sessao:
        sessao['usuario_id'] = 1
        sessao['perfil'] = 'TERAPEUTA'
        sessao['nome'] = 'Teste'

    response = client.get('/__test__/protected')

    assert response.status_code == 302
    assert '/login' in response.headers['Location']

    with client.session_transaction() as sessao:
        assert 'usuario_id' not in sessao
        assert 'perfil' not in sessao
        assert 'nome' not in sessao

def test_terapeuta_nao_acessa_rota_admin(
    client,
    monkeypatch
):
    monkeypatch.setattr(
        decorators,
        'buscar_usuario_ativo_por_id',
        lambda usuario_id: {
            'id': usuario_id,
            'nome': 'Usuário Teste',
            'perfil': 'TERAPEUTA',
        }
    )

    with client.session_transaction() as sessao:
        sessao['usuario_id'] = 1

    response = client.get('/__test__/admin')

    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']

def test_admin_acessa_rota_admin(
    client,
    monkeypatch
):
    monkeypatch.setattr(
        decorators,
        'buscar_usuario_ativo_por_id',
        lambda usuario_id: {
            'id': usuario_id,
            'nome': 'Admin Teste',
            'perfil': 'ADMIN',
        }
    )

    with client.session_transaction() as sessao:
        sessao['usuario_id'] = 1

    response = client.get('/__test__/admin')

    assert response.status_code == 200

    assert (
        'acesso administrativo permitido'
        in response.get_data(as_text=True)
    )

def test_perfil_da_sessao_nao_define_permissao_admin(
    client,
    monkeypatch
):
    monkeypatch.setattr(
        decorators,
        'buscar_usuario_ativo_por_id',
        lambda usuario_id: {
            'id': usuario_id,
            'nome': 'Usuário Teste',
            'perfil': 'TERAPEUTA',
        }
    )

    with client.session_transaction() as sessao:
        sessao['usuario_id'] = 1

        # Sessão antiga ainda acredita que é ADMIN
        sessao['perfil'] = 'ADMIN'

    response = client.get('/__test__/admin')

    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']