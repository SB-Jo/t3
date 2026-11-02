#!/usr/bin/env python3
"""assets/*/*.svg 되살리기 — 인라인 <svg> 그림이 빈 칸으로 나오는 문제를 고쳐요.

원인: 추출기(extract_arxiv.py)는 arXiv HTML을 HTML 파서(lxml)로 읽어서, 인라인 <svg>를 저장할 때
태그·속성 이름이 모두 소문자가 돼요(foreignobject, viewbox, lineargradient, clippath …).
.svg 파일은 브라우저가 XML로 읽기 때문에 대소문자가 다르면 다른 요소가 되고, 그림이 비어 보여요.

하는 일(이미 고친 파일은 그대로 두므로 여러 번 돌려도 같아요)
  1. SVG 요소·속성 이름을 원래 camelCase로 되돌려요(HTML 명세의 'adjust SVG tag/attribute names' 표 그대로).
  2. foreignObject 안의 HTML에는 XHTML 네임스페이스, <math>에는 MathML 네임스페이스를 붙여요.
     (HTML 문서 안에서는 파서가 알아서 붙이지만, 따로 떼어 낸 .svg 파일에서는 없으면 글자가 안 보여요.)
  3. foreignObject가 있는 그림에는 arXiv(LaTeXML) CSS 중 글 상자에 필요한 최소 규칙을 <style>로 넣어요
     (문단 줄바꿈, 굵게·고정폭 글꼴, --ltx-fg-color 글자색 — 없으면 어두운 제목 띠 위 흰 글씨가 검게 나와요).
     그림 안에서는 웹 글꼴을 못 읽어 기기 글꼴을 쓰므로, 글자 폭을 Times(LaTeX 조판 기준)에 맞추는
     font-size-adjust를 넣어 넓은 대체 글꼴(DejaVu Serif 등)에서도 줄 수가 크게 늘지 않게 했어요.
     글 크기는 foreignObject의 --wv-fit 값(기본 1)을 곱해요. LaTeX가 잡은 상자보다 글이 길어 잘리는 그림은
     tools/fit_svg_text.cjs가 브라우저로 재서 이 값을 넣어 줘요(arXiv 원문 페이지도 같은 그림에서 글이 상자 밖으로 넘쳐요).
  4. xlink:* 속성이 있는데 xmlns:xlink 선언이 없으면 루트에 붙여요.
  고친 뒤 XML로 다시 읽어서, 소문자 이름이 남았는지·네임스페이스가 맞는지 확인해요.

사용: python tools/fix_svg_case.py [--dry-run] [파일 …]   (파일을 안 주면 assets/*/*.svg 전체)
추출기는 다른 작업자도 쓰므로 고치지 않았어요. 그림을 다시 뽑으면 이 스크립트 → tools/fit_svg_text.cjs 순서로 다시 돌리면 돼요.
"""
import glob
import os
import re
import sys
from collections import Counter

from lxml import etree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS_SVG = 'http://www.w3.org/2000/svg'
NS_XHTML = 'http://www.w3.org/1999/xhtml'
NS_MATH = 'http://www.w3.org/1998/Math/MathML'
NS_XLINK = 'http://www.w3.org/1999/xlink'

# HTML Living Standard §13.2.6.5 — 'adjust SVG tag name' 표
SVG_TAGS = {t.lower(): t for t in (
    'altGlyph altGlyphDef altGlyphItem animateColor animateMotion animateTransform clipPath '
    'feBlend feColorMatrix feComponentTransfer feComposite feConvolveMatrix feDiffuseLighting '
    'feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR '
    'feGaussianBlur feImage feMerge feMergeNode feMorphology feOffset fePointLight '
    'feSpecularLighting feSpotLight feTile feTurbulence foreignObject glyphRef '
    'linearGradient radialGradient textPath').split()}
# 'adjust SVG attributes' 표
SVG_ATTRS = {a.lower(): a for a in (
    'attributeName attributeType baseFrequency baseProfile calcMode clipPathUnits diffuseConstant '
    'edgeMode filterUnits glyphRef gradientTransform gradientUnits kernelMatrix kernelUnitLength '
    'keyPoints keySplines keyTimes lengthAdjust limitingConeAngle markerHeight markerUnits markerWidth '
    'maskContentUnits maskUnits numOctaves pathLength patternContentUnits patternTransform patternUnits '
    'pointsAtX pointsAtY pointsAtZ preserveAlpha preserveAspectRatio primitiveUnits refX refY '
    'repeatCount repeatDur requiredExtensions requiredFeatures specularConstant specularExponent '
    'spreadMethod startOffset stdDeviation stitchTiles surfaceScale systemLanguage tableValues '
    'targetX targetY textLength viewBox viewTarget xChannelSelector yChannelSelector zoomAndPan').split()}
# 'adjust MathML attributes' 표
MATH_ATTRS = {'definitionurl': 'definitionURL'}

