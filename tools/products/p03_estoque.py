# -*- coding: utf-8 -*-
import datetime as dt
import math
import random
from lib import *

SLUG = "estoque-inteligente"
PASTA = "estoque/estoque-inteligente"
NOME = "Estoque Inteligente com Curva ABC"
NP = 300
NM = 3000
P0 = 4
PL = P0 + NP      # excel última linha produtos
M0 = 4
ML = M0 + NM

DIAS_AN = 90
DIAS_PARADO = 90
FAT_MAX = 2.0
CORTE_A, CORTE_B = 0.80, 0.95

CATS = ["Papelaria", "Escritório", "Informática", "Escolar", "Embalagens", "Limpeza", "Presentes"]
UNS = ["un", "cx", "pct", "kg", "L", "m", "par"]
FORN = ["Distribuidora Alfa", "Atacado Beta", "Importadora Gama", "Fábrica Delta", "Papelaria Central"]


def sample_data():
    rnd = random.Random(33)
    catalog = [
        ("Caderno universitário 10 matérias", "Escolar", "un", 9.5, 19.9, 30, "Papelaria Central"),
        ("Caneta esferográfica azul (cx 50)", "Papelaria", "cx", 22, 44.9, 12, "Atacado Beta"),
        ("Papel A4 75g (resma)", "Escritório", "pct", 21.5, 32.9, 40, "Distribuidora Alfa"),
        ("Pasta suspensa (pct 25)", "Escritório", "pct", 28, 54.9, 6, "Distribuidora Alfa"),
        ("Grampeador médio", "Escritório", "un", 14, 29.9, 8, "Fábrica Delta"),
        ("Mouse óptico USB", "Informática", "un", 11, 24.9, 10, "Importadora Gama"),
        ("Pen drive 32GB", "Informática", "un", 22, 44.9, 10, "Importadora Gama"),
        ("Cabo USB-C 1m", "Informática", "un", 6.5, 19.9, 20, "Importadora Gama"),
        ("Mochila escolar 20L", "Escolar", "un", 46, 99.9, 6, "Fábrica Delta"),
        ("Estojo duplo", "Escolar", "un", 8.5, 21.9, 14, "Papelaria Central"),
        ("Lápis de cor (cx 24)", "Escolar", "cx", 7.9, 18.9, 25, "Papelaria Central"),
        ("Cola branca 90g", "Escolar", "un", 1.9, 4.9, 60, "Atacado Beta"),
        ("Tesoura escolar", "Escolar", "un", 2.8, 7.9, 30, "Atacado Beta"),
        ("Fita adesiva transparente", "Embalagens", "un", 1.6, 4.5, 80, "Distribuidora Alfa"),
        ("Caixa de papelão M (pct 10)", "Embalagens", "pct", 15, 29.9, 12, "Fábrica Delta"),
        ("Plástico bolha (rolo 50m)", "Embalagens", "un", 32, 59.9, 5, "Fábrica Delta"),
        ("Sacola kraft G (pct 50)", "Embalagens", "pct", 24, 47.9, 8, "Fábrica Delta"),
        ("Álcool 70% 1L", "Limpeza", "L", 6.2, 12.9, 24, "Distribuidora Alfa"),
        ("Papel toalha (pct 2)", "Limpeza", "pct", 5.9, 11.9, 30, "Distribuidora Alfa"),
        ("Pilha AA (cartela 4)", "Presentes", "un", 7.5, 16.9, 20, "Importadora Gama"),
        ("Caneca branca para sublimação", "Presentes", "un", 4.2, 12.9, 30, "Importadora Gama"),
        ("Garrafa squeeze 600ml", "Presentes", "un", 9.9, 24.9, 12, "Importadora Gama"),
        ("Agenda 2027", "Papelaria", "un", 14, 34.9, 10, "Papelaria Central"),
        ("Marca-texto (cx 6)", "Papelaria", "cx", 9.8, 22.9, 12, "Atacado Beta"),
        ("Bloco de notas adesivas", "Papelaria", "pct", 3.4, 8.9, 40, "Atacado Beta"),
        ("Calculadora de mesa", "Escritório", "un", 17, 39.9, 5, "Importadora Gama"),
        ("Fichário argolado", "Escolar", "un", 21, 44.9, 8, "Papelaria Central"),
        ("Régua 30cm", "Escolar", "un", 0.9, 3.5, 50, "Atacado Beta"),
        ("Etiqueta adesiva (pct 100)", "Escritório", "pct", 6.4, 14.9, 15, "Distribuidora Alfa"),
        ("Toner genérico preto", "Informática", "un", 62, 119.9, 4, "Importadora Gama"),
        ("Mouse pad", "Informática", "un", 4.9, 14.9, 14, "Importadora Gama"),
        ("Clips 2/0 (cx 100)", "Escritório", "cx", 1.8, 4.9, 30, "Atacado Beta"),
        ("Envelope A4 (pct 50)", "Escritório", "pct", 14, 29.9, 6, "Distribuidora Alfa"),
        ("Tinta guache (kit 6)", "Escolar", "cx", 8.7, 19.9, 15, "Papelaria Central"),
        ("Papel fotográfico A4 (pct 20)", "Informática", "pct", 12.5, 27.9, 6, "Importadora Gama"),
        ("Luva descartável (cx 100)", "Limpeza", "cx", 21, 39.9, 6, "Distribuidora Alfa"),
        ("Pote plástico 500ml (pct 12)", "Embalagens", "pct", 11, 24.9, 8, "Fábrica Delta"),
        ("Caixa organizadora", "Presentes", "un", 18, 42.9, 7, "Fábrica Delta"),
        ("Apontador com depósito", "Escolar", "un", 1.4, 4.9, 45, "Atacado Beta"),
        ("Porta-retrato 10x15", "Presentes", "un", 6.2, 17.9, 10, "Importadora Gama"),
    ]
    start = dt.date(2026, 7, 1)
    ref = REF_DATE
    prods, movs = [], []
    for i, (nome, cat, un, custo, preco, demand_w, forn) in enumerate(catalog):
        cod = f"E{i+1:03d}"
        dem_w = demand_w / 3.0 * {0: 3.0, 1: 2.5, 2: 3.0, 8: 2.5, 6: 2.5, 7: 2.0}.get(i, 0.45)                                   # unidades vendidas por semana (aprox.)
        minimo = max(3, math.ceil(dem_w * 1.2))
        # cenários para gerar status variados
        mode = "normal"
        if i in (4, 10, 17, 24):
            mode = "ruptura"
        elif i in (7, 19, 33):
            mode = "baixo"
        elif i in (14, 22, 36):
            mode = "excesso"
        elif i in (28, 31, 38):
            mode = "parado"
        stock0 = {"excesso": minimo * 6, "parado": minimo * 3}.get(mode, minimo * 2)
        prods.append(dict(cod=cod, nome=nome, cat=cat, un=un, forn=forn, custo=custo, preco=preco, ini=stock0, minimo=minimo,
                          prazo=rnd.choice([3, 5, 7, 10]), mode=mode))
        stock = stock0
        d = start
        last_sale_cut = dt.date(2026, 6, 15)
        while d <= ref:
            # saídas semanais (1 movimento por semana)
            sale_day = d + dt.timedelta(days=rnd.randint(0, 5))
            if sale_day <= ref and mode != "parado":
                q = int(round(dem_w * rnd.uniform(0.6, 1.4)))
                if mode == "excesso":
                    q = max(1, q // 3)
                q = min(q, stock)
                if q > 0:
                    movs.append((sale_day, cod, "Saída", q, "Venda balcão"))
                    stock -= q
            if mode == "parado" and d < dt.date(2026, 7, 8):
                q = min(2, stock)
                if q > 0:
                    movs.append((d + dt.timedelta(days=2), cod, "Saída", q, "Venda balcão"))
                    stock -= q
            # reposição
            if stock <= minimo and mode in ("normal", "baixo", "excesso") and d < dt.date(2026, 10, 1):
                if not (mode == "baixo" and d >= dt.date(2026, 9, 1)):
                    q = minimo * 2 - stock
                    ed = d + dt.timedelta(days=rnd.randint(1, 3))
                    if ed <= ref:
                        movs.append((ed, cod, "Entrada", q, f"NF {rnd.randint(1000, 9999)}"))
                        stock += q
            if mode == "ruptura" and d < dt.date(2026, 8, 1) and stock <= minimo:
                q = minimo * 2 - stock
                movs.append((d + dt.timedelta(days=1), cod, "Entrada", q, f"NF {rnd.randint(1000, 9999)}"))
                stock += q
            d += dt.timedelta(days=7)
    # ruptura: força zerar
    movs.sort(key=lambda m: (m[0], m[1]))
    return prods, movs


def analyze(prods, movs):
    """Replica em Python as fórmulas da aba Posição (para conferência)."""
    res = []
    lo = REF_DATE - dt.timedelta(days=DIAS_AN)
    for p in prods:
        ent = sum(m[3] for m in movs if m[1] == p["cod"] and m[2] == "Entrada")
        sai = sum(m[3] for m in movs if m[1] == p["cod"] and m[2] == "Saída")
        atual = p["ini"] + ent - sai
        mx = math.ceil(p["minimo"] * FAT_MAX) if p["minimo"] > 0 else None
        per = sum(m[3] for m in movs if m[1] == p["cod"] and m[2] == "Saída" and lo <= m[0] <= REF_DATE)
        last = max([m[0] for m in movs if m[1] == p["cod"] and m[2] == "Saída"], default=None)
        if atual <= 0:
            st = "RUPTURA"
        elif p["minimo"] > 0 and atual <= p["minimo"]:
            st = "REPOR"
        elif mx is not None and atual > mx:
            st = "EXCESSO"
        else:
            st = "OK"
        parado = atual > 0 and (last is None or (REF_DATE - last).days > DIAS_PARADO)
        sug = max(0, mx - atual) if st in ("RUPTURA", "REPOR") and mx is not None else 0
        fat = per * (p["preco"] if p["preco"] > 0 else p["custo"])
        res.append(dict(p=p, ent=ent, sai=sai, atual=atual, mx=mx, per=per, last=last, st=st, parado=parado, sug=sug,
                        valor=atual * p["custo"], fat=fat))
    # ABC
    items = sorted([r for r in res if r["fat"] > 0], key=lambda r: -r["fat"])
    total = sum(r["fat"] for r in items)
    cum = 0
    for r in items:
        share = r["fat"] / total
        prev = cum
        cum += share
        r["cls"] = "A" if prev < CORTE_A else ("B" if prev < CORTE_B else "C")
    for r in res:
        r.setdefault("cls", "C")
    return res


def build(bk: Book):
    wb = bk.wb
    bk.inicio(
        "Estoque Inteligente com Curva ABC", "Carvex XLS · Nunca mais falte o que vende, nunca mais sobre o que não vende",
        "Registre as entradas e saídas e a planilha calcula o estoque atual de cada item, avisa o que precisa repor, o que está em excesso, "
        "o que está parado, monta a lista de compras e classifica seus produtos na Curva ABC (o que realmente paga as contas).",
        [("Config", "Informe os períodos de análise (padrão: 90 dias), o fator de estoque máximo e os cortes da Curva ABC. Cadastre fornecedores e categorias."),
         ("Cadastre os produtos", "Em Produtos: código único, nome, custo, preço de venda, estoque inicial (contagem de hoje) e estoque mínimo."),
         ("Lance as movimentações", "Em Movimentações: data, código, Entrada ou Saída e quantidade. Compras e devoluções de venda = Entrada; vendas e perdas = Saída."),
         ("Veja a Posição", "Na aba Posição, o Status mostra RUPTURA, REPOR, OK ou EXCESSO de cada item, e se está Parado."),
         ("Use a lista de compras", "Na aba Compras, veja o que comprar, de qual fornecedor e quanto vai custar.")],
        [("Config", "Parâmetros gerais, categorias, unidades e fornecedores."),
         ("Produtos", "Cadastro (até 300 itens)."),
         ("Movimentações", "Todas as entradas e saídas (até 3.000 linhas)."),
         ("Posição", "Estoque atual, status, cobertura, itens parados e sugestão de compra."),
         ("Curva ABC", "Ranking automático por faturamento e classes A/B/C com gráfico de Pareto."),
         ("Compras", "Lista de compras pronta com valores por fornecedor."),
         ("Dashboard", "Indicadores e gráficos.")],
        avisos=["O estoque inicial é a contagem física do dia em que você começou a usar a planilha. Depois disso, só lance movimentações.",
                "O Código do produto deve ser único e igual nas abas Produtos e Movimentações.",
                "Para corrigir um erro, edite a linha da movimentação (não crie uma saída para 'desfazer')."])

    # ------------------------------------------------------------- Config
    ws = bk.sheet("Config")
    bk.banner(ws, "Configurações", "Preencha as células amarelas.", 8)
    ws.set_column(0, 0, 3); ws.set_column(1, 1, 44); ws.set_column(2, 2, 16); ws.set_column(3, 3, 4)
    ws.set_column(4, 4, 18); ws.set_column(5, 5, 14); ws.set_column(6, 6, 26)
    lf = bk.fmt("lbl")
    ws.write(3, 1, "Empresa", lf); bk.w(ws, (3, 2), "Papelaria Exemplo" if bk.sample else None, bk.fmt("in"))
    ws.write(4, 1, "Data de hoje (referência)", lf)
    if bk.sample:
        bk.w(ws, "C5", REF_DATE, bk.fmt("in", nf="date", align="center"))
    else:
        bk.fx(ws, "C5", "TODAY()", bk.fmt("calc", nf="date", align="center"))
    def inp(r, label, v, nf):
        ws.write(r, 1, label, lf); bk.w(ws, (r, 2), v, bk.fmt("in", nf=nf, align="center"))
    inp(5, "Período para medir vendas (dias)", DIAS_AN, "0")
    inp(6, "Dias sem saída para considerar 'Parado'", DIAS_PARADO, "0")
    inp(7, "Estoque máximo = mínimo x (fator)", FAT_MAX, "0.0")
    inp(8, "Curva ABC: limite da classe A (% acumulado)", CORTE_A, "pct0")
    inp(9, "Curva ABC: limite da classe B (% acumulado)", CORTE_B, "pct0")
    bk.dv_num(ws, "C6", 7, 365, integer=True); bk.dv_num(ws, "C7", 7, 730, integer=True); bk.dv_num(ws, "C8", 1, 10)
    bk.dv_num(ws, "C9", 0.5, 0.95); bk.dv_num(ws, "C10", 0.8, 0.99)
    for n, r in (("Hoje", "C5"), ("DiasAn", "C6"), ("DiasParado", "C7"), ("FatMax", "C8"), ("CorteA", "C9"), ("CorteB", "C10")):
        bk.define(n, f"=Config!${r[0]}${r[1:]}")
    ws.write(11, 1, "Dica: Estoque máximo (fator 2) = 2 x o mínimo. Acima disso o item aparece como EXCESSO.", bk.fmt("note"))
    ws.write(3, 4, "Categorias", bk.fmt("h")); ws.write(3, 5, "Unidades", bk.fmt("h")); ws.write(3, 6, "Fornecedores", bk.fmt("h"))
    for i in range(30):
        bk.w(ws, (4 + i, 4), CATS[i] if i < len(CATS) and bk.sample else (CATS[i] if i < len(CATS) else None), bk.fmt("in"))
        bk.w(ws, (4 + i, 5), UNS[i] if i < len(UNS) else None, bk.fmt("in"))
        bk.w(ws, (4 + i, 6), FORN[i] if i < len(FORN) else None, bk.fmt("in"))
    bk.define("Categorias", "=Config!$E$5:$E$34"); bk.define("Unidades", "=Config!$F$5:$F$34"); bk.define("Fornecedores", "=Config!$G$5:$G$34")

    # ------------------------------------------------------------- Produtos
    prods, movs = sample_data() if bk.sample else ([], [])
    wp = bk.sheet("Produtos")
    bk.banner(wp, "Cadastro de produtos", "Um produto por linha. O código não pode repetir.", 10)
    bk.header(wp, 3, 0, ["Código", "Produto", "Categoria", "Unidade", "Fornecedor principal", "Custo unitário (R$)", "Preço de venda (R$)",
                         "Estoque inicial", "Estoque mínimo", "Prazo de reposição (dias)"], [10, 36, 14, 9, 22, 13, 13, 11, 11, 12], 44)
    fi = bk.fmt("in"); fm = bk.fmt("in", nf="money"); fn = bk.fmt("in", nf="int", align="center")
    for i in range(NP):
        r = P0 + i
        p = prods[i] if i < len(prods) else {}
        bk.w(wp, (r, 0), p.get("cod"), fi); bk.w(wp, (r, 1), p.get("nome"), fi); bk.w(wp, (r, 2), p.get("cat"), fi)
        bk.w(wp, (r, 3), p.get("un"), bk.fmt("in", align="center")); bk.w(wp, (r, 4), p.get("forn"), fi)
        bk.w(wp, (r, 5), p.get("custo"), fm); bk.w(wp, (r, 6), p.get("preco"), fm)
        bk.w(wp, (r, 7), p.get("ini"), fn); bk.w(wp, (r, 8), p.get("minimo"), fn); bk.w(wp, (r, 9), p.get("prazo"), fn)
    bk.dv_list(wp, f"C{P0+1}:C{PL}", "=Categorias"); bk.dv_list(wp, f"D{P0+1}:D{PL}", "=Unidades"); bk.dv_list(wp, f"E{P0+1}:E{PL}", "=Fornecedores")
    bk.dv_num(wp, f"F{P0+1}:G{PL}", 0); bk.dv_num(wp, f"H{P0+1}:J{PL}", 0)
    wp.data_validation(f"A{P0+1}:A{PL}", {"validate": "custom", "value": f"=COUNTIF($A${P0+1}:$A${PL},A{P0+1})=1",
                                          "error_title": "Código repetido", "error_message": "Este código já existe. Use um código único."})
    wp.freeze_panes(4, 2); wp.autofilter(3, 0, PL - 1, 9)
    bk.define("ProdCod", f"=Produtos!$A${P0+1}:$A${PL}"); bk.define("ProdNome", f"=Produtos!$B${P0+1}:$B${PL}")
    bk.define("ProdCusto", f"=Produtos!$F${P0+1}:$F${PL}")

    # ------------------------------------------------------------- Movimentações
    wm = bk.sheet("Movimentações")
    bk.banner(wm, "Movimentações de estoque", "Entrada = compra/devolução de cliente. Saída = venda/perda/consumo.", 8)
    bk.header(wm, 3, 0, ["Data", "Código", "Tipo", "Quantidade", "Observação (NF, pedido...)", "Produto", "Valor (qtd x custo)", "Alerta"],
              [12, 11, 10, 11, 30, 36, 15, 20], 36)
    for i in range(NM):
        r = M0 + i; x = r + 1
        m = movs[i] if i < len(movs) else (None,) * 5
        bk.w(wm, (r, 0), m[0], bk.fmt("in", nf="date", align="center")); bk.w(wm, (r, 1), m[1], bk.fmt("in"))
        bk.w(wm, (r, 2), m[2], bk.fmt("in", align="center")); bk.w(wm, (r, 3), m[3], fn); bk.w(wm, (r, 4), m[4], fi)
        bk.fx(wm, (r, 5), f'IF($B{x}="","",IFERROR(INDEX(ProdNome,MATCH($B{x},ProdCod,0)),"Código não cadastrado"))', bk.fmt("calc"))
        bk.fx(wm, (r, 6), f'IF(OR($B{x}="",$D{x}=""),"",$D{x}*IFERROR(INDEX(ProdCusto,MATCH($B{x},ProdCod,0)),0))', bk.fmt("calc", nf="money"))
        bk.fx(wm, (r, 7), f'IF($A{x}="","",IF(OR($B{x}="",$C{x}="",$D{x}=""),"Preencher tudo",IF($F{x}="Código não cadastrado","Código inválido","OK")))', bk.fmt("calc", align="center"))
    bk.dv_date(wm, f"A{M0+1}:A{ML}"); bk.dv_list(wm, f"B{M0+1}:B{ML}", "=ProdCod"); bk.dv_list(wm, f"C{M0+1}:C{ML}", ["Entrada", "Saída"])
    bk.dv_num(wm, f"D{M0+1}:D{ML}", 0.0001, None, "Quantidade sempre positiva")
    wm.conditional_format(f"H{M0+1}:H{ML}", {"type": "cell", "criteria": "==", "value": '"OK"', "format": wb.add_format({"font_color": "#15803D", "bold": True})})
    wm.conditional_format(f"H{M0+1}:H{ML}", {"type": "cell", "criteria": "==", "value": '"Código inválido"', "format": wb.add_format({"bg_color": C_REDL, "font_color": C_RED, "bold": True})})
    wm.conditional_format(f"H{M0+1}:H{ML}", {"type": "cell", "criteria": "==", "value": '"Preencher tudo"', "format": wb.add_format({"bg_color": C_AMBERL, "font_color": "#92400E"})})
    wm.freeze_panes(4, 0); wm.autofilter(3, 0, ML - 1, 7)
    for n, c in (("MovData", "A"), ("MovCod", "B"), ("MovTipo", "C"), ("MovQtd", "D")):
        bk.define(n, f"='Movimentações'!${c}${M0+1}:${c}${ML}")

    # ------------------------------------------------------------- Posição
    wp2 = bk.sheet("Posição")
    bk.banner(wp2, "Posição de estoque", "Tudo calculado automaticamente. Filtre a coluna Status para ver o que precisa de ação.", 24)
    heads = ["Código", "Produto", "Categoria", "Unid.", "Estoque inicial", "Entradas", "Saídas", "ESTOQUE ATUAL", "Mínimo", "Máximo", "Custo unit.",
             "Valor em estoque", "Saídas no período", "Média diária", "Cobertura (dias)", "Última saída", "STATUS", "Parado?", "Sugestão de compra (qtd)",
             "Faturamento no período", "Chave ABC", "Classe ABC", "Valor parado", "Seq. compra"]
    wid = [9, 34, 13, 7, 9, 9, 9, 11, 9, 9, 11, 14, 10, 9, 10, 12, 12, 9, 12, 14, 8, 8, 12, 7]
    bk.header(wp2, 3, 0, heads, wid, 44)
    cc = bk.fmt("calc"); ci = bk.fmt("calc", nf="int", align="center"); cm = bk.fmt("calc", nf="money"); cac = bk.fmt("calc", align="center")
    for i in range(NP):
        r = P0 + i; x = r + 1
        R = lambda c: f"Produtos!{c}{x}"
        bk.fx(wp2, (r, 0), f'IF({R("A")}="","",{R("A")})', cc)
        for c, src in ((1, "B"), (2, "C"), (3, "D")):
            bk.fx(wp2, (r, c), f'IF($A{x}="","",{R(src)}&"")', cc if c < 3 else cac)
        bk.fx(wp2, (r, 4), f'IF($A{x}="","",N({R("H")}))', ci)
        bk.fx(wp2, (r, 5), f'IF($A{x}="","",SUMIFS(MovQtd,MovCod,$A{x},MovTipo,"Entrada"))', ci)
        bk.fx(wp2, (r, 6), f'IF($A{x}="","",SUMIFS(MovQtd,MovCod,$A{x},MovTipo,"Saída"))', ci)
        bk.fx(wp2, (r, 7), f'IF($A{x}="","",E{x}+F{x}-G{x})', bk.fmt("calc", nf="int", align="center", bold=True))
        bk.fx(wp2, (r, 8), f'IF($A{x}="","",N({R("I")}))', ci)
        bk.fx(wp2, (r, 9), f'IF($A{x}="","",IF(I{x}>0,ROUNDUP(I{x}*FatMax,0),""))', ci)
        bk.fx(wp2, (r, 10), f'IF($A{x}="","",N({R("F")}))', cm)
        bk.fx(wp2, (r, 11), f'IF($A{x}="","",H{x}*K{x})', cm)
        bk.fx(wp2, (r, 12), f'IF($A{x}="","",SUMIFS(MovQtd,MovCod,$A{x},MovTipo,"Saída",MovData,">="&(Hoje-DiasAn),MovData,"<="&Hoje))', ci)
        bk.fx(wp2, (r, 13), f'IF($A{x}="","",M{x}/DiasAn)', bk.fmt("calc", nf="0.00", align="center"))
        bk.fx(wp2, (r, 14), f'IF($A{x}="","",IF(N{x}>0,H{x}/N{x},"sem giro"))', bk.fmt("calc", nf="0", align="center"))
        bk.fx(wp2, (r, 15), f'IF($A{x}="","",SUMPRODUCT(MAX((MovCod=$A{x})*(MovTipo="Saída")*MovData)))', bk.fmt("calc", nf='dd/mm/yyyy;;"sem saída"', align="center"))
        bk.fx(wp2, (r, 16), f'IF($A{x}="","",IF(H{x}<=0,"RUPTURA",IF(AND(I{x}>0,H{x}<=I{x}),"REPOR",IF(AND(J{x}<>"",H{x}>J{x}),"EXCESSO","OK"))))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wp2, (r, 17), f'IF($A{x}="","",IF(AND(H{x}>0,OR(P{x}=0,Hoje-P{x}>DiasParado)),"Parado",""))', cac)
        bk.fx(wp2, (r, 18), f'IF($A{x}="","",IF(OR(Q{x}="RUPTURA",Q{x}="REPOR"),IF(J{x}="",0,MAX(0,J{x}-H{x})),0))', ci)
        bk.fx(wp2, (r, 19), f'IF($A{x}="","",M{x}*IF(N({R("G")})>0,{R("G")},K{x}))', cm)
        bk.fx(wp2, (r, 20), f'IF($A{x}="","",IF(T{x}>0,T{x}+ROW()/1000000000,""))', bk.fmt("calc", nf="0.00", font_color="#9CA3AF"))
        bk.fx(wp2, (r, 21), f'IF($A{x}="","",IF(U{x}="","C",INDEX(\'Curva ABC\'!$H${P0+1}:$H${PL},MATCH(U{x},\'Curva ABC\'!$B${P0+1}:$B${PL},0))))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wp2, (r, 22), f'IF($A{x}="","",IF(R{x}="Parado",L{x},0))', cm)
        bk.fx(wp2, (r, 23), f'IF($A{x}="","",IF(OR(Q{x}="RUPTURA",Q{x}="REPOR"),COUNTIF($Q${P0+1}:Q{x},"RUPTURA")+COUNTIF($Q${P0+1}:Q{x},"REPOR"),""))', bk.fmt("calc", font_color="#9CA3AF"))
    for t, bg, fg in (("RUPTURA", C_RED, "#FFFFFF"), ("REPOR", C_AMBER, "#FFFFFF"), ("EXCESSO", "#3B82F6", "#FFFFFF"), ("OK", G_LIGHT, "#15803D")):
        wp2.conditional_format(f"Q{P0+1}:Q{PL}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wp2.conditional_format(f"R{P0+1}:R{PL}", {"type": "cell", "criteria": "==", "value": '"Parado"', "format": wb.add_format({"bg_color": "#E5E7EB", "font_color": "#374151", "bold": True})})
    wp2.conditional_format(f"V{P0+1}:V{PL}", {"type": "cell", "criteria": "==", "value": '"A"', "format": wb.add_format({"bg_color": G_LIGHT, "font_color": "#15803D"})})
    wp2.freeze_panes(4, 2); wp2.autofilter(3, 0, PL - 1, 23)
    wp2.set_column(20, 20, None, None, {"hidden": True}); wp2.set_column(23, 23, None, None, {"hidden": True})

    # ------------------------------------------------------------- Curva ABC
    wa = bk.sheet("Curva ABC", onepage=False)
    bk.banner(wa, "Curva ABC", "Ranking automático pelo faturamento do período (saídas x preço de venda). A = poucos itens que dão a maior parte do dinheiro.", 14)
    bk.header(wa, 3, 0, ["Ranking", "Chave", "Código", "Produto", "Faturamento (R$)", "% do total", "% acumulado", "Classe"], [8, 8, 9, 38, 16, 10, 12, 8], 30)
    wa.set_column(1, 1, None, None, {"hidden": True})
    PS = lambda c: f"Posição!${c}${P0+1}:${c}${PL}"
    for k in range(NP):
        r = P0 + k; x = r + 1
        wa.write(r, 0, k + 1, bk.fmt("plain", align="center"))
        bk.fx(wa, (r, 1), f'IFERROR(LARGE({PS("U")},A{x}),"")', cc)
        bk.fx(wa, (r, 2), f'IF(B{x}="","",INDEX({PS("A")},MATCH(B{x},{PS("U")},0)))', cac)
        bk.fx(wa, (r, 3), f'IF(B{x}="","",INDEX({PS("B")},MATCH(B{x},{PS("U")},0)))', cc)
        bk.fx(wa, (r, 4), f'IF(B{x}="","",ROUND(B{x},2))', cm)
        bk.fx(wa, (r, 5), f'IF(E{x}="","",E{x}/SUM($E${P0+1}:$E${PL}))', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wa, (r, 6), f'IF(F{x}="","",SUM($F${P0+1}:F{x}))', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wa, (r, 7), f'IF(F{x}="","",IF(G{x}-F{x}<CorteA,"A",IF(G{x}-F{x}<CorteB,"B","C")))', bk.fmt("calc", align="center", bold=True))
    for t, bg, fg in (("A", G_NEON, "#052e16"), ("B", "#FDE68A", "#78350F"), ("C", "#E5E7EB", "#374151")):
        wa.conditional_format(f"H{P0+1}:H{PL}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    # resumo por classe
    wa.merge_range(3, 9, 3, 12, "Resumo por classe", bk.fmt("h"))
    for j, h in enumerate(["Classe", "Itens", "% dos itens", "% do faturamento"]):
        wa.write(4, 9 + j, h, bk.fmt("h2"))
    wa.set_column(9, 12, 14)
    for j, cl in enumerate("ABC"):
        r = 5 + j; x = r + 1
        wa.write(r, 9, cl, bk.fmt("plain", align="center", bold=True))
        bk.fx(wa, (r, 10), f'COUNTIF($H${P0+1}:$H${PL},J{x})', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wa, (r, 11), f'IFERROR(K{x}/COUNT($E${P0+1}:$E${PL}),0)', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wa, (r, 12), f'IFERROR(SUMIF($H${P0+1}:$H${PL},J{x},$E${P0+1}:$E${PL})/SUM($E${P0+1}:$E${PL}),0)', bk.fmt("calc", nf="pct", align="center"))
    wa.merge_range(9, 9, 12, 12, "Como ler: itens A merecem estoque de segurança e reposição frequente. Itens C (a maioria) vendem pouco: "
                   "compre em pequena quantidade e evite estoque parado.", bk.fmt("note"))
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Faturamento", "categories": f"='Curva ABC'!$D${P0+1}:$D${P0+25}", "values": f"='Curva ABC'!$E${P0+1}:$E${P0+25}", "fill": {"color": G_MID}, "gap": 40})
    ln = wb.add_chart({"type": "line"})
    ln.add_series({"name": "% acumulado", "categories": f"='Curva ABC'!$D${P0+1}:$D${P0+25}", "values": f"='Curva ABC'!$G${P0+1}:$G${P0+25}",
                   "y2_axis": True, "line": {"color": G_DARK, "width": 2.25}, "marker": {"type": "circle", "size": 4}})
    ch.combine(ln)
    ch.set_title({"name": "Pareto: 25 itens que mais faturam", "name_font": {"size": 12}}); ch.set_legend({"position": "bottom"})
    ch.set_x_axis({"num_font": {"rotation": -60, "size": 7}}); ln.set_y2_axis({"num_format": "0%", "max": 1, "min": 0})
    ch.set_size({"width": 620, "height": 360}); wa.insert_chart("J15", ch)
    wa.freeze_panes(4, 0)

    # ------------------------------------------------------------- Compras
    wc = bk.sheet("Compras")
    bk.banner(wc, "Lista de compras sugerida", "Itens em RUPTURA ou REPOR. Quantidade sugerida = estoque máximo - estoque atual.", 11)
    bk.header(wc, 3, 0, ["#", "Código", "Produto", "Fornecedor", "Status", "Estoque atual", "Mínimo", "Comprar (qtd)", "Custo unit.", "Total (R$)", "Prazo (dias)"],
              [5, 9, 36, 22, 11, 10, 9, 11, 11, 14, 9], 32)
    PR = lambda c: f"Produtos!${c}${P0+1}:${c}${PL}"
    for k in range(80):
        r = P0 + k; x = r + 1
        wc.write(r, 0, k + 1, bk.fmt("plain", align="center"))
        idx = f'MATCH($A{x},{PS("X")},0)'
        bk.fx(wc, (r, 1), f'IFERROR(INDEX({PS("A")},{idx}),"")', cac)
        bk.fx(wc, (r, 2), f'IFERROR(INDEX({PS("B")},{idx}),"")', cc)
        bk.fx(wc, (r, 3), f'IFERROR(INDEX({PR("E")},{idx})&"","")', cc)
        bk.fx(wc, (r, 4), f'IFERROR(INDEX({PS("Q")},{idx}),"")', cac)
        bk.fx(wc, (r, 5), f'IFERROR(INDEX({PS("H")},{idx}),"")', ci)
        bk.fx(wc, (r, 6), f'IFERROR(INDEX({PS("I")},{idx}),"")', ci)
        bk.fx(wc, (r, 7), f'IFERROR(INDEX({PS("S")},{idx}),"")', bk.fmt("calc", nf="int", align="center", bold=True))
        bk.fx(wc, (r, 8), f'IFERROR(INDEX({PS("K")},{idx}),"")', cm)
        bk.fx(wc, (r, 9), f'IF(OR(H{x}="",I{x}=""),"",H{x}*I{x})', cm)
        bk.fx(wc, (r, 10), f'IFERROR(N(INDEX({PR("J")},{idx})),"")', ci)
    wc.write(2, 8, "TOTAL:", bk.fmt("lbl", align="right")); bk.fx(wc, (2, 9), f"SUM(J5:J{P0+80})", bk.fmt("tot", nf="money"))
    wc.conditional_format(f"E{P0+1}:E{P0+80}", {"type": "cell", "criteria": "==", "value": '"RUPTURA"', "format": wb.add_format({"bg_color": C_RED, "font_color": "#FFFFFF", "bold": True})})
    wc.conditional_format(f"E{P0+1}:E{P0+80}", {"type": "cell", "criteria": "==", "value": '"REPOR"', "format": wb.add_format({"bg_color": C_AMBER, "font_color": "#FFFFFF", "bold": True})})
    wc.freeze_panes(4, 0)

    # ------------------------------------------------------------- Dashboard
    wd = bk.sheet("Dashboard", tab=G_NEON, onepage=True)
    bk.banner(wd, "Dashboard de estoque", "Visão geral do estoque. Atualiza sozinho.", 10)
    for c in range(10):
        wd.set_column(c, c, 13)
    bk.kpi(wd, 3, 0, "PRODUTOS CADASTRADOS", f'SUMPRODUCT(--({PS("A")}<>""))', "int", 2)
    bk.kpi(wd, 3, 2, "VALOR EM ESTOQUE (custo)", f'SUM({PS("L")})', "money", 2)
    bk.kpi(wd, 3, 4, "EM RUPTURA", f'COUNTIF({PS("Q")},"RUPTURA")', "int", 2, color=C_RED)
    bk.kpi(wd, 3, 6, "PARA REPOR", f'COUNTIF({PS("Q")},"REPOR")', "int", 2, color="#B45309")
    bk.kpi(wd, 3, 8, "EM EXCESSO", f'COUNTIF({PS("Q")},"EXCESSO")', "int", 2, color=C_BLUE)
    bk.kpi(wd, 6, 0, "ITENS PARADOS", f'COUNTIF({PS("R")},"Parado")', "int", 2)
    bk.kpi(wd, 6, 2, "DINHEIRO PARADO", f'SUM({PS("W")})', "money", 2, color=C_RED)
    bk.kpi(wd, 6, 4, "% DO ESTOQUE PARADO", 'IFERROR(C8/C5,0)', "pct", 2)
    bk.kpi(wd, 6, 6, "ITENS CLASSE A", f'COUNTIF({PS("V")},"A")', "int", 2)
    bk.kpi(wd, 6, 8, "COMPRA SUGERIDA (R$)", "Compras!J3", "money", 2)
    wd.merge_range(9, 0, 9, 4, "Situação dos itens", bk.fmt("sec"))
    bk.header(wd, 10, 0, ["Status", "Itens"], height=20)
    for i, st in enumerate(["RUPTURA", "REPOR", "OK", "EXCESSO"]):
        wd.write(11 + i, 0, st, bk.fmt("plain", align="center", bold=True))
        bk.fx(wd, (11 + i, 1), f'COUNTIF({PS("Q")},A{12+i})', bk.fmt("calc", nf="int", align="center"))
    pie = wb.add_chart({"type": "doughnut"})
    pie.add_series({"name": "Situação", "categories": "=Dashboard!$A$12:$A$15", "values": "=Dashboard!$B$12:$B$15",
                    "points": [{"fill": {"color": C_RED}}, {"fill": {"color": C_AMBER}}, {"fill": {"color": G_MID}}, {"fill": {"color": "#3B82F6"}}],
                    "data_labels": {"value": True}})
    pie.set_title({"name": "Situação do estoque", "name_font": {"size": 12}}); pie.set_legend({"position": "right"}); pie.set_size({"width": 400, "height": 280})
    wd.insert_chart("D10", pie)
    ch2 = wb.add_chart({"type": "column"})
    ch2.add_series({"name": "Faturamento", "categories": f"='Curva ABC'!$D${P0+1}:$D${P0+15}", "values": f"='Curva ABC'!$E${P0+1}:$E${P0+15}", "fill": {"color": G_MID}, "gap": 50})
    ch2.set_title({"name": "Top 15 produtos por faturamento", "name_font": {"size": 12}}); ch2.set_legend({"none": True})
    ch2.set_x_axis({"num_font": {"rotation": -60, "size": 7}}); ch2.set_size({"width": 800, "height": 300})
    wd.insert_chart("A27", ch2)
    wd.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
    bk.finish()

    exp = {}
    if bk.sample:
        res = analyze(prods, movs)
        exp[("Dashboard", "A5")] = len(prods)
        exp[("Dashboard", "C5")] = round(sum(r["valor"] for r in res), 2)
        for ref, st in (("E5", "RUPTURA"), ("G5", "REPOR"), ("I5", "EXCESSO")):
            exp[("Dashboard", ref)] = sum(1 for r in res if r["st"] == st)
        exp[("Dashboard", "A8")] = sum(1 for r in res if r["parado"])
        exp[("Dashboard", "C8")] = round(sum(r["valor"] for r in res if r["parado"]), 2)
        exp[("Dashboard", "G8")] = sum(1 for r in res if r["cls"] == "A" and r["fat"] > 0)
        exp[("Dashboard", "I8")] = round(sum(r["sug"] * r["p"]["custo"] for r in res), 2)
        exp[("Posição", "H5")] = res[0]["atual"]
        exp[("Posição", "Q5")] = res[0]["st"]
        top = max(res, key=lambda r: r["fat"])
        exp[("Curva ABC", "C5")] = top["p"]["cod"]
        exp[("Curva ABC", "H5")] = "A"
        # estatísticas para documentação
        exp_info = dict(rupt=exp[("Dashboard", "E5")], repor=exp[("Dashboard", "G5")], exc=exp[("Dashboard", "I5")])
    return exp
