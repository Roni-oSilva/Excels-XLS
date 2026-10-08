/* Carvex XLS — interações da página de vendas (JS puro, sem dependências) */
(() => {
  'use strict';
  const CFG = window.CARVEX_CONFIG || {};
  const CAT = window.CARVEX_CATALOG || { produtos: [], kits: [] };
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const brl = n => 'R$ ' + Math.round(n).toLocaleString('pt-BR');
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  /* ---------- util: toast e compra ---------- */
  let toastT;
  function toast(msg) {
    const t = $('#toast'); t.textContent = msg; t.hidden = false;
    clearTimeout(toastT); toastT = setTimeout(() => (t.hidden = true), 4800);
  }
  function buy(id, nome) {
    const url = (CFG.checkout || {})[id];
    if (url) { window.open(url, '_blank', 'noopener'); return; }
    if (CFG.whatsapp) {
      const txt = encodeURIComponent(`Olá! Quero a planilha/kit: ${nome}`);
      window.open(`https://wa.me/${CFG.whatsapp}?text=${txt}`, '_blank', 'noopener'); return;
    }
    console.info('[Carvex XLS] Configure o link de compra de "' + id + '" em site/config.js');
    toast('A compra de "' + nome + '" será liberada em breve. Obrigado pelo interesse!');
  }

  /* ---------- topo ---------- */
  $('#yr').textContent = new Date().getFullYear();
  const nav = $('#nav');
  const onScroll = () => nav.classList.toggle('stuck', scrollY > 30);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  $('#guar').textContent = `Compra segura · ${CFG.guaranteeDays || 7} dias de garantia (direito de arrependimento) · Entrega digital`;
  if (CFG.whatsapp) { const w = $('#wa'); w.href = `https://wa.me/${CFG.whatsapp}`; w.hidden = false; }
  const fl = $('#footLinks');
  fl.innerHTML = '<a href="#produtos">Planilhas</a><a href="#kits">Kits</a><a href="#faq">Dúvidas</a>' +
    (CFG.instagram ? `<a href="${CFG.instagram}" target="_blank" rel="noopener">Instagram</a>` : '') +
    (CFG.email ? `<a href="mailto:${CFG.email}">${CFG.email}</a>` : '');

  /* ---------- hero: fórmulas flutuantes + marquee ---------- */
  const FUNCS = ['=SOMASES(B:B;C:C;"Entrada")', '=SEERRO(ÍNDICE(A:A;CORRESP(E2;B:B;0));"")', '=CONT.SES(F:F;"Vencido")', '=SOMARPRODUTO(D2:D9;E2:E9)', '=SE(B2>=B7;"Acima do PE";"ABAIXO do PE")',
    '=ÍNDICE(Preços!C:C;CORRESP(A2;Preços!A:A;0))', '=MÁXIMO(B2:B30)', '=ARRED(B2/(1-C2);2)', '=HOJE()-D2', '=PROCV(A2;Config!B:C;2;0)', '=SOMASE(C:C;"Saída";F:F)', '=MÉDIA(B2:B13)'];
  const fl2 = $('#floaters');
  FUNCS.slice(0, 9).forEach((f, i) => {
    const s = document.createElement('span'); s.textContent = f;
    s.style.left = (4 + (i * 11.3) % 82) + '%'; s.style.animationDuration = (14 + (i * 3.1) % 11) + 's'; s.style.animationDelay = (-i * 2.2) + 's';
    fl2.appendChild(s);
  });
  const mq = $('#marquee');
  mq.innerHTML = [...FUNCS, ...FUNCS].map(f => `<span>${f.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</span>`).join('');

  /* ---------- mock do Excel (hero) ---------- */
  const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'];
  const ent = [42300, 38900, 51200, 47800, 55400, 58100];
  const sai = [36100, 35400, 41900, 40200, 43700, 45300];
  const sheet = $('#xlSheet'), barsEl = $('#xlBars'), fEl = $('#xlFormula'), nameEl = $('#xlName'), statEl = $('#xlStat');
  const cols = ['A', 'B', 'C', 'D', 'E'];
  const cells = {};
  function mk(cls, txt, ref) { const d = document.createElement('div'); d.className = cls; d.textContent = txt; if (ref) { d.dataset.ref = ref; cells[ref] = d; } sheet.appendChild(d); return d; }
  mk('h', '');
  cols.forEach(c => mk('h', c));
  const headers = ['Mês', 'Entradas', 'Saídas', 'Saldo', 'Margem'];
  mk('h', '1'); headers.forEach((h, i) => mk('hd', h, cols[i] + '1'));
  months.forEach((m, r) => {
    mk('h', r + 2);
    mk('t', m, 'A' + (r + 2)); mk('', '', 'B' + (r + 2)); mk('', '', 'C' + (r + 2)); mk('', '', 'D' + (r + 2)); mk('', '', 'E' + (r + 2));
  });
  mk('h', '8'); mk('tot t', 'Total', 'A8'); ['B', 'C', 'D', 'E'].forEach(c => mk('tot', '', c + '8'));
  const fmt = n => n.toLocaleString('pt-BR');
  const pct = n => (n * 100).toFixed(1).replace('.', ',') + '%';
  const sel = document.createElement('div'); sel.className = 'sel'; sheet.appendChild(sel);
  const rng = document.createElement('div'); rng.className = 'rng'; rng.style.opacity = 0; sheet.appendChild(rng);
  months.forEach((m, i) => { const b = document.createElement('i'); b.dataset.m = m; barsEl.appendChild(b); });
  const bars = $$('i', barsEl);
  const box = el => ({ x: el.offsetLeft, y: el.offsetTop, w: el.offsetWidth, h: el.offsetHeight });
  function place(node, a, b) {
    const A = box(cells[a]), B = box(cells[b || a]);
    const x = Math.min(A.x, B.x), y = Math.min(A.y, B.y), x2 = Math.max(A.x + A.w, B.x + B.w), y2 = Math.max(A.y + A.h, B.y + B.h);
    Object.assign(node.style, { left: x - 1 + 'px', top: y - 1 + 'px', width: x2 - x + 'px', height: y2 - y + 'px', opacity: 1 });
  }
  function setBars(on) {
    bars.forEach((b, i) => { b.style.height = on ? (8 + ((ent[i] - sai[i]) / 14000) * 92) + '%' : '8%'; });
  }
  function put(ref, txt, neg) { const c = cells[ref]; c.textContent = txt; c.classList.remove('flash'); void c.offsetWidth; c.classList.add('flash'); if (neg) c.classList.add('neg'); }
  function resetSheet() {
    months.forEach((m, r) => { cells['B' + (r + 2)].textContent = fmt(ent[r]); cells['C' + (r + 2)].textContent = fmt(sai[r]); cells['D' + (r + 2)].textContent = ''; cells['E' + (r + 2)].textContent = ''; });
    ['B', 'C', 'D', 'E'].forEach(c => (cells[c + '8'].textContent = ''));
    setBars(false); rng.style.opacity = 0;
  }
  async function type(text) { fEl.textContent = ''; for (const ch of text) { fEl.textContent += ch; await sleep(reduce ? 0 : 38); } await sleep(reduce ? 0 : 260); }
  const sum = a => a.reduce((x, y) => x + y, 0);
  async function demo() {
    resetSheet();
    if (reduce) { // estado final estático
      months.forEach((m, r) => { put('D' + (r + 2), fmt(ent[r] - sai[r])); put('E' + (r + 2), pct((ent[r] - sai[r]) / ent[r])); });
      put('B8', fmt(sum(ent))); put('C8', fmt(sum(sai))); put('D8', fmt(sum(ent) - sum(sai))); put('E8', pct((sum(ent) - sum(sai)) / sum(ent)));
      place(sel, 'E8'); nameEl.textContent = 'E8'; fEl.textContent = '=D8/B8'; setBars(true); statEl.textContent = 'Média: ' + pct((sum(ent) - sum(sai)) / sum(ent)); return;
    }
    for (;;) {
      resetSheet(); await sleep(700);
      nameEl.textContent = 'D2'; place(sel, 'D2'); await type('=B2-C2'); put('D2', fmt(ent[0] - sai[0])); statEl.textContent = 'Soma: R$ ' + fmt(ent[0] - sai[0]);
      place(rng, 'D2', 'D7'); await sleep(380);
      for (let r = 1; r < 6; r++) { put('D' + (r + 2), fmt(ent[r] - sai[r])); await sleep(130); }
      setBars(true); rng.style.opacity = 0; await sleep(400);
      nameEl.textContent = 'E2'; place(sel, 'E2'); await type('=D2/B2'); put('E2', pct((ent[0] - sai[0]) / ent[0]));
      place(rng, 'E2', 'E7'); await sleep(300);
      for (let r = 1; r < 6; r++) { put('E' + (r + 2), pct((ent[r] - sai[r]) / ent[r])); await sleep(120); }
      rng.style.opacity = 0; await sleep(400);
      for (const [c, arr, label] of [['B', ent], ['C', sai], ['D', ent.map((v, i) => v - sai[i])]]) {
        nameEl.textContent = c + '8'; place(sel, c + '8'); place(rng, c + '2', c + '7');
        await type(`=SOMA(${c}2:${c}7)`); statEl.textContent = 'Soma: R$ ' + fmt(sum(arr)); put(c + '8', fmt(sum(arr))); await sleep(500);
      }
      rng.style.opacity = 0; nameEl.textContent = 'E8'; place(sel, 'E8'); await type('=D8/B8');
      put('E8', pct((sum(ent) - sum(sai)) / sum(ent))); statEl.textContent = 'Média: ' + pct((sum(ent) - sum(sai)) / sum(ent));
      await sleep(3600);
    }
  }
  let demoStarted = false;
  const startDemo = () => { if (demoStarted) return; demoStarted = true; demo(); };
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => setTimeout(startDemo, 250));
  addEventListener('resize', () => { const n = nameEl.textContent; if (cells[n]) place(sel, n); });

  /* inclinação 3D ao mover o mouse */
  const xl = $('#xl'), hv = $('.hero-visual');
  if (!reduce && matchMedia('(min-width:1001px)').matches) {
    hv.addEventListener('pointermove', e => {
      const r = hv.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      xl.style.transform = `rotateY(${-9 + x * 14}deg) rotateX(${4 - y * 12}deg) rotateZ(1deg)`;
    });
    hv.addEventListener('pointerleave', () => (xl.style.transform = ''));
  }

  /* ---------- contadores ---------- */
  function countUp(el) {
    const to = parseFloat(el.dataset.to), dec = +(el.dataset.dec || 0), suf = el.dataset.suf || '';
    if (reduce) { el.textContent = to.toLocaleString('pt-BR', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suf; return; }
    const t0 = performance.now(), D = 1400;
    const step = t => {
      const p = Math.min(1, (t - t0) / D), e = 1 - Math.pow(1 - p, 3);
      el.textContent = (to * e).toLocaleString('pt-BR', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suf;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  /* ---------- produtos ---------- */
  const ICONS = {
    'Financeiro': '<path d="M4 19V5M4 19h16M8 15l3-4 3 3 5-7" stroke-linecap="round" stroke-linejoin="round"/>',
    'Precificação': '<path d="M3 12V4h8l9 9-8 8-9-9z" stroke-linejoin="round"/><circle cx="7.5" cy="8.5" r="1.4"/>',
    'Estoque': '<path d="M3 8l9-5 9 5v8l-9 5-9-5V8zM3 8l9 5 9-5M12 13v8" stroke-linejoin="round"/>',
    'Vendas': '<path d="M3 4h18l-7 8v6l-4 2v-8L3 4z" stroke-linejoin="round"/>',
    'Restaurantes': '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M17 3c-2 2-3 5-3 8h3v10" stroke-linecap="round" stroke-linejoin="round"/>',
    'Oficinas': '<path d="M14.7 6.3a4 4 0 0 0-5.4 5L3 17.6 6.4 21l6.3-6.3a4 4 0 0 0 5-5.4l-2.6 2.6-2.4-.6-.6-2.4 2.6-2.6z" stroke-linejoin="round"/>',
    'Construção': '<path d="M3 21h18M5 21V10l7-6 7 6v11M9 21v-6h6v6" stroke-linejoin="round"/>',
    'Clínicas': '<rect x="3" y="4" width="18" height="17" rx="3"/><path d="M12 9v7M8.5 12.5h7" stroke-linecap="round"/>'
  };
  const icon = c => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">${ICONS[c] || ICONS['Financeiro']}</svg>`;
  const priceNow = p => (CFG.showPromo === false ? p.preco : p.promo);
  const priceHtml = p => CFG.showPromo === false ? `<b>${brl(p.preco)}</b><small>pagamento único</small>` : `<b>${brl(p.promo)}</b><s>${brl(p.preco)}</s><small>lançamento · pagamento único</small>`;
  const grid = $('#grid'), filters = $('#filters');
  const cats = ['Todas', ...new Set(CAT.produtos.map(p => p.categoria))];
  filters.innerHTML = cats.map((c, i) => `<button role="tab" class="${i ? '' : 'on'}" data-c="${c}">${c}</button>`).join('');
  grid.innerHTML = CAT.produtos.map((p, i) => `
    <article class="card reveal" style="--d:${(i % 3) * .08}s" data-c="${p.categoria}" data-id="${p.id}">
      <div class="top"><span class="ic">${icon(p.categoria)}</span><span class="tag">${p.categoria}</span></div>
      <h3>${p.nome}</h3>
      <p class="slogan">${p.slogan}</p>
      <p class="dor">${p.dor}</p>
      <div class="meta">${p.abas.filter(a => a !== 'Início').slice(0, 4).map(a => `<span>${a}</span>`).join('')}<span>+ tutorial</span></div>
      <div class="foot2"><div class="price">${priceHtml(p)}</div>
        <div class="acts"><button class="btn btn-line" data-more="${p.id}">Detalhes</button><button class="btn btn-green" data-buy="${p.id}">Comprar</button></div></div>
    </article>`).join('');
  filters.addEventListener('click', e => {
    const b = e.target.closest('button'); if (!b) return;
    $$('button', filters).forEach(x => x.classList.toggle('on', x === b));
    $$('.card', grid).forEach(c => c.classList.toggle('hide', b.dataset.c !== 'Todas' && c.dataset.c !== b.dataset.c));
  });
  const byId = id => CAT.produtos.find(p => p.id === id);
  grid.addEventListener('click', e => {
    const m = e.target.closest('[data-more]'), b = e.target.closest('[data-buy]');
    if (m) openModal(m.dataset.more); if (b) { const p = byId(b.dataset.buy); buy(p.id, p.nome); }
  });

  /* ---------- modal ---------- */
  const modal = $('#modal'); let lastFocus = null, curId = null, curView = 'dash';
  function modalImg() { const im = $('#mImg'); im.src = `img/${curId}-${curView}.webp`; im.alt = 'Captura de tela da planilha ' + byId(curId).nome; }
  function openModal(id) {
    const p = byId(id); curId = id; curView = 'dash'; lastFocus = document.activeElement;
    $('#mCat').textContent = p.categoria; $('#mTitle').textContent = p.nome; $('#mSlogan').textContent = p.slogan; $('#mResumo').textContent = p.resumo;
    $('#mDor').textContent = p.dor; $('#mList').innerHTML = p.vantagens.map(v => `<li>${v}</li>`).join('');
    $('#mAbas').innerHTML = p.abas.map(a => `<span>${a}</span>`).join('');
    $('#mPrice').textContent = brl(priceNow(p)); $('#mFrom').textContent = CFG.showPromo === false ? 'Pagamento único' : 'De ' + brl(p.preco) + ' por (lançamento)';
    $('#mKits').textContent = 'Também em: ' + p.kits.join(' · ');
    $$('#mViews button').forEach(b => b.classList.toggle('on', b.dataset.view === 'dash')); modalImg();
    $('#mBuy').onclick = () => buy(p.id, p.nome);
    modal.hidden = false; document.body.style.overflow = 'hidden'; $('#mClose').focus();
  }
  function closeModal() { modal.hidden = true; document.body.style.overflow = ''; if (lastFocus) lastFocus.focus(); }
  $('#mClose').onclick = closeModal;
  modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
  addEventListener('keydown', e => { if (e.key === 'Escape' && !modal.hidden) closeModal(); });
  $('#mViews').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; curView = b.dataset.view; $$('#mViews button').forEach(x => x.classList.toggle('on', x === b)); modalImg(); });

  /* ---------- por dentro ---------- */
  const pt = $('#peekTabs'), pi = $('#peekImg'); let peekId = CAT.produtos[0] && CAT.produtos[0].id, peekView = 'dash';
  pt.innerHTML = CAT.produtos.map((p, i) => `<button role="tab" class="${i ? '' : 'on'}" data-id="${p.id}">${p.nome.split(' ').slice(0, 3).join(' ')}</button>`).join('');
  function peek() {
    const p = byId(peekId); pi.classList.add('swap');
    setTimeout(() => { pi.src = `img/${peekId}-${peekView}.webp`; pi.alt = 'Captura de tela: ' + p.nome; pi.classList.remove('swap'); }, 180);
    $('#peekTitle').textContent = 'EXEMPLO.xlsx — ' + p.nome;
  }
  pt.addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; peekId = b.dataset.id; $$('button', pt).forEach(x => x.classList.toggle('on', x === b)); peek(); });
  $('.peek-frame .peek-views').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; peekView = b.dataset.view; $$('.peek-frame .peek-views button').forEach(x => x.classList.toggle('on', x === b)); peek(); });
  if (peekId) { pi.src = `img/${peekId}-dash.webp`; pi.alt = 'Captura de tela: ' + byId(peekId).nome; $('#peekTitle').textContent = 'EXEMPLO.xlsx — ' + byId(peekId).nome; }

  /* ---------- teste ao vivo ---------- */
  const num = el => parseInt(el.value.replace(/\D/g, ''), 10) || 0;
  const live = $('#live'), lvName = $('#lvName'), lvF = $('#lvFormula');
  const FORM = { B2: '120000', B3: '52000', B4: '41000', B5: '=B2-B3-B4', B6: '=B5/B2', B7: '=B4/(1-B3/B2)', B8: '=SE(B2>=B7;"Acima do PE";"ABAIXO do PE")' };
  function calc() {
    const v = num($('#inV')), c = num($('#inC')), f = num($('#inF'));
    const res = v - c - f, mar = v ? res / v : 0, pe = v > 0 && c < v ? f / (1 - c / v) : null;
    const set = (id, t, cls) => { const el = $(id); el.textContent = t; el.classList.remove('ok', 'bad'); if (cls) el.classList.add(cls); };
    set('#oR', (res < 0 ? '-' : '') + brl(Math.abs(res)), res >= 0 ? 'ok' : 'bad');
    set('#oM', pct(mar), res >= 0 ? 'ok' : 'bad');
    set('#oP', pe == null ? '—' : brl(pe));
    set('#oS', pe == null ? '—' : (v >= pe ? 'Acima do PE' : 'ABAIXO do PE'), pe != null && v >= pe ? 'ok' : 'bad');
    const mx = Math.max(v, pe || 0, 1);
    $('#bV').style.height = Math.max(6, (v / mx) * 100) + '%'; $('#bP').style.height = Math.max(6, ((pe || 0) / mx) * 100) + '%';
  }
  ['#inV', '#inC', '#inF'].forEach(id => {
    const el = $(id);
    el.addEventListener('input', () => { const n = num(el); el.value = n ? n.toLocaleString('pt-BR') : ''; calc(); });
    el.addEventListener('focus', () => { const r = el.parentElement.dataset.c; lvName.textContent = r; lvF.textContent = String(num(el)); });
  });
  live.addEventListener('click', e => {
    const td = e.target.closest('td[data-c]'); if (!td) return;
    $$('td', live).forEach(x => x.classList.remove('sel2')); td.classList.add('sel2');
    lvName.textContent = td.dataset.c; lvF.textContent = FORM[td.dataset.c] || '';
  });
  calc();

  /* ---------- kits ---------- */
  $('#kitGrid').innerHTML = CAT.kits.map(k => `
    <article class="kit reveal ${k.nome === 'Kit Completo' ? 'best' : ''}">
      <span class="off">-${k.desc}%</span>
      <h3>${k.nome}</h3><p>${k.historia}</p>
      <ul>${(k.nome === 'Kit Completo' ? ['As 10 planilhas da biblioteca', 'Fluxo, estoque, vendas, DRE, CMV, OS, obras e clínica', 'Atualizações da versão 1.x'] : k.produtos).map(x => `<li>${x}</li>`).join('')}</ul>
      <div class="price"><b>${brl(k.preco)}</b><s>${brl(k.soma)}</s><small>pagamento único</small></div>
      <button class="btn ${k.nome === 'Kit Completo' ? 'btn-white' : 'btn-green'}" data-kit="${k.slug}" data-n="${k.nome}">Quero o ${k.nome.toLowerCase()}</button>
    </article>`).join('');
  $('#kitGrid').addEventListener('click', e => { const b = e.target.closest('[data-kit]'); if (b) buy(b.dataset.kit, b.dataset.n); });

  /* ---------- faq ---------- */
  const FAQ = [
    ['Preciso ter Excel? Funciona no Google Planilhas?', 'Os arquivos são .xlsx comuns, feitos para Excel 2016 ou superior e LibreOffice Calc. No Google Planilhas os cálculos funcionam, mas gráficos e formatação podem mudar; recomendamos Excel.'],
    ['Tem macros ou algo para instalar?', 'Não. São planilhas sem macros e sem complementos: você baixa, abre e usa.'],
    ['Como recebo as planilhas?', 'Por download logo após o pagamento: planilha limpa, exemplo preenchido, tutorial, manual e guia rápido de cada produto.'],
    ['As fórmulas foram testadas?', 'Sim. Cada planilha foi recalculada e as respostas foram conferidas contra um cálculo independente: 263 conferências e nenhum erro de fórmula nas 20 planilhas (limpas e exemplos). Os arquivos usam apenas funções padrão do Excel.'],
    ['Os dados do exemplo são reais?', 'Não. Todos os dados do EXEMPLO são 100% fictícios, criados só para você entender o funcionamento.'],
    ['Posso alterar categorias, nomes e listas?', 'Sim. As abas Config trazem as listas editáveis (categorias, clientes, fornecedores, profissionais etc.). As células amarelas são suas; as cinzas calculam sozinhas.'],
    ['Quantos lançamentos cabem?', 'Depende da planilha (por exemplo: 1.000 lançamentos no Fluxo de Caixa, 3.000 movimentações no Estoque e 3.000 agendamentos na Agenda). O limite está descrito no manual de cada produto.'],
    ['Tem suporte e atualizações?', 'O manual traz o canal de suporte e as atualizações da versão 1.x são enviadas aos compradores.'],
    ['Posso usar para vários clientes (contador/consultor)?', 'A licença padrão é para uma empresa ou profissional. Se você atende vários clientes, fale com a gente sobre a licença profissional.'],
    ['Emite nota fiscal ou integra com o banco?', 'Não. São controles gerenciais: você lança e a planilha calcula. Elas não substituem seu sistema fiscal nem a contabilidade.'],
    ['E se eu não gostar?', `Você tem ${CFG.guaranteeDays || 7} dias de garantia (direito de arrependimento em compras online, CDC art. 49).`]
  ];
  $('#faqList').innerHTML = FAQ.map(([q, a]) => `<details><summary>${q}</summary><p>${a}</p></details>`).join('');

  /* ---------- reveal + scroll-spy ---------- */
  const io = new IntersectionObserver(es => es.forEach(en => {
    if (!en.isIntersecting) return; en.target.classList.add('in'); io.unobserve(en.target);
    $$('.count', en.target).forEach(countUp); if (en.target.classList.contains('count')) countUp(en.target);
  }), { threshold: .15 });
  $$('.reveal').forEach(el => io.observe(el));
  $$('.count').forEach(el => { if (!el.closest('.reveal')) io.observe(el); });
  const links = $$('#sheetbar a');
  const secs = links.map(a => $(a.getAttribute('href')));
  const spy = new IntersectionObserver(es => es.forEach(en => {
    if (en.isIntersecting) { const i = secs.indexOf(en.target); links.forEach((l, j) => l.classList.toggle('on', i === j)); }
  }), { rootMargin: '-45% 0px -50% 0px' });
  secs.forEach(s => s && spy.observe(s));
})();
