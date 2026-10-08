# -*- coding: utf-8 -*-
import datetime as dt
import random
from lib import *

SLUG = "agenda-retornos"
PASTA = "clinicas/agenda-retornos"
NOME = "Agenda, Faltas e Retornos para Clínicas"
NP, NA = 1000, 3000
R0 = 4
DIAS_CONF, JANELA_RET = 2, 15
D = dt.date
STATUS = ["Agendado", "Confirmado", "Compareceu", "Faltou", "Cancelado", "Remarcado"]
FORMAS = ["Pix", "Dinheiro", "Cartão de débito", "Cartão de crédito", "Transferência"]
PROFS = ["Profissional A", "Profissional B", "Profissional C", "Profissional D"]
PROCS = [("Consulta inicial", 250.0, 0), ("Retorno", 150.0, 0), ("Limpeza / manutenção", 180.0, 180), ("Avaliação", 120.0, 30), ("Procedimento A", 350.0, 15),
         ("Sessão", 140.0, 7), ("Exame complementar", 90.0, 0), ("Revisão", 130.0, 90)]
CONVS = ["Particular", "Convênio A", "Convênio B"]
ORIG = ["Indicação", "Instagram", "Google", "Convênio", "Passante"]
DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def sample_data():
    rnd = random.Random(1111)
    ref = REF_DATE
    pac = []
    for i in range(46):
        pac.append((f"P{i+1:03d}", f"Paciente {i+1:03d}", f"(00) 9{rnd.randint(1000,9999)}-{rnd.randint(1000,9999)}",
                    rnd.choices(CONVS, weights=[55, 30, 15])[0], rnd.choice(ORIG), D(2026, 1, 5) + dt.timedelta(days=rnd.randint(0, 250)), None))
    pr = {p[0]: p for p in PROCS}
    ag = []
    # dias úteis de 1/7 até 20/10
    day = D(2026, 7, 1)
    miss_w = {0: 0.24, 1: 0.12, 2: 0.13, 3: 0.14, 4: 0.22, 5: 0.10}
    while day <= D(2026, 10, 20):
        wd = day.weekday()
        if wd <= 5:
            n = rnd.randint(3, 5) if wd < 5 else rnd.randint(2, 3)
            hours = sorted(rnd.sample(range(8, 18), min(n, 9)))
            for h in hours:
                p = rnd.choice(pac)
                proc = rnd.choices([x[0] for x in PROCS], weights=[8, 14, 12, 12, 8, 22, 8, 6])[0]
                prof = rnd.choice(PROFS)
                if day < ref:
                    r = rnd.random()
                    if r < miss_w[wd]:
                        st = "Faltou"
                    elif r < miss_w[wd] + 0.06:
                        st = "Cancelado"
                    elif r < miss_w[wd] + 0.08:
                        st = "Remarcado"
                    else:
                        st = "Compareceu"
                else:
                    st = "Confirmado" if (day - ref).days <= 1 and rnd.random() < 0.5 else "Agendado"
                valor = None
                rec = forma = None
                if st == "Compareceu":
                    v = pr[proc][1]
                    if p[3] != "Particular":
                        valor = round(v * 0.6, 2)
                        v = valor
                    rec = round(v, 2) if rnd.random() < 0.9 else (round(v * 0.5, 2) if rnd.random() < 0.5 else None)
                    forma = rnd.choice(FORMAS) if rec else None
                ag.append(dict(data=day, hora=(h * 60 + rnd.choice([0, 30])) / 1440, prof=prof, pac=p[0], proc=proc, st=st, valor=valor, rec=rec, forma=forma))
        day += dt.timedelta(days=1)
    return pac, ag


