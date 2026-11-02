"""시나리오 하나 → 장면(단계) 19장. 세 버전이 같은 흐름을 쓰고, 내용만 SPEC으로 바꾼다.

흐름: 상황 → 기록 더미 → 단어로 찾기 → (왜 안 되나) → 비슷한 것 찾기 → (왜 안 되나) → Weave 시작
      → 00 사전 준비 → 01 순간 감지 → 02 단서 정리 → 03 연쇄 탐색 ①②③ (새 단서는 메모로 돌아와 반복)
      → 멈춤 → 04 전달 → 입력 → 정리
"""
import story as S
from story import (BODY, GRAY_FILL, GRAY_HL, GRAY_LINE, HL, INK, INK2, LAV, LAV2, LINE, LINE2, MUTE, PURPLE, PURPLE2,
                   RING, SUB, C, P, R, T, band, card_prims, chip_prims, scurve, tw, vcurve)

VIEW = (60, 150, 1220, 632)          # 카메라가 비추는 화면 영역(머리 아래, 파이프라인 띠 위)


class Scene:
    def __init__(self, spec):
        self.spec = spec
        self.st = S.Story(spec['name'])
        self.pos = {}                 # 카드 키 → 글자 자리
        self.box = {}                 # 요소 키 → (x, y, w, h) 세계 좌표
        self.styled = {}              # 카드 키 → 모양별 원시 목록

    # -------------------------------------------------------------- 요소 등록
    def put(self, key, prims_or_fn):
        fn = prims_or_fn if callable(prims_or_fn) else (lambda style=None, p=prims_or_fn: p)
        self.st.item(key, fn)
        self.box[key] = bbox(fn(None))

    def card(self, key, c):
        def fn(style=None, c=c, key=key):
            prims, h, pos = card_prims(key, c['kind'], c['x'], c['y'], c['w'], c['title'], c.get('meta', ''),
                                       c.get('lines', ()), img=c.get('img'), icon=c.get('icon'), style=style or 'base')
            return prims
        _, h, pos = card_prims(key, c['kind'], c['x'], c['y'], c['w'], c['title'], c.get('meta', ''), c.get('lines', ()),
                               img=c.get('img'), icon=c.get('icon'))
        c['h'] = h
        self.pos[key] = pos
        self.put(key, fn)

    # -------------------------------------------------------------- 카메라
    def fit(self, keys, zmax=1.35, pad=26, dy=0):
        x0 = min(self.box[k][0] for k in keys)
        y0 = min(self.box[k][1] for k in keys)
        x1 = max(self.box[k][0] + self.box[k][2] for k in keys)
        y1 = max(self.box[k][1] + self.box[k][3] for k in keys)
        vw, vh = VIEW[2] - VIEW[0], VIEW[3] - VIEW[1]
        z = min(zmax, vw / (x1 - x0 + 2 * pad), vh / (y1 - y0 + 2 * pad))
        return ((x0 + x1) / 2, (y0 + y1) / 2 + dy, z)


def bbox(prims):
    xs, ys = [], []
    for p in prims:
        if p[0] in ('rect', 'text', 'pic'):
            x, y, w, h = p[-5:-1] if p[0] != 'pic' else p[3:7]
            if p[0] == 'text':
                x, y, w, h = p[2], p[3], p[4], p[5]
            elif p[0] == 'rect':
                x, y, w, h = p[2], p[3], p[4], p[5]
            xs += [x, x + w]
            ys += [y, y + h]
        elif p[0] == 'curve':
            xs += [pt[0] for pt in p[2]]
            ys += [pt[1] for pt in p[2]]
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


# ------------------------------------------------------------------ 고정 요소(머리, 파이프라인 띠)
def header_prims(title, sub):
    cw = tw('HOW IT WORKS', 11, 'sb') + 28 + 0.5 * 4 / 3 * 12
    out = [R('hdr/chip', 640 - cw / 2, 28, cw, 26, prst='roundRect', fill=PURPLE, line=None),
           T('hdr/chip_t', 640 - cw / 2, 28, cw, 26, 'HOW IT WORKS', size=11, color='FFFFFF', weight='sb', align='c',
             anchor='ctr', spc=0.5),
           T('hdr/title', 0, 64, 1280, 44, [[(t, {'color': c}) for t, c in title]], size=26, color=INK, weight='b',
             align='c', anchor='ctr', spc=-0.4)]
    if sub:
        out.append(T('hdr/sub', 0, 110, 1280, 26, sub, size=13, color='5B5866', align='c', anchor='ctr'))
    return out


STAGES = [('00', '사전 준비'), ('01', '순간 감지'), ('02', '단서 정리'), ('03', '연쇄 탐색'), ('04', '전달')]


def hud_layout():
    xs = []
    widths = [24 + 8 + tw(ko, 11, 'b') + 22 for _, ko in STAGES]
    gap = 30
    total = sum(widths) + gap * 4
    x = 640 - total / 2
    for w in widths:
        xs.append((x, w))
        x += w + gap
    return xs


