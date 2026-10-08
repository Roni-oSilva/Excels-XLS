# -*- coding: utf-8 -*-
"""Gera o vídeo promocional vertical (720x1280) Carvex XLS em verde.

Recria o layout do vídeo de referência (cartões que alternam escuro/claro/verde, balões, logo no canto,
etiqueta no rodapé) com o assunto das planilhas. Renderização determinística: cada quadro é uma
captura do Chromium com o tempo definido por render(t). O MP4 NÃO deve ir para o Git (media/ está no .gitignore).

uso: python3 tools/video/make_promo.py [segundos_de_teste]
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "media")
FPS = 30

logo = open(os.path.join(ROOT, "site", "logo-mark.svg"), encoding="utf-8").read()
PATH = re.search(r' d="([^"]+)"', logo).group(1)
MARK = lambda fill: f'<svg viewBox="10 5 104 82" xmlns="http://www.w3.org/2000/svg"><path fill="{fill}" fill-rule="evenodd" d="{PATH}"/></svg>'

ICONS = {
    "wallet": '<path d="M3 7h15a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V7zm0 0 2-3h11M16 14h2" />',
    "tag": '<path d="M3 12V4h8l9 9-8 8-9-9z"/><circle cx="7.5" cy="8.5" r="1.3"/>',
    "box": '<path d="M3 8l9-5 9 5v8l-9 5-9-5V8zM3 8l9 5 9-5M12 13v8"/>',
    "cash": '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="12" cy="12" r="3"/>',
    "funnel": '<path d="M3 4h18l-7 8v6l-4 2v-8L3 4z"/>',
    "fork": '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M17 3c-2 2-3 5-3 8h3v10"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5L16 9.5"/>',
}
ic = lambda n, c="#fff": f'<svg viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{ICONS[n]}</svg>'

HTML = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&family=Plus+Jakarta+Sans:wght@700;800&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:720px;height:1280px;overflow:hidden;background:#ecfdf3;font-family:'Inter',system-ui,sans-serif}}
#stage{{position:relative;width:720px;height:1280px;overflow:hidden;background:radial-gradient(900px 700px at 50% 40%,#f7fffa,#e3f9ec)}}
.burst{{position:absolute;width:520px;height:520px}}
.b1{{left:-250px;top:-250px;transform:rotate(-12deg)}} .b2{{right:-260px;bottom:-230px;transform:rotate(18deg)}}
.logo{{position:absolute;right:44px;top:34px;width:112px;height:112px;border-radius:30px;background:linear-gradient(145deg,#22c55e,#0b7a37);box-shadow:0 18px 40px -12px rgba(11,122,55,.6);display:grid;place-items:center;z-index:20}}
.logo svg{{width:68px}}
.pill{{position:absolute;left:50%;bottom:34px;transform:translateX(-50%);background:#fff;border-radius:999px;padding:14px 38px;font:800 22px 'Inter';letter-spacing:.2em;color:#0b6b30;box-shadow:0 10px 30px -12px rgba(0,0,0,.25);z-index:20}}
.scene{{position:absolute;left:60px;top:170px;width:600px;height:1010px;border-radius:44px;padding:44px 40px;opacity:0;overflow:hidden;box-shadow:0 40px 80px -30px rgba(5,60,30,.55)}}
.dark{{background:linear-gradient(165deg,#031a0d 0%,#06301b 55%,#04170d 100%);color:#fff}}
.bright{{background:linear-gradient(160deg,#16a34a 0%,#22c55e 60%,#0e8a3e 100%);color:#fff}}
.light{{background:#fff;color:#0b2416}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:60px 40px;mask-image:linear-gradient(180deg,#000,transparent 85%)}}
.ring{{position:absolute;border:7px solid #4ade80;border-radius:50%;opacity:.8}}
.in{{opacity:0}}
.ico{{width:84px;height:84px;border-radius:24px;display:grid;place-items:center;background:rgba(255,255,255,.18);margin-bottom:26px}}
.light .ico,.dark .ico.g{{background:#16a34a}} .ico svg{{width:46px}}
.badge{{position:absolute;right:40px;top:50px;border:2px solid currentColor;border-radius:999px;padding:8px 22px;font:700 22px 'Inter';opacity:0}}
.lbl{{font:700 34px 'Plus Jakarta Sans';letter-spacing:-.01em}}
.big{{font:800 104px/1.0 'Plus Jakarta Sans';letter-spacing:-.045em;margin:6px 0 4px}}
.acc{{color:#4ade80}} .light .acc{{color:#16a34a}}
.chip{{display:inline-block;background:rgba(255,255,255,.14);border:2px solid rgba(255,255,255,.22);border-radius:999px;padding:12px 28px;font:600 27px 'Inter';margin-top:30px}}
.bub{{background:#fff;color:#0b2416;border-radius:26px;padding:24px 30px;font:600 31px/1.3 'Inter';margin-top:22px;box-shadow:0 14px 34px -16px rgba(0,0,0,.45);max-width:520px}}
.bub.me{{background:#16a34a;color:#fff;margin-left:auto}} .dark .bub.me{{background:#22c55e;color:#032212}}
.bright .bub.me{{background:#052e16;color:#fff}}
.bub b{{font-weight:800}}
.tag{{display:inline-block;border-radius:999px;padding:5px 16px;font:800 22px 'Inter';margin-left:8px;vertical-align:2px}}
.t-red{{background:#fee2e2;color:#b91c1c}} .t-amb{{background:#fef3c7;color:#92400e}} .t-grn{{background:#dcfce7;color:#166534}}
.sheet{{background:#fff;color:#0b2416;border-radius:26px;margin-top:30px;overflow:hidden;box-shadow:0 18px 40px -18px rgba(0,0,0,.6)}}
.fbar{{display:flex;gap:12px;align-items:center;background:#eef3ef;padding:14px 20px;font:700 24px 'JetBrains Mono'}}
.fbar i{{color:#16a34a}} .fbar span{{background:#fff;border-radius:8px;padding:4px 12px}}
.row{{display:flex;justify-content:space-between;padding:22px 28px;font:600 32px 'Inter';border-top:1px solid #e1ece5}}
.row b{{font:800 34px 'JetBrains Mono'}} .row.tot{{background:#dcfce7;color:#166534}}
.bars{{display:flex;gap:26px;align-items:flex-end;height:330px;margin-top:34px}}
.bars div{{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:10px;height:100%;font:800 30px 'Plus Jakarta Sans'}}
.bars i{{display:block;width:100%;border-radius:18px 18px 6px 6px}}
.cta{{display:inline-block;margin-top:46px;background:linear-gradient(135deg,#16a34a,#0b6b30);color:#fff;border-radius:999px;padding:28px 58px;font:800 40px 'Plus Jakarta Sans';box-shadow:0 20px 40px -14px rgba(11,122,55,.7)}}
.wa{{margin-top:34px;font:800 34px 'Inter';color:#86efac;letter-spacing:.01em}}
.cen{{text-align:center}}
</style></head><body>
<div id="stage">
  <svg class="burst b1" viewBox="0 0 200 200"><polygon fill="#22c55e" points="100,0 118,62 175,30 138,86 200,100 138,114 175,170 118,138 100,200 82,138 25,170 62,114 0,100 62,86 25,30 82,62"/></svg>
  <svg class="burst b2" viewBox="0 0 200 200"><polygon fill="#4ade80" points="100,0 118,62 175,30 138,86 200,100 138,114 175,170 118,138 100,200 82,138 25,170 62,114 0,100 62,86 25,30 82,62"/></svg>
  <div class="logo">{MARK('#fff')}</div>

  <!-- S1 -->
  <section class="scene dark" data-s="0" data-e="4.6"><div class="grid"></div><div class="ring" style="width:330px;height:330px;left:-80px;bottom:-110px"></div>
    <div style="margin-top:250px">
      <div class="lbl in" data-in=".2">Quando chega o fim do mês</div>
      <div class="big in" data-in=".7" style="font-size:118px">e você</div>
      <div class="big acc in" data-in="1.2" style="font-size:108px">não sabe</div>
      <div class="chip in" data-in="2.0">quanto realmente sobrou?</div>
    </div></section>
  <!-- S2 caixa -->
  <section class="scene dark" data-s="4.6" data-e="9.6"><div class="grid"></div>
    <div class="ico g in" data-in=".1">{ic('wallet')}</div><div class="badge in" data-in=".2" style="color:#d1fae5">Fluxo de Caixa</div>
    <div class="lbl in" data-in=".3">Planilha para</div><div class="big acc in" data-in=".6">caixa</div>
    <div class="sheet in" data-in="1.0">
      <div class="fbar"><span>D8</span><i>fx</i><em style="font-style:normal" data-type="=B8-C8" data-from="1.3" data-cps="14"></em></div>
      <div class="row"><span>Entradas</span><b data-count="293700" data-from="1.4" data-dur="1.6" data-fmt="money"></b></div>
      <div class="row"><span>Saídas</span><b data-count="242600" data-from="1.6" data-dur="1.6" data-fmt="money"></b></div>
      <div class="row tot"><span>Saldo</span><b data-count="51100" data-from="2.0" data-dur="1.6" data-fmt="money"></b></div>
    </div>
    <div class="chip in" data-in="3.3">margem de <b data-count="17.4" data-from="3.3" data-dur="1" data-fmt="pct1"></b> no semestre</div></section>
  <!-- S3 preço -->
  <section class="scene bright" data-s="9.6" data-e="14.6"><div class="grid"></div>
    <div class="ico in" data-in=".1">{ic('tag')}</div><div class="badge in" data-in=".2">Precificador</div>
    <div class="lbl in" data-in=".3">Planilha para</div><div class="big in" data-in=".6">preço</div>
    <div class="bub in" data-in="1.1" style="margin-top:50px">Custo do produto: <b>R$ 28,00</b></div>
    <div class="bub me in" data-in="2.0"><span data-type="Preço sugerido: R$ 63,90" data-from="2.1" data-cps="26"></span></div>
    <div class="bub in" data-in="3.2">Já com impostos, taxa de cartão, despesas fixas e <b>20% de lucro</b>.</div></section>
  <!-- S4 estoque -->
  <section class="scene light" data-s="14.6" data-e="19.6">
    <div class="ico in" data-in=".1">{ic('box')}</div><div class="badge in" data-in=".2" style="color:#0b6b30">Estoque ABC</div>
    <div class="lbl in" data-in=".3">Planilha para</div><div class="big acc in" data-in=".6">estoque</div>
    <div class="bars">
      <div><i data-bar="100" data-from="1.0" style="background:linear-gradient(#22c55e,#16a34a)"></i>A</div>
      <div><i data-bar="48" data-from="1.3" style="background:linear-gradient(#fbbf24,#d97706)"></i>B</div>
      <div><i data-bar="22" data-from="1.6" style="background:linear-gradient(#cbd5e1,#94a3b8)"></i>C</div></div>
    <div style="margin-top:34px" class="in" data-in="2.3"><span class="tag t-red" style="margin:0">7 em ruptura</span><span class="tag t-amb">5 para repor</span></div>
    <div class="bub in" data-in="3.0" style="background:#f0fdf4;border:2px solid #bbf7d0">Compra sugerida: <b>R$ 811,20</b></div></section>
  <!-- S5 cobrança -->
  <section class="scene dark" data-s="19.6" data-e="25"><div class="grid"></div>
    <div class="ico g in" data-in=".1">{ic('cash')}</div><div class="badge in" data-in=".2" style="color:#d1fae5">Contas a Receber</div>
    <div class="lbl in" data-in=".3">Planilha para</div><div class="big in" data-in=".6">cobrança</div>
    <div class="bub in" data-in="1.2" style="margin-top:40px">Cliente 03 · vencido: <b>R$ 3.517,62</b><span class="tag t-red">12 dias</span></div>
    <div class="bub me in" data-in="2.1" style="font-size:29px"><span data-type="Olá! Consta em aberto o contrato de 15/09, com multa e juros. Podemos regularizar hoje?" data-from="2.2" data-cps="34"></span></div>
    <div class="chip in" data-in="4.0">inadimplência <b data-count="24.1" data-from="4.0" data-dur=".9" data-fmt="pct1"></b></div></section>
  <!-- S6 vendas -->
  <section class="scene light" data-s="25" data-e="30">
    <div class="ico in" data-in=".1">{ic('funnel')}</div><div class="badge in" data-in=".2" style="color:#0b6b30">CRM e Funil</div>
    <div class="lbl in" data-in=".3">Planilha para</div><div class="big acc in" data-in=".6">vendas</div>
    <div class="bub in" data-in="1.2" style="margin-top:40px;max-width:none">Lead 014 · proposta enviada<span class="tag t-amb">HOJE</span></div>
    <div class="bub in" data-in="1.8" style="max-width:none">Lead 027 · negociação<span class="tag t-red">ATRASADO</span></div>
    <div class="bub in" data-in="2.4" style="max-width:none">Lead 031 · novo contato<span class="tag t-grn">Em dia</span></div>
    <div class="bub me in" data-in="3.2">Previsão: <b data-count="91735" data-from="3.3" data-dur="1.2" data-fmt="money"></b></div></section>
  <!-- S7 CMV -->
  <section class="scene bright" data-s="30" data-e="34.6"><div class="grid"></div>
    <div class="ico in" data-in=".1">{ic('fork')}</div><div class="badge in" data-in=".2">Ficha Técnica e CMV</div>
    <div class="lbl in" data-in=".3">Planilha para</div><div class="big in" data-in=".6">cardápio</div>
    <div class="bub in" data-in="1.2" style="margin-top:44px">Hambúrguer artesanal · CMV <b>34,1%</b><span class="tag t-red">ACIMA DA META</span></div>
    <div class="bub me in" data-in="2.2"><span data-type="Preço sugerido: R$ 31,90 para bater 32%" data-from="2.3" data-cps="26"></span></div></section>
  <!-- S8 testado -->
  <section class="scene dark" data-s="34.6" data-e="38.2"><div class="grid"></div><div class="ring" style="width:420px;height:420px;right:-150px;top:-120px;border-color:#22c55e"></div>
    <div class="ico g in" data-in=".1">{ic('shield')}</div>
    <div class="lbl in" data-in=".3" style="margin-top:130px">Antes de vender, a gente</div><div class="big in" data-in=".6" style="font-size:96px">testa tudo.</div>
    <div class="bub in" data-in="1.3" style="margin-top:46px"><b data-count="263" data-from="1.4" data-dur="1" data-fmt="int"></b> conferências, <b>0 erros</b> de fórmula.</div>
    <div class="bub in" data-in="2.1">Dados de exemplo 100% fictícios.</div></section>
  <!-- S9 CTA -->
  <section class="scene light cen" data-s="38.2" data-e="43"><div class="ring" style="width:420px;height:420px;right:-170px;top:-170px;border-color:#22c55e"></div>
    <div class="in" data-in=".1" style="width:190px;margin:120px auto 0">{MARK('#16a34a')}</div>
    <div class="lbl in" data-in=".5" style="margin-top:70px;font-size:44px;line-height:1.2">Quer a planilha certa<br>para o seu negócio?</div>
    <div class="cta in" data-in="1.1">Comprar planilha</div>
    <div class="wa in" data-in="1.7" style="color:#16a34a">WhatsApp (91) 98190-2529</div>
    <div class="in" data-in="2.2" style="margin-top:22px;font:600 28px Inter;color:#47604f">Tutorial + exemplo + dashboard · sem mensalidade</div></section>
  <div class="pill">CARVEX XLS</div>
</div>
<script>
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)), eo=x=>1-Math.pow(1-x,3);
const brl=n=>'R$ '+Math.round(n).toLocaleString('pt-BR');
const scenes=[...document.querySelectorAll('.scene')];
window.TOTAL=+scenes[scenes.length-1].dataset.e;
window.render=function(t){{
  scenes.forEach(s=>{{
    const a=+s.dataset.s,b=+s.dataset.e,lt=t-a;
    const vis=t>=a-0.02&&t<b;
    s.style.display=vis?'block':'none'; if(!vis) return;
    const fin=eo(clamp(lt/.5)), fout=clamp((b-t)/.35);
    const last=s===scenes[scenes.length-1];
    s.style.opacity=last?fin:Math.min(fin,fout);
    s.style.transform=`translateX(${{(1-fin)*70}}px) scale(${{.96+.04*fin}})`;
    s.querySelectorAll('[data-in]').forEach(e=>{{
      const p=eo(clamp((lt-+e.dataset.in)/.55)); e.style.opacity=p; e.style.transform=`translateY(${{(1-p)*34}}px) scale(${{.97+.03*p}})`;
    }});
    s.querySelectorAll('[data-type]').forEach(e=>{{
      const txt=e.dataset.type,n=Math.floor(Math.max(0,lt-+e.dataset.from)*(+e.dataset.cps||30));
      e.textContent=txt.slice(0,n)+(n<txt.length&&n>0?'▌':'');
    }});
    s.querySelectorAll('[data-count]').forEach(e=>{{
      const p=eo(clamp((lt-+e.dataset.from)/+e.dataset.dur)),v=+e.dataset.count*p,f=e.dataset.fmt;
      e.textContent=f==='money'?brl(v):f==='pct1'?v.toFixed(1).replace('.',',')+'%':Math.round(v).toLocaleString('pt-BR');
    }});
    s.querySelectorAll('[data-bar]').forEach(e=>{{
      const p=eo(clamp((lt-+e.dataset.from)/.8)); e.style.height=(+e.dataset.bar*p)+'%';
    }});
  }});
}};
</script></body></html>"""

