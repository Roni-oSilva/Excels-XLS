# -*- coding: utf-8 -*-
import datetime as dt
import random
from lib import *

SLUG = "ordem-de-servico"
PASTA = "oficinas/ordem-de-servico"
NOME = "Ordem de Serviço para Oficinas"
NC, NV, NPE, NEN, NOS, NIT = 300, 300, 500, 1000, 1000, 3000
R0 = 4
VALOR_HORA, MARKUP, COM_MEC, PRAZO = 120.0, 0.40, 0.30, 5
STATUS = ["Orçamento", "Aprovado", "Em execução", "Aguardando peça", "Finalizado", "Entregue", "Cancelada"]
FORMAS = ["Pix", "Dinheiro", "Cartão de débito", "Cartão de crédito", "Boleto", "Transferência"]
MECS = ["Mecânico A", "Mecânico B", "Mecânico C"]

PECAS = [  # código, descrição, custo, preço fixo (ou None), estoque inicial, mínimo
    ("PC001", "Filtro de óleo", 18.0, None, 20, 8), ("PC002", "Filtro de ar", 24.0, None, 14, 6), ("PC003", "Filtro de combustível", 31.0, None, 10, 5),
    ("PC004", "Óleo 5W30 sintético (L)", 38.0, 62.0, 60, 24), ("PC005", "Óleo 15W40 mineral (L)", 21.0, 36.0, 40, 16), ("PC006", "Pastilha de freio dianteira", 72.0, None, 8, 4),
    ("PC007", "Disco de freio (par)", 210.0, None, 4, 2), ("PC008", "Lona de freio traseira", 64.0, None, 5, 3), ("PC009", "Amortecedor dianteiro", 265.0, None, 4, 2),
    ("PC010", "Kit de embreagem", 540.0, None, 2, 1), ("PC011", "Correia dentada", 96.0, None, 5, 2), ("PC012", "Vela de ignição", 22.0, None, 24, 12),
    ("PC013", "Bateria 60Ah", 395.0, 560.0, 3, 2), ("PC014", "Lâmpada H4", 14.0, None, 18, 8), ("PC015", "Palheta limpador (par)", 38.0, None, 8, 4),
    ("PC016", "Fluido de freio DOT4", 19.0, None, 12, 6), ("PC017", "Aditivo radiador (L)", 17.0, None, 16, 6), ("PC018", "Junta do cabeçote", 120.0, None, 3, 2),
    ("PC019", "Bomba d'água", 148.0, None, 4, 2), ("PC020", "Terminal de direção", 52.0, None, 6, 3), ("PC021", "Pivô de suspensão", 58.0, None, 6, 3),
    ("PC022", "Mangueira de radiador", 44.0, None, 4, 2), ("PC023", "Cabo de vela (jogo)", 85.0, None, 3, 2), ("PC024", "Sensor de temperatura", 47.0, None, 5, 2),
]
SERV = ["Troca de óleo e filtros", "Revisão de freios", "Troca de pastilhas e discos", "Suspensão dianteira", "Troca de correia dentada", "Embreagem", "Diagnóstico elétrico", "Troca de bateria", "Arrefecimento", "Revisão geral"]


def preco(p):
    return p[3] if p[3] is not None else p[2] * (1 + MARKUP)