def hud_prims(h):
    """h = dict(cur='02', done={'00','01'}, loop=1, loop_on=True) 또는 'all'(모두 끝남)."""
    y0, hh = 648, 44
    lay = hud_layout()
    x_first, x_last = lay[0][0], lay[-1][0] + lay[-1][1]
    out = [R('hud/bar', x_first - 14, y0, x_last - x_first + 28, hh, prst='roundRect', fill='FFFFFF', alpha=92, line=LINE,
             shadow=S.L.SHADOW_SOFT)]
    cur = h.get('cur')
    done = h.get('done', set())
    # 지금 단계 표시(단계 사이를 미끄러지듯 옮겨 감)
    if cur:
        i = [s for s, _ in STAGES].index(cur)
        x, w = lay[i]
        out.append(R('hud/hl', x - 4, y0 + 5, w + 8, hh - 10, prst='roundRect', fill=LAV, line=RING, line_w=1.6,
                     glow=(8, RING, 30)))
    for i, ((no, ko), (x, w)) in enumerate(zip(STAGES, lay)):
        state = 'cur' if no == cur else ('done' if no in done or h.get('all') else 'todo')
        bf, bt, lc, lw = {'cur': (PURPLE, 'FFFFFF', INK, 'b'), 'done': ('DCD3FF', PURPLE, PURPLE, 'b'),
                          'todo': ('F1EEF8', 'B9B3C8', 'B9B3C8', 'sb')}[state]
        cy = y0 + hh / 2
        out.append(R('hud/b%s' % no, x + 10, cy - 12, 24, 24, prst='ellipse', fill=bf, line=None))
        out.append(T('hud/bn%s' % no, x + 10, cy - 12, 24, 24, '✓' if state == 'done' else no, size=8.5, color=bt,
                     weight='b', align='c', anchor='ctr'))
        out.append(T('hud/l%s' % no, x + 42, y0, w - 40, hh, ko, size=11, color=lc, weight=lw, anchor='ctr'))
        if i < 4:
            out.append(T('hud/a%d' % i, x + w + 4, y0, 22, hh, '→', size=11, color='C9C0E8', align='c', anchor='ctr'))
    # 02 ⇄ 03 반복 고리
    if h.get('loop'):
        (x2, w2), (x3, w3) = lay[2], lay[3]
        a, b = (x3 + w3 / 2, y0 + 2), (x2 + w2 / 2, y0 + 2)
        on = h.get('loop_on')
        col = PURPLE if on else 'C9C0E8'
        out.append(C('hud/loop', [a, (a[0], y0 - 26), (b[0], y0 - 26), b], w=2.2 if on else 1.6, color=col))
        out.append(T('hud/loop_head', b[0] - 7, y0 - 9, 14, 12, '▼', size=7, color=col, align='c', anchor='ctr'))
        lab = '새 단서로 다시 찾기' if on else '반복'
        lw_ = tw(lab, 8.5, 'b') + 16
        out.append(R('hud/loop_bg', (a[0] + b[0]) / 2 - lw_ / 2, y0 - 33, lw_, 18, prst='roundRect', fill='FFFFFF', line=None))
        out.append(T('hud/loop_t', (a[0] + b[0]) / 2 - lw_ / 2, y0 - 33, lw_, 18, lab, size=8.5, color=col, weight='b',
                     align='c', anchor='ctr'))
        # 연쇄 탐색 횟수
        out.append(R('hud/cnt', x3 + w3 - 12, y0 - 6, 20, 20, prst='ellipse', fill=PURPLE, line='FFFFFF', line_w=1.5))
        out.append(T('hud/cnt_t', x3 + w3 - 12, y0 - 6, 20, 20, str(h['loop']), size=8.5, color='FFFFFF', weight='b',
                     align='c', anchor='ctr'))
    return out


