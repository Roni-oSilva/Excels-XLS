# -*- coding: utf-8 -*-
"""Biblioteca comum da fábrica de planilhas Carvex XLS.

- Estilos padronizados (verde Carvex): cabeçalho escuro, células de entrada amarelas, cálculo cinza.
- Helpers para banner, KPI, tabelas, validações, aba Início.
- Cache de valores calculados: depois de recalcular no LibreOffice, os resultados são gravados
  como valor em cache das fórmulas (assim a planilha aparece com números mesmo em visualizadores
  que não calculam, como pré-visualização de e-mail/celular).
"""
import datetime as dt
import xlsxwriter
from xlsxwriter.utility import xl_cell_to_rowcol, xl_rowcol_to_cell, xl_col_to_name

REF_DATE = dt.date(2026, 10, 8)   # data fixa usada nos EXEMPLOS (as versões limpas usam HOJE())

# paleta Carvex XLS (verde)
G_DARK = "#0B3B24"
G_MID = "#16A34A"
G_NEON = "#22C55E"
G_LIGHT = "#DCFCE7"
G_PALE = "#F0FDF4"
C_INPUT = "#FFFBE6"
C_CALC = "#F1F5F2"
C_BORDER = "#C5D3CA"
C_TEXT = "#14231A"
C_MUTED = "#5B6B61"
C_RED = "#DC2626"
C_REDL = "#FEE2E2"
C_AMBER = "#F59E0B"
C_AMBERL = "#FEF3C7"
C_BLUE = "#2563EB"

NF = {
    "money": '"R$" #,##0.00;[Red]-"R$" #,##0.00',
    "money0": '"R$" #,##0;[Red]-"R$" #,##0',
    "int": "#,##0",
    "num": "#,##0.00",
    "pct": "0.0%",
    "pct0": "0%",
    "date": "dd/mm/yyyy",
    "mon": "mmm/yy",
    "time": "hh:mm",
    "gen": "General",
    "x": '0.00"x"',
    "days": '0" d"',
}

ERRORS = ("#REF!", "#VALUE!", "#DIV/0!", "#NAME?", "#N/A", "#NUM!", "#NULL!")