def analyze(pac, ag, mes=D(2026, 9, 1)):
    ref = REF_DATE
    pr = {p[0]: p for p in PROCS}
    conv = {p[0]: p[3] for p in pac}
    for a in ag:
        a["val"] = a["valor"] if a["valor"] is not None else pr[a["proc"]][1]
        a["real"] = a["val"] if a["st"] == "Compareceu" else 0
        a["perd"] = a["val"] if a["st"] == "Faltou" else 0
        a["areceber"] = max(0, a["val"] - (a["rec"] or 0)) if a["st"] == "Compareceu" else 0
        ret = pr[a["proc"]][2]
        a["ret"] = a["data"] + dt.timedelta(days=ret) if (a["st"] == "Compareceu" and ret > 0) else None
        if a["ret"]:
            later = any(b["pac"] == a["pac"] and b["data"] > a["data"] and b["st"] not in ("Cancelado", "Remarcado") for b in ag)
            a["ret_ag"] = "Sim" if later else "Não"
        else:
            a["ret_ag"] = None
        a["conf"] = a["st"] == "Agendado" and 0 <= (a["data"] - ref).days <= DIAS_CONF
        a["retpend"] = bool(a["ret"]) and a["ret_ag"] == "Não" and (ref - dt.timedelta(days=60)) <= a["ret"] <= ref + dt.timedelta(days=JANELA_RET)
    inmonth = [a for a in ag if a["data"].year == mes.year and a["data"].month == mes.month]
    ok = [a for a in inmonth if a["st"] not in ("Cancelado", "Remarcado")]
    comp = [a for a in inmonth if a["st"] == "Compareceu"]
    falt = [a for a in inmonth if a["st"] == "Faltou"]
    res = dict(agend=len(ok), comp=len(comp), falt=len(falt), taxa=len(falt) / (len(comp) + len(falt)),
               receita=sum(a["real"] for a in inmonth), perdida=sum(a["perd"] for a in inmonth),
               ticket=sum(a["real"] for a in inmonth) / len(comp), areceber=sum(a["areceber"] for a in ag),
               conf=sum(1 for a in ag if a["conf"]), retpend=sum(1 for a in ag if a["retpend"]), by_prof={}, by_dia={})
    for pf in PROFS:
        x = [a for a in inmonth if a["prof"] == pf]
        c = sum(1 for a in x if a["st"] == "Compareceu"); f = sum(1 for a in x if a["st"] == "Faltou")
        res["by_prof"][pf] = dict(ag=sum(1 for a in x if a["st"] not in ("Cancelado", "Remarcado")), c=c, f=f, rec=sum(a["real"] for a in x), perd=sum(a["perd"] for a in x))
    for i, d_ in enumerate(DIAS[:6]):
        x = [a for a in inmonth if a["data"].weekday() == i]
        res["by_dia"][d_] = dict(ag=sum(1 for a in x if a["st"] not in ("Cancelado", "Remarcado")), f=sum(1 for a in x if a["st"] == "Faltou"))
    return res