# arXiv ar5iv CSS(LaTeXML)에서 foreignObject 글 상자에 필요한 규칙만 옮겨 왔어요.
STYLE_ID = 'wv-ltx-fo'
LTX_CSS = '''
foreignObject{overflow:visible}
.ltx_foreignobject_container{display:flex;align-items:flex-end;width:100%;height:100%}
.ltx_foreignobject_container:has(>.ltx_foreignobject_content>.ltx_minipage){align-items:flex-start}
.ltx_foreignobject_content{display:block;color:#000;font-family:'Times New Roman',Times,'Liberation Serif','Nimbus Roman',Tinos,'DejaVu Serif',serif;font-size:calc(1em * var(--wv-fit, 1));line-height:1.2;text-align:left;overflow-wrap:break-word}
.ltx_foreignobject_content *{line-height:1.2}
[style*='--ltx-fg-color:']{color:var(--ltx-fg-color)}
[style*='--ltx-bg-color:']{background-color:var(--ltx-bg-color)}
.ltx_p,.ltx_para,.ltx_block,.ltx_logical-block{display:block;margin:0}
span.ltx_p:not(:last-child){margin-bottom:.3em}
.ltx_inline-logical-block,.ltx_inline-logical-block .ltx_para{display:inline}
.ltx_inline-block,.ltx_inline-block .ltx_para{display:inline-block}
.ltx_parbox{display:inline-block}
.ltx_minipage{display:inline-block;max-width:100%}
.ltx_align_bottom{vertical-align:bottom}
.ltx_font_bold{font-weight:700}
.ltx_font_medium{font-weight:400}
.ltx_font_italic,.ltx_emph{font-style:italic}
.ltx_font_smallcaps{font-variant:small-caps}
.ltx_align_center{text-align:center}
.ltx_align_top{vertical-align:top}
.ltx_font_typewriter{font-family:'Noto Sans Mono','DejaVu Sans Mono',Menlo,Consolas,monospace}
.ltx_text.ltx_font_typewriter{font-size:.875em}
.ltx_verbatim{text-align:left}
span.ltx_p:empty,span.ltx_p:has(>.ltx_text.ltx_font_typewriter.ltx_inline-block:first-child){margin-bottom:0}
span.ltx_p:has(>.ltx_text.ltx_font_typewriter.ltx_inline-block:first-child):not(:has(.ltx_parbox)){white-space:pre}
.ltx_font_typewriter .ltx_parbox .ltx_para,.ltx_font_typewriter .ltx_parbox .ltx_p{text-align:left;margin-bottom:0;font-family:inherit}
.ltx_font_typewriter .ltx_parbox .ltx_p{white-space:pre-wrap}
.ltx_font_typewriter .ltx_parbox .ltx_para,span.ltx_p:has(.ltx_parbox),.ltx_parbox,.ltx_parbox .ltx_para{white-space:normal}
.ltx_text:has(>.ltx_parbox){white-space:normal;align-items:baseline;display:flex}
.ltx_itemize,.ltx_enumerate,.ltx_description{display:block;margin:.2em 0 0 .2em}
.ltx_item{display:block;padding-left:1.2em;text-indent:-1.2em}
.ltx_item+.ltx_item{margin-top:.2em}
.ltx_item .ltx_para,.ltx_item .ltx_p{display:inline;text-indent:0}
.ltx_tag_item{display:inline-block;min-width:1.2em;text-indent:0}
.ltx_rule{vertical-align:middle;background-color:#000}
.ltx_minipage>.ltx_rule{display:block!important;margin:.2em 0}
@supports (font-size-adjust:ch-width 0.5){.ltx_foreignobject_content{font-size-adjust:ch-width .5}.ltx_text.ltx_font_typewriter{font-size-adjust:ch-width .525;font-size:1em}}
'''.strip()

TOKEN = re.compile(
    r'<(?:!--.*?-->|!\[CDATA\[.*?\]\]>|![^>]*>|\?.*?\?>|'
    r'(/?)([A-Za-z][\w:.-]*)((?:\s+[^\s=/>]+(?:\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s"\'>]+))?)*)\s*(/?)>)',
    re.S)
ATTR = re.compile(r'(\s+)([^\s=/>]+)(\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s"\'>]+))?')


def fix_attrs(attrs, table, cnt):
    def rep(m):
        name = m.group(2)
        new = table.get(name, name)
        if new != name:
            cnt['attr ' + name + '→' + new] += 1
        return m.group(1) + new + (m.group(3) or '')
    return ATTR.sub(rep, attrs)


