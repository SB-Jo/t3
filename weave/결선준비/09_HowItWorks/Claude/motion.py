"""클릭 애니메이션(p:timing) — 모션그래픽 영상처럼 움직이게 하는 효과 모음.

효과 dict: kind, spid, delay(ms), dur(ms), 그 밖의 값. 한 묶음(장이 열릴 때, 또는 클릭 한 번)의 효과는
첫 효과만 클릭(또는 장이 열리자마자)으로 시작하고 나머지는 '함께 + 지연'으로 넣는다.

움직임 원칙(모션그래픽 v17과 같은 값):
- 나타날 때는 빨리 출발해 천천히 멈춤(decel 100%), 12~16px 떠오름, 0.35~0.5초.
- 강조로 튀어나올 때는 살짝 넘쳤다가 제자리(0.6 → 1.05 → 1).
- 옮겨 가는 토큰은 곡선을 따라 가속·감속(accel 45%, decel 55%), 0.9~1.1초.
- 흐려질 때는 0.4초 동안 투명도 30%까지.
"""
from itertools import count

from lxml import etree

from hiw_lib import NS, el, q

PRESET = {
    'appear': (1, 'entr', 0), 'fade_in': (10, 'entr', 0), 'fade_out': (10, 'exit', 0), 'rise': (42, 'entr', 0),
    'pop': (53, 'entr', 16), 'zoom_in': (53, 'entr', 16), 'wipe_in': (22, 'entr', 8), 'wipe_out': (22, 'exit', 8),
    'type': (1, 'entr', 0), 'blink': (35, 'emph', 0), 'dim': (9, 'emph', 0), 'undim': (9, 'emph', 0),
    'fly': (0, 'path', 0), 'move': (0, 'path', 0), 'pulse': (6, 'emph', 0), 'ring': (53, 'entr', 16),
    'zoom_out': (53, 'exit', 16), 'sink': (42, 'exit', 0),
}
WIPE = {'left': (8, 'wipe(left)'), 'right': (2, 'wipe(right)'), 'down': (1, 'wipe(down)'), 'up': (4, 'wipe(up)')}