# ------------------------------------------------------------------ 공통 요소 만들기
def memo_items(sc):
    sp = sc.spec['memo']
    mx, my, mw = sp.get('x', 60), sp.get('y', 300), 336
    LX, CX = mx + 16, mx + 104
    rows = {'find': my + 60, 'know': my + 94, 'where': my + 128, 'new1': my + 162, 'new2': my + 194, 'stop': my + 238}
    mh = 280
    base = [R('memo/bg', mx, my, mw, mh, prst='roundRect', radius=16, fill='FFFFFF', line=LINE2, line_w=1.2,
              shadow=S.L.SHADOW_CARD),
            R('memo/ic', mx + 18, my + 16, 13, 16, prst='roundRect', radius=2.5, fill=None, line=PURPLE, line_w=1.5),
            R('memo/ic1', mx + 21, my + 22, 7, 1.5, fill=PURPLE, line=None),
            R('memo/ic2', mx + 21, my + 26, 7, 1.5, fill=PURPLE, line=None),
            T('memo/title', mx + 40, my + 13, 200, 22, '탐색 메모', size=11.5, color=PURPLE, weight='b'),
            R('memo/div', mx + 16, my + 46, mw - 32, 1, fill='EEE9FA', line=None)]
    sc.put('memo', base)
    sc.memo = dict(x=mx, y=my, w=mw, h=mh, rows=rows, CX=CX)

    def row(key, label, chips, style, lab_color=SUB, lab_w='r'):
        out = [T(key + '/lab', LX, rows[key.split('.')[1]], 90, 24, label, size=10, color=lab_color, weight=lab_w, anchor='ctr')]
        x = CX
        for i, (c, ic) in enumerate(chips):
            pr, w = chip_prims('%s/c%d' % (key, i), x, rows[key.split('.')[1]], c, style=style, pt=9.5, h=24, padx=10,
                               icon=ic)
            out += pr
            x += w + 6
        return out

    sc.put('memo.find', row('memo.find', '찾을 것', [(sp['find'], None)], 'fill'))
    sc.put('memo.know', row('memo.know', '아는 단서', [(c, None) for c in sp['know']], 'outline'))
    sc.put('memo.where', row('memo.where', '먼저 볼 곳', [(c, ic) for c, ic in sp['where']], 'soft'))
    sc.put('memo.newlab', [T('memo.newlab/lab', LX, rows['new1'], 90, 24, '+ 새 단서', size=10, color=PURPLE, weight='b',
                             anchor='ctr')])
    for i, k in enumerate(('new1', 'new2')):
        pr, _ = chip_prims('memo.slot%d' % (i + 1), CX, rows[k], ' ' * 22, style='dash', pt=9.5, h=24)
        sc.put('memo.slot%d' % (i + 1), pr)
    sc.put('memo.stop', [T('memo.stop/lab', LX, rows['stop'], 90, 24, '멈출 때', size=10, color=SUB, anchor='ctr'),
                         T('memo.stop/t', CX, rows['stop'], 220, 24, sp['stop'], size=10, color=BODY, anchor='ctr')])
    fw = chip_prims('x', 0, 0, sp['find'], pt=9.5)[1]
    pr, _ = chip_prims('memo.ans', CX + fw + 6, rows['find'], sp['answer'] + ' ✓', style='outline', pt=9.5, h=24)
    sc.put('memo.ans', pr)
    pr, _ = chip_prims('memo.stopok', CX + tw(sp['stop'], 10) + 10, rows['stop'] + 2, '멈춤', style='fill', pt=8.5, h=20,
                       padx=8)
    sc.put('memo.stopok', pr)


def token(sc, key, label, at):
    pr, w = chip_prims(key, at[0], at[1], label, style='fill', pt=9.5, h=24, padx=10)
    return pr, w


def chat_items(sc):
    sp = sc.spec['chat']
    x, y, w, h = sp.get('x', 1820), sp.get('y', 150), 380, 500
    out = [R('chat/bg', x, y, w, h, prst='roundRect', radius=28, fill='FFFFFF', line=LINE, line_w=1.0, shadow=S.L.SHADOW_CARD),
           R('chat/av', x + 20, y + 18, 34, 34, prst='ellipse', fill='C9B8FF', line=None),
           T('chat/av_t', x + 20, y + 18, 34, 34, sp['name'][0], size=12, color='FFFFFF', weight='b', align='c', anchor='ctr'),
           T('chat/name', x + 64, y + 18, 200, 34, sp['name'], size=13, color=INK, weight='b', anchor='ctr'),
           P('chat/app', S.ICON[sp.get('app', 'talk')], x + w - 42, y + 24, 22, 22),
           R('chat/div', x + 16, y + 66, w - 32, 1, fill='EEE9FA', line=None)]
    by = y + 86
    for i, (msg, tm) in enumerate(sp['msgs']):
        bw = tw(msg, 11) + 24
        out.append(R('chat/m%d' % i, x + 20, by, bw, 34, prst='roundRect', radius=14, fill=GRAY_FILL, line=None))
        out.append(T('chat/m%d_t' % i, x + 32, by, bw, 34, msg, size=11, color=INK2, anchor='ctr'))
        out.append(T('chat/m%d_tm' % i, x + 24 + bw, by + 14, 60, 18, tm, size=8, color=MUTE, anchor='ctr'))
        by += 44
    sc.put('chat', out)
    sc.chat = dict(x=x, y=y, w=w, h=h)
    # 입력창 + 키보드 도구 막대
    iy = y + h - 116
    kb = [R('kbd/in', x + 16, iy, w - 32, 42, prst='roundRect', fill='FFFFFF', line=LINE2, line_w=1.0),
          T('kbd/ph', x + 34, iy, w - 70, 42, '메시지 입력', size=10.5, color='B9B3C8', anchor='ctr'),
          R('kbd/bar', x + 16, iy + 54, w - 32, 44, prst='roundRect', radius=12, fill='F6F4FB', line=None),
          R('kbd/sp_bg', x + 26, iy + 60, 32, 32, prst='roundRect', radius=9, fill='FFFFFF', line=LINE, line_w=0.8),
          P('kbd/sp', S.ICON['spool'], x + 31, iy + 65, 22, 22)]
    for j in range(4):
        kb.append(R('kbd/d%d' % j, x + 92 + j * 66, iy + 70, 12, 12, prst='roundRect', radius=3, fill='D9D4E6', line=None))
    sc.put('kbd', kb)
    sc.put('kbd.on', [R('kbd.on/bg', x + 26, iy + 60, 32, 32, prst='roundRect', radius=9, fill=PURPLE, line=None,
                        glow=(10, RING, 45)),
                      P('kbd.on/sp', S.ICON['spool_w'], x + 31, iy + 65, 22, 22)])
    sc.put('tap', [P('tap/h', 'touch-tap.png', x + 40, iy + 82, 30, 42)])
    sc.chat['iy'] = iy
    # 자동 완성 추천 카드
    ay = iy - 182
    a = sp['answer']
    ans = [R('ans/bg', x + 16, ay, w - 32, 168, prst='roundRect', radius=16, fill='FFFFFF', line=RING, line_w=1.8,
             shadow=S.L.SHADOW_LIFT, glow=(9, RING, 26)),
           P('ans/ic', S.ICON['spool'], x + 32, ay + 14, 18, 18),
           T('ans/lab', x + 56, ay + 12, 200, 22, '자동 완성 추천', size=9.5, color=PURPLE2, weight='b', anchor='ctr'),
           T('ans/main', x + 32, ay + 40, w - 64, 32, a['main'], size=17, color=INK, weight='b', anchor='ctr'),
           T('ans/src', x + 32, ay + 78, w - 64, 20, a['src'], size=9, color=SUB, anchor='ctr'),
           R('ans/btn', x + 32, ay + 114, w - 64, 38, prst='roundRect', fill=PURPLE, line=None),
           T('ans/btn_t', x + 32, ay + 114, w - 64, 38, '✓  입력하기', size=11, color='FFFFFF', weight='b', align='c',
             anchor='ctr')]
    sc.put('ans', ans)
    sc.put('tap2', [P('tap2/h', 'touch-tap.png', x + w / 2 + 40, ay + 132, 30, 42)])
    sc.put('kbd.fill', [R('kbd.fill/bg', x + 17, iy + 1, w - 34, 40, prst='roundRect', fill='FFFFFF', line=None),
                        T('kbd.fill/t', x + 34, iy, w - 70, 42, sp['reply'], size=10.5, color=INK, anchor='ctr')])


