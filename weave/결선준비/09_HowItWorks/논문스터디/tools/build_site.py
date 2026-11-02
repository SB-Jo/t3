#!/usr/bin/env python3
"""work/<key>/{src.json, ko/*.json, meta_ko.json} + overview.json → data/*.js + index.html

사용: python tools/build_site.py
index.html은 file://로 바로 열려요(fetch 없이 script 태그로 데이터를 읽음).
"""
import glob
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p, default=None):
    if not os.path.exists(p):
        return default
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def check_claims(ov):
    """개요의 '장표 주장과 근거' 인용이 work/<key>/meta_ko.json results[]의 quote에 글자 그대로 있고 where도 같은지 확인해요."""
    found = re.findall(r'<blockquote class="q" data-k="([^"]+)">.*?<span class="w">(.*?)</span>.*?<q>(.*?)</q></blockquote>',
                       ov.get('claims') or '', re.S)
    bad = []
    for key, where, quote in found:
        quote, where = html.unescape(quote), html.unescape(where)
        rs = load(os.path.join(ROOT, 'work', key, 'meta_ko.json'), {}).get('results', [])
        if not any(quote in r.get('quote', '') and where == r.get('where') for r in rs):
            bad.append('%s: %s…' % (key, quote[:60]))
    if found:
        print('장표 주장 인용 %d개 확인, 원문(meta_ko.json)과 다른 것 %d개' % (len(found), len(bad)))
    for b in bad:
        print('  ! 인용 불일치', b)


def main():
    ov = load(os.path.join(ROOT, 'overview.json'), {'title': 'Weave · How it Works 논문 스터디', 'groups': []})
    keys = [k for g in ov['groups'] for k in g['keys']]
    os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
    scripts = []
    stats = []
    for k in keys:
        w = os.path.join(ROOT, 'work', k)
        src = load(os.path.join(w, 'src.json'))
        if not src:
            print('없음:', k)
            continue
        ko = {}
        for fn in sorted(glob.glob(os.path.join(w, 'ko', '*.json'))):
            ko.update(load(fn, {}))
        meta = load(os.path.join(w, 'meta_ko.json'), {})
        d = {'key': k, 'title': src['title'], 'authors': src['authors'], 'version': src['version'], 'url': src['url'],
             'html_url': src['html_url'], 'pdf_url': src['pdf_url'], 'abstract': src['abstract'], 'blocks': src['blocks'],
             'ko': ko, 'meta': meta}
        out = os.path.join(ROOT, 'data', k + '.js')
        with open(out, 'w', encoding='utf-8') as f:
            f.write('window.WV_PAPERS=window.WV_PAPERS||{};window.WV_PAPERS[%s]=' % json.dumps(k))
            json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
            f.write(';\n')
        scripts.append('data/%s.js' % k)
        need = [b['id'] for b in src['abstract'] + src['blocks'] if not b.get('appendix') and (b['type'] in ('h2', 'h3', 'h4', 'p', 'li', 'fn') or (b['type'] in ('fig', 'tab', 'alg') and b.get('html')))]
        stats.append('%-12s 번역 %3d/%3d  요약 %s  %.0fKB' % (k, sum(1 for i in need if i in ko), len(need), '있음' if meta else '없음', os.path.getsize(out) / 1024))
    with open(os.path.join(ROOT, 'data', 'overview.js'), 'w', encoding='utf-8') as f:
        f.write('window.WV_OVERVIEW=')
        json.dump(ov, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')
    tags = '\n'.join('<script src="%s"></script>' % s for s in scripts)
    html = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weave · How it Works 논문 스터디</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<link rel="stylesheet" href="vendor/katex/katex.min.css">
<link rel="stylesheet" href="app.css">
</head>
<body class="mode-both">
<header class="top">
  <div class="brand"><b>Weave</b> · How it Works 논문 스터디<small>멀티홉 검색 · 추론형 임베딩 · 개인 기록 기억</small></div>
  <div class="spacer"></div>
  <span class="hint">T: 보기 전환</span>
  <div class="seg"><button data-m="en">원문</button><button data-m="both" class="on">함께</button><button data-m="ko">번역</button></div>
</header>
<div class="wrap">
  <nav class="side" id="side"></nav>
  <main id="main"></main>
</div>
<script src="vendor/katex/katex.min.js"></script>
<script src="vendor/katex/contrib/auto-render.min.js"></script>
<script src="data/overview.js"></script>
%s
<script src="app.js"></script>
</body>
</html>
''' % tags
    with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print('\n'.join(stats))
    print('index.html ←', len(scripts), '편')
    check_claims(ov)


if __name__ == '__main__':
    main()
