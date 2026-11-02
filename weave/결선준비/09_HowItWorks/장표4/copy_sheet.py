#!/usr/bin/env python3
"""판마다 장별 설명·발표자 노트·다시 쓴 질문을 한 파일로 → out/문구_한눈에.md"""
import importlib
from pathlib import Path

import scene4

HERE = Path(__file__).resolve().parent
ALL = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'c3']


def plain(cap):
    t = ''.join(x for x, _ in cap['t']).replace('\n', ' ')
    return t + ('  (작게: %s)' % cap['s'] if cap.get('s') else '')


def main():
    out = ['# 문구 한눈에 (장표4)', '', '판마다 장 번호, 설명(화면 글), 배율, 발표자 노트. 아래에 다시 쓴 질문 목록.', '']
    for v in ALL:
        sp = importlib.import_module(v).SPEC
        sc = scene4.build(sp)
        out += ['## %s' % sp['file'], '', '처음 질문: “%s”' % sp['ask'], '']
        for i, h in enumerate(sp['hops']):
            q = h['q']
            if isinstance(q, str):
                out.append('%d. %s' % (i + 1, q))
            else:
                rw = q[2] if len(q) > 2 else q[1]
                out.append('%d. [%s]%s → [%s → %s]%s' % (i + 1, q[0], q[1], q[0], sp['hops'][i - 1]['token'], rw))
        out += ['', '답: %s' % sp['answer'], '', '| 장 | 설명 | 배율 | 노트 |', '|---|---|---|---|']
        for i, st in enumerate(sc.steps):
            out.append('| %d | %s | ×%.1f | %s |' % (i + 1, plain(st.cap), st.cam[2], st.notes.replace('|', '/')))
        out.append('')
    (HERE / 'out' / '문구_한눈에.md').write_text('\n'.join(out), encoding='utf-8')
    print('→ out/문구_한눈에.md')


if __name__ == '__main__':
    main()