class Book:
    def __init__(self, path, sample=False, cache=None, product="", version="1.0", shots=None):
        self.path = path
        self.sample = sample
        self.cache = cache or {}
        self.product = product
        self.version = version
        self.shots = shots
        self.wb = xlsxwriter.Workbook(path, {"default_date_format": "dd/mm/yyyy"})
        self.wb.set_properties({
            "title": product, "author": "Carvex XLS", "company": "Carvex Technology",
            "comments": "Planilha empresarial Carvex XLS" + (" (EXEMPLO com dados fictícios)" if sample else ""),
        })
        self.wb.set_calc_mode("auto")
        self._fmt = {}
        self.sheets = {}

    # ------------------------------------------------------------------ formatos
    def fmt(self, kind="base", nf=None, **kw):
        key = (kind, nf, tuple(sorted(kw.items())))
        if key in self._fmt:
            return self._fmt[key]
        p = {"font_name": "Calibri", "font_size": 10, "valign": "vcenter", "font_color": C_TEXT}
        if kind == "in":      # célula de preenchimento
            p.update(bg_color=C_INPUT, border=1, border_color=C_BORDER, locked=False)
        elif kind == "calc":  # célula automática
            p.update(bg_color=C_CALC, border=1, border_color=C_BORDER, font_color="#2F4A3A")
        elif kind == "h":     # cabeçalho
            p.update(bg_color=G_DARK, font_color="#FFFFFF", bold=True, align="center", text_wrap=True,
                     border=1, border_color=G_DARK)
        elif kind == "h2":    # sub-cabeçalho verde claro
            p.update(bg_color=G_LIGHT, font_color=G_DARK, bold=True, align="center", text_wrap=True,
                     border=1, border_color=C_BORDER)
        elif kind == "tot":   # linha de total
            p.update(bg_color=G_LIGHT, bold=True, border=1, border_color=C_BORDER, font_color=G_DARK)
        elif kind == "title":
            p.update(bg_color=G_DARK, font_color="#FFFFFF", bold=True, font_size=18, indent=1)
        elif kind == "sub":
            p.update(font_color=C_MUTED, italic=True, font_size=10, indent=1)
        elif kind == "sec":   # título de seção
            p.update(bold=True, font_size=12, font_color=G_DARK, bottom=2, bottom_color=G_NEON)
        elif kind == "note":
            p.update(font_color=C_MUTED, font_size=9, text_wrap=True, valign="top")
        elif kind == "kpil":
            p.update(bg_color=G_PALE, font_color=C_MUTED, font_size=9, align="center", bold=True,
                     top=1, left=1, right=1, border_color=C_BORDER, text_wrap=True)
        elif kind == "kpiv":
            p.update(bg_color=G_PALE, font_color=G_DARK, font_size=16, bold=True, align="center",
                     bottom=1, left=1, right=1, border_color=C_BORDER)
        elif kind == "txt":
            p.update(text_wrap=True, valign="top")
        elif kind == "lbl":
            p.update(bold=True, font_color=G_DARK)
        elif kind == "plain":
            p.update(border=1, border_color=C_BORDER)
        p.update(kw)
        if nf:
            p["num_format"] = NF.get(nf, nf)
        f = self.wb.add_format(p)
        self._fmt[key] = f
        return f

    # ------------------------------------------------------------------ planilhas
    def sheet(self, name, tab=G_MID, zoom=100, grid=False, onepage=False):
        ws = self.wb.add_worksheet(name)
        ws.set_tab_color(tab)
        ws.set_zoom(zoom)
        if not grid:
            ws.hide_gridlines(2)
        ws.set_landscape()
        ws.set_paper(9)
        ws.fit_to_pages(1, 1 if onepage else 0)
        ws.set_footer("&L&8Carvex XLS - " + self.product + "&R&8Página &P de &N")
        self.sheets[name] = ws
        return ws

    # fórmula com valor em cache (se existir)
    def fx(self, ws, ref, formula, fmt=None):
        if isinstance(ref, str):
            r, c = xl_cell_to_rowcol(ref)
        else:
            r, c = ref
        v = self.cache.get((ws.get_name(), r, c), 0)
        if not formula.startswith("="):
            formula = "=" + formula
        ws.write_formula(r, c, formula, fmt, v)

    def w(self, ws, ref, value, fmt=None):
        if isinstance(ref, str):
            r, c = xl_cell_to_rowcol(ref)
        else:
            r, c = ref
        if isinstance(value, dt.datetime):
            ws.write_datetime(r, c, value, fmt)
        elif isinstance(value, dt.date):
            ws.write_datetime(r, c, dt.datetime(value.year, value.month, value.day), fmt)
        elif value is None:
            ws.write_blank(r, c, None, fmt)
        else:
            ws.write(r, c, value, fmt)

    def close(self):
        self.wb.close()

    # ------------------------------------------------------------------ blocos prontos
    def banner(self, ws, title, subtitle="", ncols=10):
        ws.set_row(0, 36)
        ws.merge_range(0, 0, 0, ncols - 1, title, self.fmt("title"))
        ws.set_row(1, 20)
        ws.merge_range(1, 0, 1, ncols - 1, subtitle, self.fmt("sub"))
        if self.sample:
            ws.write(1, ncols - 1, "EXEMPLO - dados fictícios",
                     self.fmt("plain", bold=True, font_color=C_RED, bg_color=C_REDL, align="center"))

    def section(self, ws, row, col, text, ncols=6):
        ws.merge_range(row, col, row, col + ncols - 1, text, self.fmt("sec"))

    def header(self, ws, row, col, headers, widths=None, height=32):
        ws.set_row(row, height)
        for i, h in enumerate(headers):
            ws.write(row, col + i, h, self.fmt("h"))
            if widths:
                ws.set_column(col + i, col + i, widths[i])

    def kpi(self, ws, row, col, label, formula, nf="money", span=2, color=None):
        """Cartão de indicador (2 linhas) ocupando `span` colunas."""
        lf = self.fmt("kpil")
        vf = self.fmt("kpiv", nf=nf, **({"font_color": color} if color else {}))
        if span > 1:
            ws.merge_range(row, col, row, col + span - 1, label, lf)
            ws.merge_range(row + 1, col, row + 1, col + span - 1, "", vf)
        else:
            ws.write(row, col, label, lf)
        ws.set_row(row, 24)
        ws.set_row(row + 1, 32)
        self.fx(ws, (row + 1, col), formula, vf)

    def dv_list(self, ws, rng, source, msg=None):
        opts = {"validate": "list", "source": source, "error_title": "Valor inválido",
                "error_message": "Escolha um item da lista."}
        if msg:
            opts.update(input_title="Dica", input_message=msg)
        ws.data_validation(rng, opts)

    def dv_num(self, ws, rng, minimum=0, maximum=None, msg=None, integer=False):
        o = {"validate": "integer" if integer else "decimal", "criteria": ">=", "value": minimum,
             "error_title": "Valor inválido", "error_message": f"Digite um número maior ou igual a {minimum}."}
        if maximum is not None:
            o.update(criteria="between", minimum=minimum, maximum=maximum)
            o.pop("value")
            o["error_message"] = f"Digite um número entre {minimum} e {maximum}."
        if msg:
            o.update(input_title="Dica", input_message=msg)
        ws.data_validation(rng, o)

    def dv_date(self, ws, rng, msg="Digite a data no formato dd/mm/aaaa"):
        ws.data_validation(rng, {"validate": "date", "criteria": ">=",
                                 "value": dt.datetime(2000, 1, 1), "error_title": "Data inválida",
                                 "error_message": "Digite uma data válida (dd/mm/aaaa).",
                                 "input_title": "Data", "input_message": msg})

    def cf_text(self, ws, rng, text, bg, fg, bold=True):
        ws.conditional_format(rng, {"type": "cell", "criteria": "==", "value": f'"{text}"',
                                    "format": self.wb.add_format({"bg_color": bg, "font_color": fg, "bold": bold})})

    def define(self, name, ref):
        self.wb.define_name(name, ref)

    def hoje_cell_formula(self):
        """Fórmula da data de referência (EXEMPLO usa data fixa; versão limpa usa HOJE())."""
        return None

    # ------------------------------------------------------------------ aba Início
    def inicio(self, titulo, tagline, para_que, passos, abas, legenda=True, avisos=None):
        ws = self.sheet("Início", tab=G_DARK)
        ws.set_column(0, 0, 3)
        ws.set_column(1, 1, 26)
        ws.set_column(2, 2, 92)
        ws.merge_range(0, 0, 0, 2, titulo, self.fmt("title"))
        ws.set_row(0, 40)
        ws.merge_range(1, 0, 1, 2, tagline, self.fmt("sub"))
        r = 3
        if self.sample:
            ws.merge_range(r, 1, r, 2, "ESTE É O ARQUIVO DE EXEMPLO: todos os dados são fictícios. "
                           "Use-o para entender como a planilha funciona e comece a sua pela PLANILHA-LIMPA.xlsx.",
                           self.fmt("plain", bold=True, font_color=C_RED, bg_color=C_REDL, text_wrap=True))
            ws.set_row(r, 36)
            r += 2
        self.section(ws, r, 1, "O que esta planilha faz", 2); r += 1
        ws.merge_range(r, 1, r, 2, para_que, self.fmt("txt", font_size=11))
        ws.set_row(r, max(48, 16 * (len(para_que) // 95 + 1)))
        r += 2
        self.section(ws, r, 1, "Como começar (5 minutos)", 2); r += 1
        for i, (t, d) in enumerate(passos, 1):
            ws.write(r, 1, f"{i}. {t}", self.fmt("lbl", valign="top", text_wrap=True))
            ws.write(r, 2, d, self.fmt("txt"))
            ws.set_row(r, max(20, 15 * (len(d) // 90 + 1)))
            r += 1
        r += 1
        self.section(ws, r, 1, "Mapa das abas (clique para ir)", 2); r += 1
        for nome, desc in abas:
            ws.write_url(r, 1, f"internal:'{nome}'!A1", self.fmt("lbl", font_color=G_MID, underline=1), nome)
            ws.write(r, 2, desc, self.fmt("txt"))
            ws.set_row(r, max(18, 15 * (len(desc) // 90 + 1)))
            r += 1
        r += 1
        if legenda:
            self.section(ws, r, 1, "Legenda de cores", 2); r += 1
            ws.write(r, 1, "Amarelo", self.fmt("in", bold=True)); ws.write(r, 2, "Célula que VOCÊ preenche.", self.fmt("txt")); r += 1
            ws.write(r, 1, "Cinza", self.fmt("calc", bold=True)); ws.write(r, 2, "Cálculo automático. Não digite aqui.", self.fmt("txt")); r += 1
            ws.write(r, 1, "Verde escuro", self.fmt("h")); ws.write(r, 2, "Cabeçalho de coluna.", self.fmt("txt")); r += 1
            r += 1
        if avisos:
            self.section(ws, r, 1, "Atenção", 2); r += 1
            for a in avisos:
                ws.merge_range(r, 1, r, 2, "• " + a, self.fmt("txt"))
                ws.set_row(r, max(18, 15 * (len(a) // 95 + 1)))
                r += 1
            r += 1
        ws.merge_range(r, 1, r, 2, f"Carvex XLS · {self.product} · versão {self.version} · Dúvidas: consulte o TUTORIAL.md e o MANUAL.md que acompanham o produto.",
                       self.fmt("note"))
        ws.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
        return ws

    def finish(self, first="Início"):
        if self.shots:       # modo captura: deixa visível só a(s) aba(s) pedida(s)
            first = self.shots[0]
            for name, ws in self.sheets.items():
                if name not in self.shots:
                    ws.hide()
        # abre sempre na aba Início
        self.sheets[first].activate()
        self.sheets[first].set_first_sheet()
        self.close()


def col(n):
    return xl_col_to_name(n)


def cell(r, c, abs_=False):
    return xl_rowcol_to_cell(r, c, row_abs=abs_, col_abs=abs_)
