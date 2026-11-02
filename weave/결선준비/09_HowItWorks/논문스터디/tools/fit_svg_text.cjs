// LaTeXML 글 상자 그림(assets/*/*.svg)에서 글이 상자보다 길어 아래가 잘리는 것을 줄여요.
//
// LaTeX가 계산한 상자 높이와 브라우저 조판이 달라서, 프롬프트 상자 몇 개는 마지막 줄이 상자 밖으로 넘쳐요
// (arXiv 원문 HTML도 같은 그림에서 글이 넘쳐 캡션과 겹쳐요). 그림을 <img>로 넣으면 넘친 줄은 잘려 안 보여요.
// 이 스크립트는 그림을 헤드리스 크로미움으로 열어 상자(foreignObject)마다 글 높이를 재고, 넘치는 상자에만
// 글 크기 배율 --wv-fit(0.55–1)을 style에 넣어 상자 안에 들어오게 해요. 넘치지 않으면 배율을 지워요.
// 글자 폭은 fix_svg_case.py의 font-size-adjust로 Times 기준에 맞춰 두었으므로 다른 기기에서도 거의 같아요.
//
// 먼저 python tools/fix_svg_case.py 를 돌린 뒤에 써요(그 스크립트가 넣는 <style id="wv-ltx-fo">가 있어야 해요).
// 사용: NODE_PATH=~/.cache/weave-tools/node/node_modules node tools/fit_svg_text.cjs [--dry-run] [파일 …]
//       (파일을 안 주면 assets/*/*.svg 중 wv-ltx-fo가 있는 것 전체. 크로미움 경로는 CHROME 환경 변수로 바꿀 수 있어요.)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright-core');

const ROOT = path.dirname(__dirname);
const CHROME = process.env.CHROME || path.join(process.env.HOME, '.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
const MIN_BOX = 30;   // 한 줄짜리 제목 상자(높이 30 미만)는 띠가 더 커서 넘쳐도 괜찮아요
const SLACK = 3;      // 이만큼(px)까지 넘치는 것은 테두리 안쪽 여백에 들어가요
const SAFETY = 0.97;  // 다른 글꼴을 생각해 찾은 배율보다 조금 더 줄여요

function listFiles(args) {
  if (args.length) return args.map(f => path.resolve(f));
  const out = [];
  for (const d of fs.readdirSync(path.join(ROOT, 'assets'))) {
    const dir = path.join(ROOT, 'assets', d);
    if (!fs.statSync(dir).isDirectory()) continue;
    for (const f of fs.readdirSync(dir).sort()) {
      if (!f.endsWith('.svg')) continue;
      const p = path.join(dir, f);
      if (fs.readFileSync(p, 'utf8').includes('id="wv-ltx-fo"')) out.push(p);
    }
  }
  return out;
}

// i번째 <foreignObject …> 시작 태그의 style에서 --wv-fit를 지우고(fit가 있으면) 새로 넣어요.
function setFit(text, index, fit) {
  let n = -1;
  return text.replace(/<foreignObject\b[^>]*>/g, tag => {
    n += 1;
    if (n !== index) return tag;
    let t = tag.replace(/--wv-fit:[\d.]+;?/g, '');
    if (fit == null) return t;
    if (/\sstyle="/.test(t)) return t.replace(/\sstyle="/, ` style="--wv-fit:${fit};`);
    return t.replace(/<foreignObject\b/, `<foreignObject style="--wv-fit:${fit};"`);
  });
}

(async () => {
  const argv = process.argv.slice(2);
  const dry = argv.includes('--dry-run');
  const files = listFiles(argv.filter(a => a !== '--dry-run'));
  const browser = await chromium.launch({ executablePath: CHROME });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  let changed = 0;
  for (const file of files) {
    await page.goto('file://' + file);
    await page.waitForTimeout(100);
    const res = await page.evaluate(({ MIN_BOX, SLACK, SAFETY }) => {
      const out = [];
      const fos = [...document.getElementsByTagName('foreignObject')];
      const height = fo => {
        const c = fo.querySelector('.ltx_foreignobject_content');
        if (!c) return null;
        const m = c.querySelector(':scope > .ltx_minipage') || c;
        return m.getBoundingClientRect().height;
      };
      fos.forEach((fo, i) => {
        const box = parseFloat(fo.getAttribute('height'));
        const before = fo.style.getPropertyValue('--wv-fit').trim() || null;
        fo.style.removeProperty('--wv-fit');
        const h1 = height(fo);
        if (h1 == null || box < MIN_BOX || h1 <= box + SLACK) {
          out.push({ i, box, h: h1, before, fit: null });
          return;
        }
        let lo = 0.55, hi = 1.0;
        for (let k = 0; k < 9; k++) {
          const mid = (lo + hi) / 2;
          fo.style.setProperty('--wv-fit', String(mid));
          if (height(fo) <= box - 1) lo = mid; else hi = mid;
        }
        const fit = Math.floor(lo * SAFETY * 100) / 100;
        fo.style.setProperty('--wv-fit', String(fit));
        out.push({ i, box, h: h1, before, fit, after: height(fo) });
      });
      return out;
    }, { MIN_BOX, SLACK, SAFETY });
    let text = fs.readFileSync(file, 'utf8');
    const orig = text;
    const notes = [];
    for (const r of res) {
      const want = r.fit == null ? null : r.fit.toFixed(2);
      if ((r.before || null) !== want) text = setFit(text, r.i, want);
      if (r.fit != null) notes.push(`상자${r.i + 1} 높이 ${r.box.toFixed(0)} · 글 ${r.h.toFixed(0)} → 배율 ${want} (맞춘 뒤 ${r.after.toFixed(0)})`);
    }
    const rel = path.relative(ROOT, file);
    if (text !== orig) {
      changed += 1;
      if (!dry) fs.writeFileSync(file, text);
      console.log((dry ? '바꿀 것 ' : '맞춤 ') + rel + (notes.length ? '  ' + notes.join('; ') : '  (배율 지움)'));
    } else if (notes.length) {
      console.log('그대로 ' + rel + '  ' + notes.join('; '));
    }
  }
  await browser.close();
  console.log(`---\n검사한 SVG ${files.length}개, ${dry ? '바꿀' : '바꾼'} 파일 ${changed}개`);
})();
