from app.utils import decorators


def test_rota_de_avaliacao_exige_autenticacao(client, app):
    app.config['WTF_CSRF_ENABLED'] = False
    response = client.post('/pacientes/1/avaliacoes-chakras')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_rota_nao_permite_paciente_de_outro_terapeuta(client, monkeypatch, app):
    from app.routes import chakra_routes
    app.config['WTF_CSRF_ENABLED'] = False
    monkeypatch.setattr(decorators, 'buscar_usuario_ativo_por_id', lambda usuario_id: {'id': usuario_id, 'perfil': 'TERAPEUTA'})
    monkeypatch.setattr(chakra_routes, 'buscar_paciente_do_terapeuta', lambda terapeuta_id, paciente_id: None)
    with client.session_transaction() as session:
        session['usuario_id'] = 2
    response = client.post('/pacientes/999/avaliacoes-chakras')
    assert response.status_code == 404
