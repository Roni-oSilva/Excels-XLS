# -*- coding: utf-8 -*-
import datetime as dt
import math
import random
from lib import *

SLUG = "ficha-tecnica-cmv"
PASTA = "restaurantes/ficha-tecnica-cmv"
NOME = "Ficha Técnica e CMV para Restaurantes"
NI, NPR, NF, NW = 300, 100, 800, 500
I0 = 4
CMV_META = 0.32
IMP_TAXA = 0.11
MES_REF = dt.date(2026, 9, 1)

UNIDS = ["kg", "g", "L", "ml", "un", "dz", "pct"]
CATS = ["Pratos principais", "Lanches", "Porções", "Sobremesas", "Bebidas", "Entradas"]
MOTIVOS = ["Vencimento", "Erro de preparo", "Sobra de produção", "Queda / quebra", "Devolução do cliente", "Outros"]

# (insumo, unidade, preço da embalagem, qtd na embalagem, fator de correção)
INSUMOS = [
    ("Filé de peito de frango", "kg", 168.0, 5, 1.15), ("Carne moída", "kg", 128.0, 4, 1.05), ("Arroz", "kg", 24.0, 5, 1.0), ("Feijão", "kg", 38.0, 5, 1.0),
    ("Batata", "kg", 45.0, 10, 1.2), ("Queijo mussarela", "kg", 149.0, 3, 1.0), ("Presunto", "kg", 96.0, 3, 1.0), ("Farinha de trigo", "kg", 36.0, 10, 1.0),
    ("Molho de tomate", "kg", 28.0, 5, 1.0), ("Óleo de soja", "L", 62.0, 9, 1.0), ("Ovos", "un", 28.0, 30, 1.0), ("Tomate", "kg", 36.0, 6, 1.1),
    ("Alface", "un", 3.2, 1, 1.3), ("Cebola", "kg", 22.0, 5, 1.1), ("Pão de hambúrguer", "un", 18.0, 6, 1.0), ("Hambúrguer 150g", "un", 54.0, 12, 1.0),
    ("Bacon fatiado", "kg", 98.0, 2, 1.0), ("Macarrão", "kg", 31.0, 5, 1.0), ("Creme de leite", "un", 38.0, 12, 1.0), ("Chocolate em pó", "kg", 42.0, 2, 1.0),
    ("Leite", "L", 56.0, 12, 1.0), ("Açúcar", "kg", 21.0, 5, 1.0), ("Refrigerante lata", "un", 36.0, 12, 1.0), ("Polpa de fruta", "kg", 62.0, 5, 1.0),
    ("Cerveja long neck", "un", 98.0, 24, 1.0), ("Calabresa", "kg", 74.0, 3, 1.05),
]
# prato, categoria, rendimento, preço, qtd vendida, [(insumo, qtd líquida)]
PRATOS = [
    ("Prato do dia (frango grelhado)", "Pratos principais", 1, 32.9, 620, [("Filé de peito de frango", 0.18), ("Arroz", 0.12), ("Feijão", 0.08), ("Batata", 0.15), ("Tomate", 0.05), ("Alface", 0.2), ("Óleo de soja", 0.02)]),
    ("Hambúrguer artesanal", "Lanches", 1, 29.9, 540, [("Pão de hambúrguer", 1), ("Hambúrguer 150g", 1), ("Queijo mussarela", 0.04), ("Tomate", 0.03), ("Alface", 0.1), ("Cebola", 0.02)]),
    ("Hambúrguer bacon", "Lanches", 1, 34.9, 410, [("Pão de hambúrguer", 1), ("Hambúrguer 150g", 1), ("Queijo mussarela", 0.04), ("Bacon fatiado", 0.04), ("Cebola", 0.02)]),
    ("Porção de batata frita", "Porções", 1, 18.9, 380, [("Batata", 0.5), ("Óleo de soja", 0.08)]),
    ("Macarrão à calabresa", "Pratos principais", 1, 24.9, 260, [("Macarrão", 0.13), ("Molho de tomate", 0.12), ("Queijo mussarela", 0.05), ("Calabresa", 0.04), ("Cebola", 0.02)]),
    ("Lasanha de presunto e queijo", "Pratos principais", 1, 36.9, 210, [("Macarrão", 0.1), ("Presunto", 0.08), ("Queijo mussarela", 0.1), ("Molho de tomate", 0.15), ("Creme de leite", 0.1)]),
    ("Omelete de queijo", "Pratos principais", 1, 22.9, 140, [("Ovos", 3), ("Queijo mussarela", 0.05), ("Óleo de soja", 0.01)]),
    ("Salada da casa", "Entradas", 1, 19.9, 180, [("Alface", 0.5), ("Tomate", 0.1), ("Cebola", 0.03), ("Presunto", 0.04)]),
    ("Pudim de leite", "Sobremesas", 8, 14.9, 300, [("Leite", 1.0), ("Ovos", 6), ("Açúcar", 0.4), ("Creme de leite", 1)]),
    ("Mousse de chocolate", "Sobremesas", 6, 13.9, 220, [("Chocolate em pó", 0.3), ("Creme de leite", 3), ("Açúcar", 0.15), ("Ovos", 3)]),
    ("Refrigerante lata", "Bebidas", 1, 6.9, 900, [("Refrigerante lata", 1)]),
    ("Suco natural 400ml", "Bebidas", 1, 9.9, 450, [("Polpa de fruta", 0.2), ("Açúcar", 0.02)]),
    ("Cerveja long neck", "Bebidas", 1, 12.9, 380, [("Cerveja long neck", 1)]),
    ("Pizza de calabresa (individual)", "Pratos principais", 1, 31.9, 150, [("Farinha de trigo", 0.15), ("Queijo mussarela", 0.12), ("Calabresa", 0.1), ("Molho de tomate", 0.08), ("Cebola", 0.03)]),
]