def search_items(sc):
    sp = sc.spec['search']
    x, y, w, h = sp.get('x', 520), sp.get('y', 24), sp.get('w', 640), 58

    def fn(style=None):
        mode = '단어로 찾기' if style != 'sim' else '비슷한 것 찾기'
        mw = tw(mode, 10, 'b') + 26
        return [R('search/bg', x, y, w, h, prst='roundRect', fill='FFFFFF', line=GRAY_LINE, line_w=1.2, shadow=S.L.SHADOW_CARD),
                R('search/mode', x + 12, y + 12, mw, 34, prst='roundRect', fill='EFECF4', line=None),
                T('search/mode_t', x + 12, y + 12, mw, 34, mode, size=10, color=SUB, weight='b', align='c', anchor='ctr'),
                T('search/q', x + mw + 28, y, w - mw - 80, h, sp['query'], size=15, color=INK, weight='m', anchor='ctr'),
                R('search/lens', x + w - 44, y + 19, 16, 16, prst='ellipse', fill=None, line=MUTE, line_w=2.2),
                R('search/lens2', x + w - 30, y + 34, 9, 2.4, fill=MUTE, line=None)]
    sc.put('search', fn)


# ------------------------------------------------------------------ 시나리오 → 단계
def link(a, b):
    """두 상자 a→b를 잇는 실 조절점. 아래면 세로 S, 옆이면 가로 S."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    if by >= ay + ah - 4:                        # b가 아래
        return vcurve((ax + aw / 2, ay + ah + 2), (bx + bw / 2, by - 2), 0.5)
    if by + bh <= ay + 4:                        # b가 위
        return vcurve((ax + aw / 2, ay - 2), (bx + bw / 2, by + bh + 2), 0.5)
    if bx >= ax + aw - 4:                        # b가 오른쪽
        return scurve((ax + aw + 2, ay + min(ah / 2, 40)), (bx - 2, by + min(bh / 2, 40)), 0.5)
    return scurve((ax - 2, ay + min(ah / 2, 40)), (bx + bw + 2, by + min(bh / 2, 40)), 0.5)


def build(spec):
    sc = Scene(spec)
    st = sc.st
    for k, c in spec['records'].items():
        sc.card(k, c)
    memo_items(sc)
    chat_items(sc)
    search_items(sc)
    recs = list(spec['records'])
    W = spec['text']
    ch = sc.chat
    nmsg = len(spec['chat']['msgs'])
    sc.box['@msgs'] = (ch['x'], ch['y'], ch['w'], 86 + 44 * nmsg + 6)
    sc.box['@kbd'] = (ch['x'], ch['y'] + 76, ch['w'], ch['h'] - 76)
    sc.box['@ans'] = (ch['x'], ch['iy'] - 196, ch['w'], ch['y'] + ch['h'] - (ch['iy'] - 196))

    def tag_at(key, label, style='gray', where='tr', pt=9, name=None):
        bx, by, bw, bh = sc.box[key]
        w = tw(label, pt, 'sb') + 20
        x = bx + bw - w - 8 if where in ('tr', 'br') else bx + 10
        y = by - 11 if where in ('tr', 'tl') else by + bh - 11
        pr, _ = chip_prims(name, x, y, label, style=style, pt=pt, h=22, padx=10, weight='sb')
        return pr

    # 단어로 찾기에 걸린 단어(회색 표시)
    hits = list(spec['word']['hits'])
    for k, marks in spec['word']['hits'].items():
        rects = [band(sc.pos[k][where], sub, kind='full') for where, sub in marks]
        sc.put('wm.' + k, [R('wm.%s/%d' % (k, i), *r, prst='roundRect', radius=3, fill=GRAY_HL, alpha=42, line=None)
                           for i, r in enumerate(rects)])
    miss = spec['word']['miss']
    sc.put('miss.word', tag_at(miss, spec['word']['miss_tag'], name='miss.word'))
    # 비슷한 것 찾기 순위
    ranks = spec['sim']['ranks']
    rk = []
    for i, k in enumerate(ranks):
        bx, by, bw, bh = sc.box[k]
        sc.put('rank%d' % (i + 1), [R('rank%d/c' % (i + 1), bx - 10, by - 10, 24, 24, prst='ellipse', fill='8E88A0',
                                      line='FFFFFF', line_w=1.6),
                                    T('rank%d/t' % (i + 1), bx - 10, by - 10, 24, 24, str(i + 1), size=9.5, color='FFFFFF',
                                      weight='b', align='c', anchor='ctr')])
        rk.append('rank%d' % (i + 1))
    ga, gb = spec['sim']['gap']
    pts = link(sc.box[ga], sc.box[gb])
    mid = ((pts[0][0] + pts[3][0]) / 2, (pts[0][1] + pts[3][1]) / 2)
    sc.put('gap', [C('gap/l', pts, w=2.2, color=GRAY_LINE, dash='dash'),
                   R('gap/q', mid[0] - 15, mid[1] - 15, 30, 30, prst='ellipse', fill='FFFFFF', line=GRAY_LINE, line_w=1.4),
                   T('gap/qt', mid[0] - 15, mid[1] - 15, 30, 30, '?', size=13, color=MUTE, weight='b', align='c', anchor='ctr')])
    sc.put('gap.a', tag_at(ga, spec['sim']['tag_a'], name='gap.a'))
    sc.put('gap.b', tag_at(gb, spec['sim']['tag_b'], name='gap.b'))
    # 사전 준비: 핵심 기록마다 '언제·무엇' 정리 태그
    pk = list(spec['prep']['tags'])
    for k in pk:
        bx, by, bw, bh = sc.box[k]
        x, y = bx + 8, by + bh + 8
        out = []
        for i, t in enumerate(spec['prep']['tags'][k]):
            pr, w = chip_prims('pt.%s/%d' % (k, i), x, y, t, style='soft', pt=8.5, h=21, padx=8, weight='sb')
            out += pr
            x += w + 5
        sc.put('pt.' + k, out)
    ptk = ['pt.' + k for k in pk]

    # 홉 요소
    mm = sc.memo
    memo_box = (mm['x'], mm['y'], mm['w'], mm['h'])
    prev = None                                   # 앞 홉에서 찾은 기록(실의 출발점)
    H = []
    for i, hop in enumerate(spec['hops']):
        n = i + 1
        h = dict(n=n, hop=hop)
        f = hop.get('filter')
        if f:
            keys = f['keep']
            x0 = min(sc.box[k][0] for k in keys) - 14
            y0 = min(sc.box[k][1] for k in keys) - 16
            x1 = max(sc.box[k][0] + sc.box[k][2] for k in keys) + 14
            y1 = max(sc.box[k][1] + sc.box[k][3] for k in keys) + 14
            lab = f['label']
            lw_ = tw(lab, 9.5, 'b') + 22
            sc.put('fb%d' % n, [R('fb%d/r' % n, x0, y0, x1 - x0, y1 - y0, prst='roundRect', radius=18, fill=LAV, alpha=30,
                                  line=PURPLE2, line_w=1.6, dash='dash'),
                                R('fb%d/lb' % n, x0 + 14, y0 - 13, lw_, 26, prst='roundRect', fill=PURPLE, line=None),
                                T('fb%d/lt' % n, x0 + 14, y0 - 13, lw_, 26, lab, size=9.5, color='FFFFFF', weight='b',
                                  align='c', anchor='ctr')])
            for k, lab2 in f.get('drop', {}).items():
                sc.put('drop%d.%s' % (n, k), tag_at(k, lab2, style='grayfill', name='drop%d.%s' % (n, k)))
            h['fbox'] = (x0, y0, x1 - x0, y1 - y0)
        d = hop.get('find')
        if d:
            k = d['target']
            if prev:
                tpts = link(sc.box[prev], sc.box[k])
            else:
                tb = sc.box[k]
                tpts = scurve((mm['x'] + mm['w'] + 2, mm['rows']['where'] + 12), (tb[0] - 2, tb[1] + min(tb[3] / 2, 40)), 0.55)
            sc.put('th%d' % n, S.thread_prims('th%d' % n, tpts))
            rects = [band(sc.pos[k][where], sub, kind='low') for where, sub in d.get('marks', [])]
            if rects:
                sc.put('hm%d' % n, [R('hm%d/%d' % (n, j), *r, prst='roundRect', radius=2.5, fill=HL, alpha=45, line=None)
                                    for j, r in enumerate(rects)])
            for ck, lab2 in d.get('cands', {}).items():
                sc.put('why%d.%s' % (n, ck), tag_at(ck, lab2, style='grayfill', name='why%d.%s' % (n, ck)))
            if d.get('ok'):
                on_title = hop.get('tok_on') == 'mark' and d.get('marks') and d['marks'][0][0] == 'title'
                sc.put('ok%d' % n, tag_at(k, d['ok'], style='fill', where='tr' if on_title else 'tl', name='ok%d' % n))
            h['target'] = k
            prev = k
        # 질문 칩: 찾은 기록(또는 거르는 상자) 위 왼쪽
        qb = sc.box[h['target']] if d else h['fbox']
        qw = tw(hop['q'], 10.5, 'b') + 26
        qx, qy = hop.get('q_at', (qb[0] + qb[2] - qw + 6, qb[1] - 52) if d else (qb[0] + qb[2] - qw, qb[1] - 50))
        sc.put('q%d' % n, [R('q%d/bg' % n, qx, qy, qw, 30, prst='roundRect', fill='FFFFFF', line=PURPLE2, line_w=1.4,
                             shadow=S.L.SHADOW_SOFT),
                           T('q%d/t' % n, qx, qy, qw, 30, hop['q'], size=10.5, color=PURPLE, weight='b', align='c',
                             anchor='ctr')])
        # 토큰(새 단서): 찾은 기록 아래 오른쪽에 나타났다가 메모 칸으로
        lab = hop.get('token') if n < 3 else spec['memo']['answer']
        tkw = chip_prims('x', 0, 0, lab, pt=9.5)[1]
        ab = sc.box[h['target']] if d else h['fbox']
        at = hop.get('tok_at', (ab[0] + ab[2] - tkw - 6, ab[1] + ab[3] + (8 if d else 22)))
        on = hop.get('tok_on')
        if on == 'mark' and d and d.get('marks'):
            where, sub = d['marks'][0]
            mx_, my_, mw_, mh_ = band(sc.pos[h['target']][where], sub, kind='full')
            at = (mx_ - 8, my_ - 3)
        elif on == 'meta' and d:
            px_, py_, t_, pt_, wt_ = sc.pos[h['target']]['meta']
            at = (px_ + tw(t_, pt_) - tkw + 8, py_ - 4)
        pr, _ = chip_prims('tok%d' % n, at[0], at[1], lab, style='fill', pt=9.5, h=24, padx=10)
        sc.put('tok%d@src' % n, pr)
        if n < 3:
            dst = (mm['CX'], mm['rows']['new%d' % n])
        else:
            dst = (mm['CX'] + chip_prims('x', 0, 0, spec['memo']['find'], pt=9.5)[1] + 6, mm['rows']['find'])
        pr, _ = chip_prims('tok%d' % n, dst[0], dst[1], lab, style='fill', pt=9.5, h=24, padx=10)
        sc.put('tok%d@memo' % n, pr)
        H.append(h)
    ans_key = prev
    A_ = sc.box[ans_key]
    sc.put('th4', S.thread_prims('th4', scurve((A_[0] + A_[2] + 2, A_[1] + min(A_[3] / 2, 40)),
                                               (ch['x'] + 14, ch['iy'] - 182 + 60), 0.5)))

    # -------------------------------------------------------------- 단계
    cur = []

    def show(*ks):
        for k in ks:
            if k not in cur:
                cur.append(k)

    def hide(*ks):
        for k in ks:
            if k in cur:
                cur.remove(k)

    styles = {}

    def step(**kw):
        kw.setdefault('styles', dict(styles))
        st.step(show=list(cur), **kw)

    cloud = sc.fit(recs, zmax=0.9)
    # 1 상황
    show('chat', 'kbd')
    step(title=W['q'], sub=W['q_sub'], cam=sc.fit(['@msgs'], zmax=1.5), focus={'chat', 'kbd'}, notes=W['n_open'])
    # 2 기록 더미
    show(*recs)
    step(title=[('답은 분명 폰 어딘가에 있어요', INK)], sub=W['cloud_sub'], cam=cloud, notes=W['n_cloud'])
    # 3 단어로 찾기
    show('search', *['wm.' + k for k in hits])
    styles.update({k: 'gray' for k in hits})
    step(title=[('단어로 찾으면?', INK)], sub=W['word_sub'], cam=sc.fit(['search'] + hits, zmax=1.2),
         focus=set(['search'] + hits + ['wm.' + k for k in hits]), notes=W['n_word'],
         anim={'wm.' + k: dict(kind='zoom_in', delay=250 + 150 * j, dur=300) for j, k in enumerate(hits)})
    # 4 단어로는 못 찾는 이유
    show('miss.word')
    styles[miss] = 'gray'
    step(title=W['word_miss'], sub=W['word_miss_sub'], cam=sc.fit([miss, 'miss.word'], zmax=1.5, pad=60),
         focus={miss, 'miss.word'}, notes=W['n_word_miss'], anim={'miss.word': dict(kind='zoom_in', delay=0, dur=350)})
    # 5 비슷한 것 찾기
    hide('miss.word', *['wm.' + k for k in hits])
    for k in hits + [miss]:
        styles.pop(k, None)
    styles.update({k: 'gray' for k in ranks})
    styles['search'] = 'sim'
    show(*rk)
    step(title=[('비슷한 것을 찾으면?', INK)], sub=W['sim_sub'], cam=sc.fit(['search'] + ranks, zmax=1.15),
         focus=set(['search'] + ranks + rk), notes=W['n_sim'],
         anim={k: dict(kind='zoom_in', delay=250 + 180 * j, dur=280) for j, k in enumerate(rk)})
    # 6 비슷한 것 찾기로는 못 이어지는 이유
    hide(*rk)
    for k in ranks:
        styles.pop(k, None)
    styles.update({ga: 'gray', gb: 'gray'})
    show('gap', 'gap.a', 'gap.b')
    step(title=W['sim_gap'], sub=W['sim_gap_sub'], cam=sc.fit([ga, gb, 'gap.a', 'gap.b'], zmax=1.35, pad=40),
         focus={ga, gb, 'gap', 'gap.a', 'gap.b'}, notes=W['n_sim_gap'],
         anim={'gap': dict(kind='wipe_in', dir='down' if sc.box[gb][1] > sc.box[ga][1] + sc.box[ga][3] else 'left', delay=0, dur=600),
               'gap.a': dict(kind='zoom_in', delay=500, dur=300), 'gap.b': dict(kind='zoom_in', delay=700, dur=300)})
    # 7 Weave 시작
    hide('search', 'gap', 'gap.a', 'gap.b')
    styles.clear()
    step(title=[('Weave', PURPLE), ('는 찾은 기록에서 ', INK), ('다음 단서', PURPLE), ('를 이어요', INK)],
         sub='다섯 단계로 천천히 따라가 볼게요', cam=sc.fit(recs + ['chat'], zmax=0.8), hud=dict(), notes=W['n_intro'])
    # 8 00 사전 준비
    show(*ptk)
    step(title=W['prep'], sub=W['prep_sub'], cam=sc.fit(pk + ptk, zmax=1.3, pad=30), focus=set(pk + ptk),
         hud=dict(cur='00'), notes=W['n_prep'], anim={k: dict(kind='zoom_in', delay=200 + 220 * j, dur=320) for j, k in enumerate(ptk)})
    # 9 01 순간 감지
    show('kbd.on', 'tap')
    step(title=W['trig'], sub=W['trig_sub'], cam=sc.fit(['chat'], zmax=1.0, pad=14), focus={'chat', 'kbd', 'kbd.on', 'tap'},
         hud=dict(cur='01', done={'00'}), notes=W['n_trig'],
         anim={'kbd.on': dict(kind='zoom_in', delay=0, dur=350), 'tap': dict(kind='fade_in', delay=0, dur=300)})
    hide('tap')
    # 10 02 단서 정리
    memo_rows = ['memo', 'memo.find', 'memo.know', 'memo.where', 'memo.newlab', 'memo.slot1', 'memo.slot2', 'memo.stop']
    show(*memo_rows)
    step(title=[('무엇을, 어디부터', PURPLE), (' 찾을지 먼저 정해요', INK)], sub='탐색 메모에 찾을 것과 아는 단서를 나눠 적어요',
         cam=sc.fit(['memo'], zmax=1.5), focus=set(memo_rows), hud=dict(cur='02', done={'00', '01'}), notes=W['n_memo'])
    done01 = {'00', '01'}
    landed = []
    for h in H:
        n, hop = h['n'], h['hop']
        f, d = hop.get('filter'), hop.get('find')
        hud3 = dict(cur='03', done=done01, loop=n)
        if f:
            drops = ['drop%d.%s' % (n, k) for k in f.get('drop', {})]
            show('fb%d' % n, 'q%d' % n, *drops)
            tokf = [] if d else ['tok%d@src' % n]
            show(*tokf)
            focus = set(f['keep'] + ['fb%d' % n, 'q%d' % n] + drops + list(f.get('drop', {})) + tokf)
            step(title=f['title'], sub=f['sub'], cam=sc.fit(f['keep'] + list(f.get('drop', {})) + ['fb%d' % n, 'q%d' % n], zmax=1.25),
                 focus=focus, hud=hud3, notes=f['note'],
                 anim=dict({'fb%d' % n: dict(kind='fade_in', delay=0, dur=450), 'q%d' % n: dict(kind='zoom_in', delay=150, dur=300)},
                           **{x: dict(kind='zoom_in', delay=600 + 150 * j, dur=300) for j, x in enumerate(drops)},
                           **{x: dict(kind='zoom_in', delay=1200, dur=300) for x in tokf}))
            hide(*drops)
        if d:
            k = d['target']
            cands = list(d.get('cands', {}))
            whys = ['why%d.%s' % (n, c) for c in cands]
            extra = [x for x in ('hm%d' % n, 'ok%d' % n) if x in sc.box]
            show('th%d' % n, 'q%d' % n, *whys, *extra, 'tok%d@src' % n)
            styles[k] = 'weave'
            src = [p for p in [H[n - 2].get('target') if n > 1 else None] if p]
            fitk = [k, 'q%d' % n, 'tok%d@src' % n] + cands + (src if d.get('fit_prev', True) else []) + \
                (['fb%d' % n] if f else [])
            focus = set([k, 'th%d' % n, 'q%d' % n, 'tok%d@src' % n] + cands + whys + extra + src + (['fb%d' % n] if f else []) +
                        (memo_rows + landed if n == 1 else []))
            step(title=d['title'], sub=d['sub'], cam=sc.fit(fitk if n > 1 else ['memo', k, 'q%d' % n], zmax=1.25),
                 focus=focus, hud=hud3, notes=d['note'],
                 anim=dict({'th%d' % n: dict(kind='wipe_in', dir='down' if 'th' and src and sc.box[k][1] > sc.box[src[0]][1] + sc.box[src[0]][3] - 4 else 'left',
                                             delay=0, dur=600),
                            'q%d' % n: dict(kind='zoom_in', delay=250, dur=300),
                            'hm%d' % n: dict(kind='wipe_in', dir='left', delay=750, dur=450),
                            'ok%d' % n: dict(kind='zoom_in', delay=1100, dur=300),
                            'tok%d@src' % n: dict(kind='zoom_in', delay=1450, dur=300)},
                           **{x: dict(kind='zoom_in', delay=600 + 130 * j, dur=280) for j, x in enumerate(whys)}))
            hide(*whys)
        hide('q%d' % n, 'fb%d' % n, 'ok%d' % n)
        if n < 3:
            # 루프: 새 단서가 메모로 돌아감
            hide('tok%d@src' % n, 'memo.slot%d' % n)
            show('tok%d@memo' % n)
            landed.append('tok%d@memo' % n)
            anchor = [h['target']] if d else []
            step(title=hop['loop_title'], sub=hop['loop_sub'], cam=sc.fit(['memo'] + anchor, zmax=1.15),
                 focus=set(memo_rows + landed + anchor), hud=dict(cur='02', done=done01, loop=n, loop_on=True),
                 notes=hop['loop_note'])
    # 멈춤
    hide('tok3@src')
    show('tok3@memo', 'memo.stopok')
    step(title=[('찾을 것이 채워지면, ', INK), ('거기서 멈춰요', PURPLE)], sub=W['stop_sub'], cam=sc.fit(['memo'], zmax=1.5),
         focus=set(memo_rows + landed + ['tok3@memo', 'memo.stopok']), hud=dict(cur='03', done=done01, loop=3),
         notes=W['n_stop'], anim={'memo.stopok': dict(kind='zoom_in', delay=500, dur=300)})
    # 04 전달
    show('th4', 'ans')
    step(title=W['deliver'], sub=W['deliver_sub'], cam=sc.fit(['@ans'], zmax=1.3), focus={'chat', 'kbd', 'ans', 'th4'},
         hud=dict(cur='04', done={'00', '01', '02', '03'}), notes=W['n_deliver'],
         anim={'th4': dict(kind='wipe_in', dir='left', delay=0, dur=500), 'ans': dict(kind='rise', delay=250, dur=550)})
    # 입력하기
    show('tap2', 'kbd.fill')
    step(title=W['input'], sub=W['input_sub'], cam=sc.fit(['@ans'], zmax=1.3), focus={'chat', 'kbd', 'ans', 'tap2', 'kbd.fill'},
         hud=dict(cur='04', done={'00', '01', '02', '03'}), notes=W['n_input'],
         anim={'tap2': dict(kind='fade_in', delay=0, dur=250), 'kbd.fill': dict(kind='wipe_in', dir='left', delay=450, dur=500)})
    hide('tap2')
    # 정리
    targets = [h['target'] for h in H if 'target' in h]
    chain = memo_rows + landed + ['tok3@memo', 'memo.stopok', 'chat', 'kbd', 'ans', 'kbd.fill', 'th4'] + targets + \
        ['th%d' % h['n'] for h in H if 'target' in h] + ['hm%d' % h['n'] for h in H if 'hm%d' % h['n'] in sc.box]
    step(title=[('찾은 기록이 ', INK), ('다음 단서', PURPLE), ('가 되어, 답까지 이어져요', INK)],
         sub='핵심 엔진은 지금 단서로부터 ‘이어지는’ 기록을 찾는 온디바이스 Reasoning Embedding이에요',
         cam=sc.fit(['memo', 'chat'] + targets, zmax=0.85), focus=set(chain), hud=dict(all=True), notes=W['n_sum'])
    return sc
