# Manual do cliente — Estoque Inteligente com Curva ABC  (versão 1.0)

## 1. Objetivo
Controle de estoque com entradas e saídas, status (ruptura/repor/ok/excesso), itens parados, lista de compras por fornecedor e Curva ABC automática com gráfico de Pareto.

## 2. Funcionalidades
- Curva ABC automática, sem macros e sem ordenar nada.
- Status e lista de compras prontos para enviar ao fornecedor.
- Itens parados com valor imobilizado em R$.
- Cobertura em dias de cada item.
- Validação de códigos e alertas de lançamento.

**Capacidade:** 300 produtos, 3.000 movimentações, 80 itens na lista de compras.

## 3. Instalação
**Requisitos:** Microsoft Excel 2016 ou superior (Windows/Mac), Excel 365 ou LibreOffice Calc. Funciona no Google Sheets para a maior parte das funções, mas gráficos e formatação condicional podem mudar; prefira o Excel.
**Sem macros e sem complementos:** os arquivos são `.xlsx` comuns; nada precisa ser habilitado além da edição.
**Testes realizados:** todas as fórmulas foram recalculadas no LibreOffice 24.2 e comparadas, uma a uma, com um cálculo independente feito fora da planilha (0 erros de fórmula). Não foi possível testar no Microsoft Excel real nesta rodada: valide em uma cópia antes de vender em escala.

1. Baixe o arquivo `PLANILHA-LIMPA.xlsx` (a loja envia o link de download após a compra).
2. Salve em uma pasta do seu computador ou em um serviço de nuvem (OneDrive, Google Drive).
3. Abra, clique em *Habilitar Edição* e use **Salvar como** para criar a sua cópia de trabalho.
Não há nada para instalar.

## 4. Configuração
Na aba **Config** você informa os dados da empresa e os parâmetros do cálculo. Detalhes do preenchimento no `TUTORIAL.md`. Células amarelas: preencher. Células cinza: cálculo automático.

## 5. Utilização — mapa das abas
| Aba | Função |
|---|---|
| **Início** | Instruções. |
| **Config** | Período de análise, estoque máximo, cortes ABC, categorias, unidades, fornecedores. |
| **Produtos** | Cadastro de até 300 itens. |
| **Movimentações** | Entradas e saídas (3.000 linhas). |
| **Posição** | Estoque atual, status, cobertura, parado, sugestão de compra. |
| **Curva ABC** | Ranking por faturamento e classes A/B/C. |
| **Compras** | Lista de compras com total. |
| **Dashboard** | Indicadores, situação, top 15. |

## 6. Manutenção
- **Dados novos:** continue lançando nas linhas seguintes das abas de lançamento. As fórmulas estão prontas até o limite de capacidade (300 produtos, 3.000 movimentações, 80 itens na lista de compras.).
- **Quando encher:** salve a planilha como arquivo do período (ex.: `2026`) e comece o próximo período a partir da `PLANILHA-LIMPA.xlsx` (levando os saldos iniciais).
- **Listas (categorias, clientes etc.):** edite na aba Config. Evite apagar uma linha da lista que já esteja em uso; troque o nome.
- **Abas de resultado protegidas:** Início e as abas de relatório/dashboard estão protegidas **sem senha** para evitar digitação por engano. Para alterar: *Revisar → Desproteger Planilha*.
- **Não faça:** inserir/excluir colunas nas abas de dados, mover células com fórmulas ou colar sobre as células cinza.
- **Filtros:** use os filtros da linha de cabeçalho para consultar; limpe os filtros antes de lançar novos dados.

## 7. Backup
- Salve uma cópia por semana com a data no nome (`Planilha-2026-10-08.xlsx`).
- Mantenha uma cópia fora do computador (nuvem ou pendrive).
- Antes de qualquer alteração grande, faça *Salvar como* com outro nome.
- Se algo for apagado sem querer: *Ctrl+Z* (desfazer) e, se necessário, abra o backup.

## 8. Segurança e privacidade
Os dados ficam no seu computador. Não envie a planilha com dados de clientes por canais inseguros. Use apenas os dados necessários e respeite a LGPD. Proteja o arquivo com senha em *Arquivo → Informações → Proteger Pasta de Trabalho* se mais pessoas usam o computador.

## 9. Dúvidas e suporte
1. Releia o `TUTORIAL.md` (seções 11 a 13 trazem erros comuns e FAQ).
2. Compare com o `EXEMPLO.xlsx`.
3. Se ainda tiver dúvida, entre em contato com o canal de suporte informado na compra (informe o nome da planilha, a versão 1.0 e envie uma captura de tela).

## 10. Atualizações e licença
- **Atualizações:** correções e melhorias da versão 1.x são enviadas por e-mail/área de membros aos compradores.
- **Licença de uso (modelo, ajuste com seu advogado):** uso por uma empresa/profissional. É proibido revender, redistribuir ou compartilhar o arquivo.
- **Aviso:** a planilha é uma ferramenta gerencial e não substitui orientação contábil, jurídica, fiscal ou médica. Confirme percentuais e regras com seus profissionais.
