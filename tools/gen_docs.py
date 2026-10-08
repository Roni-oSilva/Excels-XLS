# -*- coding: utf-8 -*-
"""Gera toda a documentação e material de venda a partir de docs_a.py / docs_b.py.

Os números dos exemplos são lidos do EXEMPLO.xlsx final (valores gravados), então o texto sempre
bate com o que o cliente vê ao abrir a planilha.
"""
import importlib, os, re, sys, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "products"))
import openpyxl
from docs_a import SPECS as SA
from docs_b import SPECS as SB
from opportunities_data import OPS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = SA + SB
OPBY = {o["id"]: o for o in OPS}
LO_VERSION = "LibreOffice 24.2"

KITS = [
    ("Kit Pequeno Empresário", ["p01_fluxo", "p04_contas", "p06_dre", "p02_precificador"], 147,
     "Para o dono que quer sair do achismo: enxergar o caixa, controlar vencimentos, saber o lucro real e precificar certo.",
     ["Fluxo de Caixa Inteligente (saldo e previsão)", "Contas a Pagar e Receber (vencimentos e cobrança)", "DRE e Ponto de Equilíbrio (lucro e meta)", "Precificador (preço certo)"]),
    ("Kit Loja", ["p03_estoque", "p02_precificador", "p04_contas", "p01_fluxo"], 157,
     "Para lojas e e-commerce: estoque sem excesso nem falta, preço com margem, vendas a prazo sob controle e caixa previsível.",
     ["Estoque Inteligente com Curva ABC", "Precificador", "Contas a Pagar e Receber", "Fluxo de Caixa Inteligente"]),
    ("Kit Restaurante", ["p07_ficha", "p03_estoque", "p02_precificador", "p01_fluxo", "p04_contas"], 197,
     "Para bares e restaurantes: custo por prato, CMV real, estoque de insumos, preço de bebidas/porções e caixa.",
     ["Ficha Técnica e CMV", "Estoque Inteligente (insumos e bebidas)", "Precificador (bebidas, combos e serviços)", "Fluxo de Caixa", "Contas a Pagar e Receber"]),
    ("Kit Oficina", ["p08_oficina", "p03_estoque", "p01_fluxo", "p04_contas"], 167,
     "Para oficinas: OS com lucro por serviço, controle de peças e do caixa, e cobrança organizada.",
     ["Ordem de Serviço para Oficinas", "Estoque Inteligente (peças, óleos e consumíveis em volume)", "Fluxo de Caixa", "Contas a Pagar e Receber"]),
    ("Kit Construtora", ["p09_obras", "p04_contas", "p01_fluxo", "p06_dre"], 167,
     "Para pequenas construtoras: margem da obra em tempo real, caixa da empresa, contas e DRE consolidado.",
     ["Controle de Obras", "Contas a Pagar e Receber", "Fluxo de Caixa (empresa)", "DRE e Ponto de Equilíbrio (empresa)"]),
    ("Kit Clínica", ["p10_clinica", "p01_fluxo", "p04_contas", "p06_dre"], 149,
     "Para clínicas e consultórios: menos faltas, retornos agendados, caixa, recebíveis de convênio e lucro.",
     ["Agenda, Faltas e Retornos", "Fluxo de Caixa", "Contas a Pagar e Receber (convênios)", "DRE e Ponto de Equilíbrio"]),
    ("Kit Comercial e Serviços", ["p05_crm", "p02_precificador", "p04_contas", "p01_fluxo"], 149,
     "Para quem vende serviços: funil organizado, preço certo para o serviço, cobrança e caixa.",
     ["CRM e Funil de Vendas", "Precificador (serviços por hora)", "Contas a Pagar e Receber", "Fluxo de Caixa"]),
    ("Kit Completo", [s["mod"] for s in SPECS], 397,
     "As 10 planilhas da primeira leva, para quem quer estruturar a gestão inteira.",
     ["Todas as 10 planilhas da biblioteca", "Atualizações da versão 1.x"]),
]


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def reais(v):
    return "R$ " + f"{int(v):,}".replace(",", ".")


