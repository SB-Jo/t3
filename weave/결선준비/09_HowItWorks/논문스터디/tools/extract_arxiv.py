#!/usr/bin/env python3
"""arXiv HTML(LaTeXML) → 문단 단위 JSON.

사용: python extract_arxiv.py <arxiv_id> <key> [--html saved.html]
결과: work/<key>/src.json, work/<key>/src.txt(번역용 목록), assets/<key>/*(그림)

블록 종류
  h2·h3·h4  절 제목          p   문단        li  목록 항목
  eq        수식(latex)      fig 그림(+캡션)  tab 표(+캡션, 표 HTML)
  alg       알고리즘(줄 목록 + 캡션)          fn  각주
번역할 것은 h2·h3·h4·p·li·fn과 fig·tab·alg의 캡션(html)이에요. eq는 번역하지 않아요.
본문 html은 b·i·code·sup·sub·a·span.cite·br만 남기고, 수식은 \\( … \\) / \\[ … \\]로 바꿔요(KaTeX).
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {'User-Agent': 'Mozilla/5.0 (weave-study; personal research reading)'}


def fetch(url, binary=False, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
                final = r.geturl()
            return (data if binary else data.decode('utf-8', 'replace')), final
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 + 3 * i)
    raise last


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def clean_latex(tex):
    tex = tex.strip()
    tex = re.sub(r'\\displaystyle\s*', '', tex)
    return tex


KEEP = {'b': 'b', 'strong': 'b', 'i': 'i', 'em': 'i', 'sup': 'sup', 'sub': 'sub', 'code': 'code'}


class Inline:
    """Tag → 가벼운 HTML 문자열. 각주는 따로 모아요."""

    def __init__(self):
        self.footnotes = []

    def conv(self, node):
        out = []
        for ch in node.children:
            out.append(self.one(ch))
        s = ''.join(out)
        s = re.sub(r'[ \t\r\n]+', ' ', s)
        return s

    def one(self, ch):
        if isinstance(ch, NavigableString):
            if ch.__class__.__name__ in ('Comment', 'ProcessingInstruction', 'Doctype'):
                return ''
            return esc(str(ch))
        if not isinstance(ch, Tag):
            return ''
        cls = ch.get('class') or []
        name = ch.name
        if name == 'math':
            tex = ch.get('alttext') or ch.get_text(' ')
            tex = clean_latex(tex)
            if ch.get('display') == 'block':
                return ' \\[' + esc(tex) + '\\] '
            return '\\(' + esc(tex) + '\\)'
        if 'ltx_note' in cls and ('ltx_role_footnote' in cls or 'ltx_role_footnotetext' in cls):
            mark = ch.find(class_='ltx_note_mark')
            content = ch.find(class_='ltx_note_content')
            m = mark.get_text(strip=True) if mark else '*'
            if content:
                c2 = BeautifulSoup(str(content), 'lxml').find(class_='ltx_note_content')
                for t in c2.find_all(class_='ltx_note_mark'):
                    t.decompose()
                for t in c2.find_all(class_='ltx_tag_note'):
                    t.decompose()
                self.footnotes.append((m, Inline().conv(c2).strip()))
            return '<sup class="fnm">' + esc(m) + '</sup>'
        if 'ltx_note' in cls:
            return ''
        if 'ltx_cite' in cls:
            return '<span class="cite">' + esc(ch.get_text(' ', strip=True)) + '</span>'
        if name in ('img', 'svg', 'script', 'style', 'button'):
            return ''
        if name == 'br':
            return '<br>'
        if name == 'a':
            href = ch.get('href') or ''
            inner = self.conv(ch)
            if href.startswith('http'):
                return '<a href="' + esc(href) + '">' + inner + '</a>'
            return inner
        if name in KEEP:
            inner = self.conv(ch)
            return '<%s>%s</%s>' % (KEEP[name], inner, KEEP[name]) if inner.strip() else inner
        if 'ltx_font_bold' in cls:
            inner = self.conv(ch)
            return '<b>' + inner + '</b>' if inner.strip() else inner
        if 'ltx_font_italic' in cls or 'ltx_emph' in cls:
            inner = self.conv(ch)
            return '<i>' + inner + '</i>' if inner.strip() else inner
        if 'ltx_font_typewriter' in cls:
            inner = self.conv(ch)
            return '<code>' + inner + '</code>' if inner.strip() else inner
        return self.conv(ch)


class Extractor:
    def __init__(self, key, base_url, html):
        self.key = key
        self.base_url = base_url
        self.soup = BeautifulSoup(html, 'lxml')
        self.blocks = []
        self.n = 0
        self.figs = 0
        self.asset_dir = os.path.join(ROOT, 'assets', key)
        os.makedirs(self.asset_dir, exist_ok=True)
        self.appendix = False

    def add(self, typ, **kw):
        self.n += 1
        b = {'id': 'b%03d' % self.n, 'type': typ}
        if self.appendix:
            b['appendix'] = True
        b.update(kw)
        self.blocks.append(b)
        return b

    def text_block(self, typ, node, **kw):
        inl = Inline()
        html = inl.conv(node).strip()
        if html:
            self.add(typ, html=html, **kw)
        for m, c in inl.footnotes:
            if c:
                self.add('fn', html=c, mark=m)

    def img(self, im):
        """img(src)·object(data, 보통 SVG)·인라인 svg를 assets/<key>/에 저장해요."""
        self.figs += 1
        if im.name == 'svg':
            fn = 'fig%02d.svg' % self.figs
            svg = str(im)
            if 'xmlns=' not in svg[:200]:
                svg = svg.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1)
            with open(os.path.join(self.asset_dir, fn), 'w', encoding='utf-8') as f:
                f.write(svg)
            w = im.get('width')
            return {'src': 'assets/%s/%s' % (self.key, fn), 'w': int(float(w)) if w and re.match(r'^[\d.]+$', str(w)) else None}
        src = im.get('src') or im.get('data') or ''
        if not src:
            return None
        url = urllib.parse.urljoin(self.base_url, src)
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or '.png'
        if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'):
            ext = '.png'
        fn = 'fig%02d%s' % (self.figs, ext)
        path = os.path.join(self.asset_dir, fn)
        try:
            data, _ = fetch(url, binary=True)
            with open(path, 'wb') as f:
                f.write(data)
        except Exception as e:  # noqa: BLE001
            print('  ! image failed', url, e, file=sys.stderr)
            return None
        w = im.get('width')
        return {'src': 'assets/%s/%s' % (self.key, fn), 'w': int(float(w)) if w and re.match(r'^[\d.]+$', str(w)) else None}

    def images(self, fig):
        out = []
        for im in fig.find_all(['img', 'object', 'svg']):
            if im.name == 'svg' and im.find_parent('svg') is not None:
                continue
            if im.name == 'img' and im.find_parent('object') is not None:
                continue
            if im.name in ('object',) and (im.get('type') or '').find('svg') < 0 and not im.get('data'):
                continue
            x = self.img(im)
            if x:
                out.append(x)
        return out

    def caption(self, fig):
        cap = fig.find('figcaption', recursive=False) or fig.find('figcaption')
        if not cap:
            return ''
        return Inline().conv(cap).strip()

    def table_html(self, tab):
        """표는 구조만 남겨요(번역하지 않음)."""
        out = ['<table>']
        for tr in tab.find_all('tr'):
            out.append('<tr>')
            for td in tr.find_all(['td', 'th'], recursive=False):
                attrs = ''
                for a in ('colspan', 'rowspan'):
                    if td.get(a):
                        attrs += ' %s="%s"' % (a, td.get(a))
                tag = 'th' if (td.name == 'th' or 'ltx_th' in (td.get('class') or [])) else 'td'
                out.append('<%s%s>%s</%s>' % (tag, attrs, Inline().conv(td).strip(), tag))
            out.append('</tr>')
        out.append('</table>')
        return ''.join(out)

    def figure(self, fig):
        cls = fig.get('class') or []
        if 'ltx_table' in cls:
            tabs = fig.find_all('table', class_='ltx_tabular')
            html_tabs = [self.table_html(t) for t in tabs if t.find_parent('table', class_='ltx_tabular') is None]
            imgs = self.images(fig) if not html_tabs else []
            self.add('tab', html=self.caption(fig), table=''.join(html_tabs), img=imgs)
            return
        if 'ltx_float_algorithm' in cls or fig.find(class_='ltx_listing'):
            lines = []
            for ln in fig.find_all(class_='ltx_listingline'):
                lines.append(Inline().conv(ln).strip())
            if not lines:
                lines = [l for l in fig.get_text('\n').split('\n') if l.strip()]
            self.add('alg', html=self.caption(fig), lines=lines)
            return
        imgs = self.images(fig)
        if fig.find('table', class_='ltx_tabular') and not imgs:
            tabs = fig.find_all('table', class_='ltx_tabular')
            self.add('tab', html=self.caption(fig), table=''.join(self.table_html(t) for t in tabs), img=[])
            return
        if not imgs:
            # 그림 대신 글 상자(프롬프트 등)인 경우: 캡션을 뺀 글을 줄 단위로 남겨요
            f2 = BeautifulSoup(str(fig), 'lxml').find('figure')
            for c in f2.find_all('figcaption'):
                c.decompose()
            lines = [l.strip() for l in f2.get_text('\n').split('\n') if l.strip()]
            if lines:
                self.add('alg', html=self.caption(fig), lines=lines)
                return
        self.add('fig', html=self.caption(fig), img=imgs)

    def equation(self, tab):
        rows = []
        tag = ''
        for m in tab.find_all('math'):
            rows.append(clean_latex(m.get('alttext') or m.get_text(' ')))
        t = tab.find(class_='ltx_tag_equation')
        if t:
            tag = t.get_text(strip=True)
        if rows:
            latex = rows[0] if len(rows) == 1 else '\\begin{aligned}' + ' \\\\ '.join(rows) + '\\end{aligned}'
            self.add('eq', latex=latex, tag=tag)

    def walk(self, node):
        for ch in node.children:
            if not isinstance(ch, Tag):
                continue
            cls = ch.get('class') or []
            name = ch.name
            if 'ltx_bibliography' in cls or 'ltx_authors' in cls or 'ltx_dates' in cls:
                continue
            if 'ltx_abstract' in cls or 'ltx_title_document' in cls or 'ltx_TOC' in cls:
                continue
            if name == 'section' or 'ltx_paragraph' in cls or 'ltx_subparagraph' in cls:
                was = self.appendix
                if 'ltx_appendix' in cls:
                    self.appendix = True
                self.walk(ch)
                self.appendix = was
                continue
            if name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') and 'ltx_title' in cls:
                lvl = {'h1': 'h2', 'h2': 'h2', 'h3': 'h3'}.get(name, 'h4')
                self.text_block(lvl, ch)
                continue
            if name == 'figure':
                self.figure(ch)
                continue
            if name == 'table' and ('ltx_equation' in cls or 'ltx_equationgroup' in cls):
                self.equation(ch)
                continue
            if name in ('ul', 'ol') and ('ltx_itemize' in cls or 'ltx_enumerate' in cls or 'ltx_description' in cls):
                self.items(ch, 1)
                continue
            if name == 'p' and 'ltx_p' in cls:
                self.text_block('p', ch)
                continue
            if 'ltx_listing' in cls:
                lines = [Inline().conv(ln).strip() for ln in ch.find_all(class_='ltx_listingline')]
                if lines:
                    self.add('alg', html='', lines=lines)
                continue
            if name in ('div', 'span', 'blockquote', 'article', 'section') or 'ltx_para' in cls:
                self.walk(ch)
                continue
            if name == 'pre':
                self.add('alg', html='', lines=ch.get_text().split('\n'))
                continue
            if name == 'table':
                self.add('tab', html='', table=self.table_html(ch), img=[])
                continue

    def items(self, lst, level):
        for li in lst.find_all('li', recursive=False):
            tag = li.find(class_='ltx_tag_item')
            mark = tag.get_text(strip=True) if tag else '•'
            if tag:
                tag.extract()
            first = True
            for ch in li.children:
                if not isinstance(ch, Tag):
                    continue
                for p in ([ch] if (ch.name == 'p') else ch.find_all(['p', 'ul', 'ol', 'table', 'figure'], recursive=True)):
                    if p.find_parent('li') is not li and p.name != 'p':
                        continue
                    if p.name in ('ul', 'ol'):
                        if p.find_parent('li') is li:
                            self.items(p, level + 1)
                        continue
                    if p.name == 'table' and 'ltx_equation' in (p.get('class') or []):
                        self.equation(p)
                        continue
                    if p.name == 'figure':
                        self.figure(p)
                        continue
                    if p.name == 'p' and p.find_parent('li') is li:
                        inl = Inline()
                        html = inl.conv(p).strip()
                        if html:
                            self.add('li', html=html, mark=mark if first else '', level=level)
                            first = False
                        for m, c in inl.footnotes:
                            if c:
                                self.add('fn', html=c, mark=m)

    def run(self):
        s = self.soup
        art = s.find('article', class_='ltx_document') or s.find(class_='ltx_document') or s.body
        title_el = art.find(class_='ltx_title_document')
        title = re.sub(r'\s+', ' ', title_el.get_text(' ', strip=True)) if title_el else ''
        au = art.find(class_='ltx_authors')
        authors = re.sub(r'\s+', ' ', au.get_text(' ', strip=True)) if au else ''
        abstract = []
        ab = art.find(class_='ltx_abstract')
        if ab:
            for p in ab.find_all('p', class_='ltx_p'):
                inl = Inline()
                h = inl.conv(p).strip()
                if h:
                    self.n += 1
                    abstract.append({'id': 'b%03d' % self.n, 'type': 'p', 'html': h})
        self.walk(art)
        return {'title': title, 'authors': authors[:600], 'abstract': abstract, 'blocks': self.blocks}


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    aid, key = args[0], args[1]
    saved = None
    if '--html' in args:
        saved = args[args.index('--html') + 1]
    work = os.path.join(ROOT, 'work', key)
    os.makedirs(work, exist_ok=True)
    if saved:
        html = open(saved, encoding='utf-8').read()
        base = 'https://arxiv.org/html/%s' % aid
    else:
        html, final = fetch('https://arxiv.org/html/%s' % aid)
        base = final.rstrip('/')   # 그림 src가 '2608.30468v1/x.png' 꼴이라 끝 슬래시 없이 이어 붙여요
    with open(os.path.join(work, 'raw.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    vs = re.findall(re.escape(aid) + r'v(\d+)', html)
    ver = '%sv%d' % (aid, max(int(v) for v in vs)) if vs else aid
    data = Extractor(key, base, html).run()
    data.update({'key': key, 'arxiv': aid, 'version': ver, 'url': 'https://arxiv.org/abs/%s' % aid,
                 'html_url': 'https://arxiv.org/html/%s' % ver, 'pdf_url': 'https://arxiv.org/pdf/%s' % ver})
    with open(os.path.join(work, 'src.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    # 번역용 목록
    lines = ['# %s (%s)' % (data['title'], ver), '']
    for b in data['abstract'] + data['blocks']:
        tag = b['type'] + (' appendix' if b.get('appendix') else '')
        if b['type'] == 'eq':
            lines.append('### %s [eq] (번역 안 함) %s' % (b['id'], b['latex'][:200]))
            continue
        body = b.get('html', '')
        if b['type'] == 'alg' and not body:
            lines.append('### %s [alg] (캡션 없음, 번역 안 함)' % b['id'])
            continue
        if b['type'] in ('fig', 'tab', 'alg'):
            tag += ' caption'
        lines.append('### %s [%s]' % (b['id'], tag))
        lines.append(body)
        lines.append('')
    with open(os.path.join(work, 'src.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    cnt = {}
    for b in data['blocks']:
        k = b['type'] + ('*' if b.get('appendix') else '')
        cnt[k] = cnt.get(k, 0) + 1
    words = sum(len(re.sub(r'<[^>]+>', ' ', b.get('html', '')).split()) for b in data['abstract'] + data['blocks'] if not b.get('appendix'))
    words_app = sum(len(re.sub(r'<[^>]+>', ' ', b.get('html', '')).split()) for b in data['blocks'] if b.get('appendix'))
    print(json.dumps({'key': key, 'version': ver, 'title': data['title'], 'blocks': cnt, 'main_words': words,
                      'appendix_words': words_app, 'figures': len(os.listdir(os.path.join(ROOT, 'assets', key)))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
