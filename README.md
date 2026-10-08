# Carvex XLS — Fábrica de Planilhas Empresariais

Biblioteca comercial de planilhas Excel **prontas para vender**, cada uma nascida de uma dor real de empresas:

**DOR REAL → SOLUÇÃO → PLANILHA → TUTORIAL → PRODUTO → VENDA**

| Onde | O que tem |
|---|---|
| [`market-research/opportunities.md`](market-research/opportunities.md) | 35 oportunidades pesquisadas na web, com evidência, concorrentes, diferencial e nota (0-100) |
| [`planilhas/`](planilhas/) | Os 10 produtos da primeira leva, cada um em sua pasta |
| [`kits/`](kits/) | 8 kits por tipo de negócio, com desconto |
| [`CATALOGO.md`](CATALOGO.md) | Catálogo com categoria, público, problema, preço e status |
| [`QUALIDADE.md`](QUALIDADE.md) | Checklist de qualidade medido nos arquivos + limites conhecidos |
| [`site/`](site/) | Página de vendas **Carvex XLS** (HTML/CSS/JS estático) |
| [`tools/`](tools/) | Gerador das planilhas, da documentação, das capturas e dos testes |

## Os 10 produtos

| # | Produto | Pasta | Nota |
|---|---|---|---|
| 1 | Fluxo de Caixa Inteligente | `planilhas/financeiro/fluxo-de-caixa` | 98 |
| 2 | Precificador de Produtos e Serviços | `planilhas/precificacao/precificador` | 96 |
| 3 | Estoque Inteligente com Curva ABC | `planilhas/estoque/estoque-inteligente` | 95 |
| 4 | Contas a Pagar e Receber com Inadimplência | `planilhas/financeiro/contas-pagar-receber` | 94 |
| 5 | CRM e Funil de Vendas com Follow-up | `planilhas/vendas/crm-funil` | 92 |
| 6 | DRE e Ponto de Equilíbrio | `planilhas/financeiro/dre-ponto-equilibrio` | 91 |
| 7 | Ficha Técnica e CMV para Restaurantes | `planilhas/restaurantes/ficha-tecnica-cmv` | 90 |
| 8 | Ordem de Serviço para Oficinas | `planilhas/oficinas/ordem-de-servico` | 88 |
| 9 | Controle de Obras (Orçado x Realizado) | `planilhas/construcao/controle-de-obras` | 87 |
| 10 | Agenda, Faltas e Retornos para Clínicas | `planilhas/clinicas/agenda-retornos` | 86 |

## O que cada pasta de produto contém
```
planilhas/<categoria>/<produto>/
├── PLANILHA-LIMPA.xlsx   versão do comprador (sem dados fictícios)
├── EXEMPLO.xlsx          mesma planilha com dados 100% fictícios
├── README.md  TUTORIAL.md  MANUAL.md  GUIA-RAPIDO.md
├── img/                  capturas de tela do exemplo
└── sales/                descricao, beneficios, publico-alvo, argumentos, faq, pitch, preco
```

## Como entregar ao cliente
1. Compacte `PLANILHA-LIMPA.xlsx`, `EXEMPLO.xlsx`, `TUTORIAL.md`, `MANUAL.md` e `GUIA-RAPIDO.md` (ou converta os `.md` em PDF) em um `.zip`.
2. Suba no seu checkout/área de membros (Hotmart, Kiwify, Eduzz, Mercado Livre, loja própria...).
3. Configure o link de compra e o WhatsApp na página de vendas: `site/config.js`.

## Padrão das planilhas
- **Amarelo** = você preenche · **Cinza** = cálculo automático · **Verde-escuro** = cabeçalho.
- Sem macros; fórmulas SUMIFS/COUNTIFS/INDEX-MATCH/SUMPRODUCT; listas suspensas, validações, formatação condicional, gráficos e dashboard.
- Aba **Início** com instruções e mapa; abas de relatório protegidas **sem senha**.

## Qualidade e testes (resumo)
- 263 conferências numéricas independentes passaram e há **0 erros de fórmula** (`#REF!`, `#VALUE!`, `#DIV/0!`...) nas 20 planilhas. Veja [`QUALIDADE.md`](QUALIDADE.md).
- Testado em **LibreOffice 24.2**. **Teste no Microsoft Excel real ainda pendente**: abra cada `EXEMPLO.xlsx` no Excel e confira o Dashboard antes de escalar a venda.

## Regenerar tudo
```bash
pip install xlsxwriter openpyxl pillow     # + LibreOffice (soffice) e poppler (pdftoppm)
python3 tools/gen_opportunities.py         # market-research/opportunities.md
python3 tools/build.py                     # gera, recalcula, confere e grava as 20 planilhas
python3 tools/shots.py                     # capturas de tela (img/)
python3 tools/gen_docs.py                  # tutoriais, manuais, vendas, catálogo, kits, site/catalog.js
python3 tools/quality_report.py            # QUALIDADE.md
python3 tools/package.py                   # dist/*.zip prontos para entrega
```

## Roadmap
Os 25 produtos seguintes estão ranqueados em `CATALOGO.md` (Comissão e Metas, Separação PF/PJ, Precificador Marketplace, Capital de Giro, Aluguéis, RH, Salão, Escola, Marketing...). Os de **evidência Fraca** devem ser validados com clientes antes de produzir.