def fmt_val(v, kind):
    if v is None or v == "":
        return "-"
    if kind == "money":
        return brl(float(v))
    if kind == "pct":
        return f"{float(v)*100:.1f}%".replace(".", ",")
    if kind == "int":
        return f"{int(round(float(v))):,}".replace(",", ".")
    if kind == "n1":
        return f"{float(v):.1f}".replace(".", ",") if not (isinstance(v, float) and abs(v) < 1 and kind == "n1" and False) else str(v)
    return str(v)


def fill(text, wb):
    def rep(m):
        ref, kind = m.group(1), m.group(2)
        sheet, cell = ref.rsplit("!", 1)
        v = wb[sheet][cell].value
        if kind == "n1":
            # diferenças em pontos percentuais vêm como fração (0.034): mostrar em pontos
            fv = float(v)
            if abs(fv) < 0.5 and "Dashboard!G5" in ref:
                return f"{fv*100:.1f}".replace(".", ",")
            return f"{fv:.1f}".replace(".", ",")
        return fmt_val(v, kind)
    return re.sub(r"\{\{([^|}]+)\|(\w+)\}\}", rep, text)


def w(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt.rstrip() + "\n")


# --------------------------------------------------------------------------------------------- blocos
COMPAT = f"""**Requisitos:** Microsoft Excel 2016 ou superior (Windows/Mac), Excel 365 ou LibreOffice Calc. Funciona no Google Sheets para a maior parte das funções, mas gráficos e formatação condicional podem mudar; prefira o Excel.
**Sem macros e sem complementos:** os arquivos são `.xlsx` comuns; nada precisa ser habilitado além da edição.
**Testes realizados:** todas as fórmulas foram recalculadas no {LO_VERSION} e comparadas, uma a uma, com um cálculo independente feito fora da planilha (0 erros de fórmula). Não foi possível testar no Microsoft Excel real nesta rodada: valide em uma cópia antes de vender em escala."""


def readme(s, mod, pasta):
    o = OPBY[s["op"]]
    return f"""# {s['comercial']}

> {s['slogan']}

**Categoria:** {s['categoria']}  ·  **Versão:** 1.0  ·  **Nota de oportunidade:** {o['nota']}/100

## O que é
{s['resumo']}

## Para quem é
{chr(10).join('- ' + p for p in s['publico'])}

## Problema que resolve
{s['dor']}

*Evidência de mercado:* [{o['evid'][0][0][:110]}...]({o['evid'][0][1]}) (mais em [`market-research/opportunities.md`](../../../market-research/opportunities.md)).

## Funcionalidades
{chr(10).join('- ' + v for v in s['vantagens'])}

Abas: {', '.join('**' + a + '**' for a, _ in s['abas'])}.
Capacidade: {s['cap']}

## Como começar (5 minutos)
Leia o [`GUIA-RAPIDO.md`](GUIA-RAPIDO.md). Para o passo a passo completo, o [`TUTORIAL.md`](TUTORIAL.md).

## Arquivos disponíveis
| Arquivo | Para que serve |
|---|---|
| `PLANILHA-LIMPA.xlsx` | A versão que o comprador usa (sem dados fictícios) |
| `EXEMPLO.xlsx` | A mesma planilha preenchida com dados 100% fictícios |
| `TUTORIAL.md` | Passo a passo em 13 seções, com exemplo prático |
| `MANUAL.md` | Manual do cliente (instalação, uso, manutenção, backup) |
| `GUIA-RAPIDO.md` | Comece em 5 minutos |
| `img/` | Capturas de tela do exemplo |
| `sales/` | Material comercial: descrição, benefícios, público, argumentos, FAQ, pitch e preço |

## Preço sugerido
Individual {reais(s['preco'][0])} · promocional {reais(s['preco'][1])} · premium {reais(s['preco'][2])}. Detalhes em [`sales/preco.md`](sales/preco.md).
"""


