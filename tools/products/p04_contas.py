# -*- coding: utf-8 -*-
import datetime as dt
import random
from lib import *

SLUG = "contas-pagar-receber"
PASTA = "financeiro/contas-pagar-receber"
NOME = "Contas a Pagar e Receber com Inadimplência"
N = 1000
R0 = 4
LAST = R0 + N
MULTA, JUROS, DIAS_ALERTA = 0.02, 0.01, 7

FAIXAS = ["A vencer", "1-15 dias", "16-30 dias", "31-60 dias", "Mais de 60 dias"]
FORMAS = ["Pix", "Boleto", "Cartão de crédito", "Cartão de débito", "Transferência", "Dinheiro"]
CATD = ["Fornecedores", "Aluguel", "Folha / pró-labore", "Impostos", "Energia e água", "Internet e telefone", "Marketing", "Sistemas e contador", "Manutenção", "Outras despesas"]


def faixa(dias, saldo):
    if saldo <= 0.005:
        return "Pago"
    if dias <= 0:
        return "A vencer"
    return "1-15 dias" if dias <= 15 else "16-30 dias" if dias <= 30 else "31-60 dias" if dias <= 60 else "Mais de 60 dias"


def sample_data():
    rnd = random.Random(404)
    clientes = [(f"Cliente {i+1:02d} ({seg})", f"(00) 90000-{i+1:04d}") for i, seg in enumerate(
        ["Padaria", "Escola", "Clínica", "Mercado", "Academia", "Oficina", "Restaurante", "Escritório", "Loja de roupas", "Farmácia",
         "Hotel", "Papelaria", "Consultório", "Salão", "Construtora", "Distribuidora", "Pet shop", "Floricultura", "Autoescola", "Gráfica"])]
    forn = ["Fornecedor A (matéria-prima)", "Fornecedor B (embalagens)", "Imobiliária Exemplo (aluguel)", "Contabilidade Exemplo", "Energia Exemplo",
            "Internet Exemplo", "Agência de Marketing Exemplo", "Transportadora Exemplo"]
    rec, pag = [], []
    ref = REF_DATE
    for ci, (nome, tel) in enumerate(clientes):
        for m in range(6, 13):
            if rnd.random() < 0.55 or m in (9, 10):
                venc = dt.date(2026, m, rnd.choice([5, 10, 15, 20, 25]))
                val = round(rnd.choice([450, 780, 1200, 1850, 2400, 3100, 650]) * rnd.uniform(0.9, 1.15), 2)
                desc = f"Contrato mensal {m:02d}/2026"
                emissao = venc - dt.timedelta(days=15)
                fp = vp = fr = None
                if venc < ref:
                    r = rnd.random()
                    bad = ci in (2, 5, 9, 14)       # clientes "ruins pagadores"
                    if (r < 0.12) or (bad and r < 0.5):
                        pass                         # vencido em aberto
                    elif r < 0.2:
                        fp = min(ref, venc + dt.timedelta(days=rnd.randint(3, 12)))
                        vp = round(val * 0.5, 2); fr = "Pix"
                    else:
                        fp = min(ref, venc + dt.timedelta(days=rnd.randint(-2, 6)))
                        vp = val; fr = rnd.choice(FORMAS[:3])
                rec.append((nome, desc, emissao, venc, val, fp, vp, fr))
    for m in range(6, 13):
        for k, (f, cat, base) in enumerate([(forn[0], "Fornecedores", 7200), (forn[1], "Fornecedores", 1900), (forn[2], "Aluguel", 4200), (forn[3], "Sistemas e contador", 1350),
                                            (forn[4], "Energia e água", 980), (forn[5], "Internet e telefone", 340), (forn[6], "Marketing", 1800), (forn[7], "Fornecedores", 760)]):
            venc = dt.date(2026, m, [10, 20, 5, 15, 12, 8, 25, 18][k])
            val = round(base * rnd.uniform(0.92, 1.1), 2)
            fp = vp = fr = None
            if venc < ref:
                if not (m == 9 and k == 7):         # uma conta vencida esquecida
                    fp = venc - dt.timedelta(days=rnd.randint(0, 2)); vp = val; fr = rnd.choice(["Pix", "Boleto"])
            pag.append((f, f"{cat} {m:02d}/2026", cat, venc, val, fp, vp, fr))
    rec.sort(key=lambda r: r[3]); pag.sort(key=lambda r: r[3])
    return clientes, forn, rec, pag


