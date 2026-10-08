# tools/ — fábrica de planilhas

| Arquivo | Função |
|---|---|
| `lib.py` | Estilos, helpers (banner, KPI, validações), aba Início, cache de valores calculados |
| `products/p01..p10_*.py` | Cada produto: `build(bk)` cria a planilha (limpa ou exemplo) e devolve valores esperados |
| `build.py` | Gera → recalcula no LibreOffice → confere erros e valores esperados → regrava com cache |
| `shots.py` | Capturas de tela (LibreOffice → PDF → PNG) |
| `docs_a.py`, `docs_b.py` | Conteúdo de tutorial/manual/vendas de cada produto |
| `gen_docs.py` | Renderiza documentação, catálogo, kits e `site/catalog.js` |
| `opportunities_data.py`, `gen_opportunities.py` | Base de oportunidades e `market-research/opportunities.md` |
| `quality_report.py`, `package.py` | `QUALIDADE.md` e pacotes `.zip` de entrega |

## Criar um produto novo
1. Copie um `products/pNN_*.py` parecido e adapte `build()`; use `bk.sample` para os dados fictícios e devolva um dicionário `{(aba, "A1"): valor}` com valores calculados em Python.
2. Registre o módulo em `MODULES` (`build.py`), em `SHOTS` (`shots.py`) e escreva o spec em `docs_*.py`.
3. `python3 tools/build.py pNN` só aprova se as fórmulas baterem com o cálculo independente.