def tutorial(s, wb):
    def steps(p):
        titulo, bullets, img = p
        out = "\n".join(f"{i}. {b}" for i, b in enumerate(bullets, 1))
        return titulo, out, img
    t1, b1, i1 = steps(s["passo1"]); t2, b2, i2 = steps(s["passo2"]); t3, b3, i3 = steps(s["passo3"])
    ex = fill(s["exemplo"][0], wb) + "\n\n" + "\n".join("- " + fill(x, wb) for x in s["exemplo"][1:])
    return f"""# Tutorial — {s['comercial']}

> Leia na ordem. Em 20 minutos você terá a planilha funcionando com os seus dados.

## 1. Para que serve?
{chr(10).join('- ' + x for x in s['para_que'])}

## 2. Para quem serve?
{chr(10).join('- ' + x for x in s['publico'])}

## 3. O que você precisa antes de começar?
Separe estas informações (leva cerca de 15 minutos):
{chr(10).join('- ' + x for x in s['antes'])}

## 4. Como abrir a planilha
1. Abra o arquivo **`PLANILHA-LIMPA.xlsx`** no Excel (ou LibreOffice).
2. Se aparecer a faixa amarela *Modo de Exibição Protegido*, clique em **Habilitar Edição**.
3. Clique em **Arquivo → Salvar como** e salve uma cópia com o nome da sua empresa (ex.: `{s['comercial'].split(' ')[0]}-MinhaEmpresa.xlsx`). **Nunca trabalhe no arquivo original**: ele é a sua cópia de segurança.
4. Na primeira aba (**Início**) leia o resumo e veja o mapa das abas (clique nos nomes para navegar).
5. Quer ver tudo funcionando antes? Abra **`EXEMPLO.xlsx`** (dados fictícios) e compare com a sua.

**Legenda de cores:** células **amarelas** = você preenche; células **cinza** = cálculo automático (não digite); cabeçalhos **verde-escuro** = títulos de coluna.

## 5. Primeiro passo — {t1}
{b1}

![{t1}]({i1})

## 6. Segundo passo — {t2}
{b2}

![{t2}]({i2})

## 7. Terceiro passo — {t3}
{b3}

![{t3}]({i3})

## 8. Como interpretar os resultados
| Indicador | Como ler |
|---|---|
{chr(10).join(f'| **{a}** | {b} |' for a, b in s['indicadores'])}

## 9. Exemplo prático
{ex}

*(Todos os dados do `EXEMPLO.xlsx` são fictícios e não representam pessoas ou empresas reais.)*

## 10. Como atualizar
**Diariamente**
{chr(10).join('- ' + x for x in s['diario'])}

**Semanalmente**
{chr(10).join('- ' + x for x in s['semanal'])}

**Mensalmente**
{chr(10).join('- ' + x for x in s['mensal'])}

## 11. Erros comuns
{chr(10).join(f'{i}. {e}' for i, (e, _) in enumerate(s['erros'], 1))}

## 12. Como corrigir
{chr(10).join(f'{i}. **{e}** → {c}' for i, (e, c) in enumerate(s['erros'], 1))}

Se aparecer algo estranho (células vazias onde deveria haver número), confira: (a) a data de hoje na aba Config, (b) se os nomes (códigos, etapas, clientes) foram escolhidos pela lista suspensa e (c) se você digitou nas células **cinza**. Para restaurar uma fórmula apagada por engano, copie a mesma célula do `EXEMPLO.xlsx`.

## 13. Perguntas frequentes
{chr(10).join(f'**{q}**  {a}' + chr(10) for q, a in s['faq'])}
"""


