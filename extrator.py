"""Extração de requisitos a partir da transcrição da discovery.

Dois extratores com a mesma interface:
- ExtratorGemini: usa o Gemini (Vertex AI ou API) com saída estruturada (JSON validado por Pydantic).
- ExtratorRegras: sem IA, baseado em palavras-chave. Serve para demonstração offline e testes.
"""
from __future__ import annotations

import os
import re
from typing import Protocol

from modelos import Requisitos

PROMPT = """Você é um arquiteto de pré-vendas. Leia a transcrição de uma call de discovery
e extraia SOMENTE o que foi dito. Não invente informação.
Se algo não foi mencionado, deixe a lista vazia ou o campo nulo.

Transcrição:
\"\"\"
{transcricao}
\"\"\"
"""


class Extrator(Protocol):
    def extrair(self, transcricao: str) -> Requisitos: ...


class ExtratorGemini:
    def __init__(self, modelo: str | None = None):
        from google import genai  # importação tardia: só exige o SDK quando usado

        self.cliente = genai.Client()  # usa GOOGLE_GENAI_USE_VERTEXAI / GOOGLE_CLOUD_PROJECT
        self.modelo = modelo or os.environ.get("MODELO_GEMINI", "gemini-2.5-flash")

    def extrair(self, transcricao: str) -> Requisitos:
        resposta = self.cliente.models.generate_content(
            model=self.modelo,
            contents=PROMPT.format(transcricao=transcricao),
            config={
                "response_mime_type": "application/json",
                "response_schema": Requisitos,
                "temperature": 0.1,
            },
        )
        if resposta.parsed is not None:
            return resposta.parsed
        return Requisitos.model_validate_json(resposta.text)


class ExtratorRegras:
    """Extrator determinístico por palavras-chave (sem IA)."""

    SINAIS = {
        "dores": [r"vence", r"lento", r"caro", r"fora do ar", r"indisponib", r"manual"],
        "requisitos": [r"lgpd", r"dados de clientes", r"integra", r"alta disponibilidade", r"analytics|relat[oó]rio"],
        "restricoes": [r"or[cç]amento", r"s[oó] no", r"trimestre", r"n[aã]o pode", r"regula"],
        "proximos_passos": [r"workshop", r"pr[oó]xima reuni", r"enviar", r"poc|prova de conceito"],
    }

    def extrair(self, transcricao: str) -> Requisitos:
        dados: dict[str, list[str]] = {k: [] for k in self.SINAIS}
        decisores: list[str] = []
        prazo = None
        for linha in transcricao.splitlines():
            if ":" not in linha:
                continue
            quem, fala = (p.strip() for p in linha.split(":", 1))
            if quem.lower() in ("você", "voce", "pré-vendas", "pre-vendas"):
                continue
            baixa = fala.lower()
            for campo, padroes in self.SINAIS.items():
                if any(re.search(p, baixa) for p in padroes):
                    dados[campo].append(fala)
            for cargo in ("CFO", "CIO", "CTO", "CISO", "diretor", "diretora"):
                if re.search(rf"\b{cargo}\b", fala, re.IGNORECASE) and cargo.upper() not in [d.upper() for d in decisores]:
                    decisores.append(cargo)
            m = re.search(r"\b(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\b", baixa)
            if m and prazo is None:
                prazo = m.group(1)
        cliente = re.search(r"^#\s*cliente:\s*(.+)$", transcricao, re.IGNORECASE | re.MULTILINE)
        return Requisitos(
            cliente=cliente.group(1).strip() if cliente else "Cliente",
            decisores=decisores,
            prazo=prazo,
            **dados,
        )
