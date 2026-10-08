# Relatório de qualidade — Carvex XLS v1.0

Gerado automaticamente por `tools/quality_report.py` a partir dos arquivos finais.

## Resumo por produto
| Produto | Abas visíveis | Fórmulas (limpa) | Conferências numéricas | Erros de fórmula | Regras de validação | Gráficos | Fórmulas OK | Limpa sem dados fictícios | Docs | Material de venda | Capturas | Evidência da dor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fluxo de Caixa Inteligente | 5 | 4.342 | 5 | 0 | 10 | 2 | ✅ | ✅ | ✅ | ✅ | 4 | Alta |
| Precificador de Produtos e Serviços | 6 | 3.947 | 12 | 0 | 12 | 1 | ✅ | ✅ | ✅ | ✅ | 4 | Alta |
| Estoque Inteligente com Curva ABC | 8 | 19.125 | 13 | 0 | 15 | 3 | ✅ | ✅ | ✅ | ✅ | 5 | Alta |
| Contas a Pagar e Receber com Inadimplência | 5 | 11.496 | 25 | 0 | 15 | 2 | ✅ | ✅ | ✅ | ✅ | 3 | Alta |
| CRM e Funil de Vendas com Follow-up | 7 | 9.200 | 29 | 0 | 9 | 4 | ✅ | ✅ | ✅ | ✅ | 5 | Média |
| DRE e Ponto de Equilíbrio | 5 | 4.883 | 12 | 0 | 5 | 2 | ✅ | ✅ | ✅ | ✅ | 4 | Média |
| Ficha Técnica e CMV para Restaurantes | 8 | 6.595 | 27 | 0 | 16 | 3 | ✅ | ✅ | ✅ | ✅ | 4 | Alta |
| Ordem de Serviço para Oficinas | 10 | 36.783 | 24 | 0 | 20 | 1 | ✅ | ✅ | ✅ | ✅ | 3 | Média |
| Controle de Obras (Orçado x Realizado) | 7 | 3.767 | 30 | 0 | 20 | 2 | ✅ | ✅ | ✅ | ✅ | 3 | Média |
| Agenda, Faltas e Retornos para Clínicas | 6 | 42.880 | 38 | 0 | 14 | 2 | ✅ | ✅ | ✅ | ✅ | 4 | Média |

**Conferências numéricas** = valores calculados pelas fórmulas (recalculadas no LibreOffice) comparados com o mesmo cálculo feito de forma independente em Python, a partir dos dados do exemplo (totais, KPIs, status, ranking, classes, previsões). Todas passaram.
**Erros de fórmula** = células com `#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, `#N/A`, `#NUM!` nas versões limpa e exemplo: 0 em todos.

## Checklist de qualidade (por planilha)
- [x] Fórmulas funcionando e testadas (conferências acima)
- [x] Nenhum `#REF!`, `#VALUE!` ou `#DIV/0!` (varredura de todas as células das duas versões)
- [x] Validações e listas suspensas criadas (colunas "Regras de validação"); as fórmulas que dependem delas (nomes definidos) foram recalculadas com sucesso
- [x] Gráficos e dashboard renderizados (capturas em `img/` geradas pelo LibreOffice)
- [x] Formatação profissional padronizada (identidade verde Carvex XLS; células de entrada amarelas, cálculo cinza)
- [x] Dados fictícios separados (`EXEMPLO.xlsx`) e versão limpa criada (`PLANILHA-LIMPA.xlsx`), sem texto de exemplo
- [x] Tutorial, manual, guia rápido, README e FAQ criados
- [x] Material comercial, preço sugerido e público-alvo definidos
- [x] Problema validado por pesquisa (ver força da evidência em `market-research/opportunities.md`)

## Limites conhecidos (seja transparente com o cliente)
1. **Excel real não foi testado.** A bateria usou o LibreOffice 24.2. As funções usadas (SUMIFS, COUNTIFS, INDEX/MATCH, SUMPRODUCT, IFERROR, DATE, WEEKDAY...) existem no Excel 2016+, mas recomenda-se abrir cada arquivo no Excel e conferir o Dashboard antes de vender em escala.
2. **Comportamento interativo** das listas suspensas e validações (mensagens de erro ao digitar) foi criado, mas não testado clicando em um Excel real.
3. **Google Sheets**: cálculos devem funcionar; gráficos combinados e formatação condicional podem se comportar diferente.
4. Evidências marcadas como **Média/Fraca** vêm de conteúdo de fornecedores ou fontes secundárias; use-as como indicação, não como estatística oficial.
5. Percentuais (impostos, juros, CLT, etc.) são parâmetros do cliente; a planilha não substitui contador, advogado ou profissional de saúde.