def psych(x):
    c = math.ceil(x)
    return c - 0.1 if c - 0.1 >= x else c + 0.9


def compute():
    ins = {n: dict(un=u, preco=p, q=q, fc=fc, bruto=p / q, util=p / q * fc) for (n, u, p, q, fc) in INSUMOS}
    pr = []
    for (nome, cat, rend, preco, qtd, itens) in PRATOS:
        custo = sum(q * ins[i]["util"] for i, q in itens)
        cpp = custo / rend
        cmv = cpp / preco
        mc = preco - cpp - preco * IMP_TAXA
        pr.append(dict(nome=nome, cat=cat, rend=rend, preco=preco, qtd=qtd, itens=itens, custo=custo, cpp=cpp, cmv=cmv,
                       sug=psych(cpp / CMV_META), mc=mc, lucro=mc * qtd))
    tot = sum(p["qtd"] for p in pr)
    npr = sum(1 for p in pr if p["qtd"] > 0)
    mcmed = sum(p["mc"] * p["qtd"] for p in pr) / tot
    for p in pr:
        mix = p["qtd"] / tot
        pop = mix >= 0.7 / npr
        hi = p["mc"] >= mcmed
        p["mix"] = mix
        p["cls"] = ("Estrela" if hi else "Burro de carga") if pop else ("Quebra-cabeça" if hi else "Cão")
        p["status"] = "ACIMA DA META" if p["cmv"] > CMV_META else "OK"
    return ins, pr, mcmed


def sample_months(teor_sep):
    rnd = random.Random(707)
    rows = []
    ei = 14500.0
    for m in range(1, 10):
        rec = round(rnd.uniform(96000, 118000), 2)
        pct = rnd.uniform(0.328, 0.372)
        if m == 9:
            rec = round(sum(p["preco"] * p["qtd"] for p in compute()[1]) * 1.03, 2)
            pct = teor_sep / rec + 0.034          # real ~3,4 pp acima do teórico
        cmv = round(rec * pct, 2)
        comp = round(cmv + rnd.uniform(-800, 1200), 2)
        ef = round(ei + comp - cmv, 2)
        rows.append((ei, comp, ef, rec))
        ei = ef
    return rows


def sample_waste():
    rnd = random.Random(808)
    rows = []
    for m, n in ((7, 22), (8, 26), (9, 34)):
        for _ in range(n):
            ins = rnd.choice(["Filé de peito de frango", "Batata", "Alface", "Tomate", "Queijo mussarela", "Carne moída", "Leite", "Pão de hambúrguer", "Ovos", "Hambúrguer 150g"])
            un = {i[0]: i[1] for i in INSUMOS}[ins]
            q = round(rnd.uniform(0.2, 2.2), 2) if un in ("kg", "L") else float(rnd.randint(1, 8))
            rows.append((dt.date(2026, m, rnd.randint(1, 28)), ins, q, rnd.choices(MOTIVOS, weights=[28, 20, 28, 8, 8, 8])[0], None))
    rows.sort(key=lambda r: r[0])
    return rows


