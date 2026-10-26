from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    preco: Mapped[float] = mapped_column(Float)
    quantidade: Mapped[int] = mapped_column(Integer, default=0)
    estoque_minimo: Mapped[int] = mapped_column(Integer, default=5)

    movimentacoes: Mapped[list["Movimentacao"]] = relationship(back_populates="produto")


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    tipo: Mapped[str] = mapped_column(String(10))  # "entrada" ou "saida"
    quantidade: Mapped[int] = mapped_column(Integer)
    data: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    produto: Mapped[Produto] = relationship(back_populates="movimentacoes")