def sample_data():
    rnd = random.Random(909)
    ref = REF_DATE
    clientes = [(f"Cliente {i+1:02d}", f"(00) 9{rnd.randint(1000,9999)}-{rnd.randint(1000,9999)}") for i in range(18)]
    modelos = ["Hatch 1.0", "Sedan 1.6", "SUV 2.0", "Picape 2.8 diesel", "Hatch 1.4", "Utilitário 1.5", "Sedan 2.0", "Hatch 1.0 flex"]
    veic = []
    for i, (c, _) in enumerate(clientes):
        veic.append((f"EXE{rnd.randint(1,9)}{chr(65+i%26)}{rnd.randint(10,99)}", rnd.choice(modelos), rnd.randint(2010, 2024), c))
    oss, itens = [], []
    pec_by = {p[0]: p for p in PECAS}
    n = 1000
    for k in range(96):
        n += 1
        ent = ref - dt.timedelta(days=int(rnd.uniform(0, 128) ** 1.0))
        if k >= 72:
            ent = ref - dt.timedelta(days=rnd.randint(0, 7))
        v = rnd.choice(veic)
        age = (ref - ent).days
        if age > 14:
            status = rnd.choices(["Entregue", "Finalizado", "Cancelada"], weights=[90, 6, 4])[0]
        elif age > 6:
            status = rnd.choices(["Entregue", "Finalizado", "Em execução", "Aguardando peça"], weights=[60, 14, 16, 10])[0]
        else:
            status = rnd.choices(["Orçamento", "Aprovado", "Em execução", "Aguardando peça", "Finalizado", "Entregue"], weights=[10, 10, 22, 12, 10, 36])[0]
        horas = rnd.choice([1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 8.0])
        terc = rnd.choice([0, 0, 0, 80.0, 150.0, 260.0])
        desc = rnd.choice([0, 0, 0, 0, 30.0, 50.0])
        entrega = forma = recebido = None
        npc = rnd.choice([0, 1, 1, 2, 2, 3, 4])
        its = []
        for _ in range(npc):
            p = rnd.choice(PECAS)
            if p[0] in [i[0] for i in its]:
                continue
            q = rnd.choice([1, 1, 2, 4]) if p[0] not in ("PC004", "PC005") else rnd.choice([3, 4, 5])
            its.append((p[0], q))
        oss.append(dict(num=n, ent=ent, placa=v[0], cli=v[3], modelo=v[1], km=rnd.randint(18, 160) * 1000, serv=rnd.choice(SERV), mec=rnd.choice(MECS),
                        status=status, horas=horas, terc=float(terc), desc=float(desc), entrega=entrega, forma=forma, rec=recebido, itens=its))
    # cálculo + entrega/pagamento
    for o in oss:
        pecas = sum(q * preco(pec_by[c]) for c, q in o["itens"])
        o["mo"] = o["horas"] * VALOR_HORA
        o["pecas"] = pecas
        o["total"] = o["mo"] + pecas + o["terc"] - o["desc"]
        o["custo"] = sum(q * pec_by[c][2] for c, q in o["itens"])
        o["com"] = o["mo"] * COM_MEC
        o["lucro"] = o["total"] - o["custo"] - o["com"] - o["terc"]
        if o["status"] == "Entregue":
            o["entrega"] = min(ref, o["ent"] + dt.timedelta(days=rnd.randint(1, 5)))
            o["forma"] = rnd.choice(FORMAS)
            o["rec"] = round(o["total"], 2) if rnd.random() < 0.88 else round(o["total"] * 0.5, 2)
        elif o["status"] == "Finalizado":
            o["rec"] = None
    # garante algumas entregas em outubro
    oct_ = [o for o in oss if o["status"] == "Entregue" and o["entrega"].month == 10]
    # entradas de peças
    entradas = []
    d0 = dt.date(2026, 6, 1)
    for p in PECAS:
        for w in range(0, 18, 4):
            if rnd.random() < 0.7:
                entradas.append((d0 + dt.timedelta(days=w * 7 + rnd.randint(0, 5)), p[0], p[5] * rnd.choice([1, 2, 3]), p[2], rnd.choice(["Distribuidora Auto A", "Autopeças B", "Importadora C"]), f"NF {rnd.randint(1000,9999)}"))
    entradas.sort(key=lambda e: e[0])
    return clientes, veic, oss, entradas


def analyze(oss, entradas):
    ref = REF_DATE
    pec_by = {p[0]: p for p in PECAS}
    a = dict(fat=0.0, entregues=0, lucro=0.0, andamento=0, aguard=0, receber=0.0, atras=0, orc_val=0.0, orc_n=0, mec={})
    for o in oss:
        if o["status"] == "Entregue" and o["entrega"].year == ref.year and o["entrega"].month == ref.month:
            a["fat"] += o["total"]; a["entregues"] += 1; a["lucro"] += o["lucro"]
            m = a["mec"].setdefault(o["mec"], [0, 0.0, 0.0]); m[0] += 1; m[1] += o["mo"]; m[2] += o["com"]
        if o["status"] in ("Aprovado", "Em execução", "Aguardando peça"):
            a["andamento"] += 1
            if (ref - o["ent"]).days > PRAZO:
                a["atras"] += 1
        if o["status"] == "Aguardando peça":
            a["aguard"] += 1
        if o["status"] in ("Finalizado", "Entregue"):
            a["receber"] += max(0, o["total"] - (o["rec"] or 0))
        if o["status"] == "Orçamento":
            a["orc_n"] += 1; a["orc_val"] += o["total"]
    # estoque
    rup = rep = 0; val = 0.0
    for p in PECAS:
        ent = sum(e[2] for e in entradas if e[1] == p[0])
        sai = sum(q for o in oss if o["status"] not in ("Orçamento", "Cancelada") for c, q in o["itens"] if c == p[0])
        atual = p[4] + ent - sai
        val += atual * p[2]
        if atual <= 0:
            rup += 1
        elif atual <= p[5]:
            rep += 1
    a.update(rup=rup, rep=rep, val=val)
    return a


