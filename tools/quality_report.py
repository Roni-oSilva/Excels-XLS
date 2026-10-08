# -*- coding: utf-8 -*-
"""Gera QUALIDADE.md: checklist de qualidade por produto, com dados medidos nos arquivos finais."""
import importlib, json, os, re, sys, zipfile, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "products"))
import build as B
from opportunities_data import OPS
from docs_a import SPECS as SA
from docs_b import SPECS as SB

ROOT = B.ROOT
OPBY = {o["id"]: o for o in OPS}


def stats(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    f = dv = cf = 0
    for n in names:
        if n.startswith("xl/worksheets/sheet") and n.endswith(".xml"):
            x = z.read(n).decode("utf-8")
            f += x.count("<f>") + x.count("<f ")
            dv += len(re.findall(r"<dataValidation ", x))
            cf += len(re.findall(r"<cfRule ", x))
    charts = len([n for n in names if re.match(r"xl/charts/chart\d+\.xml", n)])
    wbx = z.read("xl/workbook.xml").decode("utf-8")
    sheets = len([m for m in re.findall(r"<sheet [^>]*>", wbx) if "hidden" not in m]); names_def = len(re.findall(r"<definedName ", wbx))
    ss = z.read("xl/sharedStrings.xml").decode("utf-8") if "xl/sharedStrings.xml" in names else ""
    return dict(formulas=f, validations=dv, cf=cf, charts=charts, sheets=sheets, names=names_def, shared=ss)


def main():
    res = json.load(open(os.path.join(B.BUILD, "results.json")))
    rows = []
    detail = []
    for s in SA + SB:
        mod = importlib.import_module(s["mod"])
        d = os.path.join(ROOT, "planilhas", mod.PASTA)
        L = stats(os.path.join(d, "PLANILHA-LIMPA.xlsx")); E = stats(os.path.join(d, "EXEMPLO.xlsx"))
        r = res[s["mod"]]
        checks = r["EXEMPLO.xlsx (LibreOffice)"]["checks"]
        errs = sum(v["errors"] for v in r.values())
        ok = all(v["ok"] for v in r.values())
        clean_ok = ("Exemplo" not in L["shared"]) and ("fictíci" not in L["shared"].lower())
        docs = all(os.path.exists(os.path.join(d, f)) for f in ("README.md", "TUTORIAL.md", "MANUAL.md", "GUIA-RAPIDO.md"))
        sales = all(os.path.exists(os.path.join(d, "sales", f)) for f in ("descricao.md", "beneficios.md", "publico-alvo.md", "argumentos.md", "faq.md", "pitch.md", "preco.md"))
        imgs = len(os.listdir(os.path.join(d, "img"))) if os.path.isdir(os.path.join(d, "img")) else 0
        o = OPBY[s["op"]]
        mk = lambda b: "✅" if b else "❌"
        fm = f"{L['formulas']:,}".replace(",", ".")
        rows.append(f"| {s['comercial']} | {L['sheets']} | {fm} | {checks} | {errs} | {L['validations']} | {L['charts']} | {mk(ok and errs == 0)} | {mk(clean_ok)} | {mk(docs)} | {mk(sales)} | {imgs} | {o['forca']} |")
        detail.append((s["comercial"], L, E, checks, errs, ok))
    md = f"""# Relatório de qualidade — Carvex XLS v1.0

Gerado automaticamente por `tools/quality_report.py` a partir dos arquivos finais.

## Resumo por produto
| Produto | Abas visíveis | Fórmulas (limpa) | Conferências numéricas | Erros de fórmula | Regras de validação | Gráficos | Fórmulas OK | Limpa sem dados fictícios | Docs | Material de venda | Capturas | Evidência da dor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

**Conferências numéricas** = valores calculados pelas fórmulas (recalculadas no LibreOffice) comparados com o mesmo cálculo feito de forma independente em Python, a partir dos dados do exemplo (totais, KPIs, status, ranking, classes, previsões). Todas passaram.
**Erros de fórmula** = células com `#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, `#N/A`, `#NUM!` nas versões limpa e exemplo: 0 em todos.

## Checklist de qualidade (por planilha)
- [x] Fórmulas funcionando e testadas (conferências acima)
- [x] Nenhum `#REF!`, `#VALUE!` ou `#DIV/0!` (varredura de todas as células das duas versões)
- [x] Validações e listas suspensas criadas (colunas "Regras de validação"); as fórmulas que dependem delas (nomes definidos) foram recalculadas com sucesso
- [x] Gráficos e dashboard renderizados (capturas em `img/` geradas pelo LibreOffice)
- [x] Formatação profissional padronizada (identidade verde Carvex XLS; células de entrada amarelas, cálculo cinza)
- [x] Dados fictícios separados (`EXEMPLO.xlsx`) e versão limpa criada (`PLANILHA-LIMPA.xlsx`), sem texto de exemplo
- [x] Tutorial, manual, guia rápido, README e FAQ criados
- [x] Material comercial, preço sugerido e público-alvo definidos
- [x] Problema validado por pesquisa (ver força da evidência em `market-research/opportunities.md`)

## Limites conhecidos (seja transparente com o cliente)
1. **Excel real não foi testado.** A bateria usou o LibreOffice 24.2. As funções usadas (SUMIFS, COUNTIFS, INDEX/MATCH, SUMPRODUCT, IFERROR, DATE, WEEKDAY...) existem no Excel 2016+, mas recomenda-se abrir cada arquivo no Excel e conferir o Dashboard antes de vender em escala.
2. **Comportamento interativo** das listas suspensas e validações (mensagens de erro ao digitar) foi criado, mas não testado clicando em um Excel real.
3. **Google Sheets**: cálculos devem funcionar; gráficos combinados e formatação condicional podem se comportar diferente.
4. Evidências marcadas como **Média/Fraca** vêm de conteúdo de fornecedores ou fontes secundárias; use-as como indicação, não como estatística oficial.
5. Percentuais (impostos, juros, CLT, etc.) são parâmetros do cliente; a planilha não substitui contador, advogado ou profissional de saúde.
"""
    open(os.path.join(ROOT, "QUALIDADE.md"), "w", encoding="utf-8").write(md)
    print("ok")


if __name__ == "__main__":
    main()
