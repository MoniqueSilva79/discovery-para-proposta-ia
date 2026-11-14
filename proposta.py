"""Gera o rascunho de proposta técnica a partir da transcrição de uma discovery.

Uso:
    python proposta.py transcricao_exemplo.txt --offline      # sem IA (regras)
    python proposta.py transcricao.txt                        # com Gemini
    python proposta.py transcricao.txt -o proposta.md
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from arquitetura import diagrama_mermaid, sugerir_componentes
from extrator import ExtratorGemini, ExtratorRegras
from modelos import Componente, Requisitos

CHECKLIST = [
    "Arquitetura revisada por especialista",
    "Custos estimados e validados na calculadora oficial do Google Cloud",
    "Premissas e riscos descritos",
    "Requisitos regulatórios (ex.: LGPD) tratados no desenho",
    "Proposta aprovada para envio ao cliente",
]


def _lista(itens: list[str]) -> str:
    return "\n".join(f"- {i}" for i in itens) if itens else "- (não mencionado na call)"


def gerar_markdown(req: Requisitos, componentes: list[Componente]) -> str:
    tabela = "\n".join(f"| {c.servico} | {c.camada} | {c.motivo} |" for c in componentes)
    checklist = "\n".join(f"- [ ] {item}" for item in CHECKLIST)
    return f"""# Proposta técnica (RASCUNHO) – {req.cliente}

> Gerado automaticamente em {date.today():%d/%m/%Y}. **Não enviar ao cliente sem revisão humana.**

## 1. Contexto e dores
{_lista(req.dores)}

## 2. Requisitos
{_lista(req.requisitos)}

## 3. Restrições
{_lista(req.restricoes)}

**Prazo crítico:** {req.prazo or "não informado"}
**Decisores:** {", ".join(req.decisores) or "não identificados"}

## 4. Arquitetura de referência (rascunho)

```mermaid
{diagrama_mermaid(componentes)}
```

| Serviço | Camada | Por quê |
|---|---|---|
{tabela}

## 5. Investimento
Estimar na calculadora oficial (https://cloud.google.com/products/calculator) com volumes confirmados pelo cliente.
Este rascunho não contém preços.

## 6. Próximos passos
{_lista(req.proximos_passos)}

## 7. Checklist de revisão
{checklist}
"""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("transcricao", type=Path)
    p.add_argument("--offline", action="store_true", help="usa o extrator por regras, sem IA")
    p.add_argument("-o", "--saida", type=Path, default=Path("proposta_rascunho.md"))
    args = p.parse_args()

    texto = args.transcricao.read_text(encoding="utf-8")
    extrator = ExtratorRegras() if args.offline else ExtratorGemini()
    req = extrator.extrair(texto)
    md = gerar_markdown(req, sugerir_componentes(req))
    args.saida.write_text(md, encoding="utf-8")
    print(f"Rascunho salvo em {args.saida}. Revise antes de enviar.")


if __name__ == "__main__":
    main()
