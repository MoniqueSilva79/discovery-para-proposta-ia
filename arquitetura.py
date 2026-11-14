"""Rascunho de arquitetura de referência no Google Cloud a partir dos requisitos.

As regras são explícitas e auditáveis: cada componente sugerido traz o motivo.
O resultado é um RASCUNHO para o especialista revisar, nunca a arquitetura final.
"""
from __future__ import annotations

from modelos import Componente, Requisitos

REGRAS: list[tuple[tuple[str, ...], Componente]] = [
    (("data center", "on-premise", "servidor", "vence"),
     Componente(id="mig", servico="Migrate to Virtual Machines", motivo="Migração das cargas do data center atual", camada="origem")),
    (("data center", "on-premise", "servidor", "vence", "vm"),
     Componente(id="gce", servico="Compute Engine", motivo="Destino das VMs migradas", camada="computacao")),
    (("dados", "relatório", "relatorio", "analytics", "indicador"),
     Componente(id="bq", servico="BigQuery", motivo="Data warehouse para análise", camada="dados")),
    (("relatório", "relatorio", "dashboard", "indicador"),
     Componente(id="looker", servico="Looker", motivo="Painéis para as áreas de negócio", camada="analytics")),
    (("arquivo", "backup", "documento", "dados"),
     Componente(id="gcs", servico="Cloud Storage", motivo="Armazenamento de objetos e backup", camada="dados")),
    (("lgpd", "dados de clientes", "sensív", "sensiv", "pii"),
     Componente(id="sdp", servico="Sensitive Data Protection", motivo="Descoberta e mascaramento de dados pessoais (LGPD)", camada="seguranca")),
    (("lgpd", "criptografia", "chave"),
     Componente(id="kms", servico="Cloud KMS", motivo="Chaves de criptografia gerenciadas pelo cliente", camada="seguranca")),
    (("atendimento", "contact center", "call center", "sac"),
     Componente(id="ces", servico="Customer Engagement Suite", motivo="Atendimento com IA e agentes virtuais", camada="atendimento")),
]

SEMPRE = [
    Componente(id="iam", servico="IAM + Cloud Audit Logs", motivo="Menor privilégio e trilha de auditoria", camada="seguranca"),
]

LIGACOES = [("mig", "gce"), ("gce", "bq"), ("gcs", "bq"), ("bq", "looker"), ("ces", "bq")]


def sugerir_componentes(req: Requisitos) -> list[Componente]:
    texto = " ".join(req.dores + req.requisitos + req.restricoes).lower()
    escolhidos: dict[str, Componente] = {}
    for gatilhos, comp in REGRAS:
        if any(g in texto for g in gatilhos):
            escolhidos.setdefault(comp.id, comp)
    for comp in SEMPRE:
        escolhidos.setdefault(comp.id, comp)
    return list(escolhidos.values())


def diagrama_mermaid(componentes: list[Componente]) -> str:
    ids = {c.id for c in componentes}
    linhas = ["flowchart LR"]
    for c in componentes:
        linhas.append(f'    {c.id}["{c.servico}"]')
    for a, b in LIGACOES:
        if a in ids and b in ids:
            linhas.append(f"    {a} --> {b}")
    return "\n".join(linhas)
