import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from arquitetura import diagrama_mermaid, sugerir_componentes  # noqa: E402
from extrator import ExtratorRegras  # noqa: E402
from proposta import gerar_markdown  # noqa: E402

TRANSCRICAO = (Path(__file__).parent / "transcricao_exemplo.txt").read_text(encoding="utf-8")


def test_extracao_por_regras():
    req = ExtratorRegras().extrair(TRANSCRICAO)
    assert req.cliente.startswith("Empresa Exemplo")
    assert any("data center" in d for d in req.dores)
    assert any("LGPD" in r for r in req.requisitos)
    assert any("orçamento" in r.lower() for r in req.restricoes)
    assert {"CFO", "CIO"} <= set(req.decisores)
    assert req.prazo == "junho"
    assert any("workshop" in p.lower() for p in req.proximos_passos)


def test_falas_do_pre_vendas_sao_ignoradas():
    req = ExtratorRegras().extrair("Você: Quem aprova o orçamento?\n")
    assert req.restricoes == []


def test_arquitetura_cobre_requisitos():
    req = ExtratorRegras().extrair(TRANSCRICAO)
    servicos = {c.servico for c in sugerir_componentes(req)}
    assert {"Migrate to Virtual Machines", "Compute Engine", "BigQuery",
            "Sensitive Data Protection", "Cloud KMS", "IAM + Cloud Audit Logs"} <= servicos


def test_mermaid_tem_ligacoes():
    req = ExtratorRegras().extrair(TRANSCRICAO)
    mermaid = diagrama_mermaid(sugerir_componentes(req))
    assert mermaid.startswith("flowchart LR")
    assert "mig --> gce" in mermaid


def test_proposta_exige_revisao_e_nao_tem_precos():
    req = ExtratorRegras().extrair(TRANSCRICAO)
    md = gerar_markdown(req, sugerir_componentes(req))
    assert "RASCUNHO" in md
    assert "Não enviar ao cliente sem revisão humana" in md
    assert "R$" not in md and "US$" not in md
