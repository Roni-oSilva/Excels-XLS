# -*- coding: utf-8 -*-
import datetime as dt
import random
from lib import *

SLUG = "crm-funil"
PASTA = "vendas/crm-funil"
NOME = "CRM e Funil de Vendas com Follow-up"
N = 1000
R0 = 4
LAST = R0 + N
ETAPAS = [("Novo", 0.10), ("Contato feito", 0.25), ("Proposta enviada", 0.50), ("Negociação", 0.75), ("Ganho", 1.0), ("Perdido", 0.0)]
ORIGENS = ["Indicação", "Instagram", "Google", "WhatsApp", "Site", "Evento", "Outros"]
MOTIVOS = ["Preço", "Fechou com concorrente", "Sem resposta", "Sem orçamento", "Prazo", "Outro"]
VENDS = [("Vendedor A", 25000.0), ("Vendedor B", 20000.0), ("Vendedor C", 18000.0), ("Vendedor D", 15000.0)]
DIAS_SC = 7


def sample_leads():
    rnd = random.Random(505)
    ref = REF_DATE
    leads = []
    for i in range(64):
        entrada = ref - dt.timedelta(days=rnd.randint(2, 130))
        origem = rnd.choices(ORIGENS, weights=[30, 18, 16, 14, 10, 6, 6])[0]
        vend = rnd.choice(VENDS)[0]
        valor = float(rnd.choice([1800, 2500, 3200, 4500, 6000, 8500, 12000, 15000]))
        r = rnd.random()
        if r < 0.28:
            etapa = "Ganho"
        elif r < 0.52:
            etapa = "Perdido"
        else:
            etapa = rnd.choices(["Novo", "Contato feito", "Proposta enviada", "Negociação"], weights=[20, 30, 30, 20])[0]
        fech = ult = prox = motivo = None
        if etapa in ("Ganho", "Perdido"):
            fech = min(ref, entrada + dt.timedelta(days=rnd.randint(7, 55)))
            ult = fech
            if etapa == "Perdido":
                motivo = rnd.choices(MOTIVOS, weights=[30, 25, 25, 10, 5, 5])[0]
            if etapa == "Ganho" and rnd.random() < 0.35:   # garante vendas no mês de referência
                fech = ref - dt.timedelta(days=rnd.randint(0, 7))
                entrada = min(entrada, fech - dt.timedelta(days=rnd.randint(10, 40)))
        else:
            ult = ref - dt.timedelta(days=rnd.choice([0, 1, 2, 3, 5, 6, 9, 12, 15]))
            ult = max(ult, entrada)
            k = rnd.random()
            if k < 0.30:
                prox = ref - dt.timedelta(days=rnd.randint(1, 6))
            elif k < 0.42:
                prox = ref
            elif k < 0.85:
                prox = ref + dt.timedelta(days=rnd.randint(1, 10))
        leads.append(dict(entrada=entrada, nome=f"Lead {i+1:03d} ({rnd.choice(['Padaria', 'Clínica', 'Loja', 'Escola', 'Oficina', 'Escritório', 'Hotel', 'Academia'])})",
                          contato=f"(00) 9{rnd.randint(1000,9999)}-{rnd.randint(1000,9999)}", origem=origem, vend=vend, etapa=etapa, valor=valor,
                          ult=ult, prox=prox, fech=fech, motivo=motivo, obs=None))
    leads.sort(key=lambda d: d["entrada"])
    return leads


