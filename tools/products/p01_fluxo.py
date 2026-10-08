# -*- coding: utf-8 -*-
import datetime as dt
import random
from lib import *

SLUG = "fluxo-de-caixa"
PASTA = "financeiro/fluxo-de-caixa"
NOME = "Fluxo de Caixa Inteligente"
N = 1000          # linhas de lançamentos disponíveis
R0 = 4            # primeira linha de dados (0-index) em Lançamentos -> Excel linha 5
LAST = R0 + N     # Excel: última linha = R0+N

CATS = [
    ("Vendas de produtos", "Entrada", "Operacional"),
    ("Prestação de serviços", "Entrada", "Operacional"),
    ("Outras receitas", "Entrada", "Não operacional"),
    ("Aporte de sócio", "Entrada", "Não operacional"),
    ("Empréstimos recebidos", "Entrada", "Não operacional"),
    ("Fornecedores / mercadorias", "Saída", "Variável"),
    ("Impostos", "Saída", "Variável"),
    ("Comissões e taxas", "Saída", "Variável"),
    ("Frete e logística", "Saída", "Variável"),
    ("Manutenção", "Saída", "Variável"),
    ("Folha de pagamento", "Saída", "Fixo"),
    ("Aluguel", "Saída", "Fixo"),
    ("Energia, água e internet", "Saída", "Fixo"),
    ("Marketing", "Saída", "Fixo"),
    ("Contador e sistemas", "Saída", "Fixo"),
    ("Pró-labore / retiradas", "Saída", "Pessoal"),
    ("Empréstimos / financiamentos", "Saída", "Financeiro"),
    ("Investimentos", "Saída", "Investimento"),
    ("Outras despesas", "Saída", "Variável"),
]
CONTAS = ["Caixa", "Banco principal", "Maquininha de cartão", "Poupança / reserva"]


def sample_rows():
    rnd = random.Random(2026)
    rows = []  # (data, tipo, categoria, descricao, conta, valor, status)
    ref = REF_DATE
    for m in range(1, 13):
        base = {1: .86, 2: .82, 3: .95, 4: .98, 5: 1.05, 6: 1.0, 7: 1.02, 8: 1.08, 9: 1.12, 10: 1.15, 11: 1.3, 12: 1.4}[m]
        def d(day):
            return dt.date(2026, m, min(day, 28))
        def st(day):
            return "Realizado" if d(day) <= ref else "Previsto"
        # vendas em 4 semanas
        for i, day in enumerate((7, 14, 21, 28)):
            v = round(rnd.uniform(9500, 13200) * base, 2)
            rows.append((d(day), "Entrada", "Vendas de produtos", f"Vendas semana {i+1}", rnd.choice(["Maquininha de cartão", "Banco principal", "Caixa"]), v, st(day)))
        v = round(rnd.uniform(6500, 9800) * base, 2)
        rows.append((d(15), "Entrada", "Prestação de serviços", "Serviços de instalação", "Banco principal", v, st(15)))
        if m in (3, 8):
            rows.append((d(10), "Entrada", "Outras receitas", "Venda de equipamento usado", "Banco principal", 2400.0, st(10)))
        if m == 1:
            rows.append((d(2), "Entrada", "Aporte de sócio", "Aporte para capital de giro", "Banco principal", 15000.0, st(2)))
        # saídas
        rows.append((d(5), "Saída", "Fornecedores / mercadorias", "Compra de mercadorias - fornecedor A", "Banco principal", round(rnd.uniform(8800, 11800) * base, 2), st(5)))
        rows.append((d(19), "Saída", "Fornecedores / mercadorias", "Compra de mercadorias - fornecedor B", "Banco principal", round(rnd.uniform(3800, 6200) * base, 2), st(19)))
        rows.append((d(20), "Saída", "Impostos", "Simples Nacional", "Banco principal", round(rnd.uniform(2300, 3100) * base, 2), st(20)))
        rows.append((d(25), "Saída", "Comissões e taxas", "Taxas de cartão", "Maquininha de cartão", round(rnd.uniform(900, 1500) * base, 2), st(25)))
        rows.append((d(12), "Saída", "Frete e logística", "Fretes de entrega", "Banco principal", round(rnd.uniform(700, 1400) * base, 2), st(12)))
        rows.append((d(5), "Saída", "Folha de pagamento", "Salários e encargos", "Banco principal", 11800.0, st(5)))
        rows.append((d(10), "Saída", "Aluguel", "Aluguel da loja", "Banco principal", 4200.0, st(10)))
        rows.append((d(15), "Saída", "Energia, água e internet", "Contas de consumo", "Banco principal", round(rnd.uniform(1100, 1500), 2), st(15)))
        rows.append((d(8), "Saída", "Marketing", "Anúncios online", "Banco principal", round(rnd.uniform(1200, 2200), 2), st(8)))
        rows.append((d(20), "Saída", "Contador e sistemas", "Contabilidade + sistema", "Banco principal", 1350.0, st(20)))
        rows.append((d(6), "Saída", "Pró-labore / retiradas", "Pró-labore do sócio", "Banco principal", 6000.0, st(6)))
        if m in (2, 6, 9):
            rows.append((d(22), "Saída", "Manutenção", "Manutenção de equipamentos", "Caixa", round(rnd.uniform(600, 1800), 2), st(22)))
        if m <= 12:
            rows.append((d(10), "Saída", "Empréstimos / financiamentos", "Parcela capital de giro", "Banco principal", 2100.0, st(10)))
        if m == 4:
            rows.append((d(14), "Saída", "Investimentos", "Compra de prateleiras", "Banco principal", 5600.0, st(14)))
    rows.sort(key=lambda r: r[0])
    return rows