def build(bk: Book):
    wb = bk.wb
    bk.inicio(
        "Ordem de Serviço para Oficinas", "Carvex XLS · Cada peça na OS, cada real no caixa",
        "Cadastre clientes, veículos e peças e abra as ordens de serviço. A planilha calcula mão de obra, peças, total, lucro de cada OS, dá baixa no estoque de peças, "
        "avisa OS atrasadas e o que falta receber, mostra o histórico por placa e o faturamento do mês.",
        [("Config", "Informe o valor da hora de mão de obra, o markup padrão sobre as peças, a comissão dos mecânicos e o prazo máximo de uma OS (dias)."),
         ("Cadastre clientes e veículos", "Em Clientes e Veículos: nome/telefone e placa/modelo/ano. Cada veículo pertence a um cliente."),
         ("Cadastre as peças", "Em Peças: código, custo e (opcional) preço fixo. Se o preço ficar vazio, a planilha usa custo + markup."),
         ("Abra a OS", "Em OS: número, data, placa, serviço, mecânico, status e horas. Em Itens da OS lance as peças usadas (mesmo número da OS)."),
         ("Entregue e receba", "Ao entregar, mude o status para Entregue, informe data de entrega, forma de pagamento e valor recebido.")],
        [("Config", "Valor da hora, markup, comissão, prazo, mecânicos e formas de pagamento."), ("Clientes", "Cadastro de clientes."), ("Veículos", "Placa, modelo e dono."),
         ("Peças", "Cadastro e estoque atual de peças."), ("Entradas", "Compras de peças (repõem o estoque)."), ("OS", "Ordens de serviço, totais e lucro."),
         ("Itens da OS", "Peças usadas em cada OS."), ("Histórico", "Todas as OS de uma placa."), ("Dashboard", "Faturamento, lucro, OS atrasadas e a receber.")],
        avisos=["O estoque de uma peça só baixa quando a OS sai do status 'Orçamento' (e não está 'Cancelada').",
                "O faturamento do mês considera apenas OS com status Entregue e data de entrega no mês.",
                "O número da OS deve ser único. Use o mesmo número em OS e em Itens da OS."])

    ws = bk.sheet("Config")
    bk.banner(ws, "Configurações", "Preencha as células amarelas.", 8)
    ws.set_column(0, 0, 3); ws.set_column(1, 1, 40); ws.set_column(2, 2, 16); ws.set_column(3, 3, 3); ws.set_column(4, 4, 22); ws.set_column(5, 5, 3); ws.set_column(6, 6, 22)
    lf = bk.fmt("lbl")
    ws.write(3, 1, "Oficina", lf); bk.w(ws, (3, 2), "Oficina Exemplo" if bk.sample else None, bk.fmt("in"))
    ws.write(4, 1, "Data de hoje (referência)", lf)
    if bk.sample:
        bk.w(ws, "C5", REF_DATE, bk.fmt("in", nf="date", align="center"))
    else:
        bk.fx(ws, "C5", "TODAY()", bk.fmt("calc", nf="date", align="center"))
    def inp(r, label, v, nf):
        ws.write(r, 1, label, lf); bk.w(ws, (r, 2), v, bk.fmt("in", nf=nf, align="center"))
    inp(5, "Valor da hora de mão de obra (R$)", VALOR_HORA if bk.sample else None, "money")
    inp(6, "Markup padrão sobre o custo das peças (%)", MARKUP if bk.sample else 0.4, "pct0")
    inp(7, "Comissão dos mecânicos sobre mão de obra (%)", COM_MEC if bk.sample else None, "pct0")
    inp(8, "Prazo máximo de uma OS aberta (dias)", PRAZO, "0")
    bk.dv_num(ws, "C6", 0); bk.dv_num(ws, "C7:C8", 0, 5); bk.dv_num(ws, "C9", 1, 90, integer=True)
    for n, a in (("Hoje", "C5"), ("ValorHora", "C6"), ("MarkupPeca", "C7"), ("ComMec", "C8"), ("PrazoMax", "C9")):
        bk.define(n, f"=Config!${a[0]}${a[1:]}")
    ws.write(3, 4, "Mecânicos", bk.fmt("h")); ws.write(3, 6, "Formas de pagamento", bk.fmt("h"))
    for i in range(10):
        bk.w(ws, (4 + i, 4), MECS[i] if (i < len(MECS) and bk.sample) else None, bk.fmt("in")); bk.w(ws, (4 + i, 6), FORMAS[i] if i < len(FORMAS) else None, bk.fmt("in"))
    bk.define("Mecanicos", "=Config!$E$5:$E$14"); bk.define("Formas", "=Config!$G$5:$G$14")
    ws.write(11, 1, "Status da OS: Orçamento, Aprovado, Em execução, Aguardando peça, Finalizado, Entregue, Cancelada (fixos).", bk.fmt("note"))
    bk.define("StatusOS", "=Config!$B$14:$B$20")
    ws.write(12, 1, "Lista de status", bk.fmt("h"))
    for i, s in enumerate(STATUS):
        ws.write(13 + i, 1, s, bk.fmt("plain"))

    clientes, veic, oss, entradas = sample_data() if bk.sample else ([], [], [], [])
    fi = bk.fmt("in")
    # ---------------- Clientes
    wc = bk.sheet("Clientes")
    bk.banner(wc, "Clientes", "Um cliente por linha.", 3)
    bk.header(wc, 3, 0, ["Nome do cliente", "Telefone", "Observação"], [32, 18, 36], 26)
    for i in range(NC):
        c = clientes[i] if i < len(clientes) else (None, None)
        bk.w(wc, (R0 + i, 0), c[0], fi); bk.w(wc, (R0 + i, 1), c[1], fi); bk.w(wc, (R0 + i, 2), None, fi)
    wc.freeze_panes(4, 0); bk.define("CliNome", f"=Clientes!$A${R0+1}:$A${R0+NC}")
    # ---------------- Veículos
    wv = bk.sheet("Veículos")
    bk.banner(wv, "Veículos", "Placa única. Escolha o cliente da lista.", 5)
    bk.header(wv, 3, 0, ["Placa", "Modelo", "Ano", "Cliente", "Observação"], [12, 24, 8, 28, 28], 26)
    for i in range(NV):
        v = veic[i] if i < len(veic) else (None,) * 4
        bk.w(wv, (R0 + i, 0), v[0], fi); bk.w(wv, (R0 + i, 1), v[1], fi); bk.w(wv, (R0 + i, 2), v[2], bk.fmt("in", nf="0", align="center")); bk.w(wv, (R0 + i, 3), v[3], fi); bk.w(wv, (R0 + i, 4), None, fi)
    bk.dv_list(wv, f"D{R0+1}:D{R0+NV}", "=CliNome"); wv.freeze_panes(4, 0)
    bk.define("VeicPlaca", f"=Veículos!$A${R0+1}:$A${R0+NV}"); bk.define("VeicModelo", f"=Veículos!$B${R0+1}:$B${R0+NV}"); bk.define("VeicCli", f"=Veículos!$D${R0+1}:$D${R0+NV}")
    # ---------------- Peças
    wp = bk.sheet("Peças")
    bk.banner(wp, "Peças e estoque", "Preço vazio = custo + markup. O estoque atual é calculado pelas Entradas e pelas OS.", 11)
    bk.header(wp, 3, 0, ["Código", "Descrição", "Custo (R$)", "Preço de venda fixo (R$)", "Estoque inicial", "Estoque mínimo", "Preço de venda EFETIVO", "Entradas", "Usadas em OS", "ESTOQUE ATUAL", "Situação"],
              [10, 34, 12, 14, 10, 10, 14, 10, 10, 12, 12], 44)
    pcol = lambda c: f"Peças!${c}${R0+1}:${c}${R0+NPE}"
    for i in range(NPE):
        r = R0 + i; x = r + 1
        p = PECAS[i] if (bk.sample and i < len(PECAS)) else None
        bk.w(wp, (r, 0), p[0] if p else None, fi); bk.w(wp, (r, 1), p[1] if p else None, fi); bk.w(wp, (r, 2), p[2] if p else None, bk.fmt("in", nf="money"))
        bk.w(wp, (r, 3), p[3] if p else None, bk.fmt("in", nf="money")); bk.w(wp, (r, 4), p[4] if p else None, bk.fmt("in", nf="int", align="center")); bk.w(wp, (r, 5), p[5] if p else None, bk.fmt("in", nf="int", align="center"))
        bk.fx(wp, (r, 6), f'IF($A{x}="","",IF($D{x}<>"",$D{x},N($C{x})*(1+MarkupPeca)))', bk.fmt("calc", nf="money", bold=True))
        bk.fx(wp, (r, 7), f'IF($A{x}="","",SUMIFS(EntQtd,EntCod,$A{x}))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wp, (r, 8), f'IF($A{x}="","",SUMIFS(ItQtd,ItCod,$A{x},ItStatus,"<>Orçamento",ItStatus,"<>Cancelada"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wp, (r, 9), f'IF($A{x}="","",N($E{x})+$H{x}-$I{x})', bk.fmt("calc", nf="int", align="center", bold=True))
        bk.fx(wp, (r, 10), f'IF($A{x}="","",IF($J{x}<=0,"RUPTURA",IF($J{x}<=N($F{x}),"REPOR","OK")))', bk.fmt("calc", align="center", bold=True))
    bk.dv_num(wp, f"C{R0+1}:F{R0+NPE}", 0)
    for t, bg, fg in (("RUPTURA", C_RED, "#FFFFFF"), ("REPOR", C_AMBER, "#FFFFFF"), ("OK", G_LIGHT, "#15803D")):
        wp.conditional_format(f"K{R0+1}:K{R0+NPE}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wp.freeze_panes(4, 2); wp.autofilter(3, 0, R0 + NPE - 1, 10)
    bk.define("PecCod", f"={pcol('A')}"); bk.define("PecDesc", f"={pcol('B')}"); bk.define("PecCusto", f"={pcol('C')}"); bk.define("PecPreco", f"={pcol('G')}")
    # ---------------- Entradas
    we = bk.sheet("Entradas")
    bk.banner(we, "Entradas de peças (compras)", "Registre cada compra para repor o estoque.", 8)
    bk.header(we, 3, 0, ["Data", "Código da peça", "Quantidade", "Custo unitário (R$)", "Fornecedor", "NF / pedido", "Descrição", "Total (R$)"], [12, 12, 11, 14, 24, 14, 32, 14], 30)
    for i in range(NEN):
        r = R0 + i; x = r + 1
        e = entradas[i] if i < len(entradas) else (None,) * 6
        bk.w(we, (r, 0), e[0], bk.fmt("in", nf="date", align="center")); bk.w(we, (r, 1), e[1], fi); bk.w(we, (r, 2), e[2], bk.fmt("in", nf="int", align="center"))
        bk.w(we, (r, 3), e[3], bk.fmt("in", nf="money")); bk.w(we, (r, 4), e[4], fi); bk.w(we, (r, 5), e[5], fi)
        bk.fx(we, (r, 6), f'IF($B{x}="","",IFERROR(INDEX(PecDesc,MATCH($B{x},PecCod,0)),"Peça não cadastrada"))', bk.fmt("calc"))
        bk.fx(we, (r, 7), f'IF(OR($C{x}="",$D{x}=""),"",$C{x}*$D{x})', bk.fmt("calc", nf="money"))
    bk.dv_date(we, f"A{R0+1}:A{R0+NEN}"); bk.dv_list(we, f"B{R0+1}:B{R0+NEN}", "=PecCod"); bk.dv_num(we, f"C{R0+1}:D{R0+NEN}", 0)
    we.freeze_panes(4, 0)
    bk.define("EntCod", f"=Entradas!$B${R0+1}:$B${R0+NEN}"); bk.define("EntQtd", f"=Entradas!$C${R0+1}:$C${R0+NEN}")

    # ---------------- OS
    wo = bk.sheet("OS")
    bk.banner(wo, "Ordens de Serviço", "Uma linha por OS. As peças usadas são lançadas na aba Itens da OS com o mesmo número.", 27)
    heads = ["Nº OS", "Data de entrada", "Placa", "Cliente", "Modelo", "Km", "Serviço / defeito relatado", "Mecânico", "Status", "Horas de mão de obra", "Serviços de terceiros (R$)", "Desconto (R$)",
             "Data de entrega", "Forma de pagamento", "Valor recebido (R$)", "Mão de obra (R$)", "Peças (R$)", "TOTAL DA OS", "Custo das peças", "Comissão do mecânico", "LUCRO BRUTO", "Margem",
             "Saldo a receber", "Dias na oficina", "ALERTA", "Mês (faturamento)", "Seq. histórico"]
    wid = [8, 11, 10, 22, 18, 9, 30, 13, 15, 9, 12, 10, 11, 15, 13, 13, 12, 13, 12, 12, 13, 8, 13, 9, 20, 10, 6]
    bk.header(wo, 3, 0, heads, wid, 56)
    cm = bk.fmt("calc", nf="money"); cac = bk.fmt("calc", align="center")
    for i in range(NOS):
        r = R0 + i; x = r + 1
        o = oss[i] if i < len(oss) else {}
        bk.w(wo, (r, 0), o.get("num"), bk.fmt("in", nf="0", align="center")); bk.w(wo, (r, 1), o.get("ent"), bk.fmt("in", nf="date", align="center")); bk.w(wo, (r, 2), o.get("placa"), fi)
        bk.w(wo, (r, 5), o.get("km"), bk.fmt("in", nf="int")); bk.w(wo, (r, 6), o.get("serv"), fi); bk.w(wo, (r, 7), o.get("mec"), fi); bk.w(wo, (r, 8), o.get("status"), fi)
        bk.w(wo, (r, 9), o.get("horas"), bk.fmt("in", nf="0.0", align="center")); bk.w(wo, (r, 10), o.get("terc"), bk.fmt("in", nf="money")); bk.w(wo, (r, 11), o.get("desc"), bk.fmt("in", nf="money"))
        bk.w(wo, (r, 12), o.get("entrega"), bk.fmt("in", nf="date", align="center")); bk.w(wo, (r, 13), o.get("forma"), fi); bk.w(wo, (r, 14), o.get("rec"), bk.fmt("in", nf="money"))
        bk.fx(wo, (r, 3), f'IF($C{x}="","",IFERROR(INDEX(VeicCli,MATCH($C{x},VeicPlaca,0)),"Placa não cadastrada"))', bk.fmt("calc"))
        bk.fx(wo, (r, 4), f'IF($C{x}="","",IFERROR(INDEX(VeicModelo,MATCH($C{x},VeicPlaca,0)),""))', bk.fmt("calc"))
        bk.fx(wo, (r, 15), f'IF($A{x}="","",N($J{x})*ValorHora)', cm)
        bk.fx(wo, (r, 16), f'IF($A{x}="","",SUMIFS(ItTotal,ItOS,$A{x}))', cm)
        bk.fx(wo, (r, 17), f'IF($A{x}="","",$P{x}+$Q{x}+N($K{x})-N($L{x}))', bk.fmt("calc", nf="money", bold=True, bg_color=G_LIGHT))
        bk.fx(wo, (r, 18), f'IF($A{x}="","",SUMIFS(ItCusto,ItOS,$A{x}))', cm)
        bk.fx(wo, (r, 19), f'IF($A{x}="","",$P{x}*ComMec)', cm)
        bk.fx(wo, (r, 20), f'IF($A{x}="","",$R{x}-$S{x}-$T{x}-N($K{x}))', bk.fmt("calc", nf="money", bold=True))
        bk.fx(wo, (r, 21), f'IF(OR($A{x}="",N($R{x})<=0),"",$U{x}/$R{x})', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wo, (r, 22), f'IF($A{x}="","",IF(OR($I{x}="Finalizado",$I{x}="Entregue"),MAX(0,$R{x}-N($O{x})),0))', cm)
        bk.fx(wo, (r, 23), f'IF(OR($A{x}="",$B{x}=""),"",IF(OR($I{x}="Entregue",$I{x}="Cancelada"),"",Hoje-$B{x}))', cac)
        bk.fx(wo, (r, 24), f'IF($A{x}="","",IF(AND(OR($I{x}="Aprovado",$I{x}="Em execução",$I{x}="Aguardando peça"),N($X{x})>PrazoMax),"ATRASADA",IF(AND(OR($I{x}="Finalizado",$I{x}="Entregue"),$W{x}>0.005),"Cobrar",IF($I{x}="Orçamento","Aguardando aprovação",""))))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wo, (r, 25), f'IF(AND($I{x}="Entregue",$M{x}<>""),DATE(YEAR($M{x}),MONTH($M{x}),1),"")', bk.fmt("calc", nf="mon", align="center"))
        bk.fx(wo, (r, 26), f'IF(AND($C{x}<>"",$C{x}=HistPlaca),COUNTIF($C${R0+1}:$C{x},HistPlaca),"")', bk.fmt("calc", font_color="#9CA3AF"))
    oe = R0 + NOS
    bk.dv_date(wo, f"B{R0+1}:B{oe}"); bk.dv_list(wo, f"C{R0+1}:C{oe}", "=VeicPlaca"); bk.dv_list(wo, f"H{R0+1}:H{oe}", "=Mecanicos"); bk.dv_list(wo, f"I{R0+1}:I{oe}", "=StatusOS")
    bk.dv_num(wo, f"J{R0+1}:L{oe}", 0); bk.dv_date(wo, f"M{R0+1}:M{oe}"); bk.dv_list(wo, f"N{R0+1}:N{oe}", "=Formas"); bk.dv_num(wo, f"O{R0+1}:O{oe}", 0)
    wo.data_validation(f"A{R0+1}:A{oe}", {"validate": "custom", "value": f"=COUNTIF($A${R0+1}:$A${oe},A{R0+1})=1", "error_title": "Nº de OS repetido", "error_message": "Já existe uma OS com esse número."})
    for t, bg, fg in (("ATRASADA", C_RED, "#FFFFFF"), ("Cobrar", C_AMBER, "#FFFFFF"), ("Aguardando aprovação", "#DBEAFE", "#1E40AF")):
        wo.conditional_format(f"Y{R0+1}:Y{oe}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    for t, bg, fg in (("Entregue", G_LIGHT, "#15803D"), ("Finalizado", "#BBF7D0", "#166534"), ("Aguardando peça", C_AMBERL, "#92400E"), ("Cancelada", "#E5E7EB", "#6B7280")):
        wo.conditional_format(f"I{R0+1}:I{oe}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg})})
    wo.freeze_panes(4, 3); wo.autofilter(3, 0, oe - 1, 26)
    wo.set_column(26, 26, None, None, {"hidden": True})
    for n, c in (("OSNum", "A"), ("OSStatus", "I")):
        bk.define(n, f"=OS!${c}${R0+1}:${c}${oe}")
    OSC = lambda c: f"OS!${c}${R0+1}:${c}${oe}"

    # ---------------- Itens
    wi = bk.sheet("Itens da OS")
    bk.banner(wi, "Itens (peças) da OS", "Uma linha por peça usada. O preço vem da aba Peças (ou digite um preço diferente).", 10)
    bk.header(wi, 3, 0, ["Nº OS", "Código da peça", "Quantidade", "Preço unitário (opcional)", "Descrição", "Preço efetivo", "Total (R$)", "Custo (R$)", "Status da OS", "Conferência"],
              [8, 12, 11, 13, 32, 12, 12, 12, 16, 20], 44)
    items = [(o["num"], c, q) for o in oss for (c, q) in o["itens"]]
    for i in range(NIT):
        r = R0 + i; x = r + 1
        it = items[i] if i < len(items) else (None,) * 3
        bk.w(wi, (r, 0), it[0], bk.fmt("in", nf="0", align="center")); bk.w(wi, (r, 1), it[1], fi); bk.w(wi, (r, 2), it[2], bk.fmt("in", nf="int", align="center")); bk.w(wi, (r, 3), None, bk.fmt("in", nf="money"))
        bk.fx(wi, (r, 4), f'IF($B{x}="","",IFERROR(INDEX(PecDesc,MATCH($B{x},PecCod,0)),"Peça não cadastrada"))', bk.fmt("calc"))
        bk.fx(wi, (r, 5), f'IF($B{x}="","",IF($D{x}<>"",$D{x},IFERROR(INDEX(PecPreco,MATCH($B{x},PecCod,0)),0)))', cm)
        bk.fx(wi, (r, 6), f'IF(OR($B{x}="",$C{x}=""),"",$C{x}*$F{x})', cm)
        bk.fx(wi, (r, 7), f'IF(OR($B{x}="",$C{x}=""),"",$C{x}*IFERROR(INDEX(PecCusto,MATCH($B{x},PecCod,0)),0))', cm)
        bk.fx(wi, (r, 8), f'IF($A{x}="","",IFERROR(INDEX(OSStatus,MATCH($A{x},OSNum,0)),"OS inexistente"))', cac)
        bk.fx(wi, (r, 9), f'IF($A{x}="","",IF($I{x}="OS inexistente","OS inexistente",IF($E{x}="Peça não cadastrada","Peça não cadastrada","OK")))', cac)
    ie = R0 + NIT
    bk.dv_list(wi, f"B{R0+1}:B{ie}", "=PecCod"); bk.dv_num(wi, f"C{R0+1}:D{ie}", 0)
    wi.conditional_format(f"J{R0+1}:J{ie}", {"type": "cell", "criteria": "!=", "value": '"OK"', "format": wb.add_format({"font_color": C_RED, "bold": True})})
    wi.freeze_panes(4, 0); wi.autofilter(3, 0, ie - 1, 9)
    for n, c in (("ItOS", "A"), ("ItCod", "B"), ("ItQtd", "C"), ("ItTotal", "G"), ("ItCusto", "H"), ("ItStatus", "I")):
        bk.define(n, f"='Itens da OS'!${c}${R0+1}:${c}${ie}")

    # ---------------- Histórico
    wh = bk.sheet("Histórico", tab=G_NEON, onepage=True)
    bk.banner(wh, "Histórico do veículo", "Escolha a placa e veja todas as OS dele (até 25).", 9)
    wh.set_column(0, 0, 5); wh.set_column(1, 1, 10); wh.set_column(2, 2, 14); wh.set_column(3, 3, 11); wh.set_column(4, 4, 11); wh.set_column(5, 5, 34); wh.set_column(6, 6, 14); wh.set_column(7, 7, 16); wh.set_column(8, 8, 14)
    wh.write(3, 1, "Placa:", bk.fmt("lbl")); bk.w(wh, (3, 2), veic[0][0] if bk.sample else None, bk.fmt("in", bold=True, align="center")); bk.dv_list(wh, "C4", "=VeicPlaca")
    bk.define("HistPlaca", "=Histórico!$C$4")
    wh.write(3, 3, "Cliente:", bk.fmt("lbl")); wh.merge_range(3, 4, 3, 5, "", bk.fmt("calc")); bk.fx(wh, (3, 4), 'IFERROR(INDEX(VeicCli,MATCH($C$4,VeicPlaca,0)),"")', bk.fmt("calc"))
    wh.write(4, 3, "Modelo:", bk.fmt("lbl")); wh.merge_range(4, 4, 4, 5, "", bk.fmt("calc")); bk.fx(wh, (4, 4), 'IFERROR(INDEX(VeicModelo,MATCH($C$4,VeicPlaca,0)),"")', bk.fmt("calc"))
    wh.write(3, 7, "OS no total:", bk.fmt("lbl")); bk.fx(wh, (3, 8), f'COUNTIF({OSC("C")},$C$4)', bk.fmt("calc", nf="int", align="center"))
    wh.write(4, 7, "Total gasto:", bk.fmt("lbl")); bk.fx(wh, (4, 8), f'SUMIFS({OSC("R")},{OSC("C")},$C$4,{OSC("I")},"<>Cancelada",{OSC("I")},"<>Orçamento")', bk.fmt("calc", nf="money"))
    bk.header(wh, 6, 0, ["#", "Nº OS", "Data", "Km", "Status", "Serviço", "Mecânico", "Total (R$)"], height=24)
    for k in range(25):
        r = 7 + k; x = r + 1
        wh.write(r, 0, k + 1, bk.fmt("plain", align="center"))
        mt = f'MATCH($A{x},{OSC("AA")},0)'
        for c, src, nf in ((1, "A", "0"), (2, "B", "date"), (3, "F", "int"), (4, "I", None), (5, "G", None), (6, "H", None), (7, "R", "money")):
            f = f'IFERROR(INDEX({OSC(src)},{mt})' + ('&"")' if nf is None else ')')
            f = f'IFERROR(INDEX({OSC(src)},{mt})&"","")' if nf is None else f'IFERROR(INDEX({OSC(src)},{mt}),"")'
            bk.fx(wh, (r, c), f, bk.fmt("calc", nf=nf, align="center") if nf and nf != "money" else bk.fmt("calc", nf=nf))
    wh.protect("", {"select_locked_cells": True, "select_unlocked_cells": True, "format_cells": False})

    # ---------------- Dashboard
    wd = bk.sheet("Dashboard", tab=G_NEON, onepage=True)
    bk.banner(wd, "Dashboard da oficina", "Mês de referência = mês da data de hoje.", 10)
    for c in range(10):
        wd.set_column(c, c, 13)
    mi = "DATE(YEAR(Hoje),MONTH(Hoje),1)"
    bk.kpi(wd, 3, 0, "FATURAMENTO DO MÊS", f'SUMIFS({OSC("R")},{OSC("Z")},{mi})', "money", 2)
    bk.kpi(wd, 3, 2, "OS ENTREGUES NO MÊS", f'COUNTIFS({OSC("Z")},{mi})', "int", 2)
    bk.kpi(wd, 3, 4, "TICKET MÉDIO", 'IFERROR(A5/C5,0)', "money", 2)
    bk.kpi(wd, 3, 6, "LUCRO BRUTO DO MÊS", f'SUMIFS({OSC("U")},{OSC("Z")},{mi})', "money", 2)
    bk.kpi(wd, 3, 8, "MARGEM DO MÊS", 'IFERROR(G5/A5,0)', "pct", 2)
    bk.kpi(wd, 6, 0, "OS EM ANDAMENTO", f'COUNTIF({OSC("I")},"Aprovado")+COUNTIF({OSC("I")},"Em execução")+COUNTIF({OSC("I")},"Aguardando peça")', "int", 2)
    bk.kpi(wd, 6, 2, "AGUARDANDO PEÇA", f'COUNTIF({OSC("I")},"Aguardando peça")', "int", 2, color="#B45309")
    bk.kpi(wd, 6, 4, "A RECEBER", f'SUM({OSC("W")})', "money", 2, color=C_RED)
    bk.kpi(wd, 6, 6, "OS ATRASADAS", f'COUNTIF({OSC("Y")},"ATRASADA")', "int", 2, color=C_RED)
    bk.kpi(wd, 6, 8, "ORÇAMENTOS PENDENTES (R$)", f'SUMIFS({OSC("R")},{OSC("I")},"Orçamento")', "money", 2)
    bk.kpi(wd, 9, 0, "PEÇAS EM RUPTURA", f'COUNTIF({pcol("K")},"RUPTURA")', "int", 2, color=C_RED)
    bk.kpi(wd, 9, 2, "PEÇAS A REPOR", f'COUNTIF({pcol("K")},"REPOR")', "int", 2, color="#B45309")
    bk.kpi(wd, 9, 4, "ESTOQUE DE PEÇAS (custo)", f'SUMPRODUCT({pcol("J")},{pcol("C")})', "money", 2)
    bk.kpi(wd, 9, 6, "CLIENTES", f'SUMPRODUCT(--(Clientes!$A${R0+1}:$A${R0+NC}<>""))', "int", 2)
    bk.kpi(wd, 9, 8, "VEÍCULOS", f'SUMPRODUCT(--(VeicPlaca<>""))', "int", 2)
    wd.merge_range(12, 0, 12, 4, "Faturamento por mês (ano da data de hoje)", bk.fmt("sec"))
    bk.header(wd, 13, 0, ["Mês", "Faturamento", "Lucro bruto", "OS entregues"], height=22)
    for m in range(12):
        r = 14 + m; x = r + 1
        bk.fx(wd, (r, 0), f"DATE(YEAR(Hoje),{m+1},1)", bk.fmt("calc", nf="mon", align="center", bold=True))
        bk.fx(wd, (r, 1), f'SUMIFS({OSC("R")},{OSC("Z")},A{x})', cm); bk.fx(wd, (r, 2), f'SUMIFS({OSC("U")},{OSC("Z")},A{x})', cm)
        bk.fx(wd, (r, 3), f'COUNTIFS({OSC("Z")},A{x})', bk.fmt("calc", nf="int", align="center"))
    wd.merge_range(12, 5, 12, 9, "Mecânicos no mês", bk.fmt("sec"))
    wd.merge_range(13, 5, 13, 6, "Mecânico", bk.fmt("h")); wd.write(13, 7, "OS entregues", bk.fmt("h")); wd.write(13, 8, "Mão de obra", bk.fmt("h")); wd.write(13, 9, "Comissão", bk.fmt("h"))
    for i in range(10):
        r = 14 + i; x = r + 1
        wd.merge_range(r, 5, r, 6, "", bk.fmt("calc")); bk.fx(wd, (r, 5), f'IF(INDEX(Mecanicos,{i+1})="","",INDEX(Mecanicos,{i+1}))', bk.fmt("calc"))
        bk.fx(wd, (r, 7), f'IF($F{x}="","",COUNTIFS({OSC("H")},$F{x},{OSC("Z")},{mi}))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wd, (r, 8), f'IF($F{x}="","",SUMIFS({OSC("P")},{OSC("H")},$F{x},{OSC("Z")},{mi}))', cm)
        bk.fx(wd, (r, 9), f'IF($F{x}="","",SUMIFS({OSC("T")},{OSC("H")},$F{x},{OSC("Z")},{mi}))', cm)
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Faturamento", "categories": "=Dashboard!$A$15:$A$26", "values": "=Dashboard!$B$15:$B$26", "fill": {"color": G_MID}, "gap": 60})
    ch.add_series({"name": "Lucro bruto", "categories": "=Dashboard!$A$15:$A$26", "values": "=Dashboard!$C$15:$C$26", "fill": {"color": G_DARK}})
    ch.set_title({"name": "Faturamento e lucro bruto por mês", "name_font": {"size": 12}}); ch.set_legend({"position": "bottom"}); ch.set_x_axis({"num_format": "mmm"}); ch.set_size({"width": 780, "height": 290})
    wd.insert_chart("A28", ch)
    wd.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
    bk.finish()

    exp = {}
    if bk.sample:
        a = analyze(oss, entradas)
        exp[("Dashboard", "A5")] = round(a["fat"], 2); exp[("Dashboard", "C5")] = a["entregues"]
        exp[("Dashboard", "E5")] = round(a["fat"] / a["entregues"], 2) if a["entregues"] else 0
        exp[("Dashboard", "G5")] = round(a["lucro"], 2)
        exp[("Dashboard", "I5")] = round(a["lucro"] / a["fat"], 4) if a["fat"] else 0
        exp[("Dashboard", "A8")] = a["andamento"]; exp[("Dashboard", "C8")] = a["aguard"]
        exp[("Dashboard", "E8")] = round(a["receber"], 2); exp[("Dashboard", "G8")] = a["atras"]
        exp[("Dashboard", "I8")] = round(a["orc_val"], 2)
        exp[("Dashboard", "A11")] = a["rup"]; exp[("Dashboard", "C11")] = a["rep"]; exp[("Dashboard", "E11")] = round(a["val"], 2)
        exp[("OS", "R5")] = round(oss[0]["total"], 2); exp[("OS", "U5")] = round(oss[0]["lucro"], 2)
        for i, m in enumerate(MECS):
            if m in a["mec"]:
                exp[("Dashboard", f"H{15+i}")] = a["mec"][m][0]; exp[("Dashboard", f"I{15+i}")] = round(a["mec"][m][1], 2); exp[("Dashboard", f"J{15+i}")] = round(a["mec"][m][2], 2)
    return exp
