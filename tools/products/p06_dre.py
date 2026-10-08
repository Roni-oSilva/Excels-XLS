# -*- coding: utf-8 -*-
import datetime as dt
import random
from lib import *

SLUG = "dre-ponto-equilibrio"
PASTA = "financeiro/dre-ponto-equilibrio"
NOME = "DRE e Ponto de Equilíbrio"
N = 1500
R0 = 4
LAST = R0 + N

CONTAS = [
    ("Receita bruta", "Receita", "Vendas e serviços faturados no mês (competência)."),
    ("Deduções e impostos sobre vendas", "Variável", "Simples/ICMS/ISS/PIS/COFINS sobre vendas, devoluções e descontos."),
    ("Custos variáveis (CMV / insumos)", "Variável", "Mercadorias, matéria-prima, embalagens e serviços de terceiros ligados à venda."),
    ("Comissões e taxas de venda", "Variável", "Comissão de vendedores, taxas de cartão e de marketplace."),
    ("Despesas com pessoal", "Fixo", "Salários, encargos, benefícios e pró-labore."),
    ("Despesas administrativas", "Fixo", "Aluguel, energia, internet, contador, sistemas, manutenção."),
    ("Despesas comerciais e marketing", "Fixo", "Anúncios, brindes, eventos, material de divulgação."),
    ("Receitas financeiras", "Receita financeira", "Rendimentos de aplicações e juros recebidos."),
    ("Despesas financeiras", "Fixo", "Juros, tarifas bancárias, IOF e parcelas de juros de empréstimos."),
    ("IRPJ / CSLL", "Imposto sobre lucro", "Imposto sobre o lucro (apenas Lucro Presumido/Real; no Simples costuma estar nas deduções)."),
]
NAMES = [c[0] for c in CONTAS]
META_LUCRO = 8000.0


def sample_rows():
    rnd = random.Random(606)
    base = [74, 66, 92, 99, 105, 111, 114, 118, 123]
    rows = []
    for m, b in enumerate(base, 1):
        rec = round(b * 1000 * rnd.uniform(0.97, 1.03), 2)
        parts = [0.38, 0.27, 0.22, 0.13]
        for k, p in enumerate(parts):
            rows.append((dt.date(2026, m, 7 + k * 7), "Receita bruta", f"Faturamento semana {k+1}", round(rec * p, 2)))
        rows.append((dt.date(2026, m, 28), "Deduções e impostos sobre vendas", "Simples Nacional", round(rec * 0.074, 2)))
        cv = round(rec * rnd.uniform(0.355, 0.385), 2)
        rows.append((dt.date(2026, m, 12), "Custos variáveis (CMV / insumos)", "Compra de mercadorias/insumos", round(cv * 0.7, 2)))
        rows.append((dt.date(2026, m, 24), "Custos variáveis (CMV / insumos)", "Compra de mercadorias/insumos (2ª)", round(cv * 0.3, 2)))
        rows.append((dt.date(2026, m, 28), "Comissões e taxas de venda", "Taxas de cartão e comissões", round(rec * 0.033, 2)))
        rows.append((dt.date(2026, m, 5), "Despesas com pessoal", "Folha de pagamento e encargos", 24800.0))
        rows.append((dt.date(2026, m, 6), "Despesas com pessoal", "Pró-labore", 7000.0))
        rows.append((dt.date(2026, m, 10), "Despesas administrativas", "Aluguel", 5200.0))
        rows.append((dt.date(2026, m, 15), "Despesas administrativas", "Energia, internet e sistemas", round(rnd.uniform(2300, 2800), 2)))
        rows.append((dt.date(2026, m, 20), "Despesas administrativas", "Contabilidade", 1400.0))
        rows.append((dt.date(2026, m, 8), "Despesas comerciais e marketing", "Anúncios online", round(rnd.uniform(3800, 5200), 2)))
        rows.append((dt.date(2026, m, 28), "Despesas financeiras", "Juros e tarifas bancárias", round(rnd.uniform(1100, 1500), 2)))
        if m % 3 == 0:
            rows.append((dt.date(2026, m, 28), "Receitas financeiras", "Rendimento da reserva", round(rnd.uniform(300, 520), 2)))
    return rows


