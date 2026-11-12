"""다른 덱의 장을 이 덱으로 옮기는 도구(같은 틀에서 나온 덱끼리): 도형·그림·전환·효과를 그대로 옮기고, 노트 글과 효과 길이를 읽는다."""
import copy
import io
import re

from lxml import etree

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
RNS = '{%s}' % NS['r']


def q(tag):
    ns, t = tag.split(':')
    return '{%s}%s' % (NS[ns], t)


def same_layout(prs, src_layout):
    """src_layout과 같은 마스터 차례·같은 이름의 장 틀(두 덱이 같은 틀에서 나왔을 때)."""
    src_prs_masters = [m.part for m in src_layout.part.package.presentation_part.presentation.slide_masters]
    mi = src_prs_masters.index(src_layout.slide_master.part)
    for lay in prs.slide_masters[mi].slide_layouts:
        if lay.name == src_layout.name:
            return lay
    raise KeyError(src_layout.name)


def note_text(slide):
    if not slide.has_notes_slide or slide.notes_slide.notes_text_frame is None:
        return ''
    return slide.notes_slide.notes_text_frame.text.strip()


def set_notes(slide, text, note_tpl):
    ns = slide.notes_slide
    if ns.notes_text_frame is None:
        for e in note_tpl:
            ns.shapes._spTree.append(copy.deepcopy(e))
    ns.notes_text_frame.text = text


def copy_slide(prs, src, note_tpl):
    """src 장을 prs 끝에 그대로 옮긴다(그림만 딸린 장). 돌려줌: 새 장."""
    new = prs.slides.add_slide(same_layout(prs, src.slide_layout))
    rid = {}
    for k, rel in src.part.rels.items():
        if rel.is_external:
            continue
        if rel.reltype.endswith('/image'):
            rid[k] = new.part.get_or_add_image_part(io.BytesIO(rel.target_part.blob))[1]
    el = copy.deepcopy(src._element)
    for e in el.iter():
        for k, v in list(e.attrib.items()):
            if k.startswith(RNS):
                assert v in rid, '옮기지 못하는 관계 %s=%s (%s)' % (k, v, src.part.partname)
                e.set(k, rid[v])
    dst = new._element
    for ch in list(dst):
        dst.remove(ch)
    for ch in list(el):
        dst.append(ch)
    for k, v in el.attrib.items():
        dst.set(k, v)
    if note_text(src):
        set_notes(new, note_text(src), note_tpl)
    return new


def groups(slide):
    """본 차례(mainSeq)의 효과 묶음: [(묶음 요소, 장이 열리면 저절로 시작하는가)]. 저절로 시작하지 않는 묶음은 클릭마다 하나씩 나온다."""
    main = slide._element.find('.//' + q('p:cTn') + '[@nodeType="mainSeq"]')
    kids = None if main is None else main.find(q('p:childTnLst'))
    out = []
    for grp in ([] if kids is None else kids):
        conds = grp.findall(q('p:cTn') + '/' + q('p:stCondLst') + '/' + q('p:cond'))
        out.append((grp, any(c.get('evt') == 'onBegin' for c in conds)))
    return out


def group_len(grp):
    """한 묶음의 효과가 모두 끝나는 때(ms, 묶음이 시작한 때부터). 끝없이 되풀이하는 효과는 세지 않는다."""
    end = 0
    for sub in grp.findall(q('p:cTn') + '/' + q('p:childTnLst') + '/' + q('p:par')):
        d0 = _delay(sub.find(q('p:cTn')))
        for eff in sub.findall(q('p:cTn') + '/' + q('p:childTnLst') + '/' + q('p:par') + '/' + q('p:cTn')):
            d1 = _delay(eff)
            inner = 0
            if eff.get('repeatCount') != 'indefinite':
                for c in eff.iter(q('p:cTn')):
                    if c is eff or not (c.get('dur') or '').isdigit():
                        continue
                    inner = max(inner, _delay(c) + int(c.get('dur')) * (2 if eff.get('autoRev') == '1' else 1))
            end = max(end, d0 + d1 + inner)
    return end


def anim_len(slide):
    """장이 열린 뒤 저절로 나오는 효과가 모두 끝나는 때(ms). 클릭으로 시작하는 묶음은 세지 않는다."""
    end = 0
    for grp, auto in groups(slide):
        if not auto:                                                    # 클릭 묶음
            break
        end = max(end, group_len(grp))
    return end


def click_lens(slide):
    """클릭 묶음마다 효과가 끝나는 때(ms). 클릭이 없는 장은 빈 목록."""
    return [group_len(g) for g, auto in groups(slide) if not auto]


def cap_repeats(slide, ms):
    """끝없이 되풀이하는 효과를 ms까지만 되풀이하게 바꾼다(녹화용 사본).
    PowerPoint는 영상으로 내보낼 때 그런 효과가 한 번 다 돌 때까지 그 장에 머물러서(11-13 시험: 10.4초짜리 효과가 있는 장이 4초 대신 11초),
    장에 머무는 시간보다 길게 돌지 않게 한다. 되풀이 수는 소수여도 된다(1000 = 한 번)."""
    for eff in slide._element.iter(q('p:cTn')):
        if eff.get('repeatCount') != 'indefinite' or not eff.get('presetID'):
            continue
        once = max([_delay(c) + int(c.get('dur')) for c in eff.iter(q('p:cTn')) if c is not eff and (c.get('dur') or '').isdigit()] or [0])
        once *= 2 if eff.get('autoRev') == '1' else 1
        if once:
            eff.set('repeatCount', str(max(int((ms - _delay(eff)) / once * 1000), 1)))