class Timeline:
    def __init__(self):
        self.steps = []

    def step(self):
        self.steps.append([])

    def add(self, kind, spid, delay=0, dur=400, **kw):
        self.steps[-1].append(dict(kind=kind, spid=spid, delay=int(delay), dur=int(dur), **kw))

    def step_len(self, i):
        out = 0
        for e in self.steps[i]:
            d = e['dur'] * (2 if e['kind'] == 'pulse' else 1)
            if e['kind'] in ('blink',):
                d = 0
            if e['kind'] == 'type':
                d = e.get('ms', 45) * e.get('n', 20)
            out = max(out, e['delay'] + d)
        return out

    # -------------------------------------------------------------- XML
    def xml(self, sp_ids, auto=None, first_auto=True):
        """auto = (첫 대기 ms, [묶음별 머무는 ms])면 클릭 없이 저절로(미리보기 영상용).
        first_auto면 첫 묶음은 장이 열리자마자(모핑이 끝난 뒤 바로), 나머지는 클릭마다."""
        ids = count(1)
        grp_of = {}
        timing = etree.Element(q('p:timing'), nsmap=NS)
        root = el('p:cTn', el('p:par', el('p:tnLst', timing)), id=next(ids), dur='indefinite', restart='never', nodeType='tmRoot')
        seq = el('p:seq', el('p:childTnLst', root), concurrent=1, nextAc='seek')
        main = el('p:cTn', seq, id=next(ids), dur='indefinite', nodeType='mainSeq')
        mkids = el('p:childTnLst', main)
        if auto:
            t0, holds = auto
            outer = el('p:cTn', el('p:par', mkids), id=next(ids), fill='hold')
            sc = el('p:stCondLst', outer)
            el('p:cond', sc, delay='indefinite')
            c = el('p:cond', sc, evt='onBegin', delay=0)
            el('p:tn', c, val=2)
            okids = el('p:childTnLst', outer)
            t = t0
            for i, effs in enumerate(self.steps):
                if not effs:
                    t += holds[i]
                    continue
                inner = el('p:cTn', el('p:par', okids), id=next(ids), fill='hold')
                el('p:cond', el('p:stCondLst', inner), delay=t)
                ik = el('p:childTnLst', inner)
                for j, e in enumerate(effs):
                    self._effect(ik, ids, e, 'afterEffect' if j == 0 else 'withEffect', grp_of)
                t += self.step_len(i) + holds[i]
        else:
            for i, effs in enumerate(self.steps):
                if not effs:
                    continue
                auto0 = first_auto and i == 0
                outer = el('p:cTn', el('p:par', mkids), id=next(ids), fill='hold')
                sc = el('p:stCondLst', outer)
                el('p:cond', sc, delay='indefinite')
                if auto0:
                    c = el('p:cond', sc, evt='onBegin', delay=0)
                    el('p:tn', c, val=2)
                inner = el('p:cTn', el('p:par', el('p:childTnLst', outer)), id=next(ids), fill='hold')
                el('p:cond', el('p:stCondLst', inner), delay=0)
                ik = el('p:childTnLst', inner)
                for j, e in enumerate(effs):
                    node = ('afterEffect' if auto0 else 'clickEffect') if j == 0 else 'withEffect'
                    self._effect(ik, ids, e, node, grp_of)
        pc = el('p:prevCondLst', seq)
        el('p:sldTgt', el('p:tgtEl', el('p:cond', pc, evt='onPrev', delay=0)))
        nc = el('p:nextCondLst', seq)
        el('p:sldTgt', el('p:tgtEl', el('p:cond', nc, evt='onNext', delay=0)))
        bl = el('p:bldLst', timing)
        for spid, n in sorted(grp_of.items()):
            if spid in sp_ids:
                for g in range(n):
                    el('p:bldP', bl, spid=spid, grpId=g, animBg=1)
        if not len(bl):
            timing.remove(bl)
        return timing

    # -------------------------------------------------------------- 조각
    @staticmethod
    def _tgt(parent, spid):
        el('p:spTgt', el('p:tgtEl', parent), spid=spid)

    def _set(self, kids, ids, spid, attr, val, delay=0, dur=1):
        s = el('p:set', kids)
        cb = el('p:cBhvr', s)
        ct = el('p:cTn', cb, id=next(ids), dur=dur, fill='hold')
        el('p:cond', el('p:stCondLst', ct), delay=delay)
        self._tgt(cb, spid)
        el('p:attrName', el('p:attrNameLst', cb)).text = attr
        el('p:strVal', el('p:to', s), val=val)

    def _fx(self, kids, ids, spid, transition, flt, dur, delay=0, prl=None):
        ae = el('p:animEffect', kids, transition=transition, filter=flt)
        if prl:
            ae.set('prLst', prl)
        cb = el('p:cBhvr', ae)
        if prl:
            cb.set('rctx', 'IE')
        ct = el('p:cTn', cb, id=next(ids), dur=dur)
        if prl:
            ct.set('fill', 'hold')
        if delay:
            el('p:cond', el('p:stCondLst', ct), delay=delay)
        self._tgt(cb, spid)

    def _anim(self, kids, ids, spid, attr, frm, to, dur, delay=0, accel=None, decel=None):
        a = el('p:anim', kids, calcmode='lin', valueType='num')
        cb = el('p:cBhvr', a, additive='base')
        ct = el('p:cTn', cb, id=next(ids), dur=dur, fill='hold')
        if accel:
            ct.set('accel', str(int(accel)))
        if decel:
            ct.set('decel', str(int(decel)))
        if delay:
            el('p:cond', el('p:stCondLst', ct), delay=delay)
        self._tgt(cb, spid)
        el('p:attrName', el('p:attrNameLst', cb)).text = attr
        tl = el('p:tavLst', a)
        for tm, v in ((0, frm), (100000, to)):
            el('p:strVal', el('p:val', el('p:tav', tl, tm=tm)), val=v)

    def _scale(self, kids, ids, spid, s0, s1, dur, delay=0, accel=None, decel=None):
        for attr in ('ppt_w', 'ppt_h'):
            self._anim(kids, ids, spid, attr, '#%s*%.3f' % (attr, s0), '#%s*%.3f' % (attr, s1), dur, delay, accel, decel)

    def _motion(self, kids, ids, spid, path, dur, delay=0, accel=45000, decel=55000):
        am = el('p:animMotion', kids, origin='layout', path=path, pathEditMode='relative', rAng=0, ptsTypes='')
        cb = el('p:cBhvr', am)
        ct = el('p:cTn', cb, id=next(ids), dur=dur, fill='hold')
        if accel:
            ct.set('accel', str(int(accel)))
        if decel:
            ct.set('decel', str(int(decel)))
        if delay:
            el('p:cond', el('p:stCondLst', ct), delay=delay)
        self._tgt(cb, spid)
        an = el('p:attrNameLst', cb)
        el('p:attrName', an).text = 'ppt_x'
        el('p:attrName', an).text = 'ppt_y'
        el('p:rCtr', am, x=0, y=0)

    @staticmethod
    def _curve_path(dx, dy, bend, to_zero=True, base=(0, 0)):
        """(dx, dy)px 떨어진 곳 ↔ 제자리 사이 3차 곡선(슬라이드 비율 좌표). bend는 수직 방향으로 휘는 정도.
        PowerPoint는 한 도형의 이동 경로를 더하지 않고 새 경로로 바꿔 끼우므로(2026-11-08 시험), 앞 경로가 끝난 자리(base px)에서
        시작해야 튀지 않는다. 예: 화면 밖에 두고 순간 이동시킨 도형(base = (-1600, 0))."""
        X, Y = dx / 1280, dy / 720
        bx, by = base[0] / 1280, base[1] / 720
        nx, ny = -Y * 720 / 1280, X * 1280 / 720
        if to_zero:     # 출발 base+(X,Y) → 도착 base
            c1 = (X * 0.62 + nx * bend * 0.56, Y * 0.62 + ny * bend * 0.56)
            c2 = (X * 0.18 + nx * bend * 0.34, Y * 0.18 + ny * bend * 0.34)
            pts = [(X, Y), c1, c2, (0, 0)]
        else:           # 출발 base → 도착 base+(X,Y)
            c1 = (X * 0.38 + nx * bend * 0.56, Y * 0.38 + ny * bend * 0.56)
            c2 = (X * 0.82 + nx * bend * 0.34, Y * 0.82 + ny * bend * 0.34)
            pts = [(0, 0), c1, c2, (X, Y)]
        pts = [(a + bx, b + by) for a, b in pts]
        return 'M %.5f %.5f C %.5f %.5f %.5f %.5f %.5f %.5f E' % tuple(v for pt in pts for v in pt)

    # -------------------------------------------------------------- 효과 하나
    def _effect(self, kids, ids, e, node, grp_of):
        spid, kind, dur = e['spid'], e['kind'], e['dur']
        g = grp_of.get(spid, 0)
        grp_of[spid] = g + 1
        pid, pcls, psub = PRESET[kind]
        if kind in ('wipe_in', 'wipe_out'):
            psub = WIPE[e.get('dir', 'left')][0]
        par = el('p:par', kids)
        ct = el('p:cTn', par, id=next(ids), presetID=pid, presetClass=pcls, presetSubtype=psub, fill='hold', grpId=g,
                nodeType=node)
        if kind == 'pulse':
            ct.set('autoRev', '1')
        if kind == 'blink':
            ct.set('repeatCount', 'indefinite')
        el('p:cond', el('p:stCondLst', ct), delay=e['delay'])
        if kind == 'type':
            it = el('p:iterate', ct, type='lt')
            el('p:tmAbs', it, val=e.get('ms', 45))
        ck = el('p:childTnLst', ct)
        if kind == 'appear':
            self._set(ck, ids, spid, 'style.visibility', 'visible')
        elif kind == 'type':
            self._set(ck, ids, spid, 'style.visibility', 'visible')
        elif kind == 'fade_in':
            self._set(ck, ids, spid, 'style.visibility', 'visible')
            self._fx(ck, ids, spid, 'in', 'fade', dur)
        elif kind == 'fade_out':
            self._fx(ck, ids, spid, 'out', 'fade', dur)
            self._set(ck, ids, spid, 'style.visibility', 'hidden', delay=max(dur - 1, 0))
        elif kind == 'rise':
            dy = e.get('dy', 14) / 720
            self._set(ck, ids, spid, 'style.visibility', 'visible')
            self._fx(ck, ids, spid, 'in', 'fade', int(dur * 0.8))
            self._anim(ck, ids, spid, 'ppt_x', '#ppt_x', '#ppt_x', dur)
            self._anim(ck, ids, spid, 'ppt_y', '#ppt_y+%.4f' % dy, '#ppt_y', dur, decel=100000)
        elif kind == 'sink':          # 살짝 가라앉으며 사라짐
            dy = e.get('dy', 10) / 720
            self._fx(ck, ids, spid, 'out', 'fade', dur)
            self._anim(ck, ids, spid, 'ppt_y', '#ppt_y', '#ppt_y+%.4f' % dy, dur, accel=100000)
            self._set(ck, ids, spid, 'style.visibility', 'hidden', delay=max(dur - 1, 0))
        elif kind == 'zoom_in':
            s0 = e.get('from', 0.88)
            self._set(ck, ids, spid, 'style.visibility', 'visible')
            self._fx(ck, ids, spid, 'in', 'fade', dur)
            self._scale(ck, ids, spid, s0, 1.0, dur, decel=100000)
        elif kind == 'pop':           # 넘쳤다가 제자리: s0 → over → 1
            s0, over = e.get('from', 0.6), e.get('over', 1.05)
            d1 = int(dur * 0.62)
            self._set(ck, ids, spid, 'style.visibility', 'visible')
            self._fx(ck, ids, spid, 'in', 'fade', max(120, int(dur * 0.45)))
            self._scale(ck, ids, spid, s0, over, d1, decel=100000)
            self._scale(ck, ids, spid, over, 1.0, dur - d1, delay=d1, accel=30000, decel=70000)
        elif kind == 'zoom_out':
            s1 = e.get('to', 0.85)
            self._fx(ck, ids, spid, 'out', 'fade', dur)
            self._scale(ck, ids, spid, 1.0, s1, dur, accel=100000)
            self._set(ck, ids, spid, 'style.visibility', 'hidden', delay=max(dur - 1, 0))
        elif kind == 'ring':          # 물결: 작게 나타나 커지며 사라짐
            s0, s1 = e.get('from', 0.2), e.get('to', 1.0)
            self._set(ck, ids, spid, 'style.visibility', 'visible')
            self._scale(ck, ids, spid, s0, s1, dur, decel=100000)
            self._fx(ck, ids, spid, 'out', 'fade', int(dur * 0.55), delay=int(dur * 0.45))
            self._set(ck, ids, spid, 'style.visibility', 'hidden', delay=dur)
        elif kind in ('wipe_in', 'wipe_out'):
            flt = WIPE[e.get('dir', 'left')][1]
            if kind == 'wipe_in':
                self._set(ck, ids, spid, 'style.visibility', 'visible')
                self._fx(ck, ids, spid, 'in', flt, dur)
            else:
                self._fx(ck, ids, spid, 'out', flt, dur)
                self._set(ck, ids, spid, 'style.visibility', 'hidden', delay=max(dur - 1, 0))
        elif kind == 'blink':         # 커서 깜빡임(다음 클릭·장이 끝날 때까지)
            a = el('p:anim', ck, calcmode='discrete', valueType='str')
            cb = el('p:cBhvr', a)
            el('p:cTn', cb, id=next(ids), dur=dur)
            self._tgt(cb, spid)
            el('p:attrName', el('p:attrNameLst', cb)).text = 'style.visibility'
            tl = el('p:tavLst', a)
            el('p:strVal', el('p:val', el('p:tav', tl, tm=0)), val='visible')
            el('p:strVal', el('p:val', el('p:tav', tl, tm=55000)), val='hidden')
        elif kind in ('dim', 'undim'):
            to = e.get('to', 0.3) if kind == 'dim' else 1.0
            self._set(ck, ids, spid, 'style.opacity', '%.2f' % to, dur=dur)
            self._fx(ck, ids, spid, 'out', 'image', dur, prl='opacity: %.2f' % to)
        elif kind == 'fly':           # (dx, dy)px 떨어진 곳에서 곡선으로 제자리로(놓인 자리가 도착점)
            if e.get('show', True):
                self._set(ck, ids, spid, 'style.visibility', 'visible')
                if e.get('fade', True):
                    self._fx(ck, ids, spid, 'in', 'fade', min(260, dur))
            self._motion(ck, ids, spid, self._curve_path(e['dx'], e['dy'], e.get('bend', 0.18), base=e.get('base', (0, 0))), dur)
            if e.get('grow'):
                g0 = e['grow']
                self._scale(ck, ids, spid, g0, 1.0, dur, accel=45000, decel=55000)
        elif kind == 'move':          # 지금 자리에서 (dx, dy)px 옮겨 가 머묾
            path = self._curve_path(e['dx'], e['dy'], e.get('bend', 0.0), to_zero=False, base=e.get('base', (0, 0)))
            self._motion(ck, ids, spid, path, dur, accel=e.get('accel', 40000), decel=e.get('decel', 60000))
        elif kind == 'pulse':
            sc = int(e.get('scale', 1.06) * 100000)
            asc = el('p:animScale', ck)
            cb = el('p:cBhvr', asc)
            el('p:cTn', cb, id=next(ids), dur=dur, fill='hold')
            self._tgt(cb, spid)
            el('p:by', asc, x=sc, y=sc)
        else:
            raise ValueError(kind)
