/* Weave · How it Works 논문 스터디 — 데이터는 data/*.js(window.WV_PAPERS, window.WV_OVERVIEW) */
(function () {
  'use strict';
  var P = window.WV_PAPERS || {};
  var O = window.WV_OVERVIEW || { groups: [] };
  var main = document.getElementById('main');
  var side = document.getElementById('side');
  var MODES = { en: '원문', both: '함께', ko: '번역' };
  var mode = localStorage.getItem('wv_mode') || 'both';

  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function setMode(m) {
    mode = m;
    localStorage.setItem('wv_mode', m);
    document.body.classList.remove('mode-en', 'mode-ko', 'mode-both');
    document.body.classList.add('mode-' + m);
    var bs = document.querySelectorAll('.seg button');
    for (var i = 0; i < bs.length; i++) bs[i].classList.toggle('on', bs[i].getAttribute('data-m') === m);
    if (main) fitWideMath();
  }
  function math(el) {
    if (window.renderMathInElement) {
      window.renderMathInElement(el, {
        delimiters: [{ left: '\\[', right: '\\]', display: true }, { left: '\\(', right: '\\)', display: false }],
        throwOnError: false, strict: 'ignore'
      });
    }
  }
  /* 칸보다 넓은 수식은 그 수식만 가로로 밀어 보게 해요(옆 칸·화면 밖으로 넘치지 않게). 보기 모드·창 크기가 바뀌면 다시 재요. */
  function fitWideMath() {
    var ks = main.querySelectorAll('.en .katex, .ko .katex'), wide = [], i;
    for (i = 0; i < ks.length; i++) ks[i].classList.remove('wide');
    for (i = 0; i < ks.length; i++) {
      var col = ks[i].closest('.en, .ko');
      if (!col || !col.offsetWidth) continue;
      if (ks[i].getBoundingClientRect().right > col.getBoundingClientRect().right + 4) wide.push(ks[i]);
    }
    for (i = 0; i < wide.length; i++) wide[i].classList.add('wide');
  }
  /* 표에서 글이 긴 칸(예시·프롬프트)은 한 줄로 늘이지 않고 줄바꿈해요. 수식을 그리기 전에 불러요(수식 원문은 짧게 셈). */
  function markLongCells(el) {
    var cs = el.querySelectorAll('.table td, .table th');
    for (var i = 0; i < cs.length; i++) {
      if ((cs[i].textContent || '').replace(/\\\(.*?\\\)/g, '0000').length > 60) cs[i].classList.add('long');
    }
  }

  /* 왼쪽 목록 */
  function renderSide(cur) {
    var h = '<a class="item home' + (cur ? '' : ' on') + '" href="#/">개요 · 읽는 순서</a>';
    h += '<a class="item home' + (cur === '_gl' ? ' on' : '') + '" href="#/glossary">용어 모음</a>';
    O.groups.forEach(function (g) {
      h += '<h4>' + esc(g.title) + '</h4>';
      g.keys.forEach(function (k) {
        var d = P[k]; if (!d) return;
        var m = d.meta || {};
        h += '<a class="item' + (cur === k ? ' on' : '') + '" href="#/p/' + k + '"><span class="nm">' + esc(m.short || d.title) +
          '</span><span class="vn">' + esc(m.venue || '') + '</span><span class="ol">' + esc(m.one_line || '') + '</span></a>';
      });
    });
    side.innerHTML = h;
  }

  /* 개요 */
  function renderHome() {
    renderSide(null);
    var h = '<section class="hero"><span class="nota">' + esc(O.updated || '') + '</span><h1>' + esc(O.title || '') + '</h1>' + (O.intro || '') + '</section>';
    if (O.reading) h += '<div class="card"><h3>읽는 순서</h3>' + O.reading + '</div>';
    h += '<div class="card"><h3>한눈에 비교</h3><div style="overflow:auto"><table class="ov"><tr><th>논문</th><th>무엇을 하나</th><th>여러 단계로 찾는 방식</th><th>질문 하나에 드는 모델 호출</th><th>미리 해 두는 일(색인)</th></tr>';
    O.groups.forEach(function (g) {
      g.keys.forEach(function (k) {
        var d = P[k]; if (!d) return; var m = d.meta || {};
        h += '<tr><td class="nm"><a href="#/p/' + k + '">' + esc(m.short || k) + '</a><small>' + esc(m.venue || '') + '</small></td><td>' + esc(m.one_line || '') +
          '</td><td>' + esc((O.hop && O.hop[k]) || m.key_idea || '') + '</td><td>' + esc((O.calls && O.calls[k]) || m.llm_calls || '') + '</td><td>' + esc((O.prep && O.prep[k]) || m.index_cost || '') + '</td></tr>';
      });
    });
    h += '</table></div>' + (O.calls || O.prep ? '<p class="nota" style="margin:8px 0 0">호출·색인 칸은 한 줄로 줄인 것이에요. 근거가 되는 자세한 정리는 각 논문 페이지의 ‘비용 구조’ 카드에 있어요.</p>' : '') + '</div>';
    if (O.claims) h += '<div class="card weave"><h3>장표 주장과 근거</h3>' + O.claims + '</div>';
    O.groups.forEach(function (g) {
      h += '<h2 style="margin:30px 0 10px;font-size:19px">' + esc(g.title) + '</h2>' + (g.desc ? '<p style="color:var(--ink2);margin-top:0">' + g.desc + '</p>' : '') + '<div class="cards">';
      g.keys.forEach(function (k) {
        var d = P[k]; if (!d) return; var m = d.meta || {};
        h += '<a class="pcard" href="#/p/' + k + '"><div class="nm">' + esc(m.short || d.title) + '</div><div class="vn">' + esc(m.venue || '') + ' · ' + esc(m.authors_short || '') +
          '</div><div class="ol">' + esc(m.one_line || '') + '</div></a>';
      });
      h += '</div>';
    });
    main.innerHTML = h;
    math(main);
    window.scrollTo(0, 0);
  }

  /* 용어 */
  function renderGlossary() {
    renderSide('_gl');
    var rows = [];
    O.groups.forEach(function (g) {
      g.keys.forEach(function (k) {
        var d = P[k]; if (!d || !d.meta || !d.meta.glossary) return;
        d.meta.glossary.forEach(function (x) { rows.push([x.term, x.ko, x.desc, d.meta.short || k, k]); });
      });
    });
    rows.sort(function (a, b) { return a[0].toLowerCase() < b[0].toLowerCase() ? -1 : 1; });
    var h = '<section class="hero"><h1>용어 모음</h1><p>논문마다 정리한 용어를 모았어요. 같은 용어가 여러 논문에 나오면 각각의 맥락으로 남겨 뒀어요.</p></section><div class="card"><table class="gl">';
    rows.forEach(function (r) { h += '<tr><td>' + esc(r[0]) + '</td><td>' + esc(r[1]) + '</td><td>' + esc(r[2]) + ' <a class="nota" href="#/p/' + r[4] + '">' + esc(r[3]) + '</a></td></tr>'; });
    h += '</table></div>';
    main.innerHTML = h;
    window.scrollTo(0, 0);
  }

  /* 블록 */
  function pair(en, ko, tag) {
    var k = ko ? ko : '<span class="untr">(번역 없음 · 원문 참고)</span>';
    return '<div class="en">' + en + '</div><div class="ko">' + k + '</div>';
  }
  function blockHTML(b, ko) {
    var t = b.type, k = ko[b.id];
    if (t === 'h2' || t === 'h3' || t === 'h4') {
      return '<' + t + ' class="blk" id="' + b.id + '">' + (k ? '<span class="hko">' + k + '</span><span class="hen">' + b.html + '</span>' : '<span>' + b.html + '</span>') + '</' + t + '>';
    }
    if (t === 'p') return '<div class="blk p" id="' + b.id + '">' + pair(b.html, k) + '<button class="flip" title="이 문단만 전환">⇄</button></div>';
    if (t === 'li') return '<div class="blk li lv' + (b.level || 1) + '" id="' + b.id + '"><span class="mark">' + esc(b.mark || '') + '</span>' + pair(b.html, k) + '<button class="flip">⇄</button></div>';
    if (t === 'fn') return '<div class="blk fn" id="' + b.id + '"><div class="en" data-m="' + esc(b.mark) + '">' + b.html + '</div><div class="ko" data-m="' + esc(b.mark) + '">' + (k || '<span class="untr">(번역 없음)</span>') + '</div></div>';
    if (t === 'eq') return '<div class="eq" id="' + b.id + '">' + (b.tag ? '<span class="tag">' + esc(b.tag) + '</span>' : '') + '\\[' + esc(b.latex) + '\\]</div>';
    var cap = b.html ? '<div class="cap">' + pair(b.html, k) + '</div>' : '';
    if (t === 'fig') {
      var im = (b.img || []).map(function (x) { return '<img loading="lazy" src="' + x.src + '"' + (x.w ? ' style="width:' + Math.min(100, Math.max(30, x.w / 5.2)) + '%"' : '') + '>'; }).join('');
      return '<div class="figure" id="' + b.id + '">' + (im ? '<div class="imgs">' + im + '</div>' : '') + cap + '</div>';
    }
    if (t === 'tab') {
      var im2 = (b.img || []).map(function (x) { return '<img loading="lazy" src="' + x.src + '">'; }).join('');
      return '<div class="table" id="' + b.id + '">' + cap + (b.table ? '<div class="tw">' + b.table + '</div>' : '') + (im2 ? '<div class="imgs">' + im2 + '</div>' : '') + '</div>';
    }
    if (t === 'alg') return '<div class="alg" id="' + b.id + '">' + cap + '<pre>' + (b.lines || []).map(function (l) { return l; }).join('\n') + '</pre></div>';
    return '';
  }

  function summaryHTML(d) {
    var m = d.meta || {};
    var h = '';
    if (m.one_line) h += '<div class="card"><h3>한 줄 요약</h3><div class="one">' + esc(m.one_line) + '</div></div>';
    var left = '', right = '';
    if (m.problem) left += '<h3>무엇이 문제인가</h3><p style="margin-top:0">' + esc(m.problem) + '</p>';
    if (m.key_idea) left += '<h3>핵심 아이디어</h3><p style="margin-top:0">' + esc(m.key_idea) + '</p>';
    if (m.pipeline && m.pipeline.length) right += '<h3>파이프라인</h3><ol class="steps">' + m.pipeline.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ol>';
    if (left || right) h += '<div class="card"><div class="grid2"><div>' + left + '</div><div>' + right + '</div></div></div>';
    if (m.llm_calls || m.index_cost) h += '<div class="card"><h3>비용 구조</h3><dl class="kv">' + (m.llm_calls ? '<dt>질문당 호출</dt><dd>' + esc(m.llm_calls) + '</dd>' : '') + (m.index_cost ? '<dt>사전 색인</dt><dd>' + esc(m.index_cost) + '</dd>' : '') + '</dl></div>';
    if (m.pipeline_figure) {
      var fb = (d.blocks || []).filter(function (b) { return b.id === m.pipeline_figure; })[0];
      if (fb) h += '<div class="card"><h3>파이프라인 그림</h3>' + blockHTML(fb, d.ko || {}).replace('id="' + fb.id + '"', '') + '</div>';
    }
    if (m.results && m.results.length) {
      h += '<div class="card"><h3>주요 결과 (원문 인용)</h3><ul class="res">' + m.results.map(function (r) {
        return '<li>' + esc(r.claim) + '<span class="w">' + esc(r.where || '') + '</span>' + (r.quote ? '<span class="q">“' + esc(r.quote).replace(/&lt;(\/?)(sub|sup)&gt;/g, '<$1$2>') + '”</span>' : '') + '</li>';
      }).join('') + '</ul></div>';
    }
    var wv = m.weave || {};
    if ((wv.borrow && wv.borrow.length) || (wv.contrast && wv.contrast.length) || (m.limits && m.limits.length)) {
      h += '<div class="card weave"><div class="grid2"><div><h3>Weave에 가져올 점</h3><ul>' + (wv.borrow || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') +
        '</ul><h3>Weave와 다른 점 · 주의</h3><ul>' + (wv.contrast || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div><div><h3>한계</h3><ul>' +
        (m.limits || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div></div></div>';
    }
    if (m.project_page_notes) h += '<div class="card"><h3>프로젝트 페이지 메모</h3><div style="white-space:pre-wrap">' + esc(typeof m.project_page_notes === 'string' ? m.project_page_notes : JSON.stringify(m.project_page_notes, null, 2)) + '</div></div>';
    if (m.glossary && m.glossary.length) h += '<div class="card"><h3>용어</h3><table class="gl">' + m.glossary.map(function (x) { return '<tr><td>' + esc(x.term) + '</td><td>' + esc(x.ko) + '</td><td>' + esc(x.desc) + '</td></tr>'; }).join('') + '</table></div>';
    return h;
  }

  function renderPaper(key, anchor) {
    var d = P[key];
    if (!d) { renderHome(); return; }
    renderSide(key);
    var m = d.meta || {}, ko = d.ko || {};
    var L = m.links || {};
    var links = [['arXiv', L.arxiv || d.url], ['PDF', L.pdf || d.pdf_url], ['HTML 원문', L.html || d.html_url], ['프로젝트', L.project], ['코드', L.code]]
      .filter(function (x) { return x[1]; }).map(function (x) { return '<a target="_blank" rel="noopener" href="' + esc(x[1]) + '">' + x[0] + '</a>'; }).join('');
    var h = '<div class="paper-head"><span class="kicker">' + esc(m.venue || 'arXiv') + '</span><h1>' + esc(d.title) + '</h1>' +
      (m.title_ko ? '<div class="tko">' + esc(m.title_ko) + '</div>' : '') + '<div class="au">' + esc(m.authors_short || d.authors) + ' · arXiv ' + esc(d.version) + '</div><div class="links">' + links + '</div></div>';
    h += summaryHTML(d);
    // 목차
    var toc = (d.blocks || []).filter(function (b) { return (b.type === 'h2' || b.type === 'h3') && !b.appendix; })
      .map(function (b) { return '<a class="l' + b.type.slice(1) + '" href="#/p/' + key + '/' + b.id + '">' + (ko[b.id] || b.html) + '</a>'; }).join('');
    h += '<div class="card"><h3>본문 전문 · 번역</h3><p class="nota" style="margin-top:0">위 막대에서 원문·함께·번역을 고를 수 있고(단축키 T), 문단 오른쪽 ⇄는 그 문단만 바꿔 보여 줘요. 표 안의 글자와 수식은 원문 그대로예요. 부록은 맨 아래에 접어 두었고, 방법을 설명하는 부분만 번역했어요.</p><div class="toc">' + toc + '</div></div>';
    h += '<div class="body"><h2 class="blk" id="abs"><span class="hko">초록</span><span class="hen">Abstract</span></h2>';
    (d.abstract || []).forEach(function (b) { h += blockHTML(b, ko); });
    var app = '';
    (d.blocks || []).forEach(function (b) { if (b.appendix) app += blockHTML(b, ko); else h += blockHTML(b, ko); });
    if (app) h += '<details class="app"><summary>부록 (원문 · 일부 번역)</summary>' + app + '</details>';
    h += '</div><p class="nota" style="margin-top:40px">원문: ' + esc(d.title) + ' (arXiv ' + esc(d.version) + '). 공부용 사본이며, 저작권은 저자에게 있어요. 인용할 때는 원문을 확인하세요.</p>';
    main.innerHTML = h;
    markLongCells(main);
    math(main);
    fitWideMath();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitWideMath);
    if (anchor) {
      var el = document.getElementById(anchor);
      if (el) { el.scrollIntoView(); window.scrollBy(0, -70); return; }
    }
    window.scrollTo(0, 0);
  }

  function route() {
    var hs = location.hash.replace(/^#\/?/, '').split('/');
    if (hs[0] === 'p' && hs[1]) renderPaper(hs[1], hs[2]);
    else if (hs[0] === 'glossary') renderGlossary();
    else renderHome();
  }

  document.addEventListener('click', function (e) {
    var t = e.target;
    if (t.classList && t.classList.contains('flip')) { t.parentNode.classList.toggle('flipped'); fitWideMath(); e.preventDefault(); }
    if (t.matches && t.matches('.seg button')) setMode(t.getAttribute('data-m'));
  });
  var rsz = 0;
  window.addEventListener('resize', function () { clearTimeout(rsz); rsz = setTimeout(fitWideMath, 150); });
  document.addEventListener('keydown', function (e) {
    if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
    if (e.key === 't' || e.key === 'T') setMode(mode === 'both' ? 'ko' : mode === 'ko' ? 'en' : 'both');
  });
  window.addEventListener('hashchange', route);
  setMode(mode);
  route();
})();
