# -*- coding: utf-8 -*-
import datetime as dt
import random
from lib import *

SLUG = "controle-de-obras"
PASTA = "construcao/controle-de-obras"
NOME = "Controle de Obras (Orçado x Realizado)"
NE, NO, NC, NM = 20, 300, 1500, 60
E0 = 4
CONTRATO = 480000.0
MARGEM_ALVO = 0.15
CATS = ["Material", "Mão de obra", "Equipamentos", "Subempreitada", "Projetos e taxas", "Outros"]
FORN = ["Depósito de Materiais Exemplo", "Concreteira Exemplo", "Elétrica Exemplo", "Hidráulica Exemplo", "Equipe de Pedreiros A", "Equipe de Acabamento B", "Locadora Exemplo", "Esquadrias Exemplo", "Tintas Exemplo", "Escritório de Projetos Exemplo"]
D = dt.date
ETAPAS = [  # nome, orçado, ini, fim, físico, ini real, fim real, fator de custo
    ("Serviços preliminares", 18000, D(2026, 5, 4), D(2026, 5, 22), 1.0, D(2026, 5, 4), D(2026, 5, 25), 1.02),
    ("Fundação", 52000, D(2026, 5, 18), D(2026, 6, 26), 1.0, D(2026, 5, 20), D(2026, 7, 3), 1.06),
    ("Estrutura", 78000, D(2026, 6, 22), D(2026, 8, 7), 1.0, D(2026, 6, 29), D(2026, 8, 14), 1.09),
    ("Alvenaria", 46000, D(2026, 7, 27), D(2026, 9, 4), 1.0, D(2026, 8, 3), D(2026, 9, 11), 1.12),
    ("Instalações elétricas", 31000, D(2026, 8, 24), D(2026, 9, 25), 0.80, D(2026, 8, 31), None, 1.18),
    ("Instalações hidráulicas", 26000, D(2026, 8, 24), D(2026, 9, 25), 1.0, D(2026, 8, 31), D(2026, 9, 28), 1.0),
    ("Revestimentos", 52000, D(2026, 9, 14), D(2026, 10, 30), 0.45, D(2026, 9, 16), None, 1.10),
    ("Esquadrias", 34000, D(2026, 10, 5), D(2026, 11, 6), 0.10, D(2026, 10, 6), None, 1.20),
    ("Pintura", 24000, D(2026, 11, 2), D(2026, 11, 27), 0.0, None, None, 1.0),
    ("Acabamentos e limpeza", 31000, D(2026, 11, 23), D(2026, 12, 18), 0.0, None, None, 1.0),
]
UN = ["m²", "m³", "un", "vb", "h", "kg"]


def sample_data():
    rnd = random.Random(1010)
    orc = []
    for (nome, val, ini, fim, fis, ir, fr, fc) in ETAPAS:
        cats = rnd.sample(["Material", "Mão de obra", "Subempreitada", "Equipamentos"], 3)
        for j, share in enumerate([0.45, 0.40, 0.15]):
            q = rnd.choice([12, 24, 40, 80, 120, 200])
            u = round(val * share / q, 2)
            orc.append(dict(etapa=nome, item=f"{nome} - {cats[j].lower()}", cat=cats[j], un=rnd.choice(UN), qtd=q, unit=u, total=q * u))
    custos = []
    hoje = REF_DATE
    for (nome, val, ini, fim, fis, ir, fr, fc) in ETAPAS:
        if fis <= 0 or ir is None:
            continue
        orc_e = sum(o["total"] for o in orc if o["etapa"] == nome)
        total_real = round(orc_e * fis * fc, 2)
        cats = [o["cat"] for o in orc if o["etapa"] == nome]
        end = min(hoje, fr or hoje)
        n = rnd.randint(4, 6)
        parts = [rnd.uniform(0.6, 1.4) for _ in range(n)]
        s = sum(parts)
        acc = 0.0
        for k in range(n):
            v = round(total_real * parts[k] / s, 2) if k < n - 1 else round(total_real - acc, 2)
            acc += v
            span = (end - ir).days
            d_ = ir + dt.timedelta(days=int(span * (k + 1) / n) - rnd.randint(0, 2))
            d_ = max(ir, min(d_, hoje))
            status = "Pago" if (hoje - d_).days > 12 or rnd.random() < 0.3 else "A pagar"
            custos.append((d_, nome, cats[k % len(cats)], rnd.choice(FORN), f"Pagamento {nome.lower()} ({k+1}/{n})", v, status, d_ + dt.timedelta(days=15)))
    custos.sort(key=lambda c: c[0])
    meds = [
        (1, D(2026, 5, 29), "Medição 1: serviços preliminares e início da fundação", 48000.0, D(2026, 6, 15), D(2026, 6, 15), 48000.0),
        (2, D(2026, 6, 30), "Medição 2: fundação concluída", 72000.0, D(2026, 7, 15), D(2026, 7, 16), 72000.0),
        (3, D(2026, 7, 31), "Medição 3: estrutura 70%", 90000.0, D(2026, 8, 14), D(2026, 8, 14), 90000.0),
        (4, D(2026, 8, 31), "Medição 4: estrutura concluída e alvenaria 40%", 78000.0, D(2026, 9, 15), D(2026, 9, 18), 78000.0),
        (5, D(2026, 9, 30), "Medição 5: alvenaria e instalações", 82000.0, D(2026, 10, 7), None, None),
        (6, D(2026, 10, 30), "Medição 6: revestimentos (prevista)", 60000.0, D(2026, 11, 13), None, None),
    ]
    return orc, custos, meds


