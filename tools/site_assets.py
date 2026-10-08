# -*- coding: utf-8 -*-
"""Otimiza as capturas de tela (planilhas/*/img -> site/img/*.webp) para a página de vendas."""
import json, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICK = {'fluxo-de-caixa': ('dashboard', 'lancamentos'), 'precificador': ('resumo', 'produtos'), 'estoque-inteligente': ('dashboard', 'posicao'),
        'contas-pagar-receber': ('painel', 'receber'), 'crm-funil': ('dashboard', 'leads'), 'dre-ponto-equilibrio': ('ponto-equilibrio', 'dre'),
        'ficha-tecnica-cmv': ('dashboard', 'pratos'), 'ordem-de-servico': ('dashboard', 'os'), 'controle-de-obras': ('resumo', 'cronograma'), 'agenda-retornos': ('relatorios', 'agenda')}


def main():
    cat = json.load(open(os.path.join(ROOT, 'site', 'catalog.json')))
    os.makedirs(os.path.join(ROOT, 'site', 'img'), exist_ok=True)
    for p in cat['produtos']:
        pid = p['id']; a, b = PICK[pid]
        for kind, name in (('dash', a), ('sheet', b)):
            im = Image.open(os.path.join(ROOT, 'planilhas', p['pasta'], 'img', name + '.png')).convert('RGB')
            if im.width > 1500:
                im = im.resize((1500, int(im.height * 1500 / im.width)), Image.LANCZOS)
            im.save(os.path.join(ROOT, 'site', 'img', f'{pid}-{kind}.webp'), 'WEBP', quality=84, method=6)
    print('imagens do site ok')


if __name__ == '__main__':
    main()