def build(bk: Book):
    wb = bk.wb
    ins, pr, mcmed = compute()
    teor_sep = sum(p["cpp"] * p["qtd"] for p in pr)
    bk.inicio(
        "Ficha Técnica e CMV", "Carvex XLS · Saiba quanto custa cada prato e onde seu dinheiro está sumindo",
        "Cadastre seus insumos e monte a ficha técnica de cada prato. A planilha calcula o custo por porção, o CMV de cada prato, o preço sugerido para "
        "atingir sua meta, classifica o cardápio (estrela, burro de carga, quebra-cabeça e cão) e compara o CMV real do mês com o CMV teórico.",
        [("Config", "Informe a meta de CMV (ex.: 32%), impostos e taxas sobre a venda e o mês de referência."),
         ("Cadastre os insumos", "Em Insumos: preço da embalagem, quantidade que vem nela e o fator de correção (perda na limpeza, quando houver)."),
         ("Cadastre os pratos", "Em Pratos: nome, rendimento (porções), preço de venda e quantidade vendida no mês."),
         ("Monte as fichas", "Em Fichas: para cada prato, liste os insumos e a quantidade LÍQUIDA que vai em 1 receita."),
         ("Feche o mês", "Em CMV Mensal, informe estoque inicial, compras, estoque final e receita. Compare com o CMV teórico e registre o desperdício.")],
        [("Config", "Meta de CMV, impostos/taxas, mês de referência e listas."), ("Insumos", "Preço e custo útil de cada ingrediente."),
         ("Pratos", "Custo, CMV, preço sugerido e classificação de cada prato."), ("Fichas", "Receitas: insumos e quantidades de cada prato."),
         ("CMV Mensal", "CMV real x teórico e perdas por mês."), ("Desperdício", "Registro diário de perdas por motivo."),
         ("Dashboard", "Indicadores, piores pratos e gráficos.")],
        avisos=["Use SEMPRE a mesma unidade do insumo na ficha (se o insumo é em kg, informe 0,150 para 150 g).",
                "Fator de correção = peso bruto / peso líquido. Ex.: 1 kg de frango rende 870 g limpos: FC = 1,15. Sem perda, deixe 1.",
                "CMV real = (estoque inicial + compras - estoque final) / receita. Faça contagem física do estoque no 1º dia do mês."])

    ws = bk.sheet("Config")
    bk.banner(ws, "Configurações", "Preencha as células amarelas.", 8)
    ws.set_column(0, 0, 3); ws.set_column(1, 1, 40); ws.set_column(2, 2, 16); ws.set_column(3, 3, 3); ws.set_column(4, 6, 24)
    lf = bk.fmt("lbl")
    ws.write(3, 1, "Restaurante", lf); bk.w(ws, (3, 2), "Restaurante Exemplo" if bk.sample else None, bk.fmt("in"))
    ws.write(4, 1, "Meta de CMV (% da venda)", lf); bk.w(ws, (4, 2), CMV_META if bk.sample else 0.32, bk.fmt("in", nf="pct", align="center"))
    ws.write(5, 1, "Impostos + taxas sobre a venda (%)", lf); bk.w(ws, (5, 2), IMP_TAXA if bk.sample else None, bk.fmt("in", nf="pct", align="center"))
    ws.write(6, 1, "Mês de referência (1º dia do mês)", lf); bk.w(ws, (6, 2), MES_REF if bk.sample else None, bk.fmt("in", nf="date", align="center"))
    ws.write(7, 1, "Ano do CMV mensal", lf); bk.w(ws, (7, 2), 2026 if bk.sample else dt.date.today().year, bk.fmt("in", nf="0", align="center"))
    bk.dv_num(ws, "C5:C6", 0, 0.95); bk.dv_date(ws, "C7", "Use o dia 1 do mês que deseja analisar"); bk.dv_num(ws, "C8", 2000, 2100, integer=True)
    ws.write(8, 1, "Dica: CMV saudável costuma ficar entre 25% e 40% do faturamento, conforme o tipo de operação.", bk.fmt("note"))
    for n, a in (("CMVMeta", "C5"), ("ImpTaxa", "C6"), ("MesRef", "C7"), ("Ano", "C8")):
        bk.define(n, f"=Config!${a[0]}${a[1:]}")
    ws.write(3, 4, "Unidades", bk.fmt("h")); ws.write(3, 5, "Categorias de prato", bk.fmt("h")); ws.write(3, 6, "Motivos de desperdício", bk.fmt("h"))
    for i in range(12):
        bk.w(ws, (4 + i, 4), UNIDS[i] if i < len(UNIDS) else None, bk.fmt("in")); bk.w(ws, (4 + i, 5), CATS[i] if i < len(CATS) else None, bk.fmt("in"))
        bk.w(ws, (4 + i, 6), MOTIVOS[i] if i < len(MOTIVOS) else None, bk.fmt("in"))
    bk.define("Unidades", "=Config!$E$5:$E$16"); bk.define("CatPrato", "=Config!$F$5:$F$16"); bk.define("Motivos", "=Config!$G$5:$G$16")

    # ---------------- Insumos
    wi = bk.sheet("Insumos")
    bk.banner(wi, "Insumos (ingredientes)", "Atualize o preço sempre que o fornecedor reajustar: todas as fichas recalculam sozinhas.", 9)
    bk.header(wi, 3, 0, ["Código", "Insumo", "Unidade", "Preço da embalagem (R$)", "Qtd na embalagem", "Fator de correção (FC)", "Custo por unidade (bruto)", "Custo por unidade ÚTIL", "Atualizado em"],
              [8, 34, 9, 14, 12, 12, 14, 14, 12], 44)
    fi = bk.fmt("in")
    for i in range(NI):
        r = I0 + i; x = r + 1
        d = INSUMOS[i] if (bk.sample and i < len(INSUMOS)) else None
        bk.w(wi, (r, 0), f"I{i+1:03d}" if d else None, fi); bk.w(wi, (r, 1), d[0] if d else None, fi); bk.w(wi, (r, 2), d[1] if d else None, bk.fmt("in", align="center"))
        bk.w(wi, (r, 3), d[2] if d else None, bk.fmt("in", nf="money")); bk.w(wi, (r, 4), d[3] if d else None, bk.fmt("in", nf="#,##0.###"))
        bk.w(wi, (r, 5), d[4] if d else None, bk.fmt("in", nf="0.00", align="center")); bk.w(wi, (r, 8), REF_DATE if d else None, bk.fmt("in", nf="date", align="center"))
        bk.fx(wi, (r, 6), f'IF(OR($B{x}="",$D{x}="",N($E{x})<=0),"",$D{x}/$E{x})', bk.fmt("calc", nf='"R$" #,##0.0000'))
        bk.fx(wi, (r, 7), f'IF($G{x}="","",$G{x}*IF($F{x}="",1,$F{x}))', bk.fmt("calc", nf='"R$" #,##0.0000', bold=True))
    bk.dv_list(wi, f"C{I0+1}:C{I0+NI}", "=Unidades"); bk.dv_num(wi, f"D{I0+1}:E{I0+NI}", 0); bk.dv_num(wi, f"F{I0+1}:F{I0+NI}", 1, 5, "FC mínimo 1 (sem perda)")
    wi.freeze_panes(4, 2); wi.autofilter(3, 0, I0 + NI - 1, 8)
    ie = I0 + NI
    for n, c in (("InsNome", "B"), ("InsUnid", "C"), ("InsBruto", "G"), ("InsUtil", "H")):
        bk.define(n, f"=Insumos!${c}${I0+1}:${c}${ie}")

    # ---------------- Fichas
    wf = bk.sheet("Fichas")
    bk.banner(wf, "Fichas técnicas (receitas)", "Uma linha por insumo de cada prato. Quantidade LÍQUIDA, na unidade do insumo.", 8)
    bk.header(wf, 3, 0, ["Prato", "Insumo", "Quantidade na receita", "Observação", "Unidade", "Custo útil unitário", "Custo do item", "Conferência"], [34, 30, 13, 22, 9, 14, 13, 20], 36)
    frows = [(p["nome"], i, q) for p in pr for (i, q) in p["itens"]] if bk.sample else []
    for i in range(NF):
        r = I0 + i; x = r + 1
        d = frows[i] if i < len(frows) else (None, None, None)
        bk.w(wf, (r, 0), d[0], fi); bk.w(wf, (r, 1), d[1], fi); bk.w(wf, (r, 2), d[2], bk.fmt("in", nf="#,##0.###")); bk.w(wf, (r, 3), None, fi)
        bk.fx(wf, (r, 4), f'IF($B{x}="","",IFERROR(INDEX(InsUnid,MATCH($B{x},InsNome,0)),""))', bk.fmt("calc", align="center"))
        bk.fx(wf, (r, 5), f'IF($B{x}="","",IFERROR(INDEX(InsUtil,MATCH($B{x},InsNome,0)),""))', bk.fmt("calc", nf='"R$" #,##0.0000'))
        bk.fx(wf, (r, 6), f'IF(OR($A{x}="",$C{x}="",$F{x}=""),"",$C{x}*$F{x})', bk.fmt("calc", nf="money"))
        bk.fx(wf, (r, 7), f'IF($A{x}="","",IF($B{x}="","Escolha o insumo",IF($F{x}="","Insumo sem custo",IF(COUNTIF(PratoNome,$A{x})=0,"Prato não cadastrado",IF($C{x}="","Falta quantidade","OK")))))', bk.fmt("calc", align="center"))
    fe = I0 + NF
    bk.dv_list(wf, f"A{I0+1}:A{fe}", "=PratoNome"); bk.dv_list(wf, f"B{I0+1}:B{fe}", "=InsNome"); bk.dv_num(wf, f"C{I0+1}:C{fe}", 0)
    wf.conditional_format(f"H{I0+1}:H{fe}", {"type": "cell", "criteria": "!=", "value": '"OK"', "format": wb.add_format({"font_color": C_RED, "bold": True})})
    wf.freeze_panes(4, 1); wf.autofilter(3, 0, fe - 1, 7)

    # ---------------- Pratos
    wp = bk.sheet("Pratos")
    bk.banner(wp, "Pratos: custo, CMV e engenharia de cardápio", "Preencha as colunas amarelas. O custo vem das fichas.", 16)
    bk.header(wp, 3, 0, ["Prato", "Categoria", "Rendimento (porções)", "Preço de venda (R$)", "Qtd vendida no mês", "Custo total da receita", "CUSTO POR PORÇÃO", "CMV %", "Status vs meta",
                         "Preço sugerido (pela meta)", "Margem de contribuição (R$)", "Lucro total no mês", "Mix de vendas", "Classe do cardápio", "O que fazer", "Chave"],
              [34, 16, 11, 12, 11, 13, 13, 9, 15, 13, 13, 13, 9, 16, 30, 8], 48)
    pe = I0 + NPR
    for i in range(NPR):
        r = I0 + i; x = r + 1
        p = pr[i] if (bk.sample and i < len(pr)) else None
        bk.w(wp, (r, 0), p["nome"] if p else None, fi); bk.w(wp, (r, 1), p["cat"] if p else None, fi)
        bk.w(wp, (r, 2), p["rend"] if p else None, bk.fmt("in", nf="0", align="center")); bk.w(wp, (r, 3), p["preco"] if p else None, bk.fmt("in", nf="money"))
        bk.w(wp, (r, 4), p["qtd"] if p else None, bk.fmt("in", nf="int", align="center"))
        bk.fx(wp, (r, 5), f'IF($A{x}="","",SUMIFS(Fichas!$G${I0+1}:$G${fe},Fichas!$A${I0+1}:$A${fe},$A{x}))', bk.fmt("calc", nf="money"))
        bk.fx(wp, (r, 6), f'IF(OR($A{x}="",N($F{x})=0),"",$F{x}/IF(N($C{x})>0,$C{x},1))', bk.fmt("calc", nf="money", bold=True, bg_color=G_LIGHT))
        bk.fx(wp, (r, 7), f'IF(OR($G{x}="",N($D{x})<=0),"",$G{x}/$D{x})', bk.fmt("calc", nf="pct", align="center", bold=True))
        bk.fx(wp, (r, 8), f'IF($A{x}="","",IF($G{x}="","Sem ficha",IF($H{x}="","Sem preço",IF($H{x}>CMVMeta,"ACIMA DA META","OK"))))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wp, (r, 9), f'IF($G{x}="","",ROUNDUP($G{x}/CMVMeta,0)+IF(ROUNDUP($G{x}/CMVMeta,0)-0.1>=$G{x}/CMVMeta,-0.1,0.9))', bk.fmt("calc", nf="money"))
        bk.fx(wp, (r, 10), f'IF(OR($G{x}="",N($D{x})<=0),"",$D{x}-$G{x}-$D{x}*ImpTaxa)', bk.fmt("calc", nf="money"))
        bk.fx(wp, (r, 11), f'IF(OR($K{x}="",N($E{x})<=0),"",$K{x}*$E{x})', bk.fmt("calc", nf="money"))
        bk.fx(wp, (r, 12), f'IF(OR($A{x}="",N($E{x})<=0),"",$E{x}/SUM($E${I0+1}:$E${pe}))', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wp, (r, 13), f'IF(OR($M{x}="",$K{x}=""),"",IF($M{x}>=0.7/NPratos,IF($K{x}>=MCmed,"Estrela","Burro de carga"),IF($K{x}>=MCmed,"Quebra-cabeça","Cão")))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wp, (r, 14), f'IF($N{x}="","",IF($N{x}="Estrela","Manter e destacar no cardápio",IF($N{x}="Burro de carga","Subir preço ou reduzir custo",IF($N{x}="Quebra-cabeça","Divulgar e sugerir ao cliente","Reformular ou retirar"))))', bk.fmt("calc"))
        bk.fx(wp, (r, 15), f'IF($H{x}="","",$H{x}+ROW()/1000000000)', bk.fmt("calc", nf="0.0000", font_color="#9CA3AF"))
    bk.dv_list(wp, f"B{I0+1}:B{pe}", "=CatPrato"); bk.dv_num(wp, f"C{I0+1}:C{pe}", 1); bk.dv_num(wp, f"D{I0+1}:E{pe}", 0)
    for t, bg, fg in (("ACIMA DA META", C_RED, "#FFFFFF"), ("OK", G_LIGHT, "#15803D"), ("Sem ficha", C_AMBERL, "#92400E")):
        wp.conditional_format(f"I{I0+1}:I{pe}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    for t, bg, fg in (("Estrela", G_NEON, "#052e16"), ("Burro de carga", "#FDE68A", "#78350F"), ("Quebra-cabeça", "#BFDBFE", "#1E3A8A"), ("Cão", "#FECACA", "#7F1D1D")):
        wp.conditional_format(f"N{I0+1}:N{pe}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wp.freeze_panes(4, 1); wp.autofilter(3, 0, pe - 1, 15)
    wp.set_column(15, 15, None, None, {"hidden": True})
    bk.define("PratoNome", f"=Pratos!$A${I0+1}:$A${pe}"); bk.define("PratoCusto", f"=Pratos!$G${I0+1}:$G${pe}"); bk.define("PratoQtd", f"=Pratos!$E${I0+1}:$E${pe}")
    wk = bk.sheet("Calc", tab="#999999")
    wk.write(0, 0, "NPratos"); bk.fx(wk, "B1", f'SUMPRODUCT(--(Pratos!$E${I0+1}:$E${pe}>0),--ISNUMBER(Pratos!$G${I0+1}:$G${pe}))')
    wk.write(1, 0, "MCmed"); bk.fx(wk, "B2", f'IFERROR(SUMPRODUCT(Pratos!$K${I0+1}:$K${pe},Pratos!$E${I0+1}:$E${pe})/SUMPRODUCT(--ISNUMBER(Pratos!$K${I0+1}:$K${pe}),Pratos!$E${I0+1}:$E${pe}),0)')
    bk.define("NPratos", "=Calc!$B$1"); bk.define("MCmed", "=Calc!$B$2")
    wk.hide()

    # ---------------- Desperdício
    ww = bk.sheet("Desperdício")
    bk.banner(ww, "Registro de desperdício", "Anote toda perda: o que não é medido não é controlado.", 8)
    bk.header(ww, 3, 0, ["Data", "Insumo", "Quantidade", "Motivo", "Observação", "Unidade", "Custo da perda (R$)", "Mês"], [12, 32, 11, 22, 24, 9, 15, 10], 32)
    wrows = sample_waste() if bk.sample else []
    for i in range(NW):
        r = I0 + i; x = r + 1
        d = wrows[i] if i < len(wrows) else (None,) * 5
        bk.w(ww, (r, 0), d[0], bk.fmt("in", nf="date", align="center")); bk.w(ww, (r, 1), d[1], fi); bk.w(ww, (r, 2), d[2], bk.fmt("in", nf="#,##0.###"))
        bk.w(ww, (r, 3), d[3], fi); bk.w(ww, (r, 4), d[4], fi)
        bk.fx(ww, (r, 5), f'IF($B{x}="","",IFERROR(INDEX(InsUnid,MATCH($B{x},InsNome,0)),""))', bk.fmt("calc", align="center"))
        bk.fx(ww, (r, 6), f'IF(OR($B{x}="",$C{x}=""),"",$C{x}*IFERROR(INDEX(InsBruto,MATCH($B{x},InsNome,0)),0))', bk.fmt("calc", nf="money"))
        bk.fx(ww, (r, 7), f'IF($A{x}="","",DATE(YEAR($A{x}),MONTH($A{x}),1))', bk.fmt("calc", nf="mon", align="center"))
    we = I0 + NW
    bk.dv_date(ww, f"A{I0+1}:A{we}"); bk.dv_list(ww, f"B{I0+1}:B{we}", "=InsNome"); bk.dv_list(ww, f"D{I0+1}:D{we}", "=Motivos"); bk.dv_num(ww, f"C{I0+1}:C{we}", 0)
    ww.freeze_panes(4, 0); ww.autofilter(3, 0, we - 1, 7)
    WR = lambda c: f"'Desperdício'!${c}${I0+1}:${c}${we}"

    # ---------------- CMV Mensal
    wm = bk.sheet("CMV Mensal", onepage=True)
    bk.banner(wm, "CMV mensal: real x teórico", "CMV real = estoque inicial + compras - estoque final. Teórico = o que as fichas dizem que deveria ter custado.", 14)
    bk.header(wm, 3, 0, ["Mês", "Estoque inicial (R$)", "Compras do mês (R$)", "Estoque final (R$)", "Receita de vendas (R$)", "CMV REAL (R$)", "CMV real %", "CMV teórico (R$)", "CMV teórico %",
                         "Diferença (R$)", "Diferença (pontos %)", "Perdas registradas (R$)", "Perda sem explicação (R$)", "Situação"],
              [10, 14, 14, 14, 15, 14, 10, 14, 11, 13, 12, 14, 15, 24], 48)
    mrows = sample_months(teor_sep) if bk.sample else []
    for m in range(12):
        r = 4 + m; x = r + 1
        d = mrows[m] if m < len(mrows) else (None,) * 4
        bk.fx(wm, (r, 0), f"DATE(Ano,{m+1},1)", bk.fmt("calc", nf="mon", align="center", bold=True))
        for c in range(4):
            bk.w(wm, (r, 1 + c), d[c], bk.fmt("in", nf="money"))
        bk.fx(wm, (r, 5), f'IF(OR($C{x}="",$E{x}=""),"",N($B{x})+$C{x}-N($D{x}))', bk.fmt("calc", nf="money", bold=True))
        bk.fx(wm, (r, 6), f'IF(OR($F{x}="",N($E{x})<=0),"",$F{x}/$E{x})', bk.fmt("calc", nf="pct", align="center", bold=True))
        bk.fx(wm, (r, 7), f'IF(AND(ISNUMBER(MesRef),$A{x}=MesRef),SUMPRODUCT(PratoCusto,PratoQtd),"")', bk.fmt("calc", nf="money"))
        bk.fx(wm, (r, 8), f'IF(OR($H{x}="",N($E{x})<=0),"",$H{x}/$E{x})', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wm, (r, 9), f'IF(OR($F{x}="",$H{x}=""),"",$F{x}-$H{x})', bk.fmt("calc", nf="money"))
        bk.fx(wm, (r, 10), f'IF(OR($G{x}="",$I{x}=""),"",$G{x}-$I{x})', bk.fmt("calc", nf="0.0%", align="center"))
        bk.fx(wm, (r, 11), f'SUMIFS({WR("G")},{WR("H")},$A{x})', bk.fmt("calc", nf="money"))
        bk.fx(wm, (r, 12), f'IF($J{x}="","",$J{x}-$L{x})', bk.fmt("calc", nf="money"))
        bk.fx(wm, (r, 13), f'IF($G{x}="","",IF($G{x}>CMVMeta+0.03,"CMV MUITO ALTO",IF($G{x}>CMVMeta,"Acima da meta","Dentro da meta")))', bk.fmt("calc", align="center", bold=True))
    for t, bg, fg in (("CMV MUITO ALTO", C_RED, "#FFFFFF"), ("Acima da meta", C_AMBERL, "#92400E"), ("Dentro da meta", G_LIGHT, "#15803D")):
        wm.conditional_format("N5:N16", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wm.write(17, 0, "Meta", bk.fmt("lbl"))
    for m in range(12):
        bk.fx(wm, (17, 1 + m), "CMVMeta", bk.fmt("calc", nf="pct0", align="center", font_color="#9CA3AF"))
    wm.write(17, 0, "Meta CMV", bk.fmt("note"))
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "CMV real %", "categories": "='CMV Mensal'!$A$5:$A$16", "values": "='CMV Mensal'!$G$5:$G$16", "fill": {"color": G_MID}, "gap": 60, "data_labels": {"value": True, "num_format": "0%"}})
    ln = wb.add_chart({"type": "line"})
    ln.add_series({"name": "Meta", "categories": "='CMV Mensal'!$A$5:$A$16", "values": "='CMV Mensal'!$B$18:$M$18", "line": {"color": "#EF4444", "dash_type": "dash", "width": 2}})
    ch.combine(ln); ch.set_title({"name": "CMV real por mês x meta", "name_font": {"size": 12}}); ch.set_legend({"position": "bottom"}); ch.set_x_axis({"num_format": "mmm"}); ch.set_y_axis({"num_format": "0%", "min": 0})
    ch.set_size({"width": 760, "height": 300}); wm.insert_chart("A20", ch)
    wm.freeze_panes(4, 1)

    # ---------------- Dashboard
    wd = bk.sheet("Dashboard", tab=G_NEON, onepage=True)
    bk.banner(wd, "Dashboard do restaurante", "Resultado do mês de referência (Config) e saúde do cardápio.", 10)
    for c in range(10):
        wd.set_column(c, c, 14)
    ix = 'MONTH(MesRef)'
    bk.kpi(wd, 3, 0, "CMV REAL (mês ref.)", f"IFERROR(INDEX('CMV Mensal'!$G$5:$G$16,{ix}),0)", "pct", 2, color="#B45309")
    bk.kpi(wd, 3, 2, "CMV TEÓRICO (fichas)", f"IFERROR(INDEX('CMV Mensal'!$I$5:$I$16,{ix}),0)", "pct", 2)
    bk.kpi(wd, 3, 4, "META DE CMV", "CMVMeta", "pct", 2)
    bk.kpi(wd, 3, 6, "PERDA ACIMA DO TEÓRICO (pontos)", f"IFERROR(INDEX('CMV Mensal'!$K$5:$K$16,{ix}),0)", "0.0%", 2, color=C_RED)
    bk.kpi(wd, 3, 8, "PERDAS REGISTRADAS (R$)", f"IFERROR(INDEX('CMV Mensal'!$L$5:$L$16,{ix}),0)", "money", 2)
    bk.kpi(wd, 6, 0, "PRATOS ACIMA DA META", f'COUNTIF(Pratos!$I${I0+1}:$I${pe},"ACIMA DA META")', "int", 2, color=C_RED)
    bk.kpi(wd, 6, 2, "PRATOS ESTRELA", f'COUNTIF(Pratos!$N${I0+1}:$N${pe},"Estrela")', "int", 2)
    bk.kpi(wd, 6, 4, "PRATOS CÃO", f'COUNTIF(Pratos!$N${I0+1}:$N${pe},"Cão")', "int", 2)
    bk.kpi(wd, 6, 6, "MARGEM DE CONTRIB. NO MÊS", f"SUM(Pratos!$L${I0+1}:$L${pe})", "money", 2)
    bk.kpi(wd, 6, 8, "PERDA SEM EXPLICAÇÃO (R$)", f"IFERROR(INDEX('CMV Mensal'!$M$5:$M$16,{ix}),0)", "money", 2, color=C_RED)
    wd.merge_range(9, 0, 9, 9, "Os 5 pratos com pior CMV", bk.fmt("sec"))
    bk.header(wd, 10, 0, ["#", "Prato", "", "", "CMV %", "Custo por porção", "Preço atual", "Preço sugerido", "Classe"], height=24)
    wd.merge_range(10, 1, 10, 3, "Prato", bk.fmt("h"))
    PR_ = lambda c: f"Pratos!${c}${I0+1}:${c}${pe}"
    for k in range(1, 6):
        r = 10 + k; x = r + 1
        wd.write(r, 0, k, bk.fmt("plain", align="center"))
        bk.fx(wd, (r, 10), f'IFERROR(LARGE({PR_("P")},{k}),"")', bk.fmt("calc", font_color="#FFFFFF"))
        mt = f"MATCH($K{x},{PR_('P')},0)"
        wd.merge_range(r, 1, r, 3, "", bk.fmt("calc")); bk.fx(wd, (r, 1), f'IF($K{x}="","",INDEX({PR_("A")},{mt}))', bk.fmt("calc"))
        bk.fx(wd, (r, 4), f'IF($K{x}="","",INDEX({PR_("H")},{mt}))', bk.fmt("calc", nf="pct", align="center", bold=True))
        bk.fx(wd, (r, 5), f'IF($K{x}="","",INDEX({PR_("G")},{mt}))', bk.fmt("calc", nf="money"))
        bk.fx(wd, (r, 6), f'IF($K{x}="","",INDEX({PR_("D")},{mt}))', bk.fmt("calc", nf="money"))
        bk.fx(wd, (r, 7), f'IF($K{x}="","",INDEX({PR_("J")},{mt}))', bk.fmt("calc", nf="money", bold=True))
        bk.fx(wd, (r, 8), f'IF($K{x}="","",INDEX({PR_("N")},{mt}))', bk.fmt("calc", align="center"))
    wd.set_column(10, 10, None, None, {"hidden": True})
    wd.merge_range(17, 0, 17, 3, "Cardápio por classe", bk.fmt("sec"))
    bk.header(wd, 18, 0, ["Classe", "Pratos"], height=20)
    for i, c in enumerate(["Estrela", "Burro de carga", "Quebra-cabeça", "Cão"]):
        wd.write(19 + i, 0, c, bk.fmt("plain", bold=True)); bk.fx(wd, (19 + i, 1), f'COUNTIF({PR_("N")},A{20+i})', bk.fmt("calc", nf="int", align="center"))
    wd.merge_range(17, 5, 17, 9, "Desperdício por motivo (mês de referência)", bk.fmt("sec"))
    wd.write(18, 5, "Motivo", bk.fmt("h")); wd.merge_range(18, 5, 18, 7, "Motivo", bk.fmt("h")); wd.merge_range(18, 8, 18, 9, "Custo (R$)", bk.fmt("h"))
    for i in range(6):
        r = 19 + i
        wd.merge_range(r, 5, r, 7, "", bk.fmt("calc")); bk.fx(wd, (r, 5), f'IF(INDEX(Motivos,{i+1})="","",INDEX(Motivos,{i+1}))', bk.fmt("calc"))
        wd.merge_range(r, 8, r, 9, "", bk.fmt("calc", nf="money")); bk.fx(wd, (r, 8), f'IF($F{r+1}="","",SUMIFS({WR("G")},{WR("D")},$F{r+1},{WR("H")},MesRef))', bk.fmt("calc", nf="money"))
    c1 = wb.add_chart({"type": "bar"})
    c1.add_series({"name": "Custo", "categories": "=Dashboard!$F$20:$F$25", "values": "=Dashboard!$I$20:$I$25", "fill": {"color": "#F87171"}, "data_labels": {"value": True, "num_format": "#,##0"}})
    c1.set_title({"name": "Perdas por motivo", "name_font": {"size": 12}}); c1.set_legend({"none": True}); c1.set_y_axis({"reverse": True}); c1.set_size({"width": 470, "height": 250})
    wd.insert_chart("F27", c1)
    c2 = wb.add_chart({"type": "column"})
    c2.add_series({"name": "Pratos", "categories": "=Dashboard!$A$20:$A$23", "values": "=Dashboard!$B$20:$B$23",
                   "points": [{"fill": {"color": G_NEON}}, {"fill": {"color": "#FCD34D"}}, {"fill": {"color": "#93C5FD"}}, {"fill": {"color": "#FCA5A5"}}], "data_labels": {"value": True}})
    c2.set_title({"name": "Engenharia de cardápio", "name_font": {"size": 12}}); c2.set_legend({"none": True}); c2.set_size({"width": 400, "height": 250})
    wd.insert_chart("A27", c2)
    wd.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
    bk.finish()

    exp = {}
    if bk.sample:
        tot_real = None
        exp[("Pratos", "G5")] = round(pr[0]["cpp"], 4); exp[("Pratos", "H5")] = round(pr[0]["cmv"], 4)
        exp[("Pratos", "J5")] = round(pr[0]["sug"], 2)
        exp[("Pratos", "K5")] = round(pr[0]["mc"], 4)
        for i, p in enumerate(pr):
            exp[("Pratos", f"N{5+i}")] = p["cls"]
        exp[("Dashboard", "A8")] = sum(1 for p in pr if p["status"] == "ACIMA DA META")
        exp[("Dashboard", "C8")] = sum(1 for p in pr if p["cls"] == "Estrela")
        exp[("Dashboard", "E8")] = sum(1 for p in pr if p["cls"] == "Cão")
        exp[("Dashboard", "G8")] = round(sum(p["lucro"] for p in pr), 2)
        m9 = sample_months(teor_sep)[8]
        cmv9 = m9[0] + m9[1] - m9[2]
        exp[("Dashboard", "A5")] = round(cmv9 / m9[3], 4)
        exp[("Dashboard", "C5")] = round(teor_sep / m9[3], 4)
        waste = sample_waste()
        wsep = sum(q * ins[i]["bruto"] for (d_, i, q, mo, ob) in waste if d_.month == 9)
        exp[("Dashboard", "I5")] = round(wsep, 2)
        exp[("Dashboard", "I8")] = round(cmv9 - teor_sep - wsep, 2)
        worst = max(pr, key=lambda p: p["cmv"])
        exp[("Dashboard", "B12")] = worst["nome"]
    return exp
