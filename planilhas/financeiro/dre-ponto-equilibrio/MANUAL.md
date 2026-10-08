# Manual do cliente — DRE e Ponto de Equilíbrio  (versão 1.0)

## 1. Objetivo
Monta o DRE mensal a partir de lançamentos simples e calcula margem de contribuição, ponto de equilíbrio, margem de segurança e faturamento necessário para a meta de lucro.

## 2. Funcionalidades
- DRE pronto a partir de lançamentos simples.
- Ponto de equilíbrio mês a mês e para a meta de lucro.
- Análise vertical automática (% da receita).
- Gráficos de lucro e de receita x equilíbrio.
- Estrutura pensada para pequenas empresas.

**Capacidade:** 1.500 lançamentos por ano.

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
| **Config** | Empresa, ano, lucro desejado e a lista das 10 contas do DRE com o que lançar em cada uma. |
| **Lançamentos** | Todos os lançamentos (1.500 linhas). |
| **DRE** | Demonstração mensal com total do ano e % da receita bruta. |
| **Ponto de Equilíbrio** | Indicadores, PE por mês, situação e gráficos. |

## 6. Manutenção
- **Dados novos:** continue lançando nas linhas seguintes das abas de lançamento. As fórmulas estão prontas até o limite de capacidade (1.500 lançamentos por ano.).
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
