# Guia rápido — Ordem de Serviço para Oficinas  (5 minutos)

**Objetivo:** ter a planilha funcionando com seus primeiros dados em menos de 5 minutos.

- [ ] **Minuto 0–1 · Prepare.** Abra `PLANILHA-LIMPA.xlsx` → *Habilitar Edição* → *Salvar como* com o nome da sua empresa.
- [ ] **Minuto 1–2 · Configure a oficina.** Abra **Config**: **C6** valor da hora de mão de obra, **C7** markup padrão sobre peças (ex.: 40%), **C8** comissão dos mecânicos sobre a mão de obra, **C9** prazo máximo de uma OS aberta (dias). Cadastre os mecânicos em **E5:E14** e as formas de pagamento em **G5:G14**.
- [ ] **Minuto 2–4 · Abra a OS e lance as peças.** Abra **OS**. Em uma linha nova: **Nº OS** (único), **Data de entrada**, **Placa** (lista), **Km**, **Serviço**, **Mecânico**, **Status** e **Horas de mão de obra**. Abra **Itens da OS** e, para cada peça usada, informe o **Nº OS**, o **Código da peça** e a **Quantidade**. O preço vem da tabela de peças (ou digite outro).
- [ ] **Minuto 4–5 · Veja o resultado.** Ao entregar, mude para **Entregue** e preencha **Data de entrega**, **Forma de pagamento** e **Valor recebido**. A OS calcula **TOTAL**, **Custo das peças**, **Comissão**, **LUCRO BRUTO**, **Margem** e **Saldo a receber**; a coluna **ALERTA** mostra ATRASADA ou Cobrar.

## Regras de ouro
1. Preencha **só** as células amarelas.
2. Escolha nomes e códigos **pela lista suspensa**.
3. Use datas no formato **dd/mm/aaaa** e valores **sem sinal de menos**.
4. Salve uma cópia por semana.

## Travou?
Compare com o `EXEMPLO.xlsx`; leia as seções *Erros comuns* e *FAQ* do `TUTORIAL.md`.
