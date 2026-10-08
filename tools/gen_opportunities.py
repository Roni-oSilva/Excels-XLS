# -*- coding: utf-8 -*-
"""Gera market-research/opportunities.md a partir de opportunities_data.py"""
import os
from opportunities_data import OPS, CRITERIOS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    ops = sorted(OPS, key=lambda o: (-o["nota"], o["id"]))
    top10 = {o["id"] for o in ops[:10]}
    prod = {o["id"] for o in OPS if o["status"] == "Produzido"}
    assert top10 == prod, (top10, prod)
    L = []
    L.append("# Pesquisa de mercado: dores reais -> oportunidades de planilhas\n")
    L.append("> Pesquisa feita na web em outubro/2026 (11+ buscas temáticas em Sebrae, Serasa Experian, Abrasel, "
             "artigos acadêmicos, blogs contábeis e conteúdo de fornecedores). **Nada aqui foi inventado**: cada "
             "oportunidade traz o link da evidência e a *força da evidência*. Números citados \"via\" outra fonte "
             "são secundários e devem ser conferidos no original antes de uso em material institucional.\n")
    L.append("## Como a nota (0-100) é calculada\n")
    L.append("| Critério | Pontos máx. |\n|---|---|")
    for c, m in CRITERIOS:
        L.append(f"| {c} | {m} |")
    L.append("\nAs sub-notas são julgamento do autor a partir das evidências (ficam em `tools/opportunities_data.py`). "
             "Oportunidades com **evidência Fraca** só devem virar produto depois de validação com clientes reais.\n")
    L.append("## Ranking\n")
    L.append("| # | Planilha | Segmento | Dor | Potencial (nota) | Evidência | Status |\n|---|---|---|---|---|---|---|")
    for i, o in enumerate(ops, 1):
        st = "✅ Produzido" if o["status"] == "Produzido" else "🗺️ Roadmap"
        L.append(f"| {i} | {o['nome']} | {o['seg']} | {o['problema']} | **{o['nota']}** | {o['forca']} | {st} |")
    L.append("\n## As 10 escolhidas para a primeira leva\n")
    for o in ops[:10]:
        L.append(f"- **{o['nome']}** ({o['nota']}) → `planilhas/{o['pasta']}/`")
    L.append("\nCritério de corte: as 10 maiores notas. O **Precificador Marketplace** e a **Separação PF/PJ** "
             "ficaram logo abaixo; ambos já estão parcialmente cobertos (taxa de plataforma no Precificador; "
             "categoria *Pró-labore* no Fluxo de Caixa).\n")
    L.append("## Detalhamento de cada oportunidade\n")
    for o in ops:
        L.append(f"### {o['id']:02d}. {o['nome']} - nota {o['nota']}\n")
        L.append(f"- **Segmento:** {o['seg']}")
        L.append(f"- **Problema:** {o['problema']}")
        L.append(f"- **Quem sofre:** {o['quem']}")
        L.append(f"- **Força da evidência:** {o['forca']}")
        L.append("- **Evidência encontrada:**")
        for t, u in o["evid"]:
            L.append(f"  - {t}" + (f" - [fonte]({u})" if u else ""))
        L.append(f"- **Como as empresas resolvem hoje:** {o['hoje']}")
        L.append(f"- **Como uma planilha resolve:** {o['solucao']}")
        L.append(f"- **Benefício:** {o['beneficio']}")
        L.append(f"- **Potencial comercial:** {o['potencial']}")
        L.append(f"- **Complexidade:** {o['complexidade']}")
        L.append(f"- **Concorrentes:** {o['concorrentes']}")
        L.append(f"- **Diferencial:** {o['dif']}")
        L.append("- **Sub-notas:** " + ", ".join(f"{c} {v}/{m}" for (c, m), v in zip(CRITERIOS, o["sub"])))
        L.append(f"- **Status:** {o['status']}" + (f" (`planilhas/{o['pasta']}/`)" if o["status"] == "Produzido" else "") + "\n")
    out = os.path.join(ROOT, "market-research", "opportunities.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("ok", len(ops), "oportunidades;", [ (o["id"], o["nota"]) for o in ops[:12]])

if __name__ == "__main__":
    main()
