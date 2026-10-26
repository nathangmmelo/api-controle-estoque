from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="API de Controle de Estoque",
    description="API REST simples para gerenciar produtos e movimentações de estoque.",
    version="1.0.0",
)


def _produto_ou_404(db: Session, produto_id: int) -> models.Produto:
    produto = crud.obter_produto(db, produto_id)
    if not produto:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto não encontrado")
    return produto


@app.get("/", tags=["Saúde"])
def raiz():
    return {"status": "ok", "docs": "/docs"}


@app.get("/produtos", response_model=list[schemas.ProdutoOut], tags=["Produtos"])
def listar(db: Session = Depends(get_db)):
    return crud.listar_produtos(db)


@app.get("/produtos/estoque-baixo", response_model=list[schemas.ProdutoOut], tags=["Produtos"])
def estoque_baixo(db: Session = Depends(get_db)):
    """Produtos com quantidade menor ou igual ao estoque mínimo."""
    return crud.listar_estoque_baixo(db)


@app.post(
    "/produtos",
    response_model=schemas.ProdutoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Produtos"],
)
def criar(dados: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    try:
        return crud.criar_produto(db, dados)
    except crud.NomeDuplicado:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um produto com esse nome")


@app.get("/produtos/{produto_id}", response_model=schemas.ProdutoOut, tags=["Produtos"])
def detalhar(produto_id: int, db: Session = Depends(get_db)):
    return _produto_ou_404(db, produto_id)


@app.patch("/produtos/{produto_id}", response_model=schemas.ProdutoOut, tags=["Produtos"])
def atualizar(produto_id: int, dados: schemas.ProdutoUpdate, db: Session = Depends(get_db)):
    produto = _produto_ou_404(db, produto_id)
    return crud.atualizar_produto(db, produto, dados)


@app.delete("/produtos/{produto_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Produtos"])
def remover(produto_id: int, db: Session = Depends(get_db)):
    produto = _produto_ou_404(db, produto_id)
    crud.remover_produto(db, produto)


@app.post(
    "/produtos/{produto_id}/movimentacoes",
    response_model=schemas.MovimentacaoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Movimentações"],
)
def movimentar(produto_id: int, dados: schemas.MovimentacaoCreate, db: Session = Depends(get_db)):
    produto = _produto_ou_404(db, produto_id)
    try:
        return crud.registrar_movimentacao(db, produto, dados)
    except crud.EstoqueInsuficiente as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Estoque insuficiente. {e}")


@app.get(
    "/produtos/{produto_id}/movimentacoes",
    response_model=list[schemas.MovimentacaoOut],
    tags=["Movimentações"],
)
def historico(produto_id: int, db: Session = Depends(get_db)):
    _produto_ou_404(db, produto_id)
    return crud.listar_movimentacoes(db, produto_id)
