# -*- coding: utf-8 -*-
"""Pipeline: gera .xlsx (limpa + exemplo), recalcula no LibreOffice, confere erros e valores esperados,
regrava com valores em cache e salva em planilhas/<pasta>/.

uso: python3 build.py [slug-ou-modulo ...]
"""
import importlib, json, os, subprocess, sys, shutil, warnings, datetime as dt
warnings.filterwarnings("ignore")
import openpyxl
from openpyxl.utils.datetime import to_excel
from xlsxwriter.utility import xl_cell_to_rowcol

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "products"))
from lib import Book, ERRORS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, ".build")
MODULES = ["p01_fluxo", "p02_precificador", "p03_estoque", "p04_contas", "p05_crm",
           "p06_dre", "p07_ficha", "p08_oficina", "p09_obras", "p10_clinica"]


XCU = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>
</oor:items>
"""


def recalc(path):
    out = os.path.join(BUILD, "recalc")
    os.makedirs(out, exist_ok=True)
    udir = os.path.join(BUILD, "lo_profile", "user")
    os.makedirs(udir, exist_ok=True)
    xcu = os.path.join(udir, "registrymodifications.xcu")
    if not os.path.exists(xcu):
        with open(xcu, "w") as f:
            f.write(XCU)
    prof = "file://" + os.path.join(BUILD, "lo_profile")
    cmd = ["soffice", "--headless", "--norestore", f"-env:UserInstallation={prof}", "--convert-to", "xlsx",
           "--outdir", out, path]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    return read_values(os.path.join(out, os.path.basename(path)))


def read_values(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    cache = {}
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if v is None:
                    continue
                if isinstance(v, (dt.datetime, dt.date)):
                    v = to_excel(v)
                elif isinstance(v, dt.time):
                    v = (v.hour * 3600 + v.minute * 60 + v.second) / 86400
                cache[(ws.title, c.row - 1, c.column - 1)] = v
    return cache


def check(cache, expected, label):
    errs = [(k, v) for k, v in cache.items() if isinstance(v, str) and v.strip() in ERRORS]
    problems = []
    if errs:
        problems.append(f"{len(errs)} células com erro, ex.: {errs[:5]}")
    for (sheet, ref), want in expected.items():
        r, c = xl_cell_to_rowcol(ref)
        got = cache.get((sheet, r, c))
        ok = (abs(got - want) < 0.01) if isinstance(want, (int, float)) and isinstance(got, (int, float)) else got == want
        if not ok:
            problems.append(f"{sheet}!{ref}: esperado {want!r}, obtido {got!r}")
    status = "OK " if not problems else "FALHA"
    print(f"   [{status}] {label}: {len(expected)} conferências, {len(errs)} erros de fórmula")
    for p in problems:
        print("      -", p)
    RESULTS.setdefault(CURRENT[0], {})[label] = dict(ok=not problems, checks=len(expected), errors=len(errs))
    return not problems


RESULTS = {}
CURRENT = [None]


def build_module(modname):
    CURRENT[0] = modname
    mod = importlib.import_module(modname)
    dest = os.path.join(ROOT, "planilhas", mod.PASTA)
    os.makedirs(dest, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    print(f"== {mod.NOME}")
    allok = True
    for sample, fname in ((False, "PLANILHA-LIMPA.xlsx"), (True, "EXEMPLO.xlsx")):
        tmp = os.path.join(BUILD, f"{modname}_{fname}")
        bk = Book(tmp, sample=sample, product=mod.NOME)
        exp = mod.build(bk) or {}
        cache = recalc(tmp)
        allok &= check(cache, exp, fname + " (LibreOffice)")
        final = os.path.join(dest, fname)
        bk2 = Book(final, sample=sample, cache=cache, product=mod.NOME)
        mod.build(bk2)
        allok &= check(read_values(final), exp, fname + " (valores gravados)")
    return allok


if __name__ == "__main__":
    wanted = sys.argv[1:] or MODULES
    mods = [m for m in MODULES if any(w in m for w in wanted)] if sys.argv[1:] else MODULES
    ok = True
    for m in mods:
        try:
            ok &= build_module(m)
        except ModuleNotFoundError as e:
            print("   (módulo ausente:", e, ")")
    rp = os.path.join(BUILD, "results.json")
    old = {}
    if os.path.exists(rp):
        old = json.load(open(rp))
    old.update(RESULTS)
    json.dump(old, open(rp, "w"), indent=1)
    sys.exit(0 if ok else 1)
