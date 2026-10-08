# -*- coding: utf-8 -*-
import math
import random
from lib import *

SLUG = "precificador"
PASTA = "precificacao/precificador"
NOME = "Precificador de Produtos e Serviços"
NP = 300   # produtos
NS = 100   # serviços
P0 = 4     # primeira linha de dados (0-index)

# parâmetros do exemplo
PAR = dict(imp=0.06, com=0.03, tax=0.035, lucro=0.20, fixos=14000.0, fat=60000.0, prolabore=5000.0, horas=120.0)


def sugerido(N):
    c = math.ceil(N)
    return c - 0.1 if c - 0.1 >= N else c + 0.9


def sample_products():
    rnd = random.Random(11)
    nomes = [("Camiseta básica algodão", "Vestuário", 28), ("Camiseta estampada", "Vestuário", 35), ("Calça jeans", "Vestuário", 74),
             ("Bermuda sarja", "Vestuário", 52), ("Boné aba reta", "Acessórios", 19), ("Meia esportiva (par)", "Acessórios", 6.5),
             ("Cinto couro sintético", "Acessórios", 21), ("Mochila escolar", "Acessórios", 66), ("Caneca personalizada", "Presentes", 9.8),
             ("Garrafa térmica 500ml", "Presentes", 31), ("Kit canetas (12 un)", "Papelaria", 8.2), ("Caderno universitário", "Papelaria", 12.5),
             ("Agenda 2027", "Papelaria", 17), ("Mouse sem fio", "Informática", 24), ("Teclado USB", "Informática", 38),
             ("Cabo HDMI 2m", "Informática", 11), ("Fone de ouvido", "Informática", 29), ("Carregador turbo", "Informática", 33),
             ("Vela aromática", "Casa", 14), ("Jogo de toalhas", "Casa", 58), ("Porta-retrato 15x21", "Casa", 7.4),
             ("Organizador multiuso", "Casa", 16), ("Luminária de mesa", "Casa", 42), ("Tapete antiderrapante", "Casa", 27)]
    rows = []
    for i, (n, cat, cost) in enumerate(nomes):
        cost = round(cost * rnd.uniform(0.95, 1.05), 2)
        frete = round(rnd.choice([0, 0.8, 1.2, 2.0, 3.5]), 2)
        lucro_ov = 0.30 if cat == "Presentes" else None
        imp_ov = None
        com_ov = 0.0 if cat in ("Papelaria",) else None
        L = cost + frete
        imp = PAR["imp"] if imp_ov is None else imp_ov
        com = PAR["com"] if com_ov is None else com_ov
        lucro = PAR["lucro"] if lucro_ov is None else lucro_ov
        fixo = PAR["fixos"] / PAR["fat"]
        M = imp + com + PAR["tax"] + fixo + lucro
        N_ = L / (1 - M)
        S = sugerido(N_)
        f = {0: 0.62, 3: 0.82, 7: 0.9, 11: 0.74}.get(i, rnd.choice([0.97, 1.0, 1.0, 1.05, 1.1]))
        praticado = round(math.floor(S * f) + 0.9, 2) if i % 5 != 4 else None
        conc = round(S * rnd.uniform(0.9, 1.12), 2) if i % 3 != 2 else None
        rows.append(dict(cod=f"P{i+1:03d}", nome=n, cat=cat, custo=cost, frete=frete, imp=imp_ov, com=com_ov, tax=None,
                         lucro=lucro_ov, conc=conc, prat=praticado, L=L, M=M, N=N_, S=S, lucro_used=lucro))
    return rows


def sample_services():
    rows = []
    hora = (PAR["fixos"] + PAR["prolabore"]) / PAR["horas"]
    for nome, cat, h, mat, desl, prat in [("Instalação padrão", "Instalação", 3.0, 45.0, 25.0, 690.0), ("Manutenção preventiva", "Manutenção", 1.5, 18.0, 25.0, 320.0),
                                           ("Visita técnica / diagnóstico", "Manutenção", 1.0, 0.0, 25.0, 150.0), ("Projeto personalizado", "Projeto", 8.0, 120.0, 0.0, 1850.0),
                                           ("Treinamento da equipe (2h)", "Treinamento", 2.0, 15.0, 0.0, 480.0)]:
        L = h * hora + mat + desl
        M = PAR["imp"] + PAR["com"] + PAR["tax"] + PAR["lucro"]
        N_ = L / (1 - M)
        rows.append(dict(nome=nome, cat=cat, h=h, mat=mat, desl=desl, prat=prat, L=L, M=M, N=N_, S=sugerido(N_)))
    return rows