def fix_text(s):
    """문자열 하나를 고쳐서 (새 문자열, 바꾼 내용 Counter)를 돌려줘요."""
    cnt = Counter()
    out = []
    pos = 0
    stack = []          # (소문자 태그 이름, 네임스페이스)
    root_done = False
    for m in TOKEN.finditer(s):
        out.append(s[pos:m.start()])
        pos = m.end()
        tok = m.group(0)
        if m.group(2) is None:          # 주석·CDATA·선언
            out.append(tok)
            continue
        closing, name, attrs, selfclose = m.group(1), m.group(2), m.group(3) or '', m.group(4)
        lname = name.lower()
        if closing:
            ns = None
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == lname:
                    ns = stack[i][1]
                    del stack[i:]
                    break
            new = SVG_TAGS.get(name, name) if ns == NS_SVG else name
            out.append(tok if new == name else tok.replace(name, new, 1))
            continue
        pname, pns = stack[-1] if stack else (None, None)
        if lname == 'svg':
            ns = NS_SVG
        elif lname == 'math':
            ns = NS_MATH
        elif pns == NS_SVG and pname == 'foreignobject':
            ns = NS_XHTML
        else:
            ns = pns or NS_SVG
        new = name
        if ns == NS_SVG:
            new = SVG_TAGS.get(name, name)
            if new != name:
                cnt['tag ' + name + '→' + new] += 1
            attrs2 = fix_attrs(attrs, SVG_ATTRS, cnt)
        elif ns == NS_MATH:
            attrs2 = fix_attrs(attrs, MATH_ATTRS, cnt)
        else:
            attrs2 = attrs
        if ns != pns and not re.search(r'\sxmlns\s*=', attrs2):
            attrs2 += ' xmlns="%s"' % ns
            cnt['xmlns ' + {NS_SVG: 'svg', NS_XHTML: 'xhtml', NS_MATH: 'mathml'}[ns] + ' 추가'] += 1
        if not root_done:
            root_done = True
            if re.search(r'\sxlink:[\w.-]+\s*=', s) and 'xmlns:xlink' not in attrs2:
                attrs2 += ' xmlns:xlink="%s"' % NS_XLINK
                cnt['xmlns:xlink 추가'] += 1
        if new == name and attrs2 == attrs:
            out.append(tok)
        else:
            out.append('<' + new + attrs2 + ('/' if selfclose else '') + '>')
        if not selfclose:
            stack.append((lname, ns))
    out.append(s[pos:])
    s2 = ''.join(out)
    style = '<style id="%s"><![CDATA[\n%s\n]]></style>' % (STYLE_ID, LTX_CSS)
    old = re.search(r'<style id="%s">.*?</style>' % STYLE_ID, s2, re.S)
    if old:
        if old.group(0) != style:          # CSS를 고쳤으면 새 것으로 바꿔요
            s2 = s2[:old.start()] + style + s2[old.end():]
            cnt['<style> 갱신'] += 1
    elif '<foreignObject' in s2 and 'ltx_foreignobject' in s2:
        m = re.search(r'<svg\b[^>]*>', s2)
        if m:
            s2 = s2[:m.end()] + style + s2[m.end():]
            cnt['<style> 추가'] += 1
    return s2, cnt


def check(s):
    """XML로 읽어 남은 문제를 목록으로 돌려줘요(없으면 빈 목록)."""
    try:
        root = etree.fromstring(s.encode('utf-8'))
    except etree.XMLSyntaxError as e:
        return ['XML 오류: %s' % e]
    bad = []
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        q = etree.QName(el)
        if q.namespace == NS_SVG:
            if q.localname in SVG_TAGS:
                bad.append('소문자 요소 ' + q.localname)
            for a in el.attrib:
                if a in SVG_ATTRS:
                    bad.append('소문자 속성 ' + a)
            if q.localname == 'foreignObject':
                for ch in el:
                    if isinstance(ch.tag, str) and etree.QName(ch).namespace == NS_SVG and etree.QName(ch).localname != 'svg':
                        bad.append('foreignObject 안 SVG 네임스페이스 요소 ' + etree.QName(ch).localname)
        if q.localname == 'math' and q.namespace != NS_MATH:
            bad.append('MathML 네임스페이스 없는 math')
    return sorted(set(bad))


def main():
    args = [a for a in sys.argv[1:] if a != '--dry-run']
    dry = '--dry-run' in sys.argv[1:]
    files = args or sorted(glob.glob(os.path.join(ROOT, 'assets', '*', '*.svg')))
    changed, total = [], Counter()
    problems = 0
    for fn in files:
        with open(fn, encoding='utf-8') as f:
            s = f.read()
        s2, cnt = fix_text(s)
        rel = os.path.relpath(fn, ROOT)
        bad = check(s2)
        if bad:
            problems += 1
            print('! %s: %s' % (rel, '; '.join(bad)))
        if s2 != s:
            changed.append(rel)
            total.update(cnt)
            print('%s %s  (%s)' % ('바꿀 것' if dry else '고침', rel, ', '.join('%s ×%d' % kv for kv in sorted(cnt.items()))))
            if not dry:
                with open(fn, 'w', encoding='utf-8') as f:
                    f.write(s2)
    print('---')
    print('검사한 SVG %d개, %s %d개, 남은 문제 있는 파일 %d개' % (len(files), '바꿀 파일' if dry else '고친 파일', len(changed), problems))
    for k, v in sorted(total.items()):
        print('  %-40s %d' % (k, v))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
