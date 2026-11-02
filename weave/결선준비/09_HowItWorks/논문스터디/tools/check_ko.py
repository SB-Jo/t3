#!/usr/bin/env python3
"""번역 검사: python check_ko.py <key>

work/<key>/src.json과 work/<key>/ko/*.json(블록 id → 한국어 html)을 맞춰 봐요.
- 본문(부록 제외)의 h2·h3·h4·p·li·fn과 fig·tab·alg 캡션이 모두 번역됐는지
- 수식 \\( … \\) · \\[ … \\]가 원문 그대로 남았는지
- 인용 <span class="cite">, 각주 표시 <sup class="fnm">, b·i·code 태그 수가 같은지
- 한글이 들어 있는지
문제가 없으면 'OK'와 함께 0으로 끝나요.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSLATE = {'h2', 'h3', 'h4', 'p', 'li', 'fn'}
CAPTION = {'fig', 'tab', 'alg'}


def maths(s):
    return re.findall(r'\\\(.*?\\\)|\\\[.*?\\\]', s, flags=re.S)


def count(s, pat):
    return len(re.findall(pat, s))


def main():
    key = sys.argv[1]
    work = os.path.join(ROOT, 'work', key)
    src = json.load(open(os.path.join(work, 'src.json'), encoding='utf-8'))
    ko = {}
    dup = []
    for fn in sorted(glob.glob(os.path.join(work, 'ko', '*.json'))):
        try:
            part = json.load(open(fn, encoding='utf-8'))
        except Exception as e:  # noqa: BLE001
            print('JSON 오류:', fn, e)
            sys.exit(2)
        for k, v in part.items():
            if k in ko:
                dup.append(k)
            ko[k] = v
    blocks = src['abstract'] + src['blocks']
    byid = {b['id']: b for b in blocks}
    need, optional = [], []
    for b in blocks:
        t = b['type']
        want = (t in TRANSLATE) or (t in CAPTION and b.get('html'))
        if not want:
            continue
        (optional if b.get('appendix') else need).append(b['id'])
    missing = [i for i in need if i not in ko]
    extra = [i for i in ko if i not in byid]
    warns = []
    for i, v in ko.items():
        b = byid.get(i)
        if not b:
            continue
        en = b.get('html', '')
        for m in maths(en):
            if m not in v:
                warns.append('%s 수식이 달라졌거나 빠짐: %s' % (i, m[:60]))
                break
        for name, pat in (('cite', r'<span class="cite">'), ('각주', r'<sup class="fnm">'), ('b', r'<b>'), ('code', r'<code>'), ('i', r'<i>')):
            a, c = count(en, pat), count(v, pat)
            if a != c and not (name == 'i' and abs(a - c) <= 1):
                warns.append('%s <%s> 개수 다름: 원문 %d / 번역 %d' % (i, name, a, c))
        plain = re.sub(r'<[^>]+>|\\\(.*?\\\)|\\\[.*?\\\]', ' ', v, flags=re.S)
        words = len(re.sub(r'<[^>]+>', ' ', en).split())
        if words >= 4 and not re.search(r'[가-힣]', plain):
            warns.append('%s 한글이 없음' % i)
        if v.count('<') != v.count('>'):
            warns.append('%s 꺾쇠 짝이 안 맞음' % i)
    done_opt = sum(1 for i in optional if i in ko)
    print('[%s] 필수 %d개 중 번역 %d개, 빠짐 %d개 | 부록 %d개 중 %d개 번역 | 중복 %d | 원문에 없는 id %d | 경고 %d'
          % (key, len(need), len(need) - len(missing), len(missing), len(optional), done_opt, len(dup), len(extra), len(warns)))
    if missing:
        print('빠진 id:', ' '.join(missing[:80]))
    if extra:
        print('원문에 없는 id:', ' '.join(extra[:40]))
    if dup:
        print('여러 파일에 중복된 id:', ' '.join(dup[:40]))
    for w in warns[:60]:
        print(' -', w)
    if not missing and not extra:
        print('OK')
        sys.exit(0)
    sys.exit(1)


if __name__ == '__main__':
    main()