RENDER = r"""
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
(async () => {
  const [html, dir, fps, limit] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 1 });
  await p.goto('file://' + html);
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1200);
  const total = await p.evaluate(() => window.TOTAL);
  const dur = limit && +limit > 0 ? Math.min(+limit, total) : total;
  const n = Math.round(dur * +fps);
  fs.mkdirSync(dir, { recursive: true });
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => window.render(t), i / +fps);
    await p.screenshot({ path: `${dir}/f${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  console.log('frames', n, 'duração', dur);
  await b.close();
})();
"""


def main():
    limit = sys.argv[1] if len(sys.argv) > 1 else "0"
    os.makedirs(OUT, exist_ok=True)
    html = os.path.join(OUT, "promo.html")
    open(html, "w", encoding="utf-8").write(HTML)
    open(os.path.join(OUT, "render.js"), "w").write(RENDER)
    frames = os.path.join(OUT, "frames")
    subprocess.run(["rm", "-rf", frames], check=True)
    subprocess.run(["node", os.path.join(OUT, "render.js"), html, frames, str(FPS), limit], check=True)
    out = os.path.join(OUT, "carvex-xls-promo.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(frames, "f%05d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "20", "-preset", "medium", "-movflags", "+faststart", out], check=True)
    print("vídeo:", out, round(os.path.getsize(out) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
