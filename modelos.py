"""Estrutura dos requisitos extraídos de uma call de discovery."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Requisitos(BaseModel):
    cliente: str = Field(default="Cliente", description="Nome da empresa cliente")
    dores: list[str] = Field(default_factory=list, description="Problemas de negócio citados")
    requisitos: list[str] = Field(default_factory=list, description="Requisitos técnicos ou de negócio")
    restricoes: list[str] = Field(default_factory=list, description="Limites de prazo, orçamento, regulação")
    decisores: list[str] = Field(default_factory=list, description="Quem aprova ou influencia a compra")
    prazo: str | None = Field(default=None, description="Prazo crítico mencionado")
    proximos_passos: list[str] = Field(default_factory=list, description="Ações combinadas na call")


class Componente(BaseModel):
    id: str
    servico: str
    motivo: str
    camada: str  # origem, computacao, dados, analytics, seguranca, atendimento
