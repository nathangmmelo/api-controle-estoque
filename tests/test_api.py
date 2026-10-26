import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Banco em memória, isolado para os testes
engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def novo_produto(client, **extra):
    corpo = {"nome": "Extintor ABC 4kg", "preco": 120.0, "quantidade": 10, "estoque_minimo": 3}
    corpo.update(extra)
    return client.post("/produtos", json=corpo)


def test_criar_e_listar(client):
    r = novo_produto(client)
    assert r.status_code == 201
    assert r.json()["nome"] == "Extintor ABC 4kg"
    assert len(client.get("/produtos").json()) == 1


def test_nome_duplicado_retorna_409(client):
    novo_produto(client)
    assert novo_produto(client).status_code == 409


def test_validacao_preco_invalido(client):
    assert novo_produto(client, preco=-5).status_code == 422


def test_produto_inexistente_404(client):
    assert client.get("/produtos/999").status_code == 404


def test_atualizar_parcialmente(client):
    pid = novo_produto(client).json()["id"]
    r = client.patch(f"/produtos/{pid}", json={"preco": 150.0})
    assert r.status_code == 200
    assert r.json()["preco"] == 150.0
    assert r.json()["nome"] == "Extintor ABC 4kg"


def test_entrada_e_saida_atualizam_estoque(client):
    pid = novo_produto(client).json()["id"]
    client.post(f"/produtos/{pid}/movimentacoes", json={"tipo": "entrada", "quantidade": 5})
    client.post(f"/produtos/{pid}/movimentacoes", json={"tipo": "saida", "quantidade": 3})
    assert client.get(f"/produtos/{pid}").json()["quantidade"] == 12
    assert len(client.get(f"/produtos/{pid}/movimentacoes").json()) == 2


def test_saida_maior_que_estoque_falha(client):
    pid = novo_produto(client, quantidade=2).json()["id"]
    r = client.post(f"/produtos/{pid}/movimentacoes", json={"tipo": "saida", "quantidade": 5})
    assert r.status_code == 400
    assert client.get(f"/produtos/{pid}").json()["quantidade"] == 2


def test_estoque_baixo(client):
    novo_produto(client, nome="Mangueira", quantidade=2, estoque_minimo=5)
    novo_produto(client, nome="Placa Saída", quantidade=50, estoque_minimo=5)
    baixos = client.get("/produtos/estoque-baixo").json()
    assert [p["nome"] for p in baixos] == ["Mangueira"]


def test_remover(client):
    pid = novo_produto(client).json()["id"]
    assert client.delete(f"/produtos/{pid}").status_code == 204
    assert client.get(f"/produtos/{pid}").status_code == 404