def manual(s):
    abas = "\n".join(f"| **{a}** | {d} |" for a, d in s["abas"])
    return f"""# Manual do cliente — {s['comercial']}  (versão 1.0)

## 1. Objetivo
{s['resumo']}

## 2. Funcionalidades
{chr(10).join('- ' + v for v in s['vantagens'])}

**Capacidade:** {s['cap']}

## 3. Instalação
{COMPAT}

1. Baixe o arquivo `PLANILHA-LIMPA.xlsx` (a loja envia o link de download após a compra).
2. Salve em uma pasta do seu computador ou em um serviço de nuvem (OneDrive, Google Drive).
3. Abra, clique em *Habilitar Edição* e use **Salvar como** para criar a sua cópia de trabalho.
Não há nada para instalar.

## 4. Configuração
Na aba **Config** você informa os dados da empresa e os parâmetros do cálculo. Detalhes do preenchimento no `TUTORIAL.md`. Células amarelas: preencher. Células cinza: cálculo automático.

## 5. Utilização — mapa das abas
| Aba | Função |
|---|---|
{abas}

## 6. Manutenção
- **Dados novos:** continue lançando nas linhas seguintes das abas de lançamento. As fórmulas estão prontas até o limite de capacidade ({s['cap']}).
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
"""


def guia(s):
    p1, p2, p3 = s["passo1"], s["passo2"], s["passo3"]
    return f"""# Guia rápido — {s['comercial']}  (5 minutos)

**Objetivo:** ter a planilha funcionando com seus primeiros dados em menos de 5 minutos.

- [ ] **Minuto 0–1 · Prepare.** Abra `PLANILHA-LIMPA.xlsx` → *Habilitar Edição* → *Salvar como* com o nome da sua empresa.
- [ ] **Minuto 1–2 · {p1[0]}.** {p1[1][0]} {p1[1][1] if len(p1[1]) > 1 else ''}
- [ ] **Minuto 2–4 · {p2[0]}.** {p2[1][0]} {p2[1][1] if len(p2[1]) > 1 else ''}
- [ ] **Minuto 4–5 · Veja o resultado.** {p3[1][0]} {p3[1][1] if len(p3[1]) > 1 else ''}

## Regras de ouro
1. Preencha **só** as células amarelas.
2. Escolha nomes e códigos **pela lista suspensa**.
3. Use datas no formato **dd/mm/aaaa** e valores **sem sinal de menos**.
4. Salve uma cópia por semana.

## Travou?
Compare com o `EXEMPLO.xlsx`; leia as seções *Erros comuns* e *FAQ* do `TUTORIAL.md`.
"""


