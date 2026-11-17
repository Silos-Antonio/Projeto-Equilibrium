import pytest
from mysql.connector import Error

from app.services import chakra_service


@pytest.fixture
def niveis_validos():
    return {chakra: 75 for chakra in chakra_service.CHAKRAS}


class CursorFake:
    def __init__(self, fail_items=False):
        self.lastrowid = 42
        self.fail_items = fail_items
        self.calls = []
    def execute(self, query, params=None):
        self.calls.append((query, params))
    def executemany(self, query, params):
        self.calls.append((query, params))
        if self.fail_items:
            raise Error('falha simulada')
    def close(self):
        pass


class ConnectionFake:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.commits = 0
        self.rollbacks = 0
        self.closed = False
    def cursor(self, **kwargs):
        return self.fake_cursor
    def commit(self):
        self.commits += 1
    def rollback(self):
        self.rollbacks += 1
    def close(self):
        self.closed = True


def test_cria_avaliacao_com_sete_itens(monkeypatch, niveis_validos):
    cursor = CursorFake()
    conn = ConnectionFake(cursor)
    monkeypatch.setattr(chakra_service, 'get_db_connection', lambda: conn)

    resultado = chakra_service.criar_avaliacao(7, 12, niveis_validos)

    assert resultado == 42
    assert len(cursor.calls[1][1]) == 7
    assert len({item[1] for item in cursor.calls[1][1]}) == 7
    assert conn.commits == 1
    assert conn.rollbacks == 0


@pytest.mark.parametrize('valor', [-1, 101])
def test_rejeita_percentual_fora_do_intervalo(valor, niveis_validos):
    niveis_validos['BASICO'] = valor
    with pytest.raises(ValueError):
        chakra_service.validar_niveis(niveis_validos)


def test_rejeita_avaliacao_incompleta(niveis_validos):
    niveis_validos.pop('BASICO')
    with pytest.raises(ValueError):
        chakra_service.validar_niveis(niveis_validos)


def test_chave_de_itens_e_unica_por_chakra():
    from pathlib import Path
    sql = (Path(__file__).parents[1] / 'database/migrations/004_avaliacoes_chakras.sql').read_text(encoding='utf-8')
    assert 'PRIMARY KEY (avaliacao_id, chakra)' in sql


def test_historico_filtra_terapeuta_e_paciente(monkeypatch):
    class HistoryCursor(CursorFake):
        def __init__(self):
            super().__init__()
            self.responses = [[{'id': 3, 'paciente_id': 12, 'observacoes': None, 'criado_em': None}], [{'chakra': 'BASICO', 'nivel_equilibrio': 30}]]
        def execute(self, query, params=None):
            super().execute(query, params)
        def fetchall(self):
            return self.responses.pop(0)
    cursor = HistoryCursor()
    monkeypatch.setattr(chakra_service, 'get_db_connection', lambda: ConnectionFake(cursor))

    result = chakra_service.listar_avaliacoes(7, 12)

    assert result[0]['itens'] == {'BASICO': 30}
    assert cursor.calls[0][1] == (7, 12)
    assert 'terapeuta_id = %s AND paciente_id = %s' in cursor.calls[0][0]
    assert 'ORDER BY criado_em DESC' in cursor.calls[0][0]


def test_rollback_em_falha_ao_gravar_itens(monkeypatch, niveis_validos):
    conn = ConnectionFake(CursorFake(fail_items=True))
    monkeypatch.setattr(chakra_service, 'get_db_connection', lambda: conn)
    with pytest.raises(Error):
        chakra_service.criar_avaliacao(7, 12, niveis_validos)
    assert conn.rollbacks == 1
    assert conn.commits == 0