def analyze(rec, pag):
    ref = REF_DATE
    out = dict(rec_open=0, rec_over=0, aging={f: [0, 0.0] for f in FAIXAS}, by_client={}, pag_open=0, pag_over=0, pag_7=0, recebido_mes=0, pago_mes=0,
               weeks_r=[0.0] * 9, weeks_p=[0.0] * 9)
    for (cli, desc, em, venc, val, fp, vp, fr) in rec:
        saldo = max(0, val - (vp or 0))
        if saldo > 0.005:
            out["rec_open"] += saldo
            dias = (ref - venc).days if venc < ref else 0
            f = faixa(dias, saldo)
            out["aging"][f][0] += 1; out["aging"][f][1] += saldo
            if dias > 0:
                out["rec_over"] += saldo
                out["by_client"][cli] = out["by_client"].get(cli, 0) + saldo
            # semanas
            if venc < ref:
                out["weeks_r"][0] += saldo
            else:
                w = (venc - ref).days // 7
                if w < 8:
                    out["weeks_r"][1 + w] += saldo
        if fp and fp.year == ref.year and fp.month == ref.month:
            out["recebido_mes"] += vp or 0
    for (f, desc, cat, venc, val, fp, vp, fr) in pag:
        saldo = max(0, val - (vp or 0))
        if saldo > 0.005:
            out["pag_open"] += saldo
            if venc < ref:
                out["pag_over"] += saldo
                out["weeks_p"][0] += saldo
            else:
                if (venc - ref).days <= DIAS_ALERTA:
                    out["pag_7"] += saldo
                w = (venc - ref).days // 7
                if w < 8:
                    out["weeks_p"][1 + w] += saldo
        if fp and fp.year == ref.year and fp.month == ref.month:
            out["pago_mes"] += vp or 0
    return out