def sales(s, dest):
    o = OPBY[s["op"]]
    ev = "\n".join(f"- {t}" + (f" ([fonte]({u}))" if u else "") for t, u in o["evid"])
    desc = f"""# {s['comercial']} — Descrição

**Nome comercial:** {s['comercial']}
**Slogan:** {s['slogan']}

## O problema
{s['dor']}

Isso não é impressão: {ev.splitlines()[0][2:]}

## A solução
{s['resumo']}

## O que você recebe
- `PLANILHA-LIMPA.xlsx` pronta para usar (abas: {', '.join(a for a, _ in s['abas'])}).
- `EXEMPLO.xlsx` preenchida com dados fictícios para você entender em minutos.
- Tutorial passo a passo, manual do cliente e guia rápido (5 minutos).
- Fórmulas verificadas, listas suspensas, validações e dashboard.
- Atualizações da versão 1.x.

## Funcionalidades
{chr(10).join('- ' + v for v in s['vantagens'])}
- Capacidade: {s['cap']}

## Texto para a página de venda (copie e adapte)
**{s['slogan']}**

{s['pitch30']}

✔ Vem pronta: baixe, abra e comece a lançar.
✔ Explicada passo a passo, com exemplo preenchido.
✔ Sem mensalidade, sem macros, sem instalação.
✔ Funciona no Excel e no LibreOffice.

## Requisitos
Excel 2016 ou superior (Windows/Mac), Excel 365 ou LibreOffice Calc.
"""
    benef = f"""# {s['comercial']} — Benefícios

| O que a planilha faz | O que o cliente ganha |
|---|---|
{chr(10).join(f'| {v} | Clareza para decidir mais rápido e com menos erro |' for v in s['vantagens'])}

## Benefícios práticos
- **Economia de tempo:** informações que levavam horas para reunir ficam prontas a um clique.
- **Menos erros:** fórmulas e validações no lugar de contas na calculadora.
- **Mais dinheiro no bolso:** {o['beneficio']}
- **Mais controle:** indicadores atualizam sozinhos conforme você lança.
- **Sem dependência de especialista:** tutorial e exemplo mostram o caminho.
- **Sem mensalidade:** pagamento único.
"""
    publico = f"""# {s['comercial']} — Público-alvo

## Quem deve comprar
{chr(10).join('- ' + x for x in s['publico'])}

## Quem sofre com o problema
{o['quem']}

## Perfil do comprador ideal
- Dono ou gestor que decide sozinho ou com um sócio.
- Hoje controla isto no caderno, no WhatsApp, em planilha improvisada ou 'de cabeça'.
- Não quer pagar mensalidade de sistema, ou ainda não está pronto para um ERP.

## Para quem NÃO é
- Empresas que já usam um sistema (ERP) completo e integrado e estão satisfeitas.
- Quem precisa de emissão de nota fiscal, integração bancária ou multiusuário simultâneo.

## Onde encontrar esse público
Grupos de empreendedores do segmento no Facebook/WhatsApp, Instagram (hashtags do segmento), Google (busca por 'planilha de ...'), marketplaces de infoprodutos e parcerias com contadores.
"""
    obj = "\n".join(f"| \"{a}\" | {b} |" for a, b in s["objecoes"])
    arg = f"""# {s['comercial']} — Argumentos de venda

## Argumentos principais
1. **Dor real e conhecida:** {s['dor']}
2. **Pronta para usar:** baixa, abre e lança; sem montar fórmula.
3. **Aprende rápido:** tutorial passo a passo + exemplo preenchido + guia de 5 minutos.
4. **Resultado visível:** dashboard e indicadores prontos.
5. **Pagamento único:** sem mensalidade nem contrato.
6. **Diferencial:** {o['dif']}

## Quebra de objeções
| Objeção | Resposta |
|---|---|
{obj}
| "Está caro." | O preço de uma planilha é menor que o de um erro de preço, uma multa por esquecimento ou um mês de dinheiro parado. Ofereça o kit se o cliente tem outras dores. |
| "E se eu não gostar?" | Informe a política de reembolso. Em compras online no Brasil existe direito de arrependimento em 7 dias (CDC, art. 49). |

## Evidência de mercado (para usar em conteúdo)
{ev}

*Use os números como indicação e cite a fonte; alguns são de fornecedores ou de terceiros e podem ter sido atualizados.*
"""
    base_faq = [("Em que formato recebo?", "Arquivos `.xlsx` (Excel) e documentos em PDF/Markdown com tutorial, manual e guia rápido."),
                ("Preciso instalar algo?", "Não. Basta ter Excel 2016+ ou LibreOffice."),
                ("Tem macros ou vírus?", "Não. São arquivos `.xlsx` sem macros."),
                ("Recebo atualizações?", "Sim, as atualizações da versão 1.x."),
                ("Posso usar em mais de uma empresa?", "A licença padrão é para uma empresa/profissional. Consulte a oferta de licença para contadores e consultores."),
                ("Serve para o Google Planilhas?", "Os cálculos funcionam, mas a experiência completa (gráficos e formatação) é no Excel/LibreOffice.")]
    faq = "# " + s["comercial"] + " — Perguntas frequentes (pré-venda)\n\n" + "\n".join(f"**{q}**  \n{a}\n" for q, a in s["faq"] + base_faq)
    pitch = f"""# {s['comercial']} — Pitch

## Frase de 10 segundos
{s['slogan']}

## Pitch de 30 segundos
{s['pitch30']}

## Roteiro de 2 minutos (chamada ou vídeo)
1. **Gancho:** "{s['dor']}"
2. **Consequência:** isso gera decisões no escuro: preço errado, dinheiro parado, multa, venda perdida.
3. **Solução:** apresente a planilha e mostre o `EXEMPLO.xlsx` (Dashboard).
4. **Como é fácil:** abas, células amarelas, tutorial e exemplo.
5. **Oferta:** preço promocional {reais(s['preco'][1])} (individual {reais(s['preco'][0])}); kits com desconto.
6. **Chamada para ação:** "Quer receber o link agora?"

## Mensagem para WhatsApp
> Olá! Você sabe responder rápido: {s['dor'].split(':')[0].lower() if ':' in s['dor'] else s['dor'][:90].lower()}...? Tenho a planilha **{s['comercial']}**: {s['resumo'][:140]}... Vem com tutorial e exemplo preenchido. Posso te mostrar? 😊

## Títulos de anúncio
- {s['slogan']}
- {s['comercial']}: pronta para usar, com tutorial e exemplo
- Chega de controlar no caderno: baixe, abra e comece hoje

## Legenda para Instagram
{s['slogan']} 👇
{s['dor']}
Na planilha **{s['comercial']}** você {s['para_que'][0][0].lower() + s['para_que'][0][1:]}
✔ Tutorial passo a passo ✔ Exemplo preenchido ✔ Sem mensalidade
Comente QUERO e receba o link!
"""
    ind, promo, prem = s["preco"]
    preco = f"""# {s['comercial']} — Preço sugerido

| Oferta | Preço |
|---|---|
| **Preço individual** | {reais(ind)} |
| **Preço promocional** (lançamento / cupom) | {reais(promo)} |
| **Preço em kit** | veja [`kits/`](../../../../kits/README.md): {', '.join(s['kits'])} |
| **Versão premium (roadmap)** | {reais(prem)} |

## Por que essa faixa
{s['preco_just']}

## Como validar o preço
- Comece no preço promocional por 2 semanas e meça a conversão; suba para o individual se a conversão for boa.
- Compare com concorrentes (planilhas pagas em marketplaces de infoprodutos e gratuitas de blogs) e com o custo do problema (multas, estoque parado, preço errado).
- Ofereça o kit na página de checkout (order bump) para aumentar o ticket médio.

*Os valores são sugestões iniciais baseadas em complexidade, valor gerado e concorrência; teste com seu público antes de fixar.*
"""
    d = os.path.join(dest, "sales")
    for name, txt in (("descricao.md", desc), ("beneficios.md", benef), ("publico-alvo.md", publico), ("argumentos.md", arg), ("faq.md", faq), ("pitch.md", pitch), ("preco.md", preco)):
        w(os.path.join(d, name), txt)


