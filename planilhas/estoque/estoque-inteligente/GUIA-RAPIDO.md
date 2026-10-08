# Guia rápido — Estoque Inteligente com Curva ABC  (5 minutos)

**Objetivo:** ter a planilha funcionando com seus primeiros dados em menos de 5 minutos.

- [ ] **Minuto 0–1 · Prepare.** Abra `PLANILHA-LIMPA.xlsx` → *Habilitar Edição* → *Salvar como* com o nome da sua empresa.
- [ ] **Minuto 1–2 · Configure e cadastre os produtos.** Abra **Config**: em **C6** o período para medir vendas (padrão 90 dias), em **C7** os dias sem saída para considerar 'Parado', em **C8** o fator do estoque máximo (2 = dobro do mínimo). Cadastre categorias (**E5:E34**), unidades (**F5:F34**) e fornecedores (**G5:G34**).
- [ ] **Minuto 2–4 · Lance as movimentações.** Abra **Movimentações**. Cada linha é um movimento: **Data**, **Código** (lista), **Tipo** (Entrada ou Saída) e **Quantidade**. Entrada = compra, devolução de cliente. Saída = venda, perda, consumo interno.
- [ ] **Minuto 4–5 · Veja o resultado.** Abra **Posição**: **ESTOQUE ATUAL** e **STATUS** (RUPTURA = zerado; REPOR = no mínimo ou abaixo; EXCESSO = acima do máximo; OK). A coluna **Parado?** marca itens com estoque e sem saída há mais do período definido; **Valor parado** soma o dinheiro empatado.

## Regras de ouro
1. Preencha **só** as células amarelas.
2. Escolha nomes e códigos **pela lista suspensa**.
3. Use datas no formato **dd/mm/aaaa** e valores **sem sinal de menos**.
4. Salve uma cópia por semana.

## Travou?
Compare com o `EXEMPLO.xlsx`; leia as seções *Erros comuns* e *FAQ* do `TUTORIAL.md`.