def build(bk: Book):
    wb = bk.wb
    bk.inicio(
        "Precificador de Produtos e Serviços", "Carvex XLS · Preço certo = lucro garantido",
        "Calcule o preço de venda de cada produto e serviço considerando custo, impostos, comissão, taxa de cartão/marketplace, "
        "despesas fixas e o lucro que você quer. Descubra quais itens dão prejuízo e quanto custa dar desconto.",
        [("Config", "Informe impostos, comissão, taxa de pagamento, lucro desejado, custos fixos mensais e faturamento médio. A planilha calcula o rateio de despesa fixa e o custo da sua hora."),
         ("Cadastre os produtos", "Em Produtos, informe o custo de cada item (compra ou produção) e, se quiser, o preço que pratica hoje."),
         ("Cadastre os serviços", "Em Serviços, informe horas gastas e materiais. O custo da hora vem da Config."),
         ("Leia o preço sugerido", "A coluna Preço sugerido já considera todos os custos e o lucro. A coluna Status avisa se seu preço atual dá PREJUÍZO."),
         ("Simule descontos", "Na aba Simulador, escolha o produto e o desconto e veja quanto precisa vender a mais para manter o lucro.")],
        [("Config", "Parâmetros gerais: impostos, comissão, taxa, lucro, custos fixos, custo da hora."),
         ("Produtos", "Cadastro e preço de venda de produtos (até 300)."),
         ("Serviços", "Cadastro e preço de serviços (até 100)."),
         ("Simulador", "Quanto custa dar desconto: lucro por unidade e vendas extras necessárias."),
         ("Resumo", "Quantos itens estão em prejuízo, margem média e gráfico de margem.")],
        avisos=["Todos os percentuais são sobre o PREÇO DE VENDA (não sobre o custo).",
                "Se a soma dos percentuais chegar a 100%, o preço não pode ser calculado e a planilha mostra 'Revisar %'.",
                "Nas colunas de % por item (amarelas), deixe em branco para usar o padrão da Config; digite 0% se o item não tem aquele custo."])

    # ---------------------------------------------------------------- Config
    ws = bk.sheet("Config")
    bk.banner(ws, "Configurações gerais", "Percentuais sobre o preço de venda. Valem para todos os itens, exceto quando você digita um percentual específico.", 5)
    ws.set_column(0, 0, 3); ws.set_column(1, 1, 46); ws.set_column(2, 2, 18); ws.set_column(3, 3, 60)
    lf, inf = bk.fmt("lbl"), bk.fmt
    def line(r, label, val, nf, hint, kind="in", formula=False):
        ws.write(r, 1, label, lf)
        if formula:
            bk.fx(ws, (r, 2), val, bk.fmt("calc", nf=nf, align="right"))
        else:
            bk.w(ws, (r, 2), val, bk.fmt(kind, nf=nf, align="right"))
        ws.write(r, 3, hint, bk.fmt("note"))
    ws.write(3, 1, "Empresa", lf); ws.merge_range(3, 2, 3, 3, "Loja Exemplo" if bk.sample else "", bk.fmt("in"))
    bk.section(ws, 4, 1, "Percentuais padrão (sobre o preço de venda)", 3)
    line(5, "Impostos sobre a venda (%)", PAR["imp"] if bk.sample else None, "pct", "Simples/Presumido: percentual efetivo do seu faturamento (confirme com seu contador).")
    line(6, "Comissão de vendedores (%)", PAR["com"] if bk.sample else None, "pct", "Média paga a vendedores/representantes.")
    line(7, "Taxa de pagamento / plataforma (%)", PAR["tax"] if bk.sample else None, "pct", "Cartão, Pix, marketplace. Use a média ponderada dos seus canais.")
    line(8, "Lucro líquido desejado (%)", PAR["lucro"] if bk.sample else None, "pct", "Quanto deve sobrar de cada venda depois de pagar tudo.")
    bk.section(ws, 10, 1, "Despesas fixas", 3)
    line(11, "Custos fixos mensais (R$)", PAR["fixos"] if bk.sample else None, "money", "Aluguel, salários, energia, contador, sistemas... (sem pró-labore).")
    line(12, "Faturamento médio mensal (R$)", PAR["fat"] if bk.sample else None, "money", "Média dos últimos 6 meses. Se não souber, use uma estimativa realista.")
    line(13, "Despesa fixa rateada (%)", "IFERROR(C12/C13,0)", "pct", "Calculado: custos fixos / faturamento. É somado ao preço dos produtos.", formula=True)
    bk.section(ws, 15, 1, "Serviços: custo da hora", 3)
    line(16, "Pró-labore desejado por mês (R$)", PAR["prolabore"] if bk.sample else None, "money", "Quanto o dono precisa tirar por mês.")
    line(17, "Horas produtivas por mês", PAR["horas"] if bk.sample else None, "int", "Horas realmente vendáveis (ex.: 6h x 20 dias = 120). Não use 220h.")
    line(18, "Custo da hora (R$)", "IFERROR((C12+C17)/C18,0)", "money", "Calculado: (custos fixos + pró-labore) / horas produtivas.", formula=True)
    for r in (5, 6, 7, 8):
        bk.dv_num(ws, f"C{r+1}", 0, 0.95, "Digite em %, ex.: 6%")
    bk.define("pImp", "=Config!$C$6"); bk.define("pCom", "=Config!$C$7"); bk.define("pTax", "=Config!$C$8")
    bk.define("pLucro", "=Config!$C$9"); bk.define("pFixo", "=Config!$C$14"); bk.define("cHora", "=Config!$C$19")
    ws.write(20, 1, "Dica: sem esses números, o preço calculado fica errado. Se ainda não sabe, comece com estimativas e refine depois.", bk.fmt("note"))

    # ---------------------------------------------------------------- Produtos
    wp = bk.sheet("Produtos")
    bk.banner(wp, "Produtos", "Preencha as colunas amarelas. Percentuais em branco usam o padrão da Config.", 21)
    heads = ["Código", "Produto", "Categoria", "Custo de compra / produção (R$)", "Frete / embalagem por un. (R$)", "Imposto % (opcional)",
             "Comissão % (opcional)", "Taxa pagto % (opcional)", "Lucro % (opcional)", "Preço do concorrente (R$)", "Preço que pratico hoje (R$)",
             "Custo total (R$)", "% sobre o preço (soma)", "Preço calculado (exato)", "PREÇO SUGERIDO", "Markup sobre o custo",
             "Preço mínimo (lucro zero)", "Lucro por un. no preço atual", "Margem líquida no preço atual", "Status", "Vs. concorrente"]
    wid = [9, 28, 13, 14, 14, 10, 10, 10, 10, 13, 13, 12, 11, 13, 14, 11, 13, 13, 12, 17, 18]
    bk.header(wp, 3, 0, heads, wid, 58)
    rows = sample_products() if bk.sample else []
    fi = bk.fmt("in"); fm = bk.fmt("in", nf="money"); fp = bk.fmt("in", nf="pct")
    cm = bk.fmt("calc", nf="money"); cp = bk.fmt("calc", nf="pct", align="center"); cc = bk.fmt("calc", align="center")
    cx = bk.fmt("calc", nf="x", align="center"); sug = bk.fmt("calc", nf="money", bold=True, bg_color=G_LIGHT)
    for i in range(NP):
        r = P0 + i; x = r + 1
        d = rows[i] if i < len(rows) else {}
        bk.w(wp, (r, 0), d.get("cod"), fi); bk.w(wp, (r, 1), d.get("nome"), fi); bk.w(wp, (r, 2), d.get("cat"), fi)
        bk.w(wp, (r, 3), d.get("custo"), fm); bk.w(wp, (r, 4), d.get("frete"), fm)
        for c, k in ((5, "imp"), (6, "com"), (7, "tax"), (8, "lucro")):
            bk.w(wp, (r, c), d.get(k), fp)
        bk.w(wp, (r, 9), d.get("conc"), fm); bk.w(wp, (r, 10), d.get("prat"), fm)
        lu = f'IF($I{x}="",pLucro,$I{x})'
        bk.fx(wp, (r, 11), f'IF(OR($B{x}="",$D{x}=""),"",$D{x}+N($E{x}))', cm)
        bk.fx(wp, (r, 12), f'IF($L{x}="","",IF($F{x}="",pImp,$F{x})+IF($G{x}="",pCom,$G{x})+IF($H{x}="",pTax,$H{x})+pFixo+{lu})', cp)
        bk.fx(wp, (r, 13), f'IF($L{x}="","",IF($M{x}>=1,"Revisar %",$L{x}/(1-$M{x})))', cm)
        bk.fx(wp, (r, 14), f'IF(ISNUMBER($N{x}),ROUNDUP($N{x},0)+IF(ROUNDUP($N{x},0)-0.1>=$N{x},-0.1,0.9),$N{x})', sug)
        bk.fx(wp, (r, 15), f'IF(AND(ISNUMBER($O{x}),N($L{x})>0),$O{x}/$L{x},"")', cx)
        bk.fx(wp, (r, 16), f'IF(ISNUMBER($N{x}),$L{x}/(1-($M{x}-{lu})),"")', cm)
        bk.fx(wp, (r, 17), f'IF(OR($K{x}="",NOT(ISNUMBER($N{x}))),"",$K{x}*(1-($M{x}-{lu}))-$L{x})', cm)
        bk.fx(wp, (r, 18), f'IF($R{x}="","",$R{x}/$K{x})', cp)
        bk.fx(wp, (r, 19), f'IF($L{x}="","",IF(NOT(ISNUMBER($N{x})),"Revisar %",IF($K{x}="","Sem preço atual",IF($R{x}<0,"PREJUÍZO",IF($K{x}<$N{x},"Abaixo do ideal","OK")))))', cc)
        bk.fx(wp, (r, 20), f'IF(OR($J{x}="",NOT(ISNUMBER($O{x}))),"",IF($O{x}<=$J{x},"Competitivo ("&ROUND(($O{x}/$J{x}-1)*100,1)&"%)","Acima do concorrente (+"&ROUND(($O{x}/$J{x}-1)*100,1)&"%)"))', cc)
    last = P0 + NP
    bk.dv_num(wp, f"D{P0+1}:E{last}", 0, None, "Valor em R$")
    bk.dv_num(wp, f"F{P0+1}:I{last}", 0, 0.95, "Em branco = usa o padrão da Config")
    bk.dv_num(wp, f"J{P0+1}:K{last}", 0, None)
    wp.conditional_format(f"T{P0+1}:T{last}", {"type": "cell", "criteria": "==", "value": '"PREJUÍZO"', "format": wb.add_format({"bg_color": C_RED, "font_color": "#FFFFFF", "bold": True})})
    wp.conditional_format(f"T{P0+1}:T{last}", {"type": "cell", "criteria": "==", "value": '"Abaixo do ideal"', "format": wb.add_format({"bg_color": C_AMBERL, "font_color": "#92400E", "bold": True})})
    wp.conditional_format(f"T{P0+1}:T{last}", {"type": "cell", "criteria": "==", "value": '"OK"', "format": wb.add_format({"bg_color": G_LIGHT, "font_color": "#15803D", "bold": True})})
    wp.conditional_format(f"T{P0+1}:T{last}", {"type": "cell", "criteria": "==", "value": '"Revisar %"', "format": wb.add_format({"bg_color": C_REDL, "font_color": C_RED, "bold": True})})
    wp.freeze_panes(4, 2)
    wp.autofilter(3, 0, last - 1, 20)
    bk.define("ProdNome", f"=Produtos!$B${P0+1}:$B${last}")

    # ---------------------------------------------------------------- Serviços
    wsv = bk.sheet("Serviços")
    bk.banner(wsv, "Serviços", "O custo da hora vem da Config (custos fixos + pró-labore / horas produtivas).", 19)
    sh = ["Serviço", "Categoria", "Horas gastas", "Materiais (R$)", "Deslocamento / outros (R$)", "Imposto % (opcional)", "Comissão % (opcional)",
          "Taxa pagto % (opcional)", "Lucro % (opcional)", "Preço que pratico hoje (R$)", "Custo da mão de obra (R$)", "Custo total (R$)",
          "% sobre o preço (soma)", "Preço calculado (exato)", "PREÇO SUGERIDO", "Valor da hora no preço sugerido", "Lucro no preço atual (R$)", "Margem no preço atual", "Status"]
    sw = [30, 14, 9, 12, 13, 10, 10, 10, 10, 14, 13, 12, 11, 13, 14, 13, 13, 11, 17]
    bk.header(wsv, 3, 0, sh, sw, 58)
    srows = sample_services() if bk.sample else []
    for i in range(NS):
        r = P0 + i; x = r + 1
        d = srows[i] if i < len(srows) else {}
        bk.w(wsv, (r, 0), d.get("nome"), fi); bk.w(wsv, (r, 1), d.get("cat"), fi)
        bk.w(wsv, (r, 2), d.get("h"), bk.fmt("in", nf="0.0"))
        bk.w(wsv, (r, 3), d.get("mat"), fm); bk.w(wsv, (r, 4), d.get("desl"), fm)
        for c in (5, 6, 7, 8):
            bk.w(wsv, (r, c), None, fp)
        bk.w(wsv, (r, 9), d.get("prat"), fm)
        lu = f'IF($I{x}="",pLucro,$I{x})'
        bk.fx(wsv, (r, 10), f'IF(OR($A{x}="",$C{x}=""),"",$C{x}*cHora)', cm)
        bk.fx(wsv, (r, 11), f'IF($K{x}="","",$K{x}+N($D{x})+N($E{x}))', cm)
        bk.fx(wsv, (r, 12), f'IF($L{x}="","",IF($F{x}="",pImp,$F{x})+IF($G{x}="",pCom,$G{x})+IF($H{x}="",pTax,$H{x})+{lu})', cp)
        bk.fx(wsv, (r, 13), f'IF($L{x}="","",IF($M{x}>=1,"Revisar %",$L{x}/(1-$M{x})))', cm)
        bk.fx(wsv, (r, 14), f'IF(ISNUMBER($N{x}),ROUNDUP($N{x},0)+IF(ROUNDUP($N{x},0)-0.1>=$N{x},-0.1,0.9),$N{x})', sug)
        bk.fx(wsv, (r, 15), f'IF(AND(ISNUMBER($O{x}),N($C{x})>0),$O{x}/$C{x},"")', cm)
        bk.fx(wsv, (r, 16), f'IF(OR($J{x}="",NOT(ISNUMBER($N{x}))),"",$J{x}*(1-($M{x}-{lu}))-$L{x})', cm)
        bk.fx(wsv, (r, 17), f'IF($Q{x}="","",$Q{x}/$J{x})', cp)
        bk.fx(wsv, (r, 18), f'IF($L{x}="","",IF(NOT(ISNUMBER($N{x})),"Revisar %",IF($J{x}="","Sem preço atual",IF($Q{x}<0,"PREJUÍZO",IF($J{x}<$N{x},"Abaixo do ideal","OK")))))', cc)
    lasts = P0 + NS
    bk.dv_num(wsv, f"C{P0+1}:E{lasts}", 0); bk.dv_num(wsv, f"F{P0+1}:I{lasts}", 0, 0.95); bk.dv_num(wsv, f"J{P0+1}:J{lasts}", 0)
    for t, bg, fg in (("PREJUÍZO", C_RED, "#FFFFFF"), ("Abaixo do ideal", C_AMBERL, "#92400E"), ("OK", G_LIGHT, "#15803D")):
        wsv.conditional_format(f"S{P0+1}:S{lasts}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wsv.freeze_panes(4, 1)

    # ---------------------------------------------------------------- Simulador
    wsm = bk.sheet("Simulador", onepage=True)
    bk.banner(wsm, "Simulador de desconto", "Descubra quanto precisa vender a mais para não perder lucro ao dar desconto.", 6)
    wsm.set_column(0, 0, 3); wsm.set_column(1, 1, 44); wsm.set_column(2, 5, 18)
    def _sim(d):
        base = d["prat"] if d["prat"] else d["S"]
        var = d["M"] - d["lucro_used"]
        return base * (1 - var) - d["L"], base * 0.9 * (1 - var) - d["L"]
    sel = next((d for d in rows if _sim(d)[0] > 0 and _sim(d)[1] > 0), rows[0]) if bk.sample else None
    first = sel["nome"] if bk.sample else None
    wsm.write(3, 1, "Escolha o produto", lf); bk.w(wsm, (3, 2), first, bk.fmt("in", bold=True)); wsm.merge_range(3, 2, 3, 4, first, bk.fmt("in", bold=True))
    bk.dv_list(wsm, "C4", "=ProdNome", "Escolha um produto cadastrado")
    wsm.write(4, 1, "Desconto que pretendo dar (%)", lf); bk.w(wsm, (4, 2), 0.10, bk.fmt("in", nf="pct", align="center"))
    bk.dv_num(wsm, "C5", 0, 0.95)
    wsm.write(5, 1, "Linha do produto na lista (apoio)", bk.fmt("note"))
    bk.fx(wsm, "C6", 'IFERROR(MATCH($C$4,ProdNome,0),"")', bk.fmt("calc", align="center"))
    P = lambda c: f"INDEX(Produtos!${c}${P0+1}:${c}${last},$C$6)"
    items = [
        ("Preço atual de venda (usa o praticado; se vazio, o sugerido)", f'IF($C$6="","",IF(N({P("K")})>0,{P("K")},{P("O")}))', "money"),
        ("Custo total por unidade", f'IF($C$6="","",{P("L")})', "money"),
        ("% de impostos, taxas e rateio fixo sobre o preço", f'IF($C$6="","",{P("M")}-IF({P("I")}="",pLucro,{P("I")}))', "pct"),
        ("Lucro por unidade hoje", 'IF($C$6="","",C8*(1-C10)-C9)', "money"),
        ("Preço com desconto", 'IF($C$6="","",C8*(1-$C$5))', "money"),
        ("Lucro por unidade com desconto", 'IF($C$6="","",C12*(1-C10)-C9)', "money"),
        ("Queda do lucro por unidade", 'IF(OR($C$6="",N(C11)<=0),"",1-C13/C11)', "pct"),
        ("Vendas a mais para manter o MESMO lucro total", 'IF($C$6="","",IF(C13<=0,"Impossível: dá prejuízo",IF(C11<=0,"",C11/C13-1)))', "pct0"),
    ]
    for i, (lab, f, nf) in enumerate(items):
        r = 7 + i
        wsm.write(r, 1, lab, lf if i < 7 else bk.fmt("lbl", bold=True))
        bk.fx(wsm, (r, 2), f, bk.fmt("calc" if i < 7 else "tot", nf=nf, align="center", bold=(i == 7)))
    bk.section(wsm, 16, 1, "Tabela de descontos para o produto escolhido", 5)
    bk.header(wsm, 17, 1, ["Desconto", "Preço com desconto", "Lucro por unidade", "Queda do lucro", "Vendas a mais necessárias"], height=30)
    for i, dsc in enumerate([0, .05, .10, .15, .20, .25, .30]):
        r = 18 + i; x = r + 1
        bk.w(wsm, (r, 1), dsc, bk.fmt("plain", nf="pct0", align="center"))
        bk.fx(wsm, (r, 2), f'IF($C$6="","",$C$8*(1-B{x}))', bk.fmt("calc", nf="money"))
        bk.fx(wsm, (r, 3), f'IF($C$6="","",C{x}*(1-$C$10)-$C$9)', bk.fmt("calc", nf="money"))
        bk.fx(wsm, (r, 4), f'IF(OR($C$6="",N($C$11)<=0),"",1-D{x}/$C$11)', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wsm, (r, 5), f'IF($C$6="","",IF(D{x}<=0,"Impossível",IF(N($C$11)<=0,"",$C$11/D{x}-1)))', bk.fmt("calc", nf="pct0", align="center"))
    wsm.merge_range(26, 1, 27, 5, "Leitura: se o desconto exigir +50% de vendas e você não consegue vender 50% a mais, dar o desconto "
                    "reduz o seu lucro total. Prefira benefícios que não reduzem o preço (frete, brinde, parcelamento).", bk.fmt("note"))
    wsm.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})

    # ---------------------------------------------------------------- Resumo
    wr = bk.sheet("Resumo", tab=G_NEON, onepage=True)
    bk.banner(wr, "Resumo", "Saúde geral da sua precificação.", 8)
    for c in range(8):
        wr.set_column(c, c, 13)
    T = lambda c: f"Produtos!${c}${P0+1}:${c}${last}"
    SV = lambda c: f"'Serviços'!${c}${P0+1}:${c}${lasts}"
    bk.kpi(wr, 3, 0, "PRODUTOS CADASTRADOS", f'COUNTIF({T("L")},">0")', "int", 2)
    bk.kpi(wr, 3, 2, "EM PREJUÍZO", f'COUNTIF({T("T")},"PREJUÍZO")', "int", 2, color=C_RED)
    bk.kpi(wr, 3, 4, "ABAIXO DO IDEAL", f'COUNTIF({T("T")},"Abaixo do ideal")', "int", 2, color="#B45309")
    bk.kpi(wr, 3, 6, "COM PREÇO OK", f'COUNTIF({T("T")},"OK")', "int", 2)
    bk.kpi(wr, 6, 0, "MARGEM MÉDIA ATUAL", f'IFERROR(AVERAGE({T("S")}),0)', "pct", 2)
    bk.kpi(wr, 6, 2, "LUCRO DESEJADO", "pLucro", "pct", 2)
    bk.kpi(wr, 6, 4, "SERVIÇOS EM PREJUÍZO", f'COUNTIF({SV("S")},"PREJUÍZO")', "int", 2, color=C_RED)
    bk.kpi(wr, 6, 6, "CUSTO DA HORA", "cHora", "money", 2)
    wr.write(9, 0, "Margem líquida no preço atual (primeiros 20 produtos)", bk.fmt("sec"))
    wr.merge_range(9, 0, 9, 7, "Margem líquida no preço atual (primeiros 20 produtos)", bk.fmt("sec"))
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Margem no preço atual", "categories": f"=Produtos!$B${P0+1}:$B${P0+20}", "values": f"=Produtos!$S${P0+1}:$S${P0+20}",
                   "fill": {"color": G_MID}, "invert_if_negative": True, "invert_if_negative_color": "#DC2626", "gap": 60})
    ch.set_title({"name": "Margem por produto (quanto sobra de cada venda)", "name_font": {"size": 12}})
    ch.set_legend({"none": True}); ch.set_y_axis({"num_format": "0%", "major_gridlines": {"visible": True, "line": {"color": "#E5E7EB"}}})
    ch.set_x_axis({"num_font": {"rotation": -45, "size": 8}})
    ch.set_size({"width": 780, "height": 340})
    wr.insert_chart("A12", ch)
    wr.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
    bk.finish()

    exp = {}
    if bk.sample:
        r0 = rows[0]
        exp[("Produtos", "N5")] = round(r0["N"], 2)
        exp[("Produtos", "O5")] = round(r0["S"], 2)
        exp[("Config", "C14")] = round(PAR["fixos"] / PAR["fat"], 6)
        exp[("Config", "C19")] = round((PAR["fixos"] + PAR["prolabore"]) / PAR["horas"], 6)
        def stat(d):
            if d["prat"] is None:
                return "Sem preço atual"
            lu = d["lucro_used"]
            prof = d["prat"] * (1 - (d["M"] - lu)) - d["L"]
            return "PREJUÍZO" if prof < 0 else ("Abaixo do ideal" if d["prat"] < d["N"] else "OK")
        sts = [stat(d) for d in rows]
        exp[("Resumo", "C5")] = sts.count("PREJUÍZO")
        exp[("Resumo", "E5")] = sts.count("Abaixo do ideal")
        exp[("Resumo", "G5")] = sts.count("OK")
        exp[("Resumo", "A5")] = len(rows)
        lucro0, lucro1 = _sim(sel)
        exp[("Simulador", "C11")] = round(lucro0, 2)
        exp[("Simulador", "C13")] = round(lucro1, 2)
        exp[("Simulador", "C15")] = round(lucro0 / lucro1 - 1, 4) if lucro1 > 0 else "Impossível: dá prejuízo"
        sv0 = srows[0]
        exp[("Serviços", "O5")] = round(sv0["S"], 2)
    return exp
