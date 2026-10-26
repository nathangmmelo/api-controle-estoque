# 📦 API de Controle de Estoque

API REST para gerenciar **produtos** e **movimentações de estoque** (entradas e saídas), com validação de dados, regras de negócio e testes automatizados.

Feita com **Python, FastAPI, SQLAlchemy e SQLite**.

## ✨ Funcionalidades

- CRUD completo de produtos
- Registro de entradas e saídas de estoque
- Bloqueio de saída maior que o estoque disponível (regra de negócio)
- Histórico de movimentações por produto
- Listagem de produtos com **estoque baixo** (quantidade ≤ estoque mínimo)
- Validação automática dos dados (Pydantic) e códigos HTTP corretos (201, 204, 400, 404, 409, 422)
- Documentação interativa gerada automaticamente (Swagger)
- 9 testes automatizados com banco isolado em memória

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| FastAPI | Framework da API |
| SQLAlchemy 2.0 | ORM |
| SQLite | Banco de dados |
| Pydantic | Validação e schemas |
| Pytest + HTTPX | Testes |

## 🚀 Como rodar

```bash
# 1. Clonar o repositório
git clone https://github.com/nathangmmelo/api-controle-estoque.git
cd api-controle-estoque

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Iniciar a API
uvicorn app.main:app --reload
```

Acesse a documentação interativa em **http://127.0.0.1:8000/docs**.
O banco `estoque.db` é criado automaticamente na primeira execução.

## 🔌 Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/produtos` | Lista todos os produtos |
| POST | `/produtos` | Cria um produto |
| GET | `/produtos/{id}` | Detalha um produto |
| PATCH | `/produtos/{id}` | Atualiza nome, preço ou estoque mínimo |
| DELETE | `/produtos/{id}` | Remove um produto |
| GET | `/produtos/estoque-baixo` | Lista produtos com estoque baixo |
| POST | `/produtos/{id}/movimentacoes` | Registra entrada ou saída |
| GET | `/produtos/{id}/movimentacoes` | Histórico de movimentações |

### Exemplo de uso

```bash
# Criar produto
curl -X POST http://127.0.0.1:8000/produtos \
  -H "Content-Type: application/json" \
  -d '{"nome": "Extintor ABC 4kg", "preco": 120.0, "quantidade": 10, "estoque_minimo": 3}'

# Registrar saída de 2 unidades
curl -X POST http://127.0.0.1:8000/produtos/1/movimentacoes \
  -H "Content-Type: application/json" \
  -d '{"tipo": "saida", "quantidade": 2}'
```

Tentar retirar mais do que existe em estoque retorna `400 Bad Request` e não altera o saldo.

## 🧪 Testes

```bash
python -m pytest -v
```

## 📁 Estrutura

```
api-controle-estoque/
├── app/
│   ├── main.py        # Rotas da API
│   ├── crud.py        # Regras de negócio e acesso ao banco
│   ├── models.py      # Tabelas (SQLAlchemy)
│   ├── schemas.py     # Validação de entrada/saída (Pydantic)
│   └── database.py    # Conexão e sessão
├── tests/
│   └── test_api.py
├── requirements.txt
└── README.md
```

## 🔮 Próximos passos

- Autenticação com JWT
- Migrações com Alembic
- Dockerfile
- Paginação e filtros na listagem

## 👤 Autor

**Nathan Gabriel Martins de Melo**
[GitHub](https://github.com/nathangmmelo)