def analyze(leads):
    ref = REF_DATE
    prob = dict(ETAPAS)
    o = dict(abertos=0, valor_aberto=0.0, pond=0.0, ganho_mes=0.0, ganhos=0, perdidos=0, ticket=0, atras=0, ciclo=[], by_orig={}, by_vend={})
    for d in leads:
        sit = "Ganho" if d["etapa"] == "Ganho" else ("Perdido" if d["etapa"] == "Perdido" else "Aberto")
        if sit == "Aberto":
            o["abertos"] += 1; o["valor_aberto"] += d["valor"]; o["pond"] += d["valor"] * prob[d["etapa"]]
            dias = (ref - (d["ult"] or d["entrada"])).days
            if d["prox"] is None:
                fu = "ATRASADO" if dias > DIAS_SC else "Definir data"
            else:
                fu = "ATRASADO" if d["prox"] < ref else ("HOJE" if d["prox"] == ref else "Em dia")
            d["fu"] = fu
            if fu == "ATRASADO":
                o["atras"] += 1
        elif sit == "Ganho":
            o["ganhos"] += 1
            o["ticket"] += d["valor"]
            if d["fech"] and d["fech"].year == ref.year and d["fech"].month == ref.month:
                o["ganho_mes"] += d["valor"]
            if d["fech"]:
                o["ciclo"].append((d["fech"] - d["entrada"]).days)
        else:
            o["perdidos"] += 1
        bo = o["by_orig"].setdefault(d["origem"], [0, 0]); bo[0] += 1; bo[1] += 1 if sit == "Ganho" else 0
        bv = o["by_vend"].setdefault(d["vend"], dict(g=0, p=0, mes=0.0, n=0)); bv["n"] += 1
        if sit == "Ganho":
            bv["g"] += 1
            if d["fech"] and d["fech"].year == ref.year and d["fech"].month == ref.month:
                bv["mes"] += d["valor"]
        elif sit == "Perdido":
            bv["p"] += 1
    o["ticket"] = o["ticket"] / o["ganhos"] if o["ganhos"] else 0
    return o