def build(bk: Book):
    wb = bk.wb
    bk.inicio(
        "Agenda, Faltas e Retornos", "Carvex XLS · Menos horários vazios, mais retornos agendados",
        "Registre a agenda com status de cada atendimento. A planilha calcula a taxa de falta por profissional e dia da semana, a receita perdida com faltas, "
        "lista quem precisa ser confirmado e quais pacientes devem retornar e ainda não têm retorno agendado. Sem dados clínicos: só o necessário para a gestão.",
        [("Config", "Cadastre profissionais, procedimentos (valor e dias para retorno), convênios e formas de pagamento."),
         ("Cadastre os pacientes", "Em Pacientes: código, nome, telefone e convênio. NÃO registre diagnósticos, exames ou informações de saúde."),
         ("Lance a agenda", "Em Agenda: data, hora, profissional, código do paciente, procedimento e status. Atualize o status ao longo do dia."),
         ("Confirme e recupere", "Na aba Pendências veja quem confirmar nos próximos dias e quem precisa de retorno agendado."),
         ("Meça os resultados", "Na aba Relatórios veja taxa de falta, receita perdida e receita por profissional.")],
        [("Config", "Profissionais, procedimentos, convênios, janelas de alerta."), ("Pacientes", "Cadastro mínimo e histórico de presença."),
         ("Agenda", "Todos os agendamentos (até 3.000 linhas)."), ("Pendências", "Confirmações e retornos a agendar, com telefone."),
         ("Relatórios", "Indicadores do mês, por profissional, por dia da semana e tendência mensal.")],
        avisos=["Privacidade: use apenas dados de identificação e contato necessários para o agendamento (LGPD). Nunca lance informações de saúde.",
                "Status 'Cancelado' e 'Remarcado' não contam como falta. 'Faltou' é a ausência sem aviso.",
                "O valor padrão vem da tabela de procedimentos. Para convênio ou desconto, digite o valor cobrado na coluna própria."])

    ws = bk.sheet("Config")
    bk.banner(ws, "Configurações", "Preencha as células amarelas.", 12)
    ws.set_column(0, 0, 3); ws.set_column(1, 1, 38); ws.set_column(2, 2, 16); ws.set_column(3, 3, 3)
    ws.set_column(4, 4, 22); ws.set_column(5, 5, 3); ws.set_column(6, 6, 26); ws.set_column(7, 8, 14); ws.set_column(9, 9, 3); ws.set_column(10, 10, 18); ws.set_column(11, 11, 3); ws.set_column(12, 12, 20)
    lf = bk.fmt("lbl")
    ws.write(3, 1, "Clínica", lf); bk.w(ws, (3, 2), "Clínica Exemplo" if bk.sample else None, bk.fmt("in"))
    ws.write(4, 1, "Data de hoje (referência)", lf)
    if bk.sample:
        bk.w(ws, "C5", REF_DATE, bk.fmt("in", nf="date", align="center"))
    else:
        bk.fx(ws, "C5", "TODAY()", bk.fmt("calc", nf="date", align="center"))
    ws.write(5, 1, "Confirmar agendamentos com até (dias)", lf); bk.w(ws, "C6", DIAS_CONF, bk.fmt("in", nf="0", align="center"))
    ws.write(6, 1, "Alertar retornos que vencem em (dias)", lf); bk.w(ws, "C7", JANELA_RET, bk.fmt("in", nf="0", align="center"))
    ws.write(7, 1, "Mês de análise (1º dia; opcional)", lf); bk.w(ws, "C8", D(2026, 9, 1) if bk.sample else None, bk.fmt("in", nf="date", align="center"))
    ws.write(8, 1, "Mês de análise efetivo", lf); bk.fx(ws, "C9", 'IF(ISNUMBER($C$8),DATE(YEAR($C$8),MONTH($C$8),1),DATE(YEAR(Hoje),MONTH(Hoje),1))', bk.fmt("calc", nf="date", align="center"))
    ws.write(9, 1, "Deixe o mês vazio para analisar o mês atual.", bk.fmt("note"))
    bk.dv_num(ws, "C6:C7", 0, 60, integer=True); bk.dv_date(ws, "C8")
    for n, a in (("Hoje", "C5"), ("DiasConf", "C6"), ("JanelaRet", "C7"), ("MesAn", "C9")):
        bk.define(n, f"=Config!${a[0]}${a[1:]}")
    ws.write(3, 4, "Profissionais", bk.fmt("h"))
    for i in range(10):
        bk.w(ws, (4 + i, 4), PROFS[i] if (bk.sample and i < len(PROFS)) else None, bk.fmt("in"))
    ws.write(3, 6, "Procedimento", bk.fmt("h")); ws.write(3, 7, "Valor (R$)", bk.fmt("h")); ws.write(3, 8, "Dias p/ retorno", bk.fmt("h"))
    for i in range(30):
        p = PROCS[i] if i < len(PROCS) else (None, None, None)
        bk.w(ws, (4 + i, 6), p[0], bk.fmt("in")); bk.w(ws, (4 + i, 7), p[1], bk.fmt("in", nf="money")); bk.w(ws, (4 + i, 8), p[2], bk.fmt("in", nf="0", align="center"))
    ws.write(3, 10, "Convênios", bk.fmt("h"))
    for i in range(10):
        bk.w(ws, (4 + i, 10), CONVS[i] if i < len(CONVS) else None, bk.fmt("in"))
    ws.write(3, 12, "Formas de pagamento", bk.fmt("h"))
    for i in range(10):
        bk.w(ws, (4 + i, 12), FORMAS[i] if i < len(FORMAS) else None, bk.fmt("in"))
    ws.write(16, 1, "Status do agendamento (fixos)", bk.fmt("h"))
    for i, s in enumerate(STATUS):
        ws.write(17 + i, 1, s, bk.fmt("plain"))
    ws.write(24, 1, "Origem do paciente", bk.fmt("h"))
    for i in range(6):
        bk.w(ws, (25 + i, 1), ORIG[i] if i < len(ORIG) else None, bk.fmt("in"))
    bk.define("ProfLista", "=Config!$E$5:$E$14"); bk.define("ProcNome", "=Config!$G$5:$G$34"); bk.define("ProcValor", "=Config!$H$5:$H$34"); bk.define("ProcRet", "=Config!$I$5:$I$34")
    bk.define("Convenios", "=Config!$K$5:$K$14"); bk.define("Formas", "=Config!$M$5:$M$14"); bk.define("StatusAg", "=Config!$B$18:$B$23"); bk.define("Origens", "=Config!$B$26:$B$31")

    pac, ag = sample_data() if bk.sample else ([], [])
    fi = bk.fmt("in"); fd = bk.fmt("in", nf="date", align="center"); fm = bk.fmt("in", nf="money")
    cac = bk.fmt("calc", align="center"); cm = bk.fmt("calc", nf="money")
    # ---------------- Pacientes
    wp = bk.sheet("Pacientes")
    bk.banner(wp, "Pacientes (cadastro mínimo)", "Somente identificação e contato. Sem informações de saúde.", 10)
    bk.header(wp, 3, 0, ["Código", "Nome", "Telefone", "Convênio", "Origem", "Cadastro em", "Observação administrativa", "Consultas realizadas", "Faltas", "Última visita"], [9, 30, 17, 14, 13, 12, 28, 11, 8, 12], 36)
    pe = R0 + NP
    for i in range(NP):
        r = R0 + i; x = r + 1
        p = pac[i] if i < len(pac) else (None,) * 7
        bk.w(wp, (r, 0), p[0], fi); bk.w(wp, (r, 1), p[1], fi); bk.w(wp, (r, 2), p[2], fi); bk.w(wp, (r, 3), p[3], fi); bk.w(wp, (r, 4), p[4], fi); bk.w(wp, (r, 5), p[5], fd); bk.w(wp, (r, 6), p[6], fi)
        bk.fx(wp, (r, 7), f'IF($A{x}="","",COUNTIFS(AgPac,$A{x},AgStatus,"Compareceu"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wp, (r, 8), f'IF($A{x}="","",COUNTIFS(AgPac,$A{x},AgStatus,"Faltou"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wp, (r, 9), f'IF($A{x}="","",SUMPRODUCT(MAX((AgPac=$A{x})*(AgStatus="Compareceu")*AgData)))', bk.fmt("calc", nf='dd/mm/yyyy;;"-"', align="center"))
    bk.dv_list(wp, f"D{R0+1}:D{pe}", "=Convenios"); bk.dv_list(wp, f"E{R0+1}:E{pe}", "=Origens"); bk.dv_date(wp, f"F{R0+1}:F{pe}")
    wp.data_validation(f"A{R0+1}:A{pe}", {"validate": "custom", "value": f"=COUNTIF($A${R0+1}:$A${pe},A{R0+1})=1", "error_title": "Código repetido", "error_message": "Use um código único."})
    wp.conditional_format(f"I{R0+1}:I{pe}", {"type": "cell", "criteria": ">=", "value": 2, "format": wb.add_format({"bg_color": C_REDL, "font_color": C_RED, "bold": True})})
    wp.freeze_panes(4, 2); wp.autofilter(3, 0, pe - 1, 9)
    bk.define("PacCod", f"=Pacientes!$A${R0+1}:$A${pe}"); bk.define("PacNome", f"=Pacientes!$B${R0+1}:$B${pe}")
    bk.define("PacTel", f"=Pacientes!$C${R0+1}:$C${pe}"); bk.define("PacConv", f"=Pacientes!$D${R0+1}:$D${pe}")

    # ---------------- Agenda
    wa = bk.sheet("Agenda")
    bk.banner(wa, "Agenda", "Uma linha por agendamento. Atualize o status ao longo do dia.", 22)
    heads = ["Data", "Hora", "Profissional", "Cód. paciente", "Procedimento", "Status", "Valor cobrado (se diferente da tabela)", "Valor recebido (R$)", "Forma de pagamento",
             "Paciente", "Convênio", "Dia", "Valor do atendimento", "Receita realizada", "Receita perdida (falta)", "A receber", "Retorno previsto", "Retorno agendado?", "ALERTA", "Mês", "Seq. confirmar", "Seq. retorno"]
    bk.header(wa, 3, 0, heads, [11, 7, 15, 10, 22, 12, 14, 13, 16, 20, 13, 6, 12, 12, 12, 11, 11, 10, 17, 9, 6, 6], 56)
    for i in range(NA):
        r = R0 + i; x = r + 1
        a = ag[i] if i < len(ag) else {}
        bk.w(wa, (r, 0), a.get("data"), fd); bk.w(wa, (r, 1), a.get("hora"), bk.fmt("in", nf="time", align="center")); bk.w(wa, (r, 2), a.get("prof"), fi)
        bk.w(wa, (r, 3), a.get("pac"), fi); bk.w(wa, (r, 4), a.get("proc"), fi); bk.w(wa, (r, 5), a.get("st"), bk.fmt("in", align="center"))
        bk.w(wa, (r, 6), a.get("valor"), fm); bk.w(wa, (r, 7), a.get("rec"), fm); bk.w(wa, (r, 8), a.get("forma"), fi)
        bk.fx(wa, (r, 9), f'IF($D{x}="","",IFERROR(INDEX(PacNome,MATCH($D{x},PacCod,0)),"Paciente não cadastrado"))', bk.fmt("calc"))
        bk.fx(wa, (r, 10), f'IF($D{x}="","",IFERROR(INDEX(PacConv,MATCH($D{x},PacCod,0))&"",""))', cac)
        bk.fx(wa, (r, 11), f'IF($A{x}="","",CHOOSE(WEEKDAY($A{x},2),"Seg","Ter","Qua","Qui","Sex","Sáb","Dom"))', cac)
        bk.fx(wa, (r, 12), f'IF($E{x}="","",IF($G{x}<>"",$G{x},IFERROR(INDEX(ProcValor,MATCH($E{x},ProcNome,0)),0)))', cm)
        bk.fx(wa, (r, 13), f'IF($M{x}="","",IF($F{x}="Compareceu",$M{x},0))', cm)
        bk.fx(wa, (r, 14), f'IF($M{x}="","",IF($F{x}="Faltou",$M{x},0))', cm)
        bk.fx(wa, (r, 15), f'IF($M{x}="","",IF($F{x}="Compareceu",MAX(0,$M{x}-N($H{x})),0))', cm)
        bk.fx(wa, (r, 16), f'IF(AND($F{x}="Compareceu",$E{x}<>"",$A{x}<>""),IF(IFERROR(INDEX(ProcRet,MATCH($E{x},ProcNome,0)),0)>0,$A{x}+INDEX(ProcRet,MATCH($E{x},ProcNome,0)),""),"")', bk.fmt("calc", nf="date", align="center"))
        bk.fx(wa, (r, 17), f'IF($Q{x}="","",IF(COUNTIFS(AgPac,$D{x},AgData,">"&$A{x},AgStatus,"<>Cancelado",AgStatus,"<>Remarcado")>0,"Sim","Não"))', cac)
        bk.fx(wa, (r, 18), f'IF($A{x}="","",IF(AND($F{x}="Agendado",$A{x}-Hoje>=0,$A{x}-Hoje<=DiasConf),"CONFIRMAR",IF(AND($A{x}<Hoje,OR($F{x}="Agendado",$F{x}="Confirmado")),"Atualizar status",IF(AND($F{x}="Compareceu",$P{x}>0.005),"Cobrar",IF($F{x}="Faltou","Falta: reagendar","")))))', bk.fmt("calc", align="center", bold=True))
        bk.fx(wa, (r, 19), f'IF($A{x}="","",DATE(YEAR($A{x}),MONTH($A{x}),1))', bk.fmt("calc", nf="mon", align="center"))
        bk.fx(wa, (r, 20), f'IF($S{x}="CONFIRMAR",MAX($U$4:$U{x-1})+1,"")', bk.fmt("calc", font_color="#9CA3AF"))
        bk.fx(wa, (r, 21), f'IF(AND($R{x}="Não",$Q{x}<>"",$Q{x}<=Hoje+JanelaRet,$Q{x}>=Hoje-60),MAX($V$4:$V{x-1})+1,"")', bk.fmt("calc", font_color="#9CA3AF"))
    ae = R0 + NA
    bk.dv_date(wa, f"A{R0+1}:A{ae}"); bk.dv_list(wa, f"C{R0+1}:C{ae}", "=ProfLista"); bk.dv_list(wa, f"D{R0+1}:D{ae}", "=PacCod"); bk.dv_list(wa, f"E{R0+1}:E{ae}", "=ProcNome")
    bk.dv_list(wa, f"F{R0+1}:F{ae}", "=StatusAg"); bk.dv_num(wa, f"G{R0+1}:H{ae}", 0); bk.dv_list(wa, f"I{R0+1}:I{ae}", "=Formas")
    wa.data_validation(f"B{R0+1}:B{ae}", {"validate": "time", "criteria": "between", "minimum": dt.time(0, 0), "maximum": dt.time(23, 59), "error_title": "Hora inválida", "error_message": "Digite no formato hh:mm."})
    for t, bg, fg in (("Compareceu", G_LIGHT, "#15803D"), ("Faltou", C_RED, "#FFFFFF"), ("Confirmado", "#DBEAFE", "#1E40AF"), ("Agendado", "#F3F4F6", "#374151"), ("Cancelado", "#E5E7EB", "#6B7280"), ("Remarcado", "#E5E7EB", "#6B7280")):
        wa.conditional_format(f"F{R0+1}:F{ae}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    for t, bg, fg in (("CONFIRMAR", C_AMBER, "#FFFFFF"), ("Atualizar status", C_AMBERL, "#92400E"), ("Cobrar", "#DBEAFE", "#1E40AF"), ("Falta: reagendar", C_REDL, C_RED)):
        wa.conditional_format(f"S{R0+1}:S{ae}", {"type": "cell", "criteria": "==", "value": f'"{t}"', "format": wb.add_format({"bg_color": bg, "font_color": fg, "bold": True})})
    wa.freeze_panes(4, 1); wa.autofilter(3, 0, ae - 1, 21)
    wa.set_column(20, 21, None, None, {"hidden": True})
    for n, c in (("AgData", "A"), ("AgPac", "D"), ("AgStatus", "F")):
        bk.define(n, f"=Agenda!${c}${R0+1}:${c}${ae}")
    AG = lambda c: f"Agenda!${c}${R0+1}:${c}${ae}"
    wa.write(3, 20, "", bk.fmt("h")); wa.write(3, 21, "", bk.fmt("h"))

    # ---------------- Pendências
    wd = bk.sheet("Pendências", tab=G_NEON)
    bk.banner(wd, "Pendências do dia", "Confirmações a fazer e retornos que ainda não têm data marcada.", 15)
    wd.merge_range(3, 0, 3, 6, "1) CONFIRMAR agendamentos (próximos dias)", bk.fmt("sec"))
    wd.merge_range(3, 8, 3, 14, "2) RETORNOS a agendar", bk.fmt("sec"))
    hh = ["#", "Data", "Hora", "Paciente", "Telefone", "Profissional", "Procedimento"]
    bk.header(wd, 4, 0, hh, [4, 11, 7, 24, 16, 15, 20], 24)
    hh2 = ["#", "Retorno previsto", "Última visita", "Paciente", "Telefone", "Profissional", "Procedimento"]
    for j, h in enumerate(hh2):
        wd.write(4, 8 + j, h, bk.fmt("h"))
    wd.set_column(7, 7, 3); wd.set_column(8, 8, 4); wd.set_column(9, 10, 12); wd.set_column(11, 11, 24); wd.set_column(12, 12, 16); wd.set_column(13, 13, 15); wd.set_column(14, 14, 20)
    for k in range(60):
        r = 5 + k; x = r + 1
        wd.write(r, 0, k + 1, bk.fmt("plain", align="center")); wd.write(r, 8, k + 1, bk.fmt("plain", align="center"))
        m1 = f'MATCH($A{x},{AG("U")},0)'; m2 = f'MATCH($I{x},{AG("V")},0)'
        for c, src, nf in ((1, "A", "date"), (2, "B", "time"), (3, "J", None), (5, "C", None), (6, "E", None)):
            f = f'IFERROR(INDEX({AG(src)},{m1}),"")' if nf else f'IFERROR(INDEX({AG(src)},{m1})&"","")'
            bk.fx(wd, (r, c), f, bk.fmt("calc", nf=nf, align="center") if nf else bk.fmt("calc"))
        bk.fx(wd, (r, 4), f'IFERROR(INDEX(PacTel,MATCH(INDEX({AG("D")},{m1}),PacCod,0))&"","")', bk.fmt("calc"))
        bk.fx(wd, (r, 9), f'IFERROR(INDEX({AG("Q")},{m2}),"")', bk.fmt("calc", nf="date", align="center"))
        bk.fx(wd, (r, 10), f'IFERROR(INDEX({AG("A")},{m2}),"")', bk.fmt("calc", nf="date", align="center"))
        bk.fx(wd, (r, 11), f'IFERROR(INDEX({AG("J")},{m2})&"","")', bk.fmt("calc"))
        bk.fx(wd, (r, 12), f'IFERROR(INDEX(PacTel,MATCH(INDEX({AG("D")},{m2}),PacCod,0))&"","")', bk.fmt("calc"))
        bk.fx(wd, (r, 13), f'IFERROR(INDEX({AG("C")},{m2})&"","")', bk.fmt("calc"))
        bk.fx(wd, (r, 14), f'IFERROR(INDEX({AG("E")},{m2})&"","")', bk.fmt("calc"))
    wd.freeze_panes(5, 0)

    # ---------------- Relatórios
    wr = bk.sheet("Relatórios", tab=G_NEON, onepage=True)
    bk.banner(wr, "Relatórios da clínica", "Mês de análise definido na Config (vazio = mês atual).", 10)
    for c in range(10):
        wr.set_column(c, c, 13)
    wr.set_column(0, 0, 16)
    bk.kpi(wr, 3, 0, "AGENDADAS NO MÊS", f'COUNTIFS({AG("T")},MesAn,{AG("F")},"<>Cancelado",{AG("F")},"<>Remarcado")', "int", 2)
    bk.kpi(wr, 3, 2, "COMPARECERAM", f'COUNTIFS({AG("T")},MesAn,{AG("F")},"Compareceu")', "int", 2)
    bk.kpi(wr, 3, 4, "FALTARAM", f'COUNTIFS({AG("T")},MesAn,{AG("F")},"Faltou")', "int", 2, color=C_RED)
    bk.kpi(wr, 3, 6, "TAXA DE FALTA", "IFERROR(E5/(C5+E5),0)", "pct", 2, color=C_RED)
    bk.kpi(wr, 3, 8, "RECEITA REALIZADA", f'SUMIFS({AG("N")},{AG("T")},MesAn)', "money", 2)
    bk.kpi(wr, 6, 0, "RECEITA PERDIDA (faltas)", f'SUMIFS({AG("O")},{AG("T")},MesAn)', "money", 2, color=C_RED)
    bk.kpi(wr, 6, 2, "TICKET MÉDIO", "IFERROR(I5/C5,0)", "money", 2)
    bk.kpi(wr, 6, 4, "A RECEBER (total)", f'SUM({AG("P")})', "money", 2, color="#B45309")
    bk.kpi(wr, 6, 6, "CONFIRMAÇÕES PENDENTES", f'COUNT({AG("U")})', "int", 2)
    bk.kpi(wr, 6, 8, "RETORNOS A AGENDAR", f'COUNT({AG("V")})', "int", 2)
    wr.merge_range(9, 0, 9, 6, "Por profissional (mês de análise)", bk.fmt("sec"))
    bk.header(wr, 10, 0, ["Profissional", "Agendadas", "Compareceu", "Faltou", "Taxa de falta", "Receita", "Perdida em faltas"], height=30)
    for i in range(10):
        r = 11 + i; x = r + 1
        bk.fx(wr, (r, 0), f'IF(INDEX(ProfLista,{i+1})="","",INDEX(ProfLista,{i+1}))', bk.fmt("plain", bold=True))
        bk.fx(wr, (r, 1), f'IF($A{x}="","",COUNTIFS({AG("C")},$A{x},{AG("T")},MesAn,{AG("F")},"<>Cancelado",{AG("F")},"<>Remarcado"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wr, (r, 2), f'IF($A{x}="","",COUNTIFS({AG("C")},$A{x},{AG("T")},MesAn,{AG("F")},"Compareceu"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wr, (r, 3), f'IF($A{x}="","",COUNTIFS({AG("C")},$A{x},{AG("T")},MesAn,{AG("F")},"Faltou"))', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wr, (r, 4), f'IF($A{x}="","",IFERROR(D{x}/(C{x}+D{x}),0))', bk.fmt("calc", nf="pct", align="center", bold=True))
        bk.fx(wr, (r, 5), f'IF($A{x}="","",SUMIFS({AG("N")},{AG("C")},$A{x},{AG("T")},MesAn))', cm)
        bk.fx(wr, (r, 6), f'IF($A{x}="","",SUMIFS({AG("O")},{AG("C")},$A{x},{AG("T")},MesAn))', cm)
    wr.conditional_format("E12:E21", {"type": "data_bar", "bar_color": "#FCA5A5", "bar_solid": True, "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 0.5})
    wr.merge_range(22, 0, 22, 3, "Faltas por dia da semana", bk.fmt("sec"))
    bk.header(wr, 23, 0, ["Dia", "Agendadas", "Faltou", "Taxa de falta"], height=26)
    for i, d_ in enumerate(DIAS[:6]):
        r = 24 + i; x = r + 1
        wr.write(r, 0, d_, bk.fmt("plain", bold=True, align="center"))
        bk.fx(wr, (r, 1), f'COUNTIFS({AG("L")},$A{x},{AG("T")},MesAn,{AG("F")},"<>Cancelado",{AG("F")},"<>Remarcado")', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wr, (r, 2), f'COUNTIFS({AG("L")},$A{x},{AG("T")},MesAn,{AG("F")},"Faltou")', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wr, (r, 3), f'IF(B{x}=0,0,C{x}/B{x})', bk.fmt("calc", nf="pct", align="center", bold=True))
    wr.merge_range(22, 5, 22, 9, "Tendência mensal (ano da data de hoje)", bk.fmt("sec"))
    for j, h in enumerate(["Mês", "Compareceu", "Faltou", "Taxa de falta", "Receita"]):
        wr.write(23, 5 + j, h, bk.fmt("h"))
    for m in range(12):
        r = 24 + m; x = r + 1
        bk.fx(wr, (r, 5), f"DATE(YEAR(Hoje),{m+1},1)", bk.fmt("calc", nf="mon", align="center", bold=True))
        bk.fx(wr, (r, 6), f'COUNTIFS({AG("T")},$F{x},{AG("F")},"Compareceu")', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wr, (r, 7), f'COUNTIFS({AG("T")},$F{x},{AG("F")},"Faltou")', bk.fmt("calc", nf="int", align="center"))
        bk.fx(wr, (r, 8), f'IF(G{x}+H{x}=0,"",H{x}/(G{x}+H{x}))', bk.fmt("calc", nf="pct", align="center"))
        bk.fx(wr, (r, 9), f'SUMIFS({AG("N")},{AG("T")},$F{x})', cm)
    c1 = wb.add_chart({"type": "column"})
    c1.add_series({"name": "Taxa de falta", "categories": "=Relatórios!$A$25:$A$30", "values": "=Relatórios!$D$25:$D$30", "fill": {"color": "#F87171"}, "data_labels": {"value": True, "num_format": "0%"}, "gap": 60})
    c1.set_title({"name": "Em que dia mais faltam?", "name_font": {"size": 12}}); c1.set_legend({"none": True}); c1.set_y_axis({"num_format": "0%"}); c1.set_size({"width": 400, "height": 260})
    wr.insert_chart("A39", c1)
    c2 = wb.add_chart({"type": "column"})
    c2.add_series({"name": "Compareceu", "categories": "=Relatórios!$F$25:$F$36", "values": "=Relatórios!$G$25:$G$36", "fill": {"color": G_MID}, "gap": 60})
    c2.add_series({"name": "Faltou", "categories": "=Relatórios!$F$25:$F$36", "values": "=Relatórios!$H$25:$H$36", "fill": {"color": "#F87171"}})
    c2.set_title({"name": "Comparecimentos x faltas por mês", "name_font": {"size": 12}}); c2.set_legend({"position": "bottom"}); c2.set_x_axis({"num_format": "mmm"}); c2.set_size({"width": 480, "height": 260})
    wr.insert_chart("F39", c2)
    wr.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
    bk.finish()

    exp = {}
    if bk.sample:
        r_ = analyze(pac, ag)
        exp[("Relatórios", "A5")] = r_["agend"]; exp[("Relatórios", "C5")] = r_["comp"]; exp[("Relatórios", "E5")] = r_["falt"]
        exp[("Relatórios", "G5")] = round(r_["taxa"], 4); exp[("Relatórios", "I5")] = round(r_["receita"], 2)
        exp[("Relatórios", "A8")] = round(r_["perdida"], 2); exp[("Relatórios", "C8")] = round(r_["ticket"], 2)
        exp[("Relatórios", "E8")] = round(r_["areceber"], 2); exp[("Relatórios", "G8")] = r_["conf"]; exp[("Relatórios", "I8")] = r_["retpend"]
        for i, pf in enumerate(PROFS):
            b = r_["by_prof"][pf]
            exp[("Relatórios", f"B{12+i}")] = b["ag"]; exp[("Relatórios", f"C{12+i}")] = b["c"]; exp[("Relatórios", f"D{12+i}")] = b["f"]
            exp[("Relatórios", f"F{12+i}")] = round(b["rec"], 2)
        for i, d_ in enumerate(DIAS[:6]):
            exp[("Relatórios", f"B{25+i}")] = r_["by_dia"][d_]["ag"]; exp[("Relatórios", f"C{25+i}")] = r_["by_dia"][d_]["f"]
    return exp
