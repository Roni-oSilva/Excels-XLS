# Página de vendas — Carvex XLS

Site estático (HTML + CSS + JS puro, sem build e sem dependências). Tema verde Carvex, com referências ao Excel:
janela de planilha animada (fórmula sendo digitada, seleção de células, intervalo tracejado, gráfico), barra de abas
de planilha no rodapé (navegação por seção), mini planilha interativa ("Teste ao vivo") e marquee de funções do Excel.

## Abrir localmente
Abra `index.html` no navegador, ou: `npx http-server site -p 8080`.

## Ligar os botões de compra (obrigatório antes de publicar)
Edite **`config.js`**:
- `checkout[...]`: link de pagamento de cada planilha/kit (Hotmart, Kiwify, Eduzz, Mercado Pago...).
- `whatsapp`: número com DDI+DDD (ex.: `5511999999999`). Se um produto não tiver link, o botão abre o WhatsApp; sem WhatsApp, mostra "em breve".
- `showPromo`: `true` mostra o preço promocional (e o individual riscado); `false` mostra só o individual.
- `guaranteeDays`, `instagram`, `email`.

## Atualizar produtos, preços e kits
Os dados vêm de `catalog.js` (gerado). Para alterar preços: edite `tools/docs_a.py` / `tools/docs_b.py` (campo `preco`) e `tools/gen_docs.py` (kits), então rode:
```bash
python3 tools/gen_docs.py && python3 tools/site_assets.py
```

## Arquivos
| Arquivo | Função |
|---|---|
| `index.html` | Estrutura e textos |
| `styles.css` | Visual (variáveis de cor no `:root`) |
| `app.js` | Animações e interações |
| `config.js` | Links de compra e contatos (edite) |
| `catalog.js` / `catalog.json` | Produtos e kits (gerados) |
| `img/` | Capturas das planilhas (WebP, geradas por `tools/site_assets.py`) |
| `logo-mark.svg`, `favicon.svg` | Logo Carvex em verde (vetorizado a partir do logo original) |

## Publicar
Qualquer hospedagem estática serve: GitHub Pages, Netlify, Vercel, Cloudflare Pages ou um servidor comum. Publique a pasta `site/`.
As fontes (Plus Jakarta Sans, Inter, JetBrains Mono) vêm do Google Fonts; sem internet a página usa fontes do sistema.

## Acessibilidade e desempenho
Contraste AA nos textos principais, foco visível, `prefers-reduced-motion` desliga as animações, imagens em WebP com `loading="lazy"`.

## Observação sobre afirmações
Estatísticas da seção "Dores" vêm de fontes de terceiros (Serasa Experian, inFlow, Sebrae-PR, UFSM) e estão em `market-research/opportunities.md`. Não há depoimentos inventados. Os números de teste (20 planilhas, 263 conferências, 0 erros) vêm de `QUALIDADE.md`.