def main():
    catalog = []
    for s in SPECS:
        mod = importlib.import_module(s["mod"])
        dest = os.path.join(ROOT, "planilhas", mod.PASTA)
        wb = openpyxl.load_workbook(os.path.join(dest, "EXEMPLO.xlsx"), data_only=True)
        w(os.path.join(dest, "README.md"), readme(s, mod, mod.PASTA))
        w(os.path.join(dest, "TUTORIAL.md"), tutorial(s, wb))
        w(os.path.join(dest, "MANUAL.md"), manual(s))
        w(os.path.join(dest, "GUIA-RAPIDO.md"), guia(s))
        sales(s, dest)
        catalog.append(dict(mod=s["mod"], nome=s["comercial"], categoria=s["categoria"], pasta=mod.PASTA, publico=s["publico"][0], dor=s["dor"],
                            preco=s["preco"], op=OPBY[s["op"]]["nota"], slogan=s["slogan"], resumo=s["resumo"], abas=[a for a, _ in s["abas"]]))
        print("docs:", mod.PASTA)
    by = {c["mod"]: c for c in catalog}
    # ---------------- kits
    kit_rows, kit_json = [], []
    for nome, mods, preco, historia, itens in KITS:
        soma = sum(by[m]["preco"][0] for m in mods)
        desc = round((1 - preco / soma) * 100)
        slug = nome.lower().replace(" ", "-").replace("é", "e").replace("ç", "c").replace("ó", "o").replace("á", "a").replace("í", "i").replace("ã", "a")
        ordem = "\n".join(f"{i}. **{by[m]['nome']}**: [`planilhas/{by[m]['pasta']}/`](../planilhas/{by[m]['pasta']}/)" for i, m in enumerate(mods, 1))
        w(os.path.join(ROOT, "kits", f"{slug}.md"), f"""# {nome}

> {historia}

## O que inclui
{ordem}

## Preço
- Soma dos produtos avulsos: **{reais(soma)}**
- **Preço do kit: {reais(preco)}** (economia de {desc}%)

## Ordem de implantação sugerida
{chr(10).join(f'{i}. {x}' for i, x in enumerate(itens, 1))}

Comece por uma planilha, use por 1 semana e adicione a próxima. Cada produto tem `TUTORIAL.md`, `MANUAL.md` e `GUIA-RAPIDO.md` na sua pasta.

## Argumento de venda
Quem compra uma planilha costuma descobrir, na primeira semana, que precisa da seguinte (o caixa pede o contas a pagar; o contas a pagar pede o DRE). O kit entrega o sistema inteiro com {desc}% de desconto e uma ordem clara de implantação.
""")
        kit_rows.append(f"| [{nome}](kits/{slug}.md) | {', '.join(by[m]['nome'] for m in mods) if nome != 'Kit Completo' else 'Todas as 10 planilhas'} | {reais(soma)} | **{reais(preco)}** ({desc}% off) |")
        kit_json.append(dict(nome=nome, slug=slug, produtos=[by[m]["nome"] for m in mods], soma=soma, preco=preco, desc=desc, historia=historia))
    w(os.path.join(ROOT, "kits", "README.md"), "# Kits Carvex XLS\n\nCombos por tipo de negócio, com desconto sobre a soma dos produtos.\n\n| Kit | Inclui | Avulso | Preço do kit |\n|---|---|---|---|\n" + "\n".join(
        x.replace("(kits/", "(").replace("](kits/", "](") for x in kit_rows) + "\n")
    # ---------------- catálogo
    rows = [f"| [{c['nome']}](planilhas/{c['pasta']}/) | {c['categoria']} | {c['publico']} | {c['dor']} | {reais(c['preco'][0])} (promo {reais(c['preco'][1])}) | ✅ Pronto v1.0 |" for c in catalog]
    road = [o for o in sorted(OPS, key=lambda o: -o["nota"]) if o["status"] == "Roadmap"]
    w(os.path.join(ROOT, "CATALOGO.md"), f"""# Catálogo de produtos — Carvex XLS

## Produtos prontos (primeira leva)
| Produto | Categoria | Público | Problema | Preço | Status |
|---|---|---|---|---|---|
{chr(10).join(rows)}

> **Status "Pronto v1.0"**: planilha limpa + exemplo + tutorial + manual + guia rápido + material de venda; fórmulas conferidas no {LO_VERSION}. Recomenda-se um teste final no Excel antes de vender em escala.

## Kits
| Kit | Inclui | Avulso | Preço do kit |
|---|---|---|---|
{chr(10).join(kit_rows)}

## Premium (roadmap de upgrades)
{chr(10).join(f"- **{c['nome']}**: {reais(c['preco'][2])}" for c in catalog)}

## Próximos produtos (roadmap, por nota de oportunidade)
| # | Produto | Segmento | Nota | Evidência |
|---|---|---|---|---|
{chr(10).join(f"| {i} | {o['nome']} | {o['seg']} | {o['nota']} | {o['forca']} |" for i, o in enumerate(road, 1))}

Pesquisa completa em [`market-research/opportunities.md`](market-research/opportunities.md).
""")
    # catálogo JSON para a página de vendas
    out = dict(produtos=[dict(nome=c["nome"], slug=c["mod"], categoria=c["categoria"], slogan=c["slogan"], dor=c["dor"], resumo=c["resumo"], preco=c["preco"][0], promo=c["preco"][1], premium=c["preco"][2],
                              pasta=c["pasta"], abas=c["abas"], nota=c["op"], publico=c["publico"]) for c in catalog], kits=kit_json)
    os.makedirs(os.path.join(ROOT, "site"), exist_ok=True)
    with open(os.path.join(ROOT, "site", "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "site", "catalog.js"), "w", encoding="utf-8") as f:
        f.write("window.CARVEX_CATALOG = " + json.dumps(out, ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    main()
