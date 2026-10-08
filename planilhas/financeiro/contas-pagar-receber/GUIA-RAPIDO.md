# Guia rápido — Contas a Pagar e Receber com Inadimplência  (5 minutos)

**Objetivo:** ter a planilha funcionando com seus primeiros dados em menos de 5 minutos.

- [ ] **Minuto 0–1 · Prepare.** Abra `PLANILHA-LIMPA.xlsx` → *Habilitar Edição* → *Salvar como* com o nome da sua empresa.
- [ ] **Minuto 1–2 · Configure e cadastre clientes e fornecedores.** Abra **Config**: **C6** multa (ex.: 2%), **C7** juros ao mês (ex.: 1%), **C8** dias de alerta para pagar (ex.: 7). Cadastre clientes com telefone em **E5:F104** e fornecedores em **H5:H64**.
- [ ] **Minuto 2–4 · Lance receber e pagar.** Abra **Receber**: preencha **Cliente** (lista), **Descrição**, **Emissão**, **Vencimento** e **Valor**. Quando o cliente pagar, preencha **Data do pagamento**, **Valor pago** e **Forma**. Pagamento parcial? Digite um valor menor: o saldo continua em aberto.
- [ ] **Minuto 4–5 · Veja o resultado.** Em **Receber**, filtre o Status 'Vencido' e copie a coluna **Mensagem de cobrança** (WhatsApp). Em **Pagar**, filtre 'Vencida' e 'Vence em breve' para priorizar pagamentos.

## Regras de ouro
1. Preencha **só** as células amarelas.
2. Escolha nomes e códigos **pela lista suspensa**.
3. Use datas no formato **dd/mm/aaaa** e valores **sem sinal de menos**.
4. Salve uma cópia por semana.

## Travou?
Compare com o `EXEMPLO.xlsx`; leia as seções *Erros comuns* e *FAQ* do `TUTORIAL.md`.