def _next_id(slide):
    return max([int(c.get('id')) for c in slide._element.iter(q('p:cTn')) if (c.get('id') or '').isdigit()] or [0]) + 1


def auto_play(slide, starts):
    """클릭 묶음을 저절로 나오게 바꾼다(녹화용 사본): 클릭 묶음 j는 장이 열린 뒤 starts[j] ms에 시작한다.
    클릭 묶음의 효과를 저절로 시작하는 첫 묶음 안으로 옮기고 그만큼 늦춘다(첫 묶음이 없으면 만든다)."""
    gs = groups(slide)
    clicks = [g for g, auto in gs if not auto]
    assert len(clicks) == len(starts), (len(clicks), len(starts))
    if not clicks:
        return
    first = next((g for g, auto in gs if auto), None)
    if first is None:
        main = slide._element.find('.//' + q('p:cTn') + '[@nodeType="mainSeq"]')
        first = etree.fromstring(
            '<p:par xmlns:p="%s"><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0">'
            '<p:tn val="%s"/></p:cond></p:stCondLst><p:childTnLst/></p:cTn></p:par>' % (NS['p'], _next_id(slide), main.get('id')))
        main.find(q('p:childTnLst')).insert(0, first)
    host = first.find(q('p:cTn')).find(q('p:childTnLst'))
    for g, at in zip(clicks, starts):
        for inner in list(g.find(q('p:cTn')).find(q('p:childTnLst'))):
            cond = inner.find(q('p:cTn')).find(q('p:stCondLst')).find(q('p:cond'))
            cond.set('delay', str(int(round(at)) + _delay(inner.find(q('p:cTn')))))
            for c in inner.iter(q('p:cTn')):
                if c.get('nodeType') == 'clickEffect':
                    c.set('nodeType', 'afterEffect')
            host.append(inner)
        g.getparent().remove(g)


def _delay(ctn):
    c = ctn.find(q('p:stCondLst') + '/' + q('p:cond'))
    d = c.get('delay') if c is not None else None
    return int(d) if d and d.lstrip('-').isdigit() else 0


def trans_ms(slide):
    """장 전환 길이(ms)."""
    m = re.search(r'p14:dur="(\d+)"', etree.tostring(slide._element, encoding='unicode'))
    if m:
        return int(m.group(1))
    t = slide._element.find('.//' + q('p:transition'))
    return {'slow': 1000, 'med': 750, 'fast': 500}.get(t.get('spd', 'fast'), 500) if t is not None else 0


def spoken(note):
    """노트에서 소리 내어 말할 글만: 괄호 속 무대 지시(겹친 괄호까지)와 줄바꿈을 뺀다."""
    t = note
    while re.search(r'\([^()]*\)', t):
        t = re.sub(r'\([^()]*\)', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def add_mark(slide, box, rgb, name='mk', at=None):
    """장 맨 위에 작은 네모(녹화에서 그 장이 시작한 때를 찾는 표)를 얹는다. box = (x, y, w, h) px(1280×720 기준).
    at(ms)을 주면 장이 열린 뒤 그때 나타난다(클릭 구간이 시작하는 때의 표. auto_play()로 클릭을 없앤 뒤에 부른다).
    옮겨 온 장은 python-pptx의 shapes가 옛 도형 나무를 붙들고 있어서, 지금 나무에 직접 넣는다."""
    tree = slide._element.find(q('p:cSld')).find(q('p:spTree'))
    ids = [int(e.get('id')) for e in tree.iter() if e.tag.endswith('}cNvPr') and (e.get('id') or '').isdigit()]
    x, y, w, h = [int(round(v * 9525)) for v in box]
    spid = max(ids) + 1
    xml = ('<p:sp xmlns:p="%s" xmlns:a="%s"><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
           '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
           '<a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr></p:sp>') % (
        NS['p'], NS['a'], spid, name, x, y, w, h, rgb)
    tree.append(etree.fromstring(xml))
    if at is None:
        return
    first = next(g for g, auto in groups(slide) if auto)
    n = _next_id(slide)
    eff = ('<p:par xmlns:p="%s"><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst><p:par>'
           '<p:cTn id="%d" presetID="1" presetClass="entr" presetSubtype="0" fill="hold" nodeType="afterEffect"><p:stCondLst><p:cond delay="0"/>'
           '</p:stCondLst><p:childTnLst><p:set><p:cBhvr><p:cTn id="%d" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
           '<p:tgtEl><p:spTgt spid="%d"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
           '<p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>') % (
        NS['p'], n, int(round(at)), n + 1, n + 2, spid)
    first.find(q('p:cTn')).find(q('p:childTnLst')).append(etree.fromstring(eff))
