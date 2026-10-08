# -*- coding: utf-8 -*-
"""Gera dist/<produto>.zip e dist/<kit>.zip com os arquivos de entrega ao cliente."""
import importlib, os, sys, zipfile, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "products"))
import build as B
from gen_docs import KITS, SPECS

ROOT = B.ROOT
DIST = os.path.join(ROOT, "dist")
FILES = ["PLANILHA-LIMPA.xlsx", "EXEMPLO.xlsx", "TUTORIAL.md", "MANUAL.md", "GUIA-RAPIDO.md"]


def add_product(z, mod, prefix=""):
    d = os.path.join(ROOT, "planilhas", mod.PASTA)
    nome = os.path.basename(mod.PASTA)
    for f in FILES:
        z.write(os.path.join(d, f), f"{prefix}{nome}/{f}")
    img = os.path.join(d, "img")
    for f in sorted(os.listdir(img)):
        z.write(os.path.join(img, f), f"{prefix}{nome}/img/{f}")


def main():
    os.makedirs(DIST, exist_ok=True)
    mods = {s["mod"]: importlib.import_module(s["mod"]) for s in SPECS}
    for k, m in mods.items():
        with zipfile.ZipFile(os.path.join(DIST, f"{os.path.basename(m.PASTA)}.zip"), "w", zipfile.ZIP_DEFLATED) as z:
            add_product(z, m)
    for nome, ms, preco, hist, itens in KITS:
        slug = nome.lower().replace(" ", "-").replace("é", "e").replace("ç", "c").replace("ó", "o").replace("á", "a").replace("í", "i").replace("ã", "a")
        with zipfile.ZipFile(os.path.join(DIST, f"{slug}.zip"), "w", zipfile.ZIP_DEFLATED) as z:
            for k in ms:
                add_product(z, mods[k], prefix="")
    print("zips em", DIST, len(os.listdir(DIST)))


if __name__ == "__main__":
    main()
