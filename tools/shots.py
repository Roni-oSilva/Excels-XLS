# -*- coding: utf-8 -*-
"""Gera capturas de tela (PNG) das abas principais do EXEMPLO.xlsx via LibreOffice -> PDF -> PNG."""
import importlib, os, subprocess, sys, glob, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "products"))
from PIL import Image, ImageChops
from lib import Book
import build as B

SHOTS = {
    "p01_fluxo": [("inicio", "Início"), ("lancamentos", "Lançamentos"), ("mensal", "Mensal"), ("dashboard", "Dashboard")],
    "p02_precificador": [("inicio", "Início"), ("produtos", "Produtos"), ("simulador", "Simulador"), ("resumo", "Resumo")],
    "p03_estoque": [("inicio", "Início"), ("posicao", "Posição"), ("curva-abc", "Curva ABC"), ("compras", "Compras"), ("dashboard", "Dashboard")],
    "p04_contas": [("inicio", "Início"), ("receber", "Receber"), ("painel", "Painel")],
    "p05_crm": [("inicio", "Início"), ("leads", "Leads"), ("agenda", "Agenda"), ("funil", "Funil"), ("dashboard", "Dashboard")],
    "p06_dre": [("inicio", "Início"), ("lancamentos", "Lançamentos"), ("dre", "DRE"), ("ponto-equilibrio", "Ponto de Equilíbrio")],
    "p07_ficha": [("inicio", "Início"), ("pratos", "Pratos"), ("cmv-mensal", "CMV Mensal"), ("dashboard", "Dashboard")],
    "p08_oficina": [("inicio", "Início"), ("os", "OS"), ("dashboard", "Dashboard")],
    "p09_obras": [("inicio", "Início"), ("cronograma", "Cronograma"), ("resumo", "Resumo")],
    "p10_clinica": [("inicio", "Início"), ("agenda", "Agenda"), ("pendencias", "Pendências"), ("relatorios", "Relatórios")],
}


def crop(path):
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    # ignora o rodapé de impressão ("Página 1 de 1") que fica na margem inferior da página
    body = im.crop((0, 0, im.width, im.height - 70))
    bbox = ImageChops.difference(body, bg.crop((0, 0, body.width, body.height))).getbbox()
    if bbox:
        l, t, r, b = bbox
        im = im.crop((max(0, l - 14), max(0, t - 14), min(im.width, r + 14), min(im.height, b + 14)))
    im.save(path, optimize=True)


def main(only=None):
    for mod_name, items in SHOTS.items():
        if only and not any(o in mod_name for o in only):
            continue
        mod = importlib.import_module(mod_name)
        dest = os.path.join(B.ROOT, "planilhas", mod.PASTA, "img")
        os.makedirs(dest, exist_ok=True)
        print("==", mod.NOME)
        for fname, sheet in items:
            tmp = os.path.join(B.BUILD, f"shot_{mod_name}_{fname}.xlsx")
            bk = Book(tmp, sample=True, product=mod.NOME, shots=[sheet])
            mod.build(bk)
            outdir = os.path.join(B.BUILD, "pdf"); os.makedirs(outdir, exist_ok=True)
            B.recalc(tmp)   # garante perfil LO + recálculo (também gera xlsx recalculado)
            rec = os.path.join(B.BUILD, "recalc", os.path.basename(tmp))
            subprocess.run(["soffice", "--headless", "--norestore", f"-env:UserInstallation=file://{B.BUILD}/lo_profile", "--convert-to", "pdf", "--outdir", outdir, tmp],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
            pdf = os.path.join(outdir, os.path.basename(tmp).replace(".xlsx", ".pdf"))
            prefix = os.path.join(outdir, f"{mod_name}_{fname}")
            subprocess.run(["pdftoppm", "-r", "125", "-png", "-f", "1", "-l", "1", pdf, prefix], check=True)
            png = sorted(glob.glob(prefix + "*.png"))[0]
            final = os.path.join(dest, f"{fname}.png")
            os.replace(png, final)
            crop(final)
            print("  ", final.replace(B.ROOT + "/", ""))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
