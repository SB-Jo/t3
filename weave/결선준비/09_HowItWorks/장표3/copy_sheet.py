#!/usr/bin/env python3
"""판 8개의 장별 설명(제목·부제)·뱃지·발표자 노트를 한 파일로 → out/문구_한눈에.md"""
import importlib
from pathlib import Path

import scene3

HERE = Path(__file__).resolve().parent
ALL = ['a1', 'a2', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3']


def main():
    out = ['# How it Works v3 — 장별 문구 (판 8개)', '',
           '각 장의 설명 제목 / 부제 / 뱃지와 발표자 노트. `out/<판>_png/sNN.png`와 번호가 같다.', '']
    for v in ALL:
        spec = importlib.import_module(v).SPEC
        sc = scene3.build(spec)
        out += ['## %s  (%d장)' % (spec['file'], len(sc.steps)), '']
        out += ['| 장 | 자리 | 설명 | 발표자 노트 |', '|---|---|---|---|']
        for i, st in enumerate(sc.steps, 1):
            t = ' '.join(''.join(x for x, _ in st.cap['t']).split())
            s = st.cap.get('s', '')
            b = st.cap.get('badge')
            cap = ('`%s` ' % b if b else '') + '**%s**' % t + ('<br>%s' % s if s else '')
            out.append('| %d | %s | %s | %s |' % (i, {'left': '왼쪽', 'right': '오른쪽', 'top': '위'}[st.cap.get('side', 'top')], cap,
                                                st.notes.replace('|', '/')))
        out.append('')
        out += ['다시 쓴 질문:', '']
        for n, hop in enumerate(spec['hops'], 1):
            q = hop['q']
            if isinstance(q, str):
                out.append('%d. %s' % (n, q))
            else:
                rw = q[2] if len(q) > 2 else q[1]
                out.append('%d. [%s]%s → [%s]%s' % (n, q[0], q[1], spec['hops'][n - 2]['token'], rw))
        out.append('')
    (HERE / 'out' / '문구_한눈에.md').write_text('\n'.join(out), encoding='utf-8')
    print('→ out/문구_한눈에.md')


if __name__ == '__main__':
    main()