def build(bk: Book):
    SALDO_INI = 18000.0
    wb = bk.wb
    inicio_abas = [
        ("Config", "Dados da empresa, ano, saldo inicial e lista de categorias (você pode renomear e criar categorias)."),
        ("Lançamentos", "Onde você registra TODAS as entradas e saídas (previstas ou realizadas)."),
        ("Mensal", "Relatório mês a mês: entradas, saídas, resultado, saldo realizado e saldo projetado."),
        ("Dashboard", "Indicadores e gráficos: saldo atual, meses de reserva, maiores despesas."),
    ]
    bk.inicio(
        "Fluxo de Caixa Inteligente", "Carvex XLS · Saiba quanto realmente sobra no fim do mês",
        "Registre cada entrada e saída (já realizada ou prevista) e a planilha mostra o saldo atual, o saldo projetado mês a mês, "
        "se o caixa vai ficar negativo, quantos meses de reserva você tem e para onde vai o seu dinheiro.",
        [("Abra a aba Config", "Preencha o nome da empresa, o ano de análise e o saldo inicial (quanto havia em caixa + bancos em 1º de janeiro)."),
         ("Revise as categorias", "Na Config, ajuste a lista de categorias ao seu negócio. Cada categoria é de um Tipo (Entrada ou Saída)."),
         ("Lance os movimentos", "Na aba Lançamentos, uma linha por movimento: data, tipo, categoria, descrição, conta, valor e status."),
         ("Use Previsto e Realizado", "Contas que ainda vão acontecer entram como 'Previsto'. Quando acontecerem, troque para 'Realizado'."),
         ("Leia o Dashboard", "Veja o saldo atual, o saldo projetado e a coluna Alerta da aba Mensal. Vermelho = atenção.")],
        inicio_abas,
        avisos=["Digite sempre valores POSITIVOS; a planilha usa o campo Tipo para somar ou subtrair.",
                "Não digite nas células cinza (cálculo automático). Cada linha usa as colunas H a K como apoio.",
                "A coluna Conferência avisa quando a categoria não combina com o Tipo (ex.: 'Aluguel' marcado como Entrada)."],
    )

    # ------------------------------------------------------------- Config
    ws = bk.sheet("Config")
    bk.banner(ws, "Configurações", "Preencha as células amarelas. As categorias alimentam as listas da aba Lançamentos.", 6)
    ws.set_column(0, 0, 3); ws.set_column(1, 1, 34); ws.set_column(2, 2, 18); ws.set_column(3, 3, 18)
    ws.set_column(4, 4, 3); ws.set_column(5, 5, 28)
    lf = bk.fmt("lbl")
    ws.write("B4", "Empresa", lf); bk.w(ws, "C4", "Empresa Exemplo Ltda" if bk.sample else "", bk.fmt("in")); ws.merge_range("C4:D4", "Empresa Exemplo Ltda" if bk.sample else "", bk.fmt("in"))
    ws.write("B5", "Ano de análise", lf); bk.w(ws, "C5", 2026 if bk.sample else dt.date.today().year, bk.fmt("in", nf="0", align="center"))
    ws.write("B6", "Saldo inicial do ano (R$)", lf); bk.w(ws, "C6", SALDO_INI if bk.sample else 0, bk.fmt("in", nf="money"))
    ws.write("B7", "Data de hoje (referência)", lf)
    if bk.sample:
        bk.w(ws, "C7", REF_DATE, bk.fmt("in", nf="date", align="center"))
        ws.write("D7", "fixa no exemplo", bk.fmt("note"))
    else:
        bk.fx(ws, "C7", "TODAY()", bk.fmt("calc", nf="date", align="center"))
        ws.write("D7", "automática", bk.fmt("note"))
    ws.write("B8", "Meta de reserva (meses de despesas)", lf); bk.w(ws, "C8", 3, bk.fmt("in", nf="0", align="center"))
    bk.dv_num(ws, "C5", 2000, 2100, "Ano que será analisado", integer=True)
    bk.dv_num(ws, "C8", 0, 36, "Quantos meses de despesas você quer ter guardados", integer=True)
    bk.define("Ano", "=Config!$C$5"); bk.define("SaldoIni", "=Config!$C$6"); bk.define("Hoje", "=Config!$C$7"); bk.define("MetaReserva", "=Config!$C$8")

    bk.section(ws, 9, 1, "Categorias (edite livremente; máximo 40)", 3)
    bk.header(ws, 10, 1, ["Categoria", "Tipo", "Natureza"], height=24)
    for i in range(40):
        r = 11 + i
        if i < len(CATS):
            c, t, n = CATS[i]
        else:
            c = t = n = None
        bk.w(ws, (r, 1), c, bk.fmt("in")); bk.w(ws, (r, 2), t, bk.fmt("in", align="center")); bk.w(ws, (r, 3), n, bk.fmt("in", align="center"))
    bk.dv_list(ws, "C12:C51", ["Entrada", "Saída"])
    bk.dv_list(ws, "D12:D51", ["Operacional", "Não operacional", "Fixo", "Variável", "Pessoal", "Financeiro", "Investimento"])
    bk.define("CatNome", "=Config!$B$12:$B$51"); bk.define("CatTipo", "=Config!$C$12:$C$51")
    ws.write("F11", "Contas (caixa / bancos)", bk.fmt("h"))
    for i in range(12):
        bk.w(ws, (11 + i, 5), CONTAS[i] if i < len(CONTAS) else None, bk.fmt("in"))
    bk.define("Contas", "=Config!$F$12:$F$23")
    ws.freeze_panes(3, 0)

    # ------------------------------------------------------------- Lançamentos
    wl = bk.sheet("Lançamentos")
    bk.banner(wl, "Lançamentos", "Uma linha por entrada ou saída. Valores sempre positivos. Previsto = ainda vai acontecer.", 11)
    heads = ["Data", "Tipo", "Categoria", "Descrição", "Conta", "Valor (R$)", "Status", "Ano", "Mês", "Valor líquido", "Conferência"]
    widths = [12, 10, 28, 36, 20, 14, 12, 7, 6, 14, 18]
    bk.header(wl, 3, 0, heads, widths)
    rows = sample_rows() if bk.sample else []
    fin, fit = bk.fmt("in", nf="date", align="center"), bk.fmt("in")
    fic, fim, fis = bk.fmt("in", align="center"), bk.fmt("in", nf="money"), bk.fmt("in", align="center")
    cn, cm = bk.fmt("calc", align="center"), bk.fmt("calc", nf="money")
    for i in range(N):
        r = R0 + i; x = r + 1
        row = rows[i] if i < len(rows) else (None,) * 7
        bk.w(wl, (r, 0), row[0], fin); bk.w(wl, (r, 1), row[1], fic); bk.w(wl, (r, 2), row[2], fit)
        bk.w(wl, (r, 3), row[3], fit); bk.w(wl, (r, 4), row[4], fit); bk.w(wl, (r, 5), row[5], fim); bk.w(wl, (r, 6), row[6], fis)
        bk.fx(wl, (r, 7), f'IF($A{x}="","",YEAR($A{x}))', cn)
        bk.fx(wl, (r, 8), f'IF($A{x}="","",MONTH($A{x}))', cn)
        bk.fx(wl, (r, 9), f'IF(OR($A{x}="",$F{x}=""),"",IF($B{x}="Entrada",$F{x},-$F{x}))', cm)
        bk.fx(wl, (r, 10), f'IF($A{x}="","",IF(OR($B{x}="",$C{x}="",$F{x}="",$G{x}=""),"Preencher tudo",'
                           f'IF(IFERROR(INDEX(CatTipo,MATCH($C{x},CatNome,0)),"")<>$B{x},"Categoria x Tipo?","OK")))', cn)
    rng = f"A{R0+1}:K{LAST}"
    bk.dv_date(wl, f"A{R0+1}:A{LAST}")
    bk.dv_list(wl, f"B{R0+1}:B{LAST}", ["Entrada", "Saída"])
    bk.dv_list(wl, f"C{R0+1}:C{LAST}", "=CatNome")
    bk.dv_list(wl, f"E{R0+1}:E{LAST}", "=Contas")
    bk.dv_num(wl, f"F{R0+1}:F{LAST}", 0, None, "Digite o valor SEM sinal de menos")
    bk.dv_list(wl, f"G{R0+1}:G{LAST}", ["Realizado", "Previsto"])
    wl.conditional_format(f"K{R0+1}:K{LAST}", {"type": "cell", "criteria": "==", "value": '"OK"', "format": wb.add_format({"font_color": "#15803D", "bold": True})})
    wl.conditional_format(f"K{R0+1}:K{LAST}", {"type": "text", "criteria": "containing", "value": "?", "format": wb.add_format({"bg_color": C_REDL, "font_color": C_RED, "bold": True})})
    wl.conditional_format(f"K{R0+1}:K{LAST}", {"type": "cell", "criteria": "==", "value": '"Preencher tudo"', "format": wb.add_format({"bg_color": C_AMBERL, "font_color": "#92400E"})})
    wl.conditional_format(f"G{R0+1}:G{LAST}", {"type": "cell", "criteria": "==", "value": '"Previsto"', "format": wb.add_format({"font_color": C_BLUE, "italic": True})})
    wl.autofilter(3, 0, LAST - 1, 10)
    wl.freeze_panes(4, 0)
    wl.write_comment("G4", "Realizado = já aconteceu.\nPrevisto = ainda vai acontecer (conta futura, venda esperada).")

    # ------------------------------------------------------------- Mensal
    wm = bk.sheet("Mensal", onepage=True)
    bk.banner(wm, "Relatório mensal", "Realizado x Previsto. O saldo projetado soma o que já aconteceu com o que ainda vai acontecer.", 11)
    mh = ["Mês", "Entradas realizadas", "Saídas realizadas", "Resultado do mês", "Saldo realizado (fim do mês)",
          "Entradas previstas", "Saídas previstas", "Resultado projetado", "Saldo projetado (fim do mês)", "Margem realizada", "Alerta"]
    bk.header(wm, 3, 0, mh, [12, 16, 16, 16, 18, 16, 16, 16, 18, 12, 22], 44)
    L = lambda c: f"'Lançamentos'!${c}${R0+1}:${c}${LAST}"
    cm = bk.fmt("calc", nf="money"); cmon = bk.fmt("calc", nf="mon", align="center", bold=True); cp = bk.fmt("calc", nf="pct", align="center")
    for m in range(12):
        r = 4 + m; x = r + 1
        bk.fx(wm, (r, 0), f"DATE(Ano,{m+1},1)", cmon)
        bk.fx(wm, (r, 1), f'SUMIFS({L("F")},{L("B")},"Entrada",{L("G")},"Realizado",{L("H")},Ano,{L("I")},MONTH($A{x}))', cm)
        bk.fx(wm, (r, 2), f'SUMIFS({L("F")},{L("B")},"Saída",{L("G")},"Realizado",{L("H")},Ano,{L("I")},MONTH($A{x}))', cm)
        bk.fx(wm, (r, 3), f"B{x}-C{x}", cm)
        bk.fx(wm, (r, 4), (f"SaldoIni+D{x}" if m == 0 else f"E{x-1}+D{x}"), cm)
        bk.fx(wm, (r, 5), f'SUMIFS({L("F")},{L("B")},"Entrada",{L("G")},"Previsto",{L("H")},Ano,{L("I")},MONTH($A{x}))', cm)
        bk.fx(wm, (r, 6), f'SUMIFS({L("F")},{L("B")},"Saída",{L("G")},"Previsto",{L("H")},Ano,{L("I")},MONTH($A{x}))', cm)
        bk.fx(wm, (r, 7), f"(B{x}+F{x})-(C{x}+G{x})", cm)
        bk.fx(wm, (r, 8), (f"SaldoIni+H{x}" if m == 0 else f"I{x-1}+H{x}"), cm)
        bk.fx(wm, (r, 9), f'IF(B{x}=0,"",D{x}/B{x})', cp)
        bk.fx(wm, (r, 10), f'IF(I{x}<0,"SALDO NEGATIVO",IF(H{x}<0,"Mês no vermelho","OK"))', bk.fmt("calc", align="center"))
    tf = bk.fmt("tot", nf="money")
    wm.write(16, 0, "Total", bk.fmt("tot", align="center"))
    for c in (1, 2, 3, 5, 6, 7):
        bk.fx(wm, (16, c), f"SUM({col(c)}5:{col(c)}16)", tf)
    bk.fx(wm, (16, 4), "E16", tf); bk.fx(wm, (16, 8), "I16", tf)
    bk.fx(wm, (16, 9), 'IF(B17=0,"",D17/B17)', bk.fmt("tot", nf="pct", align="center"))
    wm.write(16, 10, "", bk.fmt("tot"))
    wm.conditional_format("K5:K16", {"type": "cell", "criteria": "==", "value": '"SALDO NEGATIVO"', "format": wb.add_format({"bg_color": C_RED, "font_color": "#FFFFFF", "bold": True})})
    wm.conditional_format("K5:K16", {"type": "cell", "criteria": "==", "value": '"Mês no vermelho"', "format": wb.add_format({"bg_color": C_AMBERL, "font_color": "#92400E", "bold": True})})
    wm.conditional_format("K5:K16", {"type": "cell", "criteria": "==", "value": '"OK"', "format": wb.add_format({"font_color": "#15803D", "bold": True})})
    wm.conditional_format("I5:I16", {"type": "cell", "criteria": "<", "value": 0, "format": wb.add_format({"font_color": C_RED, "bold": True})})
    wm.merge_range(18, 0, 19, 10, "Como ler: 'Saldo realizado' só considera o que já aconteceu. 'Saldo projetado' inclui o que está Previsto. "
                   "Se o projetado ficar negativo em algum mês, aja antes: antecipe recebimentos, renegocie prazos ou reduza gastos.", bk.fmt("note"))
    wm.freeze_panes(4, 1)
    wm.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})

    # ------------------------------------------------------------- Calc (oculta) para ranking de categorias
    wc = bk.sheet("Calc", tab="#999999")
    wc.write_row(0, 0, ["Categoria", "Tipo", "Saída realizada no ano", "Chave de ordenação"])
    for i in range(40):
        r = 1 + i; x = r + 1
        bk.fx(wc, (r, 0), f'IF(Config!B{12+i}="","",Config!B{12+i})')
        bk.fx(wc, (r, 1), f'IF(Config!C{12+i}="","",Config!C{12+i})')
        bk.fx(wc, (r, 2), f'IF(A{x}="",0,IF(B{x}<>"Saída",0,SUMIFS({L("F")},{L("C")},A{x},{L("B")},"Saída",{L("G")},"Realizado",{L("H")},Ano)))')
        bk.fx(wc, (r, 3), f'IF(C{x}>0,C{x}+ROW()/1000000000,"")')
    wc.hide()

    # ------------------------------------------------------------- Dashboard
    wd = bk.sheet("Dashboard", tab=G_NEON, onepage=True)
    bk.banner(wd, "Dashboard", "Visão rápida da saúde financeira. Atualiza sozinho conforme você lança.", 12)
    for c in range(12):
        wd.set_column(c, c, 12)
    bk.kpi(wd, 3, 0, "SALDO ATUAL (realizado)", 'SaldoIni+SUMIFS(' + L("J") + ',' + L("G") + ',"Realizado",' + L("H") + ',Ano)', "money", 3)
    bk.kpi(wd, 3, 3, "ENTRADAS NO ANO", "Mensal!B17", "money", 3)
    bk.kpi(wd, 3, 6, "SAÍDAS NO ANO", "Mensal!C17", "money", 3)
    bk.kpi(wd, 3, 9, "RESULTADO NO ANO", "Mensal!D17", "money", 3)
    bk.kpi(wd, 6, 0, "MARGEM NO ANO", 'IF(Mensal!B17=0,0,Mensal!D17/Mensal!B17)', "pct", 3)
    bk.kpi(wd, 6, 3, "SALDO PROJETADO (dez)", "Mensal!I16", "money", 3)
    bk.kpi(wd, 6, 6, "MESES DE RESERVA", 'IFERROR(A5/(Mensal!C17/MAX(1,COUNTIF(Mensal!C5:C16,">0"))),0)', "0.0", 3)
    bk.kpi(wd, 6, 9, "SITUAÇÃO DA RESERVA", 'IF(G8>=MetaReserva,"Reserva saudável",IF(G8>=1,"Abaixo da meta","CRÍTICO: <1 mês"))', "gen", 3)
    # os KPIs acima usam A5 (saldo atual) - garante referência correta
    wd.merge_range(9, 0, 9, 5, "Maiores saídas do ano (realizado)", bk.fmt("sec"))
    bk.header(wd, 10, 0, ["#", "Categoria", "", "Valor", "% das saídas"], height=22)
    wd.merge_range(10, 1, 10, 2, "Categoria", bk.fmt("h"))
    for k in range(1, 9):
        r = 10 + k; x = r + 1
        wd.write(r, 0, k, bk.fmt("plain", align="center"))
        bk.fx(wd, (r, 5), f'IFERROR(LARGE(Calc!$D$2:$D$41,{k}),"")', bk.fmt("calc", font_color="#FFFFFF", font_size=6))   # chave
        wd.merge_range(r, 1, r, 2, "", bk.fmt("calc"))
        bk.fx(wd, (r, 1), f'IF(F{x}="","",INDEX(Calc!$A$2:$A$41,MATCH(F{x},Calc!$D$2:$D$41,0)))', bk.fmt("calc"))
        bk.fx(wd, (r, 3), f'IF(F{x}="","",ROUND(F{x},2))', bk.fmt("calc", nf="money"))
        bk.fx(wd, (r, 4), f'IF(OR(F{x}="",Mensal!$C$17=0),"",D{x}/Mensal!$C$17)', bk.fmt("calc", nf="pct", align="center"))
    wd.write(10, 5, "chave", bk.fmt("note"))

    # gráficos
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Entradas", "categories": "=Mensal!$A$5:$A$16", "values": "=Mensal!$B$5:$B$16", "fill": {"color": G_MID}, "gap": 80})
    ch.add_series({"name": "Saídas", "categories": "=Mensal!$A$5:$A$16", "values": "=Mensal!$C$5:$C$16", "fill": {"color": "#F87171"}})
    ln = wb.add_chart({"type": "line"})
    ln.add_series({"name": "Saldo realizado", "categories": "=Mensal!$A$5:$A$16", "values": "=Mensal!$E$5:$E$16",
                   "line": {"color": G_DARK, "width": 2.5}, "marker": {"type": "circle", "size": 5}, "y2_axis": True})
    ln.add_series({"name": "Saldo projetado", "categories": "=Mensal!$A$5:$A$16", "values": "=Mensal!$I$5:$I$16",
                   "line": {"color": C_BLUE, "width": 2, "dash_type": "dash"}, "y2_axis": True})
    ch.combine(ln)
    ch.set_title({"name": "Entradas x Saídas e saldo", "name_font": {"size": 12}})
    ch.set_legend({"position": "bottom"})
    ch.set_y_axis({"num_format": '#,##0', "major_gridlines": {"visible": True, "line": {"color": "#E5E7EB"}}})
    ln.set_y2_axis({"num_format": '#,##0'})
    ch.set_x_axis({"num_format": "mmm"})
    ch.set_size({"width": 520, "height": 300})
    wd.insert_chart("A21", ch)
    bar = wb.add_chart({"type": "bar"})
    bar.add_series({"name": "Saídas", "categories": "=Dashboard!$B$12:$B$19", "values": "=Dashboard!$D$12:$D$19",
                    "fill": {"color": G_MID}, "data_labels": {"value": True, "num_format": '#,##0'}})
    bar.set_title({"name": "Para onde vai o dinheiro", "name_font": {"size": 12}})
    bar.set_legend({"none": True}); bar.set_y_axis({"reverse": True}); bar.set_size({"width": 500, "height": 300})
    wd.insert_chart("G21", bar)
    wd.set_column(5, 5, None, None, {"hidden": True})
    wd.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})

    bk.finish()

    # ------------------------------------------------------------- valores esperados (conferidos no LibreOffice)
    exp = {}
    if bk.sample:
        real = [r for r in rows if r[6] == "Realizado"]
        ent = sum(r[5] for r in real if r[1] == "Entrada"); sai = sum(r[5] for r in real if r[1] == "Saída")
        exp[("Dashboard", "A5")] = round(SALDO_INI + ent - sai, 2)
        exp[("Mensal", "B17")] = round(ent, 2)
        exp[("Mensal", "C17")] = round(sai, 2)
        tot_ent = sum(r[5] for r in rows if r[1] == "Entrada"); tot_sai = sum(r[5] for r in rows if r[1] == "Saída")
        exp[("Mensal", "I16")] = round(SALDO_INI + tot_ent - tot_sai, 2)
        jan = [r for r in real if r[0].month == 1]
        exp[("Mensal", "D5")] = round(sum(r[5] for r in jan if r[1] == "Entrada") - sum(r[5] for r in jan if r[1] == "Saída"), 2)
    return exp