def analyze(orc, custos, meds):
    hoje = REF_DATE
    a = {}
    tot_orc = sum(o["total"] for o in orc)
    real = sum(c[5] for c in custos)
    eacs = []
    fis_pond = 0.0
    atras = 0
    rows = []
    for (nome, val, ini, fim, fis, ir, fr, fc) in ETAPAS:
        o = sum(x["total"] for x in orc if x["etapa"] == nome)
        r = sum(c[5] for c in custos if c[1] == nome)
        eac = r / fis if fis >= 0.05 else o
        h = max(0, min(1, ((hoje - ini).days + 1) / ((fim - ini).days + 1)))
        sit = "Concluída" if fis >= 1 else ("A iniciar" if hoje < ini else ("ATRASADA" if fis < h - 0.1 else "Em dia"))
        atras += sit == "ATRASADA"
        fis_pond += o * fis
        eacs.append(eac)
        rows.append(dict(nome=nome, o=o, r=r, eac=eac, fis=fis, sit=sit, desv=eac - o))
    eac_tot = sum(eacs) + (real - sum(r["r"] for r in rows))
    a.update(orc=tot_orc, real=real, fis=fis_pond / tot_orc, eac=eac_tot, margem=CONTRATO - eac_tot, atras=atras, rows=rows,
             recebido=sum(m[6] or 0 for m in meds), pago=sum(c[5] for c in custos if c[6] == "Pago"),
             areceber=sum(m[3] - (m[6] or 0) for m in meds))
    return a