def build(bk: Book):
    wb = bk.wb
    bk.inicio(
        "Contas a Pagar e Receber", "Carvex XLS · Controle de vencimentos, cobrança e inadimplência",
        "Registre o que você tem a receber e a pagar. A planilha mostra o status de cada conta, calcula multa e juros dos atrasados, "
        "monta a mensagem de cobrança pronta, ranqueia os clientes que mais devem e prevê o saldo das próximas 8 semanas.",
        [("Config", "Informe multa, juros, quantos dias antes quer ser avisado e cadastre clientes (com telefone), fornecedores, categorias e formas de pagamento."),
         ("Lance as contas a receber", "Na aba Receber: cliente, descrição, vencimento e valor. Quando o cliente pagar, preencha a data e o valor pago."),
         ("Lance as contas a pagar", "Na aba Pagar: fornecedor, categoria, vencimento e valor. Ao pagar, preencha data e valor pago."),
         ("Cobre quem está atrasado", "Na aba Receber, a coluna Mensagem de cobrança já traz o texto pronto para copiar e enviar por WhatsApp."),
         ("Acompanhe o Painel", "Veja inadimplência, aging por faixa de atraso, maiores devedores e o saldo previsto semana a semana.")],
        [("Config", "Parâmetros e cadastros."), ("Receber", "Contas a receber (até 1.000 linhas)."), ("Pagar", "Contas a pagar (até 1.000 linhas)."),
         ("Painel", "Indicadores, aging, ranking de devedores e previsão de 8 semanas.")],
        avisos=["Para pagamento parcial, preencha o valor pago menor que o valor da conta: o saldo continua em aberto.",
                "Multa e juros são estimativas pela taxa informada na Config (juros pro rata por dia). Confira o que foi combinado em contrato.",
                "O Painel usa a data de hoje da Config. No arquivo de exemplo a data é fixa (08/10/2026)."])

    ws = bk.sheet("Config")
    bk.banner(ws, "Configurações e cadastros", "Preencha as células amarelas.", 13)
    ws.set_column(0, 0, 3); ws.set_column(1, 1, 36); ws.set_column(2, 2, 14); ws.set_column(3, 3, 3)
    ws.set_column(4, 4, 28); ws.set_column(5, 5, 16); ws.set_column(6, 6, 3); ws.set_column(7, 7, 30); ws.set_column(8, 8, 3)
    ws.set_column(9, 9, 24); ws.set_column(10, 10, 3); ws.set_column(11, 11, 20)
    lf = bk.fmt("lbl")
    ws.write(3, 1, "Empresa", lf); bk.w(ws, (3, 2), "Serviços Exemplo" if bk.sample else None, bk.fmt("in"))
    ws.write(4, 1, "Data de hoje (referência)", lf)
    if bk.sample:
        bk.w(ws, "C5", REF_DATE, bk.fmt("in", nf="date", align="center"))
    else:
        bk.fx(ws, "C5", "TODAY()", bk.fmt("calc", nf="date", align="center"))
    ws.write(5, 1, "Multa por atraso (%)", lf); bk.w(ws, "C6", MULTA, bk.fmt("in", nf="pct", align="center"))
    ws.write(6, 1, "Juros de mora ao mês (%)", lf); bk.w(ws, "C7", JUROS, bk.fmt("in", nf="pct", align="center"))
    ws.write(7, 1, "Avisar contas a pagar com até (dias)", lf); bk.w(ws, "C8", DIAS_ALERTA, bk.fmt("in", nf="0", align="center"))
    bk.dv_num(ws, "C6:C7", 0, 0.5); bk.dv_num(ws, "C8", 1, 60, integer=True)
    for n, a in (("Hoje", "C5"), ("Multa", "C6"), ("Juros", "C7"), ("DiasAlerta", "C8")):
        bk.define(n, f"=Config!${a[0]}${a[1:]}")
    clientes, forn, rec, pag = sample_data() if bk.sample else ([], [], [], [])
    ws.write(3, 4, "Clientes", bk.fmt("h")); ws.write(3, 5, "Telefone", bk.fmt("h"))
    for i in range(100):
        c = clientes[i] if i < len(clientes) else (None, None)
        bk.w(ws, (4 + i, 4), c[0], bk.fmt("in")); bk.w(ws, (4 + i, 5), c[1], bk.fmt("in"))
    ws.write(3, 7, "Fornecedores", bk.fmt("h"))
    for i in range(60):
        bk.w(ws, (4 + i, 7), forn[i] if i < len(forn) else None, bk.fmt("in"))
    ws.write(3, 9, "Categorias de despesa", bk.fmt("h"))
    for i in range(30):
        bk.w(ws, (4 + i, 9), CATD[i] if i < len(CATD) else None, bk.fmt("in"))
    ws.write(3, 11, "Formas de pagamento", bk.fmt("h"))
    for i in range(12):
        bk.w(ws, (4 + i, 11), FORMAS[i] if i < len(FORMAS) else None, bk.fmt("in"))
    bk.define("ClienteNome", "=Config!$E$5:$E$104"); bk.define("ClienteTel", "=Config!$F$5:$F$104")
    bk.define("FornNome", "=Config!$H$5:$H$64"); bk.define("CatDesp", "=Config!$J$5:$J$34"); bk.define("Formas", "=Config!$L$5:$L$16")

    # ---------------- Receber
    wr = bk.sheet("Receber")
    bk.banner(wr, "Contas a Receber", "Preencha cliente, vencimento e valor. Ao receber, preencha data e valor pago.", 15)
    bk.header(wr, 3, 0, ["Cliente", "Descrição", "Emissão", "Vencimento", "Valor (R$)", "Data do pagamento", "Valor pago (R$)", "Forma", "STATUS",
                         "Dias de atraso", "Faixa", "Saldo em aberto", "Multa + juros", "Total a cobrar hoje", "Mensagem de cobrança (copie e envie)"],
              [30, 28, 11, 11, 13, 12, 13, 15, 16, 8, 15, 14, 12, 14, 70], 44)
    fd = bk.fmt("in", nf="date", align="center"); fi = bk.fmt("in"); fm = bk.fmt("in", nf="money")
    cc = bk.fmt("calc"); cm = bk.fmt("calc", nf="money"); cac = bk.fmt("calc", align="center")
    for i in range(N):
        r = R0 + i; x = r + 1
        d = rec[i] if i < len(rec) else (None,) * 8
        bk.w(wr, (r, 0), d[0], fi); bk.w(wr, (r, 1), d[1], fi); bk.w(wr, (r, 2), d[2], fd); bk.w(wr, (r, 3), d[3], fd)
        bk.w(wr, (r, 4), d[4], fm); bk.w(wr, (r, 5), d[5], fd); bk.w(wr, (r, 6), d[6], fm); bk.w(wr, (r, 7), d[7], fi)
        bk.fx(wr, (r, 8), f'IF($E{x}="","",IF($L{x}<=0.005,"Pago",IF($D{x}="","Sem vencimento",IF($D{x}<Hoje,IF(N($G{x})>0,"Vencido (parcial)","Vencido"),IF($D{x}=Hoje,"Vence hoje","A vencer")))))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wr, (r, 9), f'IF(OR($E{x}="",$D{x}=""),"",IF(AND($L{x}>0.005,$D{x}<Hoje),Hoje-$D{x},0))', cac)
        bk.fx(wr, (r, 10), f'IF($J{x}="","",IF($L{x}<=0.005,"Pago",IF($J{x}<=0,"A vencer",IF($J{x}<=15,"1-15 dias",IF($J{x}<=30,"16-30 dias",IF($J{x}<=60,"31-60 dias","Mais de 60 dias"))))))', cac)
        bk.fx(wr, (r, 11), f'IF($E{x}="","",MAX(0,$E{x}-N($G{x})))', cm)
        bk.fx(wr, (r, 12), f'IF(OR($L{x}="",$J{x}=""),"",IF($J{x}>0,ROUND($L{x}*Multa+$L{x}*Juros/30*$J{x},2),0))', cm)
        bk.fx(wr, (r, 13), f'IF($L{x}="","",IF($L{x}<=0.005,0,$L{x}+N($M{x})))', bk.fmt("calc", nf="money", bold=True))
        bk.fx(wr, (r, 14), f'IF(OR($I{x}="Vencido",$I{x}="Vencido (parcial)"),"Olá, "&$A{x}&"! Consta em aberto \'"&$B{x}&"\' com vencimento em "&DAY($D{x})&"/"&MONTH($D{x})&"/"&YEAR($D{x})&", no valor de R$ "&FIXED($N{x},2)&" (com multa e juros). Podemos ajudar a regularizar hoje? Obrigado!",'
                            f'IF($I{x}="Vence hoje","Olá, "&$A{x}&"! Lembrete: \'"&$B{x}&"\' vence hoje, no valor de R$ "&FIXED($L{x},2)&". Obrigado!",""))', bk.fmt("calc", font_color="#374151"))
    bk.dv_list(wr, f"A{R0+1}:A{LAST}", "=ClienteNome"); bk.dv_date(wr, f"C{R0+1}:D{LAST}"); bk.dv_date(wr, f"F{R0+1}:F{LAST}")
    bk.dv_num(wr, f"E{R0+1}:E{LAST}", 0); bk.dv_num(wr, f"G{R0+1}:G{LAST}", 0); bk.dv_list(wr, f"H{R0+1}:H{LAST}", "=Formas")
    for t, bg, fg in (("Pago", G_LIGHT, "#15803D"), ("Vencido", C_RED, "#FFFFFF"), ("Vencido (parcial)", "#F87171", "#FFFFFF"), ("Vence hoje", C_AMBER, "#FFFFFF"), ("A vencer", "#DBEAFE", "#1E40AF")):
        wr.conditional_format(f"I{R0+1}:I{LAST}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wr.freeze_panes(4, 1); wr.autofilter(3, 0, LAST - 1, 14)
    RR = lambda c: f"Receber!${c}${R0+1}:${c}${LAST}"

    # ---------------- Pagar
    wp = bk.sheet("Pagar")
    bk.banner(wp, "Contas a Pagar", "Preencha fornecedor, categoria, vencimento e valor. Ao pagar, preencha data e valor pago.", 12)
    bk.header(wp, 3, 0, ["Fornecedor", "Descrição", "Categoria", "Vencimento", "Valor (R$)", "Data do pagamento", "Valor pago (R$)", "Forma", "STATUS",
                         "Dias p/ vencer (negativo = atrasada)", "Saldo a pagar", "Ação"], [30, 28, 20, 11, 13, 12, 13, 15, 17, 14, 14, 24], 56)
    for i in range(N):
        r = R0 + i; x = r + 1
        d = pag[i] if i < len(pag) else (None,) * 8
        bk.w(wp, (r, 0), d[0], fi); bk.w(wp, (r, 1), d[1], fi); bk.w(wp, (r, 2), d[2], fi); bk.w(wp, (r, 3), d[3], fd)
        bk.w(wp, (r, 4), d[4], fm); bk.w(wp, (r, 5), d[5], fd); bk.w(wp, (r, 6), d[6], fm); bk.w(wp, (r, 7), d[7], fi)
        bk.fx(wp, (r, 8), f'IF($E{x}="","",IF($K{x}<=0.005,"Pago",IF($D{x}="","Sem vencimento",IF($D{x}<Hoje,"Vencida",IF($D{x}=Hoje,"Vence hoje",IF($D{x}-Hoje<=DiasAlerta,"Vence em breve","A vencer"))))))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wp, (r, 9), f'IF(OR($E{x}="",$D{x}=""),"",IF($K{x}<=0.005,"",$D{x}-Hoje))', cac)
        bk.fx(wp, (r, 10), f'IF($E{x}="","",MAX(0,$E{x}-N($G{x})))', cm)
        bk.fx(wp, (r, 11), f'IF($I{x}="Vencida","PAGAR JÁ (multa e juros)",IF($I{x}="Vence hoje","Pagar hoje",IF($I{x}="Vence em breve","Programar pagamento","")))', cac)
    bk.dv_list(wp, f"A{R0+1}:A{LAST}", "=FornNome"); bk.dv_list(wp, f"C{R0+1}:C{LAST}", "=CatDesp"); bk.dv_date(wp, f"D{R0+1}:D{LAST}"); bk.dv_date(wp, f"F{R0+1}:F{LAST}")
    bk.dv_num(wp, f"E{R0+1}:E{LAST}", 0); bk.dv_num(wp, f"G{R0+1}:G{LAST}", 0); bk.dv_list(wp, f"H{R0+1}:H{LAST}", "=Formas")
    for t, bg, fg in (("Pago", G_LIGHT, "#15803D"), ("Vencida", C_RED, "#FFFFFF"), ("Vence hoje", C_AMBER, "#FFFFFF"), ("Vence em breve", C_AMBERL, "#92400E"), ("A vencer", "#DBEAFE", "#1E40AF")):
        wp.conditional_format(f"I{R0+1}:I{LAST}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wp.freeze_panes(4, 1); wp.autofilter(3, 0, LAST - 1, 11)
    PP = lambda c: f"Pagar!${c}${R0+1}:${c}${LAST}"

    # ---------------- Calc (oculta)
    wk = bk.sheet("Calc", tab="#999999")
    wk.write_row(0, 0, ["Cliente", "Em atraso (R$)", "Chave", "Telefone"])
    for i in range(100):
        r = 1 + i; x = r + 1
        bk.fx(wk, (r, 0), f'IF(Config!E{5+i}="","",Config!E{5+i})')
        bk.fx(wk, (r, 1), f'IF(A{x}="",0,SUMIFS({RR("L")},{RR("A")},A{x},{RR("J")},">0"))')
        bk.fx(wk, (r, 2), f'IF(B{x}>0,B{x}+ROW()/1000000000,"")')
        bk.fx(wk, (r, 3), f'IF(A{x}="","",Config!F{5+i}&"")')
    wk.hide()

    # ---------------- Painel
    wd = bk.sheet("Painel", tab=G_NEON, onepage=True)
    bk.banner(wd, "Painel de contas", "Inadimplência, vencimentos e previsão. Atualiza sozinho.", 12)
    for c in range(12):
        wd.set_column(c, c, 13)
    bk.kpi(wd, 3, 0, "A RECEBER EM ABERTO", f'SUM({RR("L")})', "money", 3)
    bk.kpi(wd, 3, 3, "VENCIDO A RECEBER", f'SUMIFS({RR("L")},{RR("J")},">0")', "money", 3, color=C_RED)
    bk.kpi(wd, 3, 6, "INADIMPLÊNCIA (% do aberto)", 'IFERROR(D5/A5,0)', "pct", 3, color=C_RED)
    bk.kpi(wd, 3, 9, "RECEBIDO NO MÊS", f'SUMIFS({RR("G")},{RR("F")},">="&DATE(YEAR(Hoje),MONTH(Hoje),1),{RR("F")},"<="&DATE(YEAR(Hoje),MONTH(Hoje)+1,0))', "money", 3)
    bk.kpi(wd, 6, 0, "A PAGAR EM ABERTO", f'SUM({PP("K")})', "money", 3)
    bk.kpi(wd, 6, 3, "VENCIDO A PAGAR", f'SUMIFS({PP("K")},{PP("I")},"Vencida")', "money", 3, color=C_RED)
    bk.kpi(wd, 6, 6, "A PAGAR NOS PRÓXIMOS DIAS (alerta)", f'SUMIFS({PP("K")},{PP("D")},">="&Hoje,{PP("D")},"<="&(Hoje+DiasAlerta))', "money", 3, color="#B45309")
    bk.kpi(wd, 6, 9, "PAGO NO MÊS", f'SUMIFS({PP("G")},{PP("F")},">="&DATE(YEAR(Hoje),MONTH(Hoje),1),{PP("F")},"<="&DATE(YEAR(Hoje),MONTH(Hoje)+1,0))', "money", 3)
    wd.merge_range(9, 0, 9, 3, "Aging: quanto está atrasado e há quanto tempo", bk.fmt("sec"))
    bk.header(wd, 10, 0, ["Faixa", "Títulos", "Valor em aberto", "% do total"], height=22)
    for i, f in enumerate(FAIXAS):
        r = 11 + i; x = r + 1
        wd.write(r, 0, f, bk.fmt("plain", align="center", bold=True))
        bk.fx(wd, (r, 1), f'COUNTIFS({RR("K")},A{x},{RR("L")},">0.005")', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wd, (r, 2), f'SUMIFS({RR("L")},{RR("K")},A{x})', bk.fmt("calc", nf="money"))
        bk.fx(wd, (r, 3), f'IFERROR(C{x}/SUM($C$12:$C$16),0)', bk.fmt("calc", nf="pct", align="center"))
    wd.merge_range(9, 5, 9, 11, "Maiores devedores (em atraso)", bk.fmt("sec"))
    wd.write(10, 5, "#", bk.fmt("h")); wd.merge_range(10, 6, 10, 8, "Cliente", bk.fmt("h")); wd.merge_range(10, 9, 10, 10, "Em atraso (R$)", bk.fmt("h")); wd.write(10, 11, "Telefone", bk.fmt("h"))
    for k in range(1, 6):
        r = 10 + k; x = r + 1
        wd.write(r, 5, k, bk.fmt("plain", align="center"))
        bk.fx(wd, (r, 12), f'IFERROR(LARGE(Calc!$C$2:$C$101,{k}),"")', bk.fmt("calc", font_color="#FFFFFF"))
        wd.merge_range(r, 6, r, 8, "", cc); bk.fx(wd, (r, 6), f'IF(M{x}="","",INDEX(Calc!$A$2:$A$101,MATCH(M{x},Calc!$C$2:$C$101,0)))', cc)
        wd.merge_range(r, 9, r, 10, "", cm); bk.fx(wd, (r, 9), f'IF(M{x}="","",ROUND(M{x},2))', cm)
        bk.fx(wd, (r, 11), f'IF(M{x}="","",INDEX(Calc!$D$2:$D$101,MATCH(M{x},Calc!$C$2:$C$101,0)))', cac)
    wd.set_column(12, 12, None, None, {"hidden": True})
    wd.merge_range(18, 0, 18, 6, "Previsão das próximas 8 semanas (somente contas em aberto)", bk.fmt("sec"))
    bk.header(wd, 19, 0, ["Semana", "Início", "Fim", "A receber", "A pagar", "Saldo da semana", "Saldo acumulado"], height=24)
    wd.write(20, 0, "Em atraso", bk.fmt("plain", align="center", bold=True)); wd.write(20, 1, "-", cac); wd.write(20, 2, "-", cac)
    bk.fx(wd, (20, 3), f'SUMIFS({RR("L")},{RR("D")},"<"&Hoje)', cm); bk.fx(wd, (20, 4), f'SUMIFS({PP("K")},{PP("D")},"<"&Hoje)', cm)
    bk.fx(wd, (20, 5), "D21-E21", cm); bk.fx(wd, (20, 6), "F21", cm)
    for i in range(8):
        r = 21 + i; x = r + 1
        wd.write(r, 0, f"Semana {i+1}", bk.fmt("plain", align="center", bold=True))
        bk.fx(wd, (r, 1), f"Hoje+{7*i}", bk.fmt("calc", nf="date", align="center")); bk.fx(wd, (r, 2), f"B{x}+6", bk.fmt("calc", nf="date", align="center"))
        bk.fx(wd, (r, 3), f'SUMIFS({RR("L")},{RR("D")},">="&B{x},{RR("D")},"<="&C{x})', cm)
        bk.fx(wd, (r, 4), f'SUMIFS({PP("K")},{PP("D")},">="&B{x},{PP("D")},"<="&C{x})', cm)
        bk.fx(wd, (r, 5), f"D{x}-E{x}", cm); bk.fx(wd, (r, 6), f"G{x-1}+F{x}", bk.fmt("calc", nf="money", bold=True))
    wd.conditional_format("F21:G29", {"type": "cell", "criteria": "<", "value": 0, "format": wb.add_format({"font_color": C_RED, "bold": True})})
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Valor em aberto", "categories": "=Painel!$A$12:$A$16", "values": "=Painel!$C$12:$C$16",
                   "points": [{"fill": {"color": "#93C5FD"}}, {"fill": {"color": "#FCD34D"}}, {"fill": {"color": "#FB923C"}}, {"fill": {"color": "#EF4444"}}, {"fill": {"color": "#991B1B"}}],
                   "data_labels": {"value": True, "num_format": "#,##0"}})
    ch.set_title({"name": "Aging da carteira a receber", "name_font": {"size": 12}}); ch.set_legend({"none": True}); ch.set_size({"width": 520, "height": 290})
    wd.insert_chart("A32", ch)
    c2 = wb.add_chart({"type": "column"})
    c2.add_series({"name": "A receber", "categories": "=Painel!$A$21:$A$29", "values": "=Painel!$D$21:$D$29", "fill": {"color": G_MID}})
    c2.add_series({"name": "A pagar", "categories": "=Painel!$A$21:$A$29", "values": "=Painel!$E$21:$E$29", "fill": {"color": "#F87171"}})
    l2 = wb.add_chart({"type": "line"})
    l2.add_series({"name": "Saldo acumulado", "categories": "=Painel!$A$21:$A$29", "values": "=Painel!$G$21:$G$29", "line": {"color": G_DARK, "width": 2.5}, "marker": {"type": "circle"}})
    c2.combine(l2); c2.set_title({"name": "Previsão: receber x pagar", "name_font": {"size": 12}}); c2.set_legend({"position": "bottom"}); c2.set_size({"width": 520, "height": 290})
    wd.insert_chart("G32", c2)
    wd.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
    bk.finish()

    exp = {}
    if bk.sample:
        a = analyze(rec, pag)
        exp[("Painel", "A5")] = round(a["rec_open"], 2)
        exp[("Painel", "D5")] = round(a["rec_over"], 2)
        exp[("Painel", "G5")] = round(a["rec_over"] / a["rec_open"], 4)
        exp[("Painel", "J5")] = round(a["recebido_mes"], 2)
        exp[("Painel", "A8")] = round(a["pag_open"], 2)
        exp[("Painel", "D8")] = round(a["pag_over"], 2)
        exp[("Painel", "G8")] = round(a["pag_7"], 2)
        exp[("Painel", "J8")] = round(a["pago_mes"], 2)
        for i, f in enumerate(FAIXAS):
            exp[("Painel", f"C{12+i}")] = round(a["aging"][f][1], 2)
            exp[("Painel", f"B{12+i}")] = a["aging"][f][0]
        top = sorted(a["by_client"].items(), key=lambda kv: -kv[1])[0]
        exp[("Painel", "G12")] = top[0]
        exp[("Painel", "J12")] = round(top[1], 2)
        exp[("Painel", "D21")] = round(a["weeks_r"][0], 2); exp[("Painel", "E21")] = round(a["weeks_p"][0], 2)
        exp[("Painel", "D22")] = round(a["weeks_r"][1], 2); exp[("Painel", "E22")] = round(a["weeks_p"][1], 2)
        exp[("Painel", "D25")] = round(a["weeks_r"][4], 2)
    return exp
