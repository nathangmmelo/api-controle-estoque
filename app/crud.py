from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


class EstoqueInsuficiente(Exception):
    pass


class NomeDuplicado(Exception):
    pass


def listar_produtos(db: Session) -> list[models.Produto]:
    return list(db.scalars(select(models.Produto).order_by(models.Produto.nome)))


def listar_estoque_baixo(db: Session) -> list[models.Produto]:
    stmt = select(models.Produto).where(
        models.Produto.quantidade <= models.Produto.estoque_minimo
    )
    return list(db.scalars(stmt))


def obter_produto(db: Session, produto_id: int) -> models.Produto | None:
    return db.get(models.Produto, produto_id)


def criar_produto(db: Session, dados: schemas.ProdutoCreate) -> models.Produto:
    existe = db.scalar(select(models.Produto).where(models.Produto.nome == dados.nome))
    if existe:
        raise NomeDuplicado(dados.nome)
    produto = models.Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def atualizar_produto(
    db: Session, produto: models.Produto, dados: schemas.ProdutoUpdate
) -> models.Produto:
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


def remover_produto(db: Session, produto: models.Produto) -> None:
    for mov in produto.movimentacoes:
        db.delete(mov)
    db.delete(produto)
    db.commit()


def registrar_movimentacao(
    db: Session, produto: models.Produto, dados: schemas.MovimentacaoCreate
) -> models.Movimentacao:
    if dados.tipo == "saida":
        if produto.quantidade < dados.quantidade:
            raise EstoqueInsuficiente(
                f"Disponível: {produto.quantidade}, solicitado: {dados.quantidade}"
            )
        produto.quantidade -= dados.quantidade
    else:
        produto.quantidade += dados.quantidade

    mov = models.Movimentacao(
        produto_id=produto.id, tipo=dados.tipo, quantidade=dados.quantidade
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


def listar_movimentacoes(db: Session, produto_id: int) -> list[models.Movimentacao]:
    stmt = (
        select(models.Movimentacao)
        .where(models.Movimentacao.produto_id == produto_id)
        .order_by(models.Movimentacao.id.desc())
    )
    return list(db.scalars(stmt))