def build(bk: Book):
    wb = bk.wb
    bk.inicio(
        "Controle de Obras", "Carvex XLS · Descubra o estouro de custo e prazo enquanto ainda dá tempo de agir",
        "Monte o orçamento por etapa, lance os custos reais e atualize o % físico de cada etapa. A planilha compara orçado x realizado, projeta o custo final da obra, "
        "calcula a margem prevista, mostra o cronograma em Gantt e controla as medições recebidas.",
        [("Config", "Informe o nome da obra, o valor do contrato, as datas de início e fim previstas e a margem mínima que você aceita."),
         ("Cronograma", "Liste as etapas (até 20) com início e fim previstos. Atualize o % físico executado toda semana."),
         ("Orçamento", "Para cada etapa, liste os itens: categoria, unidade, quantidade e custo unitário. O total orçado é calculado."),
         ("Custos", "Lance cada nota, compra, folha ou serviço pago com data, etapa e categoria. Marque Pago ou A pagar."),
         ("Medições", "Registre as medições (faturamentos) à obra e os recebimentos. Veja tudo no Resumo.")],
        [("Config", "Dados da obra, contrato e parâmetros."), ("Cronograma", "Etapas, datas, % físico e Gantt automático."),
         ("Orçamento", "Itens orçados por etapa e categoria."), ("Custos", "Custos reais lançados."),
         ("Medições", "Faturamentos e recebimentos da obra."), ("Resumo", "Margem prevista, custo projetado, orçado x realizado e fluxo.")],
        avisos=["O nome da etapa deve ser igual no Cronograma, Orçamento e Custos (use a lista suspensa).",
                "Atualize o % físico com a realidade do canteiro: é ele que permite projetar o custo final (custo real / % físico).",
                "Projeção de custo é uma estimativa. Revise com o engenheiro responsável antes de decidir."])

    ws = bk.sheet("Config")
    bk.banner(ws, "Dados da obra", "Preencha as células amarelas.", 5)
    ws.set_column(0, 0, 3); ws.set_column(1, 1, 38); ws.set_column(2, 2, 22); ws.set_column(3, 3, 3); ws.set_column(4, 4, 24); ws.set_column(5, 5, 3); ws.set_column(6, 6, 34)
    lf = bk.fmt("lbl")
    ws.write(3, 1, "Obra", lf); bk.w(ws, (3, 2), "Reforma Comercial Exemplo" if bk.sample else None, bk.fmt("in"))
    ws.write(4, 1, "Cliente", lf); bk.w(ws, (4, 2), "Cliente Exemplo" if bk.sample else None, bk.fmt("in"))
    ws.write(5, 1, "Valor do contrato (R$)", lf); bk.w(ws, (5, 2), CONTRATO if bk.sample else None, bk.fmt("in", nf="money"))
    ws.write(6, 1, "Início previsto", lf); bk.w(ws, (6, 2), D(2026, 5, 4) if bk.sample else None, bk.fmt("in", nf="date", align="center"))
    ws.write(7, 1, "Fim previsto", lf); bk.w(ws, (7, 2), D(2026, 12, 18) if bk.sample else None, bk.fmt("in", nf="date", align="center"))
    ws.write(8, 1, "Margem mínima aceitável (%)", lf); bk.w(ws, (8, 2), MARGEM_ALVO, bk.fmt("in", nf="pct0", align="center"))
    ws.write(9, 1, "Data de hoje (referência)", lf)
    if bk.sample:
        bk.w(ws, "C10", REF_DATE, bk.fmt("in", nf="date", align="center"))
    else:
        bk.fx(ws, "C10", "TODAY()", bk.fmt("calc", nf="date", align="center"))
    bk.dv_num(ws, "C6", 0); bk.dv_date(ws, "C7:C8"); bk.dv_num(ws, "C9", 0, 0.9)
    for n, a in (("Contrato", "C6"), ("DataIni", "C7"), ("DataFim", "C8"), ("MargemAlvo", "C9"), ("Hoje", "C10")):
        bk.define(n, f"=Config!${a[0]}${a[1:]}")
    ws.write(3, 4, "Categorias de custo", bk.fmt("h")); ws.write(3, 6, "Fornecedores", bk.fmt("h"))
    for i in range(20):
        bk.w(ws, (4 + i, 4), CATS[i] if i < len(CATS) else None, bk.fmt("in")); bk.w(ws, (4 + i, 6), FORN[i] if (bk.sample and i < len(FORN)) else None, bk.fmt("in"))
    bk.define("CatCusto", "=Config!$E$5:$E$24"); bk.define("Forn", "=Config!$G$5:$G$24")

    orc, custos, meds = sample_data() if bk.sample else ([], [], [])
    fi = bk.fmt("in"); fd = bk.fmt("in", nf="date", align="center"); fm = bk.fmt("in", nf="money")
    cm = bk.fmt("calc", nf="money"); cac = bk.fmt("calc", align="center")
    # ---------------- Cronograma
    wc = bk.sheet("Cronograma", tab=G_NEON)
    NW = 40
    bk.banner(wc, "Cronograma e Gantt", "Verde claro = previsto. Verde escuro = executado (% físico). Coluna destacada = semana atual.", 12 + NW)
    bk.header(wc, 3, 0, ["Etapa", "Início previsto", "Fim previsto", "% físico executado", "Início real", "Fim real", "Duração (dias)", "% do tempo decorrido", "Físico - tempo", "SITUAÇÃO", "Peso no orçamento"],
              [28, 11, 11, 11, 11, 11, 9, 11, 9, 12, 10], 48)
    wc.set_column(11, 11, 2)
    for i in range(NE):
        r = E0 + i; x = r + 1
        e = ETAPAS[i] if (bk.sample and i < len(ETAPAS)) else None
        bk.w(wc, (r, 0), e[0] if e else None, fi); bk.w(wc, (r, 1), e[2] if e else None, fd); bk.w(wc, (r, 2), e[3] if e else None, fd)
        bk.w(wc, (r, 3), e[4] if e else None, bk.fmt("in", nf="pct0", align="center")); bk.w(wc, (r, 4), e[5] if e else None, fd); bk.w(wc, (r, 5), e[6] if e else None, fd)
        bk.fx(wc, (r, 6), f'IF(OR($B{x}="",$C{x}=""),"",$C{x}-$B{x}+1)', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wc, (r, 7), f'IF($G{x}="","",MAX(0,MIN(1,(Hoje-$B{x}+1)/$G{x})))', bk.fmt("calc", nf="pct0", align="center"))
        bk.fx(wc, (r, 8), f'IF($H{x}="","",N($D{x})-$H{x})', bk.fmt("calc", nf="0%", align="center"))
        bk.fx(wc, (r, 9), f'IF($A{x}="","",IF(N($D{x})>=1,"Concluída",IF(Hoje<$B{x},"A iniciar",IF(N($D{x})<$H{x}-0.1,"ATRASADA","Em dia"))))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wc, (r, 10), f'IF($A{x}="","",IFERROR(SUMIFS(OrcTotal,OrcEtapa,$A{x})/SUM(OrcTotal),0))', bk.fmt("calc", nf="pct", align="center"))
    ce = E0 + NE
    bk.dv_date(wc, f"B{E0+1}:C{ce}"); bk.dv_date(wc, f"E{E0+1}:F{ce}"); bk.dv_num(wc, f"D{E0+1}:D{ce}", 0, 1, "Digite em %, de 0% a 100%")
    for t, bg, fg in (("ATRASADA", C_RED, "#FFFFFF"), ("Concluída", G_NEON, "#052e16"), ("Em dia", G_LIGHT, "#15803D"), ("A iniciar", "#E5E7EB", "#374151")):
        wc.conditional_format(f"J{E0+1}:J{ce}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    # Gantt semanal
    for w in range(NW):
        c = 12 + w
        wc.set_column(c, c, 3.2)
        if w == 0:
            bk.fx(wc, (3, c), "IF(DataIni=\"\",\"\",DataIni-WEEKDAY(DataIni,2)+1)", bk.fmt("h", nf="dd/mm", rotation=90, font_size=8))
        else:
            bk.fx(wc, (3, c), f'IF({col(c-1)}4="","",{col(c-1)}4+7)', bk.fmt("h", nf="dd/mm", rotation=90, font_size=8))
    for i in range(NE):
        for w in range(NW):
            wc.write_blank(E0 + i, 12 + w, None, bk.fmt("plain", border_color="#E5E7EB"))
    g = f"M{E0+1}:{col(11+NW)}{ce}"
    wc.conditional_format(g, {"type": "formula", "criteria": f'=AND($B{E0+1}<>"",$C{E0+1}<>"",M$4<>"",$B{E0+1}<=M$4+6,$C{E0+1}>=M$4,M$4<=$B{E0+1}+N($D{E0+1})*$G{E0+1}-1)', "format": wb.add_format({"bg_color": G_DARK})})
    wc.conditional_format(g, {"type": "formula", "criteria": f'=AND($B{E0+1}<>"",$C{E0+1}<>"",M$4<>"",$B{E0+1}<=M$4+6,$C{E0+1}>=M$4)', "format": wb.add_format({"bg_color": "#86EFAC"})})
    wc.conditional_format(g, {"type": "formula", "criteria": '=AND(M$4<>"",M$4<=Hoje,Hoje<=M$4+6)', "format": wb.add_format({"bg_color": "#FEF3C7"})})
    wc.freeze_panes(4, 1)
    bk.define("EtapaLista", f"=Cronograma!$A${E0+1}:$A${ce}")

    # ---------------- Orçamento
    wo = bk.sheet("Orçamento")
    bk.banner(wo, "Orçamento por etapa", "Custo orçado (sem BDI). Total = quantidade x custo unitário.", 8)
    bk.header(wo, 3, 0, ["Etapa", "Item / serviço", "Categoria", "Un.", "Quantidade", "Custo unitário (R$)", "TOTAL ORÇADO (R$)"], [28, 40, 16, 7, 11, 15, 16], 36)
    for i in range(NO):
        r = E0 + i; x = r + 1
        o = orc[i] if i < len(orc) else None
        bk.w(wo, (r, 0), o["etapa"] if o else None, fi); bk.w(wo, (r, 1), o["item"] if o else None, fi); bk.w(wo, (r, 2), o["cat"] if o else None, fi)
        bk.w(wo, (r, 3), o["un"] if o else None, bk.fmt("in", align="center")); bk.w(wo, (r, 4), o["qtd"] if o else None, bk.fmt("in", nf="#,##0.##")); bk.w(wo, (r, 5), o["unit"] if o else None, fm)
        bk.fx(wo, (r, 6), f'IF(OR($E{x}="",$F{x}=""),"",$E{x}*$F{x})', bk.fmt("calc", nf="money", bold=True))
    oe = E0 + NO
    bk.dv_list(wo, f"A{E0+1}:A{oe}", "=EtapaLista"); bk.dv_list(wo, f"C{E0+1}:C{oe}", "=CatCusto"); bk.dv_num(wo, f"E{E0+1}:F{oe}", 0)
    wo.write(2, 5, "Total orçado:", bk.fmt("lbl", align="right")); bk.fx(wo, (2, 6), f"SUM(G{E0+1}:G{oe})", bk.fmt("tot", nf="money"))
    wo.freeze_panes(4, 0); wo.autofilter(3, 0, oe - 1, 6)
    bk.define("OrcEtapa", f"=Orçamento!$A${E0+1}:$A${oe}"); bk.define("OrcCat", f"=Orçamento!$C${E0+1}:$C${oe}"); bk.define("OrcTotal", f"=Orçamento!$G${E0+1}:$G${oe}")

    # ---------------- Custos
    wk = bk.sheet("Custos")
    bk.banner(wk, "Custos reais da obra", "Lance cada pagamento/nota. Marque 'A pagar' o que ainda não saiu do caixa.", 10)
    bk.header(wk, 3, 0, ["Data", "Etapa", "Categoria", "Fornecedor", "Descrição", "Valor (R$)", "Status", "Vencimento", "Mês", "Conferência"], [11, 26, 16, 28, 38, 14, 10, 11, 9, 18], 30)
    for i in range(NC):
        r = E0 + i; x = r + 1
        c = custos[i] if i < len(custos) else (None,) * 8
        bk.w(wk, (r, 0), c[0], fd); bk.w(wk, (r, 1), c[1], fi); bk.w(wk, (r, 2), c[2], fi); bk.w(wk, (r, 3), c[3], fi); bk.w(wk, (r, 4), c[4], fi)
        bk.w(wk, (r, 5), c[5], fm); bk.w(wk, (r, 6), c[6], bk.fmt("in", align="center")); bk.w(wk, (r, 7), c[7], fd)
        bk.fx(wk, (r, 8), f'IF($A{x}="","",DATE(YEAR($A{x}),MONTH($A{x}),1))', bk.fmt("calc", nf="mon", align="center"))
        bk.fx(wk, (r, 9), f'IF($A{x}="","",IF(OR($B{x}="",$C{x}="",$F{x}="",$G{x}=""),"Preencher tudo",IF(COUNTIF(EtapaLista,$B{x})=0,"Etapa inválida","OK")))', cac)
    ke = E0 + NC
    bk.dv_date(wk, f"A{E0+1}:A{ke}"); bk.dv_list(wk, f"B{E0+1}:B{ke}", "=EtapaLista"); bk.dv_list(wk, f"C{E0+1}:C{ke}", "=CatCusto"); bk.dv_list(wk, f"D{E0+1}:D{ke}", "=Forn")
    bk.dv_num(wk, f"F{E0+1}:F{ke}", 0); bk.dv_list(wk, f"G{E0+1}:G{ke}", ["Pago", "A pagar"]); bk.dv_date(wk, f"H{E0+1}:H{ke}")
    wk.conditional_format(f"J{E0+1}:J{ke}", {"type": "cell", "criteria": "!=", "value": '"OK"', "format": wb.add_format({"font_color": C_RED, "bold": True})})
    wk.conditional_format(f"G{E0+1}:G{ke}", {"type": "cell", "criteria": "==", "value": '"A pagar"', "format": wb.add_format({"font_color": "#B45309", "bold": True})})
    wk.freeze_panes(4, 0); wk.autofilter(3, 0, ke - 1, 9)
    for n, c in (("CustoData", "A"), ("CustoEtapa", "B"), ("CustoCat", "C"), ("CustoValor", "F"), ("CustoStatus", "G"), ("CustoMes", "I")):
        bk.define(n, f"=Custos!${c}${E0+1}:${c}${ke}")

    # ---------------- Medições
    wm = bk.sheet("Medições")
    bk.banner(wm, "Medições e recebimentos", "Cada medição é um faturamento ao cliente. Preencha data e valor ao receber.", 9)
    bk.header(wm, 3, 0, ["Nº", "Data da medição", "Descrição", "Valor medido (R$)", "Vencimento", "Data do recebimento", "Valor recebido (R$)", "Saldo a receber", "Situação"], [6, 12, 46, 15, 12, 12, 15, 15, 13], 36)
    for i in range(NM):
        r = E0 + i; x = r + 1
        m = meds[i] if i < len(meds) else (None,) * 7
        bk.w(wm, (r, 0), m[0], bk.fmt("in", nf="0", align="center")); bk.w(wm, (r, 1), m[1], fd); bk.w(wm, (r, 2), m[2], fi); bk.w(wm, (r, 3), m[3], fm)
        bk.w(wm, (r, 4), m[4], fd); bk.w(wm, (r, 5), m[5], fd); bk.w(wm, (r, 6), m[6], fm)
        bk.fx(wm, (r, 7), f'IF($D{x}="","",MAX(0,$D{x}-N($G{x})))', cm)
        bk.fx(wm, (r, 8), f'IF($D{x}="","",IF($H{x}<=0.005,"Recebida",IF(AND($E{x}<>"",$E{x}<Hoje),"ATRASADA","A receber")))', bk.fmt("calc", align="center", bold=True))
    me = E0 + NM
    bk.dv_date(wm, f"B{E0+1}:B{me}"); bk.dv_date(wm, f"E{E0+1}:F{me}"); bk.dv_num(wm, f"D{E0+1}:D{me}", 0); bk.dv_num(wm, f"G{E0+1}:G{me}", 0)
    for t, bg, fg in (("Recebida", G_LIGHT, "#15803D"), ("ATRASADA", C_RED, "#FFFFFF"), ("A receber", "#DBEAFE", "#1E40AF")):
        wm.conditional_format(f"I{E0+1}:I{me}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wm.freeze_panes(4, 0)
    MV = lambda c: f"Medições!${c}${E0+1}:${c}${me}"

    # ---------------- Resumo
    wr = bk.sheet("Resumo", tab=G_NEON, onepage=True)
    bk.banner(wr, "Resumo da obra", "Orçado x realizado, custo projetado e margem prevista. Atualiza sozinho.", 10)
    wr.set_column(0, 0, 30)
    for c in range(1, 10):
        wr.set_column(c, c, 14)
    # tabela de etapas primeiro (referências dos KPIs)
    wr.merge_range(12, 0, 12, 7, "Etapas: orçado, realizado e custo projetado", bk.fmt("sec"))
    bk.header(wr, 13, 0, ["Etapa", "Orçado", "Realizado", "% físico", "Custo projetado (EAC)", "Desvio projetado (R$)", "Desvio %", "Situação"], height=36)
    for i in range(NE):
        r = 14 + i; x = r + 1; cr = E0 + 1 + i
        bk.fx(wr, (r, 0), f'IF(Cronograma!A{cr}="","",Cronograma!A{cr})', bk.fmt("plain", bold=True))
        bk.fx(wr, (r, 1), f'IF($A{x}="","",SUMIFS(OrcTotal,OrcEtapa,$A{x}))', cm)
        bk.fx(wr, (r, 2), f'IF($A{x}="","",SUMIFS(CustoValor,CustoEtapa,$A{x}))', cm)
        bk.fx(wr, (r, 3), f'IF($A{x}="","",N(Cronograma!D{cr}))', bk.fmt("calc", nf="pct0", align="center"))
        bk.fx(wr, (r, 4), f'IF($A{x}="","",IF($D{x}>=0.05,$C{x}/$D{x},$B{x}))', cm)
        bk.fx(wr, (r, 5), f'IF($A{x}="","",$E{x}-$B{x})', cm)
        bk.fx(wr, (r, 6), f'IF(OR($A{x}="",N($B{x})=0),"",$F{x}/$B{x})', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wr, (r, 7), f'IF($A{x}="","",Cronograma!J{cr})', bk.fmt("calc", align="center", bold=True))
    wr.write(34, 0, "TOTAL DA OBRA", bk.fmt("tot"))
    bk.fx(wr, (34, 1), "SUM(OrcTotal)", bk.fmt("tot", nf="money")); bk.fx(wr, (34, 2), "SUM(CustoValor)", bk.fmt("tot", nf="money"))
    bk.fx(wr, (34, 3), "IFERROR(SUMPRODUCT(B15:B34,D15:D34)/SUM(B15:B34),0)", bk.fmt("tot", nf="pct", align="center"))
    bk.fx(wr, (34, 4), "SUM(E15:E34)+(C35-SUM(C15:C34))", bk.fmt("tot", nf="money")); bk.fx(wr, (34, 5), "E35-B35", bk.fmt("tot", nf="money"))
    bk.fx(wr, (34, 6), "IF(B35=0,0,F35/B35)", bk.fmt("tot", nf="pct", align="center")); wr.write(34, 7, "", bk.fmt("tot"))
    for t, bg, fg in (("ATRASADA", C_RED, "#FFFFFF"), ("Concluída", G_NEON, "#052e16"), ("Em dia", G_LIGHT, "#15803D")):
        wr.conditional_format("H15:H34", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wr.conditional_format("F15:F35", {"type": "cell", "criteria": ">", "value": 0, "format": wb.add_format({"font_color": C_RED, "bold": True})})
    bk.kpi(wr, 3, 0, "VALOR DO CONTRATO", "Contrato", "money", 1)
    bk.kpi(wr, 3, 1, "ORÇADO", "B35", "money", 2); bk.kpi(wr, 3, 3, "REALIZADO", "C35", "money", 2)
    bk.kpi(wr, 3, 5, "% CUSTO CONSUMIDO", "IFERROR(C35/B35,0)", "pct", 2); bk.kpi(wr, 3, 7, "% FÍSICO DA OBRA", "D35", "pct", 2)
    bk.kpi(wr, 6, 0, "CUSTO FINAL PROJETADO", "E35", "money", 1)
    bk.kpi(wr, 6, 1, "MARGEM PREVISTA (R$)", "A5-A8", "money", 2, color="#15803D")
    bk.kpi(wr, 6, 3, "MARGEM PREVISTA (%)", "IF(A5=0,0,B8/A5)", "pct", 2)
    bk.kpi(wr, 6, 5, "MARGEM ORÇADA (%)", "IF(A5=0,0,(A5-B5)/A5)", "pct", 2)
    bk.kpi(wr, 6, 7, "ALERTA", 'IF(A5=0,"-",IF(B8<0,"OBRA NO PREJUÍZO",IF(D8<MargemAlvo,"Margem abaixo da meta","Margem dentro da meta")))', "gen", 2, color=C_RED)
    wr.set_row(7, 36)
    bk.kpi(wr, 9, 0, "RECEBIDO (medições)", f'SUM({MV("G")})', "money", 1)
    bk.kpi(wr, 9, 1, "PAGO (custos)", 'SUMIFS(CustoValor,CustoStatus,"Pago")', "money", 2)
    bk.kpi(wr, 9, 3, "SALDO DE CAIXA DA OBRA", "A11-B11", "money", 2)
    bk.kpi(wr, 9, 5, "A RECEBER (medições)", f'SUM({MV("H")})', "money", 2)
    bk.kpi(wr, 9, 7, "ETAPAS ATRASADAS", f'COUNTIF(Cronograma!$J${E0+1}:$J${ce},"ATRASADA")', "int", 2, color=C_RED)
    wr.merge_range(37, 0, 37, 4, "Custos por categoria", bk.fmt("sec"))
    bk.header(wr, 38, 0, ["Categoria", "Orçado", "Realizado", "% do realizado"], height=22)
    for i in range(6):
        r = 39 + i; x = r + 1
        bk.fx(wr, (r, 0), f'IF(INDEX(CatCusto,{i+1})="","",INDEX(CatCusto,{i+1}))', bk.fmt("plain", bold=True))
        bk.fx(wr, (r, 1), f'IF($A{x}="","",SUMIFS(OrcTotal,OrcCat,$A{x}))', cm)
        bk.fx(wr, (r, 2), f'IF($A{x}="","",SUMIFS(CustoValor,CustoCat,$A{x}))', cm)
        bk.fx(wr, (r, 3), f'IF(OR($A{x}="",$C$35=0),"",C{x}/$C$35)', bk.fmt("calc", nf="pct", align="center"))
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Orçado", "categories": "=Resumo!$A$15:$A$24", "values": "=Resumo!$B$15:$B$24", "fill": {"color": "#D1D5DB"}, "gap": 60})
    ch.add_series({"name": "Custo projetado", "categories": "=Resumo!$A$15:$A$24", "values": "=Resumo!$E$15:$E$24", "fill": {"color": G_MID}})
    ch.add_series({"name": "Realizado", "categories": "=Resumo!$A$15:$A$24", "values": "=Resumo!$C$15:$C$24", "fill": {"color": G_DARK}})
    ch.set_title({"name": "Orçado x projetado x realizado por etapa", "name_font": {"size": 12}}); ch.set_legend({"position": "bottom"})
    ch.set_x_axis({"num_font": {"rotation": -45, "size": 8}}); ch.set_size({"width": 820, "height": 330})
    wr.insert_chart("A47", ch)
    pie = wb.add_chart({"type": "doughnut"})
    pie.add_series({"name": "Realizado por categoria", "categories": "=Resumo!$A$40:$A$45", "values": "=Resumo!$C$40:$C$45", "data_labels": {"percentage": True}})
    pie.set_title({"name": "Realizado por categoria", "name_font": {"size": 12}}); pie.set_size({"width": 400, "height": 250}); pie.set_legend({"position": "right"})
    wr.insert_chart("F38", pie)
    wr.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
    bk.finish()

    exp = {}
    if bk.sample:
        a = analyze(orc, custos, meds)
        exp[("Resumo", "B35")] = round(a["orc"], 2); exp[("Resumo", "C35")] = round(a["real"], 2)
        exp[("Resumo", "D35")] = round(a["fis"], 4); exp[("Resumo", "E35")] = round(a["eac"], 2)
        exp[("Resumo", "B8")] = round(a["margem"], 2)
        exp[("Resumo", "D8")] = round(a["margem"] / CONTRATO, 4)
        exp[("Resumo", "A11")] = round(a["recebido"], 2); exp[("Resumo", "B11")] = round(a["pago"], 2)
        exp[("Resumo", "F11")] = round(a["areceber"], 2); exp[("Resumo", "H11")] = a["atras"]
        for i, rw in enumerate(a["rows"]):
            exp[("Resumo", f"H{15+i}")] = rw["sit"]
            exp[("Resumo", f"E{15+i}")] = round(rw["eac"], 2)
    return exp
