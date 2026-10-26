from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    preco: float = Field(gt=0)
    quantidade: int = Field(default=0, ge=0)
    estoque_minimo: int = Field(default=5, ge=0)


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    preco: float | None = Field(default=None, gt=0)
    estoque_minimo: int | None = Field(default=None, ge=0)


class ProdutoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    preco: float
    quantidade: int
    estoque_minimo: int


class MovimentacaoCreate(BaseModel):
    tipo: Literal["entrada", "saida"]
    quantidade: int = Field(gt=0)


class MovimentacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    tipo: str
    quantidade: int
    data: datetime