def build(bk: Book):
    wb = bk.wb
    bk.inicio(
        "CRM e Funil de Vendas", "Carvex XLS · Nenhum lead esquecido, nenhuma venda perdida por falta de follow-up",
        "Cadastre seus leads, acompanhe cada um pelas etapas do funil e marque o próximo contato. A planilha mostra a agenda de follow-up do dia, "
        "o valor previsto de vendas, a conversão por origem, o ranking dos vendedores e o cumprimento da meta do mês.",
        [("Config", "Ajuste as etapas e suas probabilidades, as origens dos leads, os vendedores e a meta mensal de cada um."),
         ("Cadastre os leads", "Na aba Leads, uma linha por lead: data de entrada, nome, contato, origem, vendedor, etapa e valor potencial."),
         ("Marque o próximo contato", "Preencha 'Último contato' e 'Próximo follow-up'. A coluna Follow-up avisa ATRASADO, HOJE ou Em dia."),
         ("Abra a Agenda todo dia", "A aba Agenda lista só quem precisa de contato hoje ou está atrasado."),
         ("Feche com data e motivo", "Ao mudar a etapa para Ganho ou Perdido, preencha a data de fechamento (e o motivo, se perdeu).")],
        [("Config", "Etapas do funil, origens, vendedores, metas e motivos de perda."), ("Leads", "Cadastro e acompanhamento (até 1.000 leads)."),
         ("Agenda", "Follow-ups de hoje e atrasados."), ("Funil", "Leads por etapa, conversão por origem e motivos de perda."),
         ("Vendedores", "Ranking, conversão e meta de cada vendedor."), ("Dashboard", "Indicadores e gráficos.")],
        avisos=["Não renomeie as etapas 'Ganho' e 'Perdido': a planilha as usa nos cálculos. As demais etapas podem ser renomeadas.",
                "A probabilidade de cada etapa é uma estimativa sua; ajuste conforme seu histórico de fechamento.",
                "A data de fechamento é obrigatória para Ganho/Perdido; sem ela a venda não entra nos relatórios do mês."])

    # ---------------- Config
    ws = bk.sheet("Config")
    bk.banner(ws, "Configurações", "Preencha as células amarelas.", 11)
    ws.set_column(0, 0, 3); ws.set_column(1, 1, 36); ws.set_column(2, 2, 14); ws.set_column(3, 3, 3)
    ws.set_column(4, 4, 20); ws.set_column(5, 5, 3); ws.set_column(6, 6, 20); ws.set_column(7, 7, 16); ws.set_column(8, 8, 3); ws.set_column(9, 9, 26)
    lf = bk.fmt("lbl")
    ws.write(3, 1, "Empresa", lf); bk.w(ws, (3, 2), "Consultoria Exemplo" if bk.sample else None, bk.fmt("in"))
    ws.write(4, 1, "Data de hoje (referência)", lf)
    if bk.sample:
        bk.w(ws, "C5", REF_DATE, bk.fmt("in", nf="date", align="center"))
    else:
        bk.fx(ws, "C5", "TODAY()", bk.fmt("calc", nf="date", align="center"))
    ws.write(5, 1, "Dias sem contato para alertar", lf); bk.w(ws, "C6", DIAS_SC, bk.fmt("in", nf="0", align="center"))
    bk.dv_num(ws, "C6", 1, 90, integer=True)
    bk.define("Hoje", "=Config!$C$5"); bk.define("DiasSC", "=Config!$C$6")
    ws.write(8, 1, "Etapa do funil", bk.fmt("h")); ws.write(8, 2, "Probabilidade", bk.fmt("h"))
    for i, (e, p) in enumerate(ETAPAS):
        bk.w(ws, (9 + i, 1), e, bk.fmt("in", bold=True)); bk.w(ws, (9 + i, 2), p, bk.fmt("in", nf="pct0", align="center"))
    bk.dv_num(ws, "C10:C15", 0, 1)
    bk.define("Etapas", "=Config!$B$10:$B$15"); bk.define("EtapaProb", "=Config!$C$10:$C$15")
    ws.write(3, 4, "Origens dos leads", bk.fmt("h"))
    for i in range(10):
        bk.w(ws, (4 + i, 4), ORIGENS[i] if i < len(ORIGENS) else None, bk.fmt("in"))
    ws.write(3, 6, "Vendedores", bk.fmt("h")); ws.write(3, 7, "Meta mensal (R$)", bk.fmt("h"))
    for i in range(10):
        v = VENDS[i] if i < len(VENDS) and bk.sample else (VENDS[i] if False else (None, None))
        bk.w(ws, (4 + i, 6), v[0], bk.fmt("in")); bk.w(ws, (4 + i, 7), v[1], bk.fmt("in", nf="money"))
    ws.write(3, 9, "Motivos de perda", bk.fmt("h"))
    for i in range(10):
        bk.w(ws, (4 + i, 9), MOTIVOS[i] if i < len(MOTIVOS) else None, bk.fmt("in"))
    bk.define("Origens", "=Config!$E$5:$E$14"); bk.define("Vendedores", "=Config!$G$5:$G$14"); bk.define("Motivos", "=Config!$J$5:$J$14")

    # ---------------- Leads
    leads = sample_leads() if bk.sample else []
    wl = bk.sheet("Leads")
    bk.banner(wl, "Leads", "Uma linha por lead. Atualize etapa, último contato e próximo follow-up sempre que falar com o cliente.", 21)
    heads = ["Nº", "Data de entrada", "Lead (nome / empresa)", "Contato", "Origem", "Vendedor", "Etapa", "Valor potencial (R$)", "Último contato",
             "Próximo follow-up", "Data de fechamento", "Motivo da perda", "Observações", "Prob.", "Valor ponderado", "Situação", "Dias sem contato",
             "FOLLOW-UP", "Seq. agenda", "Conferência"]
    wid = [6, 11, 32, 17, 13, 14, 16, 14, 11, 11, 11, 20, 26, 7, 13, 10, 9, 14, 7, 22]
    bk.header(wl, 3, 0, heads, wid, 44)
    fi = bk.fmt("in"); fd = bk.fmt("in", nf="date", align="center"); fm = bk.fmt("in", nf="money")
    cc = bk.fmt("calc", align="center"); cm = bk.fmt("calc", nf="money")
    for i in range(N):
        r = R0 + i; x = r + 1
        d = leads[i] if i < len(leads) else {}
        bk.fx(wl, (r, 0), f'IF($C{x}="","",ROW()-{R0})', cc)
        bk.w(wl, (r, 1), d.get("entrada"), fd); bk.w(wl, (r, 2), d.get("nome"), fi); bk.w(wl, (r, 3), d.get("contato"), fi)
        bk.w(wl, (r, 4), d.get("origem"), fi); bk.w(wl, (r, 5), d.get("vend"), fi); bk.w(wl, (r, 6), d.get("etapa"), fi)
        bk.w(wl, (r, 7), d.get("valor"), fm); bk.w(wl, (r, 8), d.get("ult"), fd); bk.w(wl, (r, 9), d.get("prox"), fd)
        bk.w(wl, (r, 10), d.get("fech"), fd); bk.w(wl, (r, 11), d.get("motivo"), fi); bk.w(wl, (r, 12), d.get("obs"), fi)
        bk.fx(wl, (r, 13), f'IF($C{x}="","",IFERROR(INDEX(EtapaProb,MATCH($G{x},Etapas,0)),0))', bk.fmt("calc", nf="pct0", align="center"))
        bk.fx(wl, (r, 14), f'IF($C{x}="","",IF($P{x}="Aberto",N($H{x})*$N{x},0))', cm)
        bk.fx(wl, (r, 15), f'IF($C{x}="","",IF($G{x}="Ganho","Ganho",IF($G{x}="Perdido","Perdido","Aberto")))', cc)
        bk.fx(wl, (r, 16), f'IF(OR($C{x}="",$P{x}<>"Aberto"),"",IF($I{x}="",Hoje-$B{x},Hoje-$I{x}))', cc)
        bk.fx(wl, (r, 17), f'IF(OR($C{x}="",$P{x}<>"Aberto"),"",IF($J{x}="",IF($Q{x}>DiasSC,"ATRASADO","Definir data"),IF($J{x}<Hoje,"ATRASADO",IF($J{x}=Hoje,"HOJE","Em dia"))))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wl, (r, 18), f'IF($R{x}="","",IF(OR($R{x}="ATRASADO",$R{x}="HOJE",$R{x}="Definir data"),COUNTIF($R${R0+1}:$R{x},"ATRASADO")+COUNTIF($R${R0+1}:$R{x},"HOJE")+COUNTIF($R${R0+1}:$R{x},"Definir data"),""))', bk.fmt("calc", font_color="#9CA3AF", align="center"))
        bk.fx(wl, (r, 19), f'IF($C{x}="","",IF(OR($B{x}="",$E{x}="",$F{x}="",$G{x}=""),"Preencher entrada/origem/vendedor/etapa",IF(AND(OR($P{x}="Ganho",$P{x}="Perdido"),$K{x}=""),"Falta data de fechamento",IF(AND($P{x}="Perdido",$L{x}=""),"Informe o motivo da perda","OK"))))', cc)
    bk.dv_date(wl, f"B{R0+1}:B{LAST}"); bk.dv_list(wl, f"E{R0+1}:E{LAST}", "=Origens"); bk.dv_list(wl, f"F{R0+1}:F{LAST}", "=Vendedores")
    bk.dv_list(wl, f"G{R0+1}:G{LAST}", "=Etapas"); bk.dv_num(wl, f"H{R0+1}:H{LAST}", 0); bk.dv_date(wl, f"I{R0+1}:K{LAST}"); bk.dv_list(wl, f"L{R0+1}:L{LAST}", "=Motivos")
    for t, bg, fg in (("ATRASADO", C_RED, "#FFFFFF"), ("HOJE", C_AMBER, "#FFFFFF"), ("Em dia", G_LIGHT, "#15803D"), ("Definir data", C_AMBERL, "#92400E")):
        wl.conditional_format(f"R{R0+1}:R{LAST}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wl.conditional_format(f"P{R0+1}:P{LAST}", {"type": "cell", "criteria": "==", "value": '"Ganho"', "format": wb.add_format({"bg_color": G_NEON, "font_color": "#052e16", "bold": True})})
    wl.conditional_format(f"P{R0+1}:P{LAST}", {"type": "cell", "criteria": "==", "value": '"Perdido"', "format": wb.add_format({"font_color": "#6B7280", "italic": True})})
    wl.conditional_format(f"T{R0+1}:T{LAST}", {"type": "cell", "criteria": "!=", "value": '"OK"', "format": wb.add_format({"font_color": C_RED})})
    wl.freeze_panes(4, 3); wl.autofilter(3, 0, LAST - 1, 19)
    wl.set_column(18, 18, None, None, {"hidden": True})
    LL = lambda c: f"Leads!${c}${R0+1}:${c}${LAST}"

    # ---------------- Agenda
    wa = bk.sheet("Agenda", tab=G_NEON)
    bk.banner(wa, "Agenda de follow-up", "Quem precisa de contato HOJE ou está ATRASADO. Atualize a data na aba Leads depois de falar com o cliente.", 10)
    bk.header(wa, 3, 0, ["#", "Prioridade", "Lead", "Contato", "Etapa", "Vendedor", "Valor potencial", "Último contato", "Próx. follow-up", "Dias sem contato"],
              [5, 14, 32, 17, 16, 14, 14, 12, 12, 10], 32)
    for k in range(100):
        r = R0 + k; x = r + 1
        wa.write(r, 0, k + 1, bk.fmt("plain", align="center"))
        idx = f'MATCH($A{x},{LL("S")},0)'
        for c, src, nf in ((1, "R", None), (2, "C", None), (3, "D", None), (4, "G", None), (5, "F", None), (6, "H", "money"), (7, "I", "date"), (8, "J", "date"), (9, "Q", "int")):
            f = f'IFERROR(INDEX({LL(src)},{idx})&"","")' if nf is None else f'IFERROR(IF(INDEX({LL(src)},{idx})="","",INDEX({LL(src)},{idx})),"")'
            kw = dict(align="center", bold=True) if c == 1 else (dict(align="center") if nf in ("date", "int") else {})
            bk.fx(wa, (r, c), f, bk.fmt("calc", nf=nf, **kw))
    for t, bg, fg in (("ATRASADO", C_RED, "#FFFFFF"), ("HOJE", C_AMBER, "#FFFFFF"), ("Definir data", C_AMBERL, "#92400E")):
        wa.conditional_format(f"B{R0+1}:B{R0+100}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wa.freeze_panes(4, 0)

    # ---------------- Funil
    wf = bk.sheet("Funil", onepage=True)
    bk.banner(wf, "Funil de vendas", "Onde estão os leads, de onde vêm os que fecham e por que perdemos.", 8)
    wf.set_column(0, 0, 3); wf.set_column(1, 1, 24); wf.set_column(2, 7, 15)
    bk.header(wf, 3, 1, ["Etapa", "Leads", "Valor (R$)", "Valor ponderado", "% dos leads"], height=24)
    for i in range(6):
        r = 4 + i; x = r + 1
        bk.fx(wf, (r, 1), f"INDEX(Etapas,{i+1})", bk.fmt("plain", bold=True))
        bk.fx(wf, (r, 2), f'COUNTIF({LL("G")},B{x})', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wf, (r, 3), f'SUMIFS({LL("H")},{LL("G")},B{x})', cm)
        bk.fx(wf, (r, 4), f'SUMIFS({LL("O")},{LL("G")},B{x})', cm)
        bk.fx(wf, (r, 5), f'IFERROR(C{x}/SUM($C$5:$C$10),0)', bk.fmt("calc", nf="pct", align="center"))
    wf.write(10, 1, "Total", bk.fmt("tot")); bk.fx(wf, (10, 2), "SUM(C5:C10)", bk.fmt("tot", nf="int", align="center"))
    bk.fx(wf, (10, 3), "SUM(D5:D10)", bk.fmt("tot", nf="money")); bk.fx(wf, (10, 4), "SUM(E5:E10)", bk.fmt("tot", nf="money")); wf.write(10, 5, "", bk.fmt("tot"))
    wf.merge_range(12, 1, 12, 6, "Conversão por origem (de onde vêm os clientes que fecham)", bk.fmt("sec"))
    bk.header(wf, 13, 1, ["Origem", "Leads", "Ganhos", "Perdidos", "Conversão", "Valor ganho (R$)"], height=24)
    for i in range(10):
        r = 14 + i; x = r + 1
        bk.fx(wf, (r, 1), f'IF(INDEX(Origens,{i+1})="","",INDEX(Origens,{i+1}))', bk.fmt("plain", bold=True))
        bk.fx(wf, (r, 2), f'IF(B{x}="","",COUNTIF({LL("E")},B{x}))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wf, (r, 3), f'IF(B{x}="","",COUNTIFS({LL("E")},B{x},{LL("P")},"Ganho"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wf, (r, 4), f'IF(B{x}="","",COUNTIFS({LL("E")},B{x},{LL("P")},"Perdido"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wf, (r, 5), f'IF(B{x}="","",IFERROR(D{x}/C{x},0))', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wf, (r, 6), f'IF(B{x}="","",SUMIFS({LL("H")},{LL("E")},B{x},{LL("P")},"Ganho"))', cm)
    wf.merge_range(25, 1, 25, 3, "Motivos de perda", bk.fmt("sec"))
    bk.header(wf, 26, 1, ["Motivo", "Leads perdidos", "% das perdas"], height=24)
    for i in range(10):
        r = 27 + i; x = r + 1
        bk.fx(wf, (r, 1), f'IF(INDEX(Motivos,{i+1})="","",INDEX(Motivos,{i+1}))', bk.fmt("plain", bold=True))
        bk.fx(wf, (r, 2), f'IF(B{x}="","",COUNTIFS({LL("L")},B{x},{LL("P")},"Perdido"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wf, (r, 3), f'IF(B{x}="","",IFERROR(C{x}/COUNTIF({LL("P")},"Perdido"),0))', bk.fmt("calc", nf="pct", align="center"))
    ch = wb.add_chart({"type": "bar"})
    ch.add_series({"name": "Leads", "categories": "=Funil!$B$5:$B$9", "values": "=Funil!$C$5:$C$9", "fill": {"color": G_MID}, "data_labels": {"value": True}, "gap": 40})
    ch.set_title({"name": "Funil: leads por etapa", "name_font": {"size": 12}}); ch.set_legend({"none": True}); ch.set_y_axis({"reverse": True}); ch.set_size({"width": 430, "height": 260})
    wf.insert_chart("H4", ch)
    c2 = wb.add_chart({"type": "column"})
    c2.add_series({"name": "Conversão", "categories": "=Funil!$B$15:$B$24", "values": "=Funil!$F$15:$F$24", "fill": {"color": G_DARK}, "data_labels": {"value": True, "num_format": "0%"}})
    c2.set_title({"name": "Conversão por origem", "name_font": {"size": 12}}); c2.set_legend({"none": True}); c2.set_y_axis({"num_format": "0%"}); c2.set_size({"width": 430, "height": 260})
    wf.insert_chart("H19", c2)
    wf.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})

    # ---------------- Vendedores
    wv = bk.sheet("Vendedores", onepage=True)
    bk.banner(wv, "Vendedores: ranking e metas", "Mês de referência = mês da data de hoje (Config).", 11)
    bk.header(wv, 3, 0, ["Vendedor", "Leads", "Em aberto", "Ganhos", "Perdidos", "Conversão", "Vendido no mês (R$)", "Meta do mês (R$)", "% da meta", "Previsão ponderada (R$)", "Follow-ups atrasados", "Ranking"],
              [20, 8, 10, 8, 9, 11, 16, 16, 10, 16, 12, 9], 44)
    mi = 'DATE(YEAR(Hoje),MONTH(Hoje),1)'; mf = 'DATE(YEAR(Hoje),MONTH(Hoje)+1,0)'
    for i in range(10):
        r = 4 + i; x = r + 1
        bk.fx(wv, (r, 0), f'IF(INDEX(Vendedores,{i+1})="","",INDEX(Vendedores,{i+1}))', bk.fmt("plain", bold=True))
        bk.fx(wv, (r, 1), f'IF($A{x}="","",COUNTIF({LL("F")},$A{x}))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wv, (r, 2), f'IF($A{x}="","",COUNTIFS({LL("F")},$A{x},{LL("P")},"Aberto"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wv, (r, 3), f'IF($A{x}="","",COUNTIFS({LL("F")},$A{x},{LL("P")},"Ganho"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wv, (r, 4), f'IF($A{x}="","",COUNTIFS({LL("F")},$A{x},{LL("P")},"Perdido"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wv, (r, 5), f'IF($A{x}="","",IFERROR(D{x}/(D{x}+E{x}),0))', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wv, (r, 6), f'IF($A{x}="","",SUMIFS({LL("H")},{LL("F")},$A{x},{LL("P")},"Ganho",{LL("K")},">="&{mi},{LL("K")},"<="&{mf}))', cm)
        bk.fx(wv, (r, 7), f'IF($A{x}="","",N(INDEX(Config!$H$5:$H$14,{i+1})))', cm)
        bk.fx(wv, (r, 8), f'IF($A{x}="","",IF(H{x}>0,G{x}/H{x},0))', bk.fmt("calc", nf="pct0", align="center", bold=True))
        bk.fx(wv, (r, 9), f'IF($A{x}="","",SUMIFS({LL("O")},{LL("F")},$A{x}))', cm)
        bk.fx(wv, (r, 10), f'IF($A{x}="","",COUNTIFS({LL("F")},$A{x},{LL("R")},"ATRASADO"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wv, (r, 11), f'IF($A{x}="","",RANK(G{x},$G$5:$G$14))', bk.fmt("calc", align="center", bold=True))
    wv.write(14, 0, "Total", bk.fmt("tot"))
    for c in (1, 2, 3, 4, 10):
        bk.fx(wv, (14, c), f"SUM({col(c)}5:{col(c)}14)", bk.fmt("tot", nf="int", align="center"))
    for c in (6, 7, 9):
        bk.fx(wv, (14, c), f"SUM({col(c)}5:{col(c)}14)", bk.fmt("tot", nf="money"))
    bk.fx(wv, (14, 5), 'IFERROR(D15/(D15+E15),0)', bk.fmt("tot", nf="pct", align="center")); bk.fx(wv, (14, 8), 'IF(H15>0,G15/H15,0)', bk.fmt("tot", nf="pct0", align="center")); wv.write(14, 11, "", bk.fmt("tot"))
    wv.conditional_format("I5:I14", {"type": "data_bar", "bar_color": G_NEON, "bar_solid": True, "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1.2})
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Vendido no mês", "categories": "=Vendedores!$A$5:$A$14", "values": "=Vendedores!$G$5:$G$14", "fill": {"color": G_MID}})
    ch.add_series({"name": "Meta", "categories": "=Vendedores!$A$5:$A$14", "values": "=Vendedores!$H$5:$H$14", "fill": {"color": "#D1D5DB"}})
    ch.set_title({"name": "Vendido x meta do mês", "name_font": {"size": 12}}); ch.set_legend({"position": "bottom"}); ch.set_size({"width": 760, "height": 300})
    wv.insert_chart("A18", ch)
    wv.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})

    # ---------------- Dashboard
    wd = bk.sheet("Dashboard", tab=G_NEON, onepage=True)
    bk.banner(wd, "Dashboard comercial", "Resumo do funil e das metas do mês.", 10)
    for c in range(10):
        wd.set_column(c, c, 13)
    bk.kpi(wd, 3, 0, "LEADS EM ABERTO", f'COUNTIF({LL("P")},"Aberto")', "int", 2)
    bk.kpi(wd, 3, 2, "VALOR EM ABERTO", f'SUMIFS({LL("H")},{LL("P")},"Aberto")', "money", 2)
    bk.kpi(wd, 3, 4, "PREVISÃO PONDERADA", f'SUM({LL("O")})', "money", 2)
    bk.kpi(wd, 3, 6, "VENDIDO NO MÊS", "Vendedores!G15", "money", 2)
    bk.kpi(wd, 3, 8, "META DO MÊS", "Vendedores!H15", "money", 2)
    bk.kpi(wd, 6, 0, "% DA META", "Vendedores!I15", "pct0", 2)
    bk.kpi(wd, 6, 2, "CONVERSÃO (ganhos / fechados)", "Vendedores!F15", "pct", 2)
    bk.kpi(wd, 6, 4, "TICKET MÉDIO", f'IFERROR(AVERAGEIFS({LL("H")},{LL("P")},"Ganho"),0)', "money", 2)
    bk.kpi(wd, 6, 6, "CICLO MÉDIO DE VENDA (dias)", f'IFERROR(SUMPRODUCT(({LL("P")}="Ganho")*({LL("K")}>0)*({LL("K")}-{LL("B")}))/SUMPRODUCT(({LL("P")}="Ganho")*({LL("K")}>0)),0)', "0", 2)
    bk.kpi(wd, 6, 8, "FOLLOW-UPS ATRASADOS", f'COUNTIF({LL("R")},"ATRASADO")', "int", 2, color=C_RED)
    wd.merge_range(9, 0, 9, 4, "Vendas ganhas por mês (ano da data de hoje)", bk.fmt("sec"))
    bk.header(wd, 10, 0, ["Mês", "Vendido (R$)", "Meta (R$)"], height=22)
    for m in range(12):
        r = 11 + m; x = r + 1
        bk.fx(wd, (r, 0), f"DATE(YEAR(Hoje),{m+1},1)", bk.fmt("calc", nf="mon", align="center", bold=True))
        bk.fx(wd, (r, 1), f'SUMIFS({LL("H")},{LL("P")},"Ganho",{LL("K")},">="&A{x},{LL("K")},"<="&DATE(YEAR(A{x}),MONTH(A{x})+1,0))', cm)
        bk.fx(wd, (r, 2), "SUM(Config!$H$5:$H$14)", cm)
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Vendido", "categories": "=Dashboard!$A$12:$A$23", "values": "=Dashboard!$B$12:$B$23", "fill": {"color": G_MID}, "gap": 60})
    ln = wb.add_chart({"type": "line"})
    ln.add_series({"name": "Meta", "categories": "=Dashboard!$A$12:$A$23", "values": "=Dashboard!$C$12:$C$23", "line": {"color": "#EF4444", "dash_type": "dash", "width": 2}})
    ch.combine(ln); ch.set_title({"name": "Vendido x meta", "name_font": {"size": 12}}); ch.set_legend({"position": "bottom"}); ch.set_x_axis({"num_format": "mmm"}); ch.set_size({"width": 560, "height": 300})
    wd.insert_chart("E10", ch)
    wd.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
    bk.finish()

    exp = {}
    if bk.sample:
        a = analyze(leads)
        exp[("Dashboard", "A5")] = a["abertos"]
        exp[("Dashboard", "C5")] = round(a["valor_aberto"], 2)
        exp[("Dashboard", "E5")] = round(a["pond"], 2)
        exp[("Dashboard", "G5")] = round(a["ganho_mes"], 2)
        exp[("Dashboard", "I5")] = round(sum(m for _, m in VENDS), 2)
        exp[("Dashboard", "C8")] = round(a["ganhos"] / (a["ganhos"] + a["perdidos"]), 4)
        exp[("Dashboard", "E8")] = round(a["ticket"], 2)
        exp[("Dashboard", "G8")] = round(sum(a["ciclo"]) / len(a["ciclo"]), 4) if a["ciclo"] else 0
        exp[("Dashboard", "I8")] = a["atras"]
        for v, dd in a["by_vend"].items():
            i = [n for n, _ in VENDS].index(v)
            exp[("Vendedores", f"G{5+i}")] = round(dd["mes"], 2)
            exp[("Vendedores", f"D{5+i}")] = dd["g"]
        for o_, (n, g) in a["by_orig"].items():
            i = ORIGENS.index(o_)
            exp[("Funil", f"C{15+i}")] = n
            exp[("Funil", f"D{15+i}")] = g
    return exp