def analyze(rows):
    from collections import defaultdict
    d = defaultdict(lambda: [0.0] * 13)
    for (dtx, conta, desc, val) in rows:
        d[conta][dtx.month - 1] += val
        d[conta][12] += val
    A = {}
    for k in range(13):
        rec = d["Receita bruta"][k]; ded = d["Deduções e impostos sobre vendas"][k]
        cv = d["Custos variáveis (CMV / insumos)"][k]; com = d["Comissões e taxas de venda"][k]
        mc = rec - ded - cv - com
        pes = d["Despesas com pessoal"][k]; adm = d["Despesas administrativas"][k]; cml = d["Despesas comerciais e marketing"][k]
        op = mc - pes - adm - cml
        rf = d["Receitas financeiras"][k]; df = d["Despesas financeiras"][k]
        ll = op + rf - df - d["IRPJ / CSLL"][k]
        cf = pes + adm + cml + df
        A[k] = dict(rec=rec, mc=mc, op=op, ll=ll, cf=cf, mcp=(mc / rec if rec else 0), pe=(cf / (mc / rec) if rec and mc > 0 else None))
    return A


def build(bk: Book):
    wb = bk.wb
    bk.inicio(
        "DRE e Ponto de Equilíbrio", "Carvex XLS · Descubra o lucro real e quanto precisa vender para pagar as contas",
        "Lance receitas, custos e despesas escolhendo a conta do DRE. A planilha monta a Demonstração do Resultado mês a mês, calcula a margem "
        "de contribuição, o ponto de equilíbrio, a margem de segurança e o faturamento necessário para atingir o lucro que você deseja.",
        [("Config", "Informe empresa, ano e o lucro líquido mensal que você deseja. Leia a lista de contas para saber o que lançar em cada uma."),
         ("Lance tudo em Lançamentos", "Data, conta do DRE, descrição e valor (sempre positivo). Use a data de competência (quando a venda ou o custo ocorreu)."),
         ("Abra a aba DRE", "Veja mês a mês a receita, a margem de contribuição, o resultado operacional e o lucro líquido."),
         ("Abra a aba Ponto de Equilíbrio", "Veja quanto você precisa faturar por mês para não ter prejuízo e quanto precisa para atingir sua meta de lucro."),
         ("Revise mensalmente", "Feche o mês até o dia 10, comparando o lucro com a meta.")],
        [("Config", "Parâmetros e lista de contas."), ("Lançamentos", "Todos os lançamentos (até 1.500 linhas)."),
         ("DRE", "Demonstração do Resultado mês a mês, com % da receita bruta."), ("Ponto de Equilíbrio", "Indicadores, ponto de equilíbrio por mês e gráficos.")],
        avisos=["O DRE usa regime de competência (quando vendeu/gastou), diferente do Fluxo de Caixa (quando recebeu/pagou).",
                "Não renomeie as contas da Config: elas são a estrutura do DRE. Detalhe pela coluna Descrição.",
                "Esta planilha é uma ferramenta gerencial. Não substitui a contabilidade oficial."])

    ws = bk.sheet("Config")
    bk.banner(ws, "Configurações", "Preencha as células amarelas.", 5)
    ws.set_column(0, 0, 3); ws.set_column(1, 1, 40); ws.set_column(2, 2, 22); ws.set_column(3, 3, 86)
    lf = bk.fmt("lbl")
    ws.write(3, 1, "Empresa", lf); bk.w(ws, (3, 2), "Empresa Exemplo" if bk.sample else None, bk.fmt("in"))
    ws.write(4, 1, "Ano do DRE", lf); bk.w(ws, (4, 2), 2026 if bk.sample else dt.date.today().year, bk.fmt("in", nf="0", align="center"))
    ws.write(5, 1, "Lucro líquido desejado por mês (R$)", lf); bk.w(ws, (5, 2), META_LUCRO if bk.sample else None, bk.fmt("in", nf="money"))
    bk.dv_num(ws, "C5", 2000, 2100, integer=True); bk.dv_num(ws, "C6", 0)
    bk.define("Ano", "=Config!$C$5"); bk.define("MetaLucro", "=Config!$C$6")
    bk.header(ws, 8, 1, ["Conta do DRE", "Comportamento", "O que lançar aqui"], height=24)
    for i, (n, t, d) in enumerate(CONTAS):
        ws.write(9 + i, 1, n, bk.fmt("plain", bold=True)); ws.write(9 + i, 2, t, bk.fmt("plain", align="center")); ws.write(9 + i, 3, d, bk.fmt("plain"))
    bk.define("ContaNome", "=Config!$B$10:$B$19"); bk.define("ContaComp", "=Config!$C$10:$C$19")
    ws.write(20, 1, "Fixo = não muda com o volume de vendas. Variável = cresce junto com as vendas.", bk.fmt("note"))

    wl = bk.sheet("Lançamentos")
    bk.banner(wl, "Lançamentos", "Valores sempre positivos. A conta define se soma ou subtrai no DRE.", 7)
    bk.header(wl, 3, 0, ["Data (competência)", "Conta do DRE", "Descrição", "Valor (R$)", "Ano", "Mês", "Comportamento"], [14, 36, 40, 15, 7, 6, 20], 32)
    rows = sample_rows() if bk.sample else []
    for i in range(N):
        r = R0 + i; x = r + 1
        d = rows[i] if i < len(rows) else (None,) * 4
        bk.w(wl, (r, 0), d[0], bk.fmt("in", nf="date", align="center")); bk.w(wl, (r, 1), d[1], bk.fmt("in"))
        bk.w(wl, (r, 2), d[2], bk.fmt("in")); bk.w(wl, (r, 3), d[3], bk.fmt("in", nf="money"))
        bk.fx(wl, (r, 4), f'IF($A{x}="","",YEAR($A{x}))', bk.fmt("calc", align="center"))
        bk.fx(wl, (r, 5), f'IF($A{x}="","",MONTH($A{x}))', bk.fmt("calc", align="center"))
        bk.fx(wl, (r, 6), f'IF($B{x}="","",IFERROR(INDEX(ContaComp,MATCH($B{x},ContaNome,0)),"Conta inválida"))', bk.fmt("calc", align="center"))
    bk.dv_date(wl, f"A{R0+1}:A{LAST}"); bk.dv_list(wl, f"B{R0+1}:B{LAST}", "=ContaNome"); bk.dv_num(wl, f"D{R0+1}:D{LAST}", 0, None, "Digite sempre positivo")
    wl.freeze_panes(4, 0); wl.autofilter(3, 0, LAST - 1, 6)
    L = lambda c: f"'Lançamentos'!${c}${R0+1}:${c}${LAST}"

    # ---------------- DRE
    wd = bk.sheet("DRE", tab=G_NEON, onepage=True)
    bk.banner(wd, "DRE: Demonstração do Resultado do Exercício", "Calculada automaticamente a partir dos lançamentos. % = sobre a receita bruta.", 15)
    wd.set_column(0, 0, 38); wd.set_column(1, 12, 11.5); wd.set_column(13, 13, 14); wd.set_column(14, 14, 10)
    wd.set_row(3, 26)
    wd.write(3, 0, "Linha", bk.fmt("h"))
    for m in range(12):
        bk.fx(wd, (3, 1 + m), f"DATE(Ano,{m+1},1)", bk.fmt("h", nf="mmm/yy"))
    wd.write(3, 13, "Total do ano", bk.fmt("h")); wd.write(3, 14, "% da receita bruta", bk.fmt("h"))
    # linha: (rótulo, tipo, fórmula/lançamento, estilo)
    def sumif(conta, mcol):
        return f'SUMIFS({L("D")},{L("B")},"{conta}",{L("E")},Ano,{L("F")},{mcol})'
    layout = [
        (5, "Receita bruta", "acc", "Receita bruta", "n"),
        (6, "(-) Deduções e impostos sobre vendas", "acc", "Deduções e impostos sobre vendas", "n"),
        (7, "= RECEITA LÍQUIDA", "f", "{c}5-{c}6", "t"),
        (8, "(-) Custos variáveis (CMV / insumos)", "acc", "Custos variáveis (CMV / insumos)", "n"),
        (9, "(-) Comissões e taxas de venda", "acc", "Comissões e taxas de venda", "n"),
        (10, "= MARGEM DE CONTRIBUIÇÃO", "f", "{c}7-{c}8-{c}9", "t"),
        (11, "Margem de contribuição (%)", "p", "IF({c}5=0,0,{c}10/{c}5)", "p"),
        (12, "(-) Despesas com pessoal", "acc", "Despesas com pessoal", "n"),
        (13, "(-) Despesas administrativas", "acc", "Despesas administrativas", "n"),
        (14, "(-) Despesas comerciais e marketing", "acc", "Despesas comerciais e marketing", "n"),
        (15, "= RESULTADO OPERACIONAL", "f", "{c}10-{c}12-{c}13-{c}14", "t"),
        (16, "(+) Receitas financeiras", "acc", "Receitas financeiras", "n"),
        (17, "(-) Despesas financeiras", "acc", "Despesas financeiras", "n"),
        (18, "= RESULTADO ANTES DO IR", "f", "{c}15+{c}16-{c}17", "t"),
        (19, "(-) IRPJ / CSLL", "acc", "IRPJ / CSLL", "n"),
        (20, "= LUCRO LÍQUIDO", "f", "{c}18-{c}19", "T"),
        (21, "Margem líquida (%)", "p", "IF({c}5=0,0,{c}20/{c}5)", "p"),
    ]
    for (xr, label, kind, spec, sty) in layout:
        r = xr - 1
        lf_ = bk.fmt("tot") if sty in ("t", "T") else bk.fmt("plain", italic=(sty == "p"))
        wd.write_string(r, 0, label, lf_)
        for m in range(13):
            c = col(1 + m)
            nf = "pct" if sty == "p" else "money"
            f = bk.fmt("tot", nf=nf, align="right") if sty in ("t", "T") else bk.fmt("calc", nf=nf, italic=(sty == "p"), align="center" if sty == "p" else "right")
            if sty == "T":
                f = bk.fmt("tot", nf="money", font_size=11)
            if m == 12:      # total do ano
                if kind == "acc":
                    bk.fx(wd, (r, 13), f"SUM(B{xr}:M{xr})", f)
                elif kind == "f":
                    bk.fx(wd, (r, 13), spec.format(c="N"), f)
                else:
                    bk.fx(wd, (r, 13), spec.format(c="N"), f)
                continue
            if kind == "acc":
                bk.fx(wd, (r, 1 + m), sumif(spec, f"MONTH({c}$4)"), f)
            else:
                bk.fx(wd, (r, 1 + m), spec.format(c=c), f)
        if sty != "p":
            bk.fx(wd, (r, 14), f"IF($N$5=0,0,N{xr}/$N$5)", bk.fmt("tot" if sty in ("t", "T") else "calc", nf="pct", align="center"))
        else:
            wd.write(r, 14, "", bk.fmt("calc"))
    wd.conditional_format("B20:N20", {"type": "cell", "criteria": "<", "value": 0, "format": wb.add_format({"font_color": C_RED, "bold": True})})
    wd.conditional_format("B15:N15", {"type": "cell", "criteria": "<", "value": 0, "format": wb.add_format({"font_color": C_RED, "bold": True})})
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Lucro líquido", "categories": "=DRE!$B$4:$M$4", "values": "=DRE!$B$20:$M$20", "fill": {"color": G_MID}, "invert_if_negative": True, "invert_if_negative_color": "#DC2626", "gap": 60})
    ch.set_title({"name": "Lucro líquido por mês", "name_font": {"size": 12}}); ch.set_legend({"none": True}); ch.set_x_axis({"num_format": "mmm"}); ch.set_size({"width": 700, "height": 280})
    wd.insert_chart("A24", ch)
    wd.freeze_panes(4, 1)
    wd.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})

    # ---------------- Ponto de Equilíbrio
    wp = bk.sheet("Ponto de Equilíbrio", tab=G_NEON, onepage=True)
    bk.banner(wp, "Ponto de Equilíbrio", "Quanto precisa faturar para não ter prejuízo e para atingir a meta de lucro.", 10)
    for c in range(10):
        wp.set_column(c, c, 14)
    bk.kpi(wp, 3, 0, "RECEITA BRUTA NO ANO", "DRE!N5", "money", 2)
    bk.kpi(wp, 3, 2, "LUCRO LÍQUIDO NO ANO", "DRE!N20", "money", 2)
    bk.kpi(wp, 3, 4, "MARGEM LÍQUIDA", "DRE!N21", "pct", 2)
    bk.kpi(wp, 3, 6, "MARGEM DE CONTRIBUIÇÃO", "DRE!N11", "pct", 2)
    bk.kpi(wp, 3, 8, "PONTO DE EQUILÍBRIO / MÊS", 'IFERROR(C8/G5,0)', "money", 2)
    bk.kpi(wp, 6, 0, "MARGEM DE SEGURANÇA", 'IF(A5=0,0,1-(I5*COUNTIF(B12:B23,">0"))/A5)', "pct", 2)
    bk.kpi(wp, 6, 2, "CUSTOS FIXOS MÉDIOS / MÊS", 'IFERROR(E24/COUNTIF(B12:B23,">0"),0)', "money", 2)
    bk.kpi(wp, 6, 4, "FATURAMENTO P/ META DE LUCRO", 'IFERROR((C8+MetaLucro)/G5,0)', "money", 2, color="#1D4ED8")
    bk.kpi(wp, 6, 6, "MESES ACIMA DO PE", 'COUNTIF(I12:I23,"Acima do PE")', "int", 2)
    bk.kpi(wp, 6, 8, "MESES ABAIXO DO PE", 'COUNTIF(I12:I23,"ABAIXO do PE")', "int", 2, color=C_RED)
    bk.header(wp, 10, 0, ["Mês", "Receita bruta", "Margem de contribuição", "MC %", "Custos fixos", "Ponto de equilíbrio (R$)", "Receita - PE", "Margem de segurança", "Situação", "Lucro líquido"], height=36)
    IDX = lambda row: f"INDEX(DRE!$B${row}:$M${row},MONTH($A{{x}}))"
    for m in range(12):
        r = 11 + m; x = r + 1
        I = lambda row: IDX(row).format(x=x)
        bk.fx(wp, (r, 0), f"DATE(Ano,{m+1},1)", bk.fmt("calc", nf="mon", align="center", bold=True))
        bk.fx(wp, (r, 1), I(5), cm := bk.fmt("calc", nf="money"))
        bk.fx(wp, (r, 2), I(10), cm)
        bk.fx(wp, (r, 3), f"IF(B{x}=0,0,C{x}/B{x})", bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wp, (r, 4), f"{I(12)}+{I(13)}+{I(14)}+{I(17)}", cm)
        bk.fx(wp, (r, 5), f'IF(OR(B{x}=0,D{x}<=0),"",E{x}/D{x})', cm)
        bk.fx(wp, (r, 6), f'IF(F{x}="","",B{x}-F{x})', cm)
        bk.fx(wp, (r, 7), f'IF(F{x}="","",G{x}/B{x})', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wp, (r, 8), f'IF(B{x}=0,"",IF(F{x}="","MC negativa",IF(B{x}>=F{x},"Acima do PE","ABAIXO do PE")))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wp, (r, 9), I(20), cm)
    wp.write(23, 0, "Ano", bk.fmt("tot", align="center"))
    for c in (1, 2, 4, 9):
        bk.fx(wp, (23, c), f"SUM({col(c)}12:{col(c)}23)", bk.fmt("tot", nf="money"))
    bk.fx(wp, (23, 3), "IF(B24=0,0,C24/B24)", bk.fmt("tot", nf="pct", align="center"))
    for c in (5, 6, 7, 8):
        wp.write(23, c, "", bk.fmt("tot"))
    wp.conditional_format("I12:I23", {"type": "cell", "criteria": "==", "value": '"ABAIXO do PE"', "format": wb.add_format({"bg_color": C_RED, "font_color": "#FFFFFF", "bold": True})})
    wp.conditional_format("I12:I23", {"type": "cell", "criteria": "==", "value": '"Acima do PE"', "format": wb.add_format({"bg_color": G_LIGHT, "font_color": "#15803D", "bold": True})})
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Receita bruta", "categories": "='Ponto de Equilíbrio'!$A$12:$A$23", "values": "='Ponto de Equilíbrio'!$B$12:$B$23", "fill": {"color": G_MID}, "gap": 60})
    ln = wb.add_chart({"type": "line"})
    ln.add_series({"name": "Ponto de equilíbrio", "categories": "='Ponto de Equilíbrio'!$A$12:$A$23", "values": "='Ponto de Equilíbrio'!$F$12:$F$23", "line": {"color": "#EF4444", "width": 2.5, "dash_type": "dash"}, "marker": {"type": "diamond", "size": 6}})
    ch.combine(ln); ch.set_title({"name": "Receita x Ponto de equilíbrio", "name_font": {"size": 12}}); ch.set_legend({"position": "bottom"}); ch.set_x_axis({"num_format": "mmm"}); ch.set_size({"width": 700, "height": 300})
    wp.insert_chart("A27", ch)
    wp.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
    bk.finish()

    exp = {}
    if bk.sample:
        A = analyze(rows)
        t = A[12]
        exp[("DRE", "N5")] = round(t["rec"], 2); exp[("DRE", "N10")] = round(t["mc"], 2)
        exp[("DRE", "N15")] = round(t["op"], 2); exp[("DRE", "N20")] = round(t["ll"], 2)
        exp[("DRE", "B20")] = round(A[0]["ll"], 2); exp[("DRE", "C20")] = round(A[1]["ll"], 2)
        n = sum(1 for k in range(12) if A[k]["rec"] > 0)
        cf_med = sum(A[k]["cf"] for k in range(12)) / n
        mcp = t["mc"] / t["rec"]
        exp[("Ponto de Equilíbrio", "I5")] = round(cf_med / mcp, 2)
        exp[("Ponto de Equilíbrio", "E8")] = round((cf_med + META_LUCRO) / mcp, 2)
        exp[("Ponto de Equilíbrio", "F12")] = round(A[0]["pe"], 2)
        abaixo = sum(1 for k in range(12) if A[k]["rec"] > 0 and A[k]["pe"] and A[k]["rec"] < A[k]["pe"])
        acima = sum(1 for k in range(12) if A[k]["rec"] > 0 and A[k]["pe"] and A[k]["rec"] >= A[k]["pe"])
        exp[("Ponto de Equilíbrio", "G8")] = acima; exp[("Ponto de Equilíbrio", "I8")] = abaixo
        exp[("Ponto de Equilíbrio", "A8")] = round(1 - (cf_med / mcp * n) / t["rec"], 4)
    return exp
