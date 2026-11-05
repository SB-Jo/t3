#!/usr/bin/env python3
"""결선 Appendix 새 장 7개를 HTML로 만든다(2026-11-05). render.cjs → out/*.art.png, *.layout.json → apply_appendix.py.

  python make_pages.py   → page-a1 ~ page-a7 .html, notes-a1 ~ a7 .txt
숫자와 인용은 모두 원문에서 확인한 값이다. 시험 조건을 함께 적고, Weave 성능처럼 읽히지 않게 한다.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ICON = {'cal': '../../assets/icons/galaxy/samsung-calendar.png', 'note': '../../assets/icons/app-notes.png',
        'mail': '../../assets/icons/galaxy/samsung-email-blue.png', 'talk': '../../assets/icons/app-kakao.png',
        'gal': '../../assets/icons/galaxy/samsung-gallery.png', 'wal': '../../../09_HowItWorks/장표5/assets/samsung-wallet.png',
        'map': '../../../09_HowItWorks/장표5/assets/app-map.png'}
BLUE, PURPLE, GRAY = '#2F7BF6', '#6B4EFF', '#6F7690'

CSS = """
  .t-label { top: 30px; } .t-title { top: 62px; } .t-sub { top: 116px; font-size: 16.5px; }
  .panel { position: absolute; background: #fff; border: 1px solid var(--card-line); border-radius: 16px; box-shadow: 0 8px 24px rgba(107,78,255,.06); }
  .tx { position: absolute; font-size: 12px; line-height: 17px; color: var(--ink-2); white-space: nowrap; }
  .tx b { font-weight: 700; color: var(--ink); }
  .tx em { font-style: normal; font-weight: 700; color: #6B4EFF; }
  .th { position: absolute; font-size: 11.5px; line-height: 16px; font-weight: 700; color: #6B4EFF; white-space: nowrap; }
  .st { position: absolute; font-size: 12px; line-height: 17px; font-weight: 700; color: var(--ink); white-space: nowrap; }
  .rule { position: absolute; height: 1px; background: #EEE9FA; }
  .src { position: absolute; left: 62px; font-size: 11px; line-height: 15px; color: #8E88A0; white-space: nowrap; }
  .note { position: absolute; font-size: 12.5px; line-height: 19px; color: var(--ink-2); white-space: nowrap; }
  .note b { font-weight: 700; color: var(--ink); }
  .note em { font-style: normal; font-weight: 700; color: #6B4EFF; }
  .box { position: absolute; border-radius: 11px; background: #fff; border: 1.6px solid #DCD6EA; }
  .box.em { border-color: #2F7BF6; background: #F3F8FF; }
  .box.ll { border-color: #6B4EFF; background: #F5F1FF; }
  .box.ru { border-color: #6F7690; border-style: dashed; background: #F8F8FB; }
  .box.ok { border-color: #6B4EFF; background: #F5F1FF; }
  .box.no { border-color: #E4DFEF; background: #FAF9FC; }
  .bt { position: absolute; font-size: 12px; line-height: 16px; font-weight: 700; color: var(--ink); text-align: center; white-space: nowrap; }
  .bs { position: absolute; font-size: 10.5px; line-height: 14px; color: #6A6474; text-align: center; white-space: nowrap; }
  .lane { position: absolute; font-size: 11.5px; line-height: 16px; font-weight: 700; color: #8E88A0; white-space: nowrap; }
  .chipt { position: absolute; font-size: 10.5px; line-height: 14px; color: #6A6474; white-space: nowrap; }
  .chipb { position: absolute; font-size: 11px; line-height: 15px; font-weight: 700; color: var(--ink); white-space: nowrap; }
  .tag { position: absolute; font-size: 10px; line-height: 14px; font-weight: 700; white-space: nowrap; }
  .tag.on { color: #6B4EFF; } .tag.off { color: #A29DB2; }
  .app { position: absolute; }
  .wrap { position: absolute; left: 0; top: 10px; width: 1280px; height: 720px; }
  svg.fxl { position: absolute; left: 0; top: 0; width: 1280px; height: 720px; pointer-events: none; overflow: visible; z-index: 2; }
"""


def page(name, chip, title, sub, body, svg='', notes=''):
    html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{chip} — {title}</title>
<link rel="stylesheet" href="../../pages/theme.css">
<style>{CSS}</style>
</head>
<body>
<div class="slide" id="slide">
  <div class="bg bg-base"></div><div class="bg bg-peach"></div><div class="bg bg-lav"></div>
  <div class="t-label" data-x>{chip}</div>
  <div class="t-title" data-x>{title}</div>
  <div class="t-sub" data-x>{sub}</div>
  <div class="wrap">
{body}
  <svg class="fxl" viewBox="0 0 1280 720"><defs>
    <marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M1 1 9 5 1 9z" fill="#8B6BFF"/></marker>
    <marker id="ag" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M1 1 9 5 1 9z" fill="#A29DB2"/></marker>
  </defs>{svg}</svg>
  </div>
</div>
<script>document.fonts.ready.then(() => {{ window.pageReady = true; }});</script>
</body>
</html>
"""
    (HERE / f'{name}.html').write_text(html, encoding='utf-8')
    (HERE / f'notes-{name}.txt').write_text(notes.strip() + '\n', encoding='utf-8')


def T(cls, x, y, html, w=None, extra=''):
    wd = f' width:{w}px;' if w else ''
    return f'  <div class="{cls}" data-x style="left:{x}px; top:{y}px;{wd}{extra}">{html}</div>\n'


def BOX(cls, x, y, w, h):
    return f'  <div class="box {cls}" style="left:{x}px; top:{y}px; width:{w}px; height:{h}px;"></div>\n'


def NODE(cls, x, y, w, h, title, sub=None):
    o = BOX(cls, x, y, w, h)
    if sub:
        o += T('bt', x, y + 8, title, w) + T('bs', x, y + 26, sub, w)
    else:
        o += T('bt', x, y + (h - 16) / 2, title, w)
    return o


def ARROW(x1, y1, x2, y2, c='#8B6BFF', m='ah', dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{c}" stroke-width="1.8" fill="none" marker-end="url(#{m})"{d}/>'


def IMG(key, x, y, s=16):
    return f'  <img class="app" src="{ICON[key]}" alt="" style="left:{x}px; top:{y}px; width:{s}px; height:{s}px; border-radius:4px; z-index:6;">\n'


# ──────────────────────────────────────────── A1 파이프라인 전체
def a1():
    b = ''
    b += '  <div class="panel" style="left:60px; top:148px; width:1160px; height:476px;"></div>\n'
    # 00
    b += T('lane', 80, 162, '00 사전 준비 (충전 중, 유휴 시간)')
    b += NODE('', 80, 184, 150, 44, '허용한 기록', '노트, 메일, 사진, 알림 글자')
    b += NODE('em', 290, 184, 230, 44, '벡터 색인', 'Reasoning Embedding')
    b += NODE('em', 540, 184, 200, 44, '키워드 색인', 'BM25')
    b += NODE('ru', 760, 184, 250, 44, '메타데이터', '{ date, app, from }')
    # 01
    b += T('lane', 80, 244, '01 순간 감지')
    b += NODE('', 80, 266, 210, 34, '위로 밀기 (UX 1)')
    b += NODE('', 304, 266, 210, 34, '실타래 버튼 (UX 2)')
    b += NODE('ru', 528, 266, 300, 34, '위치 + 탑승권 + 대화 상대 (UX 3)')
    # 02, 03
    b += T('lane', 80, 316, '02 질문 다시 쓰기, 03 연쇄 탐색')
    y = 340
    b += NODE('em', 80, y, 190, 54, '① 한 번 찾아 보기', 'BM25 + Reasoning Embedding')
    b += NODE('', 316, y + 8, 96, 38, '충분한가?')
    b += NODE('ll', 458, y, 160, 54, '② 모자라면 나누기', 'sLLM 1~2B')
    b += NODE('em', 664, y, 200, 54, '③ 홉마다 찾기', 'Reasoning Embedding + 필터')
    b += NODE('ru', 930, y, 270, 54, '④ 단서로 다시 쓰기', '이름은 기록에서 복사, 날짜는 규칙 계산')
    b += T('bs', 664, y + 60, '반복은 2~3홉까지. 새 단서가 없으면 멈춥니다', 536)
    b += T('tag on', 417, y + 12, '아니요')
    # 04
    b += T('lane', 80, 426, '04 전달')
    y2 = 448
    b += NODE('ll', 80, y2, 160, 44, '요약 (UX 1)', '바뀐 내용 반영, 파일 첨부')
    b += NODE('ll', 252, y2, 160, 44, '정확한 이름 (UX 2)', '라벨을 읽은 이름')
    b += NODE('ll', 424, y2, 160, 44, '보낼 말 (UX 3)', '상대의 말투 그대로')
    b += NODE('ru', 596, y2, 300, 44, '못 찾으면 찾은 단서까지만 보여 줍니다', '단정하지 않고 원문과 출처를 함께 보여 줍니다')
    b += NODE('', 908, y2, 292, 44, '입력과 전송은 사용자가 합니다', '기기 안에서 처리, 외부 전송 없음')
    # 범례
    for i, (c, t) in enumerate([('em', '기록을 찾는 일 (임베딩, 키워드)'), ('ll', '글을 쓰는 일 (sLLM)'), ('ru', '규칙과 메타데이터')]):
        x = 80 + i * 250
        b += f'  <div class="box {c}" style="left:{x}px; top:510px; width:18px; height:12px; border-radius:4px;"></div>\n'
        b += T('chipt', x + 24, 509, t)
    # 두 줄
    b += T('note', 80, 538, '<b>1. 우리는 Multi-hop Retrieval 파이프라인을 씁니다.</b> 표준은 없고, 논문들이 공유하는 뼈대를 따릅니다.')
    b += T('note', 80, 562, '<b>2. 홉 사이는 질문 다시 쓰기가 잇고, 각 홉의 기록은 Reasoning Embedding이 찾습니다.</b> 임베딩은 앞 기록을 기억하지 않습니다.')
    b += T('note', 80, 590, '설계안이며 실측 전입니다. 2홉 지연은 S26 Snapdragon 공개 측정값으로 계산하면 생성 약 0.8~1.7초에 검색 시간을 더한 값입니다(Exynos 측정값 없음).', extra=' font-size:11.5px; color:#8E88A0;')
    b += T('src', 62, 636, '* 출처: Wei et al., "A Survey of Reasoning-Intensive Retrieval", ACL 2026 · Kim et al., "Hi-Q", NeurIPS 2026 · Trivedi et al., "IRCoT", ACL 2023 · Qualcomm AI Hub, Qwen3-1.7B 성능 측정값')
    svg = ''
    svg += ARROW(230, 206, 288, 206)
    svg += ARROW(270, 367, 314, 367) + ARROW(412, 367, 456, 367) + ARROW(618, 367, 662, 367)
    svg += ARROW(864, 360, 928, 360) + ARROW(930, 376, 866, 376)
    # 충분하면 바로, 홉을 돌아 찾으면 그때 04 전달로
    svg += '<path d="M764 394 L764 434 L126 434" stroke="#8B6BFF" stroke-width="1.8" fill="none" marker-end="url(#ah)"/>'
    svg += '<path d="M364 386 L364 434" stroke="#8B6BFF" stroke-width="1.8" fill="none"/>'
    b += T('tag on', 370, 402, '네, 바로 전달')
    b += T('tag on', 704, 412, '답을 찾으면')
    notes = """Appendix · 파이프라인. Weave의 전체 구조입니다. 기술 질문이 오면 이 장을 먼저 띄웁니다.
Weave는 평소에 허용한 기록을 벡터, 키워드 색인, 메타데이터로 저장합니다. 사용자가 부르거나 상황이 맞으면 처음 질문 그대로 한 번 찾아 봅니다. 여기서 답이 나오면 바로 끝납니다. 답이 모자라면 sLLM이 질문을 나누고, 각 질문을 Reasoning Embedding으로 찾습니다. 찾은 단서를 빈칸에 넣어 질문을 다시 쓰고 다음 기록을 찾습니다. 이름은 기록에서 복사하고 날짜는 규칙으로 계산해서 지어낼 여지를 줄입니다. 마지막으로 sLLM이 화면에 맞게 요약, 이름, 보낼 말을 만듭니다.
주의: 설계안입니다. 지연 수치는 S26 Snapdragon의 Qwen3-1.7B 공개 측정값(prefill 3,288.5 tok/s, decode 42.4 tok/s)으로 계산한 값이고 실측이 아닙니다."""
    page('page-a1', 'Appendix · 파이프라인', 'Weave 파이프라인 전체 구조', '여러 멀티홉 연구가 공유하는 뼈대 위에 온디바이스 제약을 더한 설계입니다.', b, svg, notes)


# ──────────────────────────────────────────── A2 관련 연구 지도
def a2():
    b = ''
    steps = ['① 한 번 찾아 보기', '② 모자라면 나누기', '③ 1홉 찾기', '④ 단서로 다시 쓰기', '③ 2홉 찾기', '⑤ 답과 근거']
    x, svg = 92, ''
    cls = ['em', 'll', 'em', 'ru', 'em', 'll']
    for i, s in enumerate(steps):
        b += NODE(cls[i], x, 150, 156, 30, s)
        if i < 5:
            svg += ARROW(x + 156, 165, x + 180, 165)
        x += 186
    cards = [
        ('미리 그래프를 만드는 쪽', False, 'HippoRAG 2 (ICML 2025), PropRAG, GRASP',
         ['색인할 때 LLM으로 관계를 뽑아', '그래프를 만들고 그래프를 따라 찾습니다.'],
         ['정해 둔 관계를 여러 단계로 정확히 잇고', '근거를 설명하기 쉽습니다.'],
         ['기록이 들어올 때마다', 'LLM으로 관계를 뽑아야 합니다.']),
        ('찾으면서 다시 쓰는 쪽', True, 'IRCoT (ACL 2023), Hi-Q (NeurIPS 2026), DER-RAG',
         ['찾은 단서를 넣어 질문을 다시 쓰고', '한 번 더 찾습니다.'],
         ['그래프와 학습이 필요 없고', '임베딩을 갈아 끼울 수 있습니다.'],
         ['질문당 LLM 호출: IRCoT 2.92회, Hi-Q 5.7회', '(비용 맞춤 2.93회), DER-RAG 8.00~9.63회']),
        ('임베딩이 직접 잇는 쪽', False, 'MDR (ICLR 2021), GRITHopper (EACL 2026)',
         ['질문과 찾은 기록을 함께 인코더에 넣어', '다음 기록을 찾습니다.'],
         ['글을 생성하지 않습니다. MuSiQue 2번째 홉', 'Hits@1 76.13 (GPT-4o 분해 48.53)'],
         ['대화형 데이터는 시험 전입니다.', 'Weave에서는 보조 경로 후보입니다.']),
        ('코드를 실행하는 에이전트 쪽', False, '코딩 에이전트, RLM, PyRAG',
         ['LLM이 코퍼스를 프로그램처럼 탐색하고', '하위 호출을 반복합니다.'],
         ['중간 상태를 명시적으로 드러내고', '실행 결과를 그대로 씁니다.'],
         ['코드를 짜고 실행할 LLM이 필요해', '소형 모델에는 부담이 큽니다.']),
    ]
    cw, gap, x0 = 280, 13, 60
    for i, (name, me, reps, how, good, lim) in enumerate(cards):
        x = x0 + i * (cw + gap)
        st = 'border:2px solid #6B4EFF; background:#FBFAFF;' if me else ''
        b += f'  <div class="panel" style="left:{x}px; top:192px; width:{cw}px; height:316px; {st}"></div>\n'
        b += T('st', x + 16, 202, name, extra=' font-size:14.5px; line-height:20px;')
        if me:
            b += f'  <div class="box ll" style="left:{x + cw - 72}px; top:202px; width:58px; height:20px; border-radius:10px; background:#6B4EFF;"></div>\n'
            b += T('tag', x + cw - 72, 205, 'Weave', 58, ' color:#fff; text-align:center;')
        b += T('tx', x + 16, 228, reps, extra=' font-size:10.5px; color:#6A6474;')
        y = 254
        for head, lines in (('홉을 잇는 방법', how), ('잘하는 것', good), ('기기 안에서 걸리는 것', lim)):
            b += T('th', x + 16, y, head)
            b += T('tx', x + 16, y + 18, '<br>'.join(lines))
            y += 84
    b += T('note', 62, 518, '<b>왜 Hi-Q를 출발 뼈대로 보나요?</b> 그래프 없이 임베딩만 갈아 끼우고, 안 풀릴 때만 나누는 구조가 Weave 설계와 같습니다. 다만 저자 자체 비교이고 영어 위키, 서버 LLM 결과이며,')
    b += T('note', 62, 538, '시험한 공개 모델 중 가장 작은 것도 27B입니다. 1등이라는 증거가 아니라 출발점으로 봅니다. <b>점수 비교 주의:</b> 논문마다 모델이 달라 MuSiQue 단일 검색도 Hi-Q 표는 32.8, GRASP 표는 37.2 EM입니다.')
    b += T('note', 62, 564, '<b>나누기와 잇기의 근거 (Hi-Q):</b> 막힌 사례 279문항에서 같은 top-5로 필요한 문단을 다 찾는 비율 <em>7.9% → 42.7%</em>, 늘 나누면 <em>60.7 → 57.3 EM</em>(100문항), 다시 쓰기 순서를 빼면 <em>57.9 → 47.1 EM</em>')
    b += T('src', 62, 596, '* 출처: Gutiérrez et al., "HippoRAG 2", ICML 2025 · Jenkins et al., "GRASP", arXiv 2605.16598 · Trivedi et al., "IRCoT", ACL 2023 · Kim et al., "Hi-Q", NeurIPS 2026 · Lee & Lim, "DER-RAG", arXiv 2609.06065')
    b += T('src', 62, 612, '   Xiong et al., "MDR", ICLR 2021 · Erker et al., "GRITHopper", EACL 2026 · 숫자는 모두 영어 공개 벤치마크(위키백과)에서 잰 값으로 Weave 성능이 아닙니다')
    notes = """Appendix · 관련 연구. Multi-hop Retrieval에는 정해진 표준이 없습니다. 논문들은 위의 뼈대를 공유하고, 갈래는 크게 넷입니다. Weave는 둘째 갈래인 찾으면서 다시 쓰는 쪽에 속하고, 셋째 갈래인 임베딩 연결을 보조 경로 후보로 둡니다.
숫자 출처: Hi-Q 표 8(LLM 호출: 전체 5.7회, 비용 맞춤 2.93회, IRCoT 2.92회), DER-RAG(9.63/8.00/9.11회), GRITHopper(MuSiQue open retrieval Hits@1 2홉 76.13, GPT4o + GRITLM 분해 48.53), Hi-Q 표 3(Clean n=279, Root@5 7.9 → Leaf@5 42.7), 표 6(always-decompose 57.3 vs 60.7, N=100, dependency-aware 제거 47.1 vs 57.9).
예상 질문: Hi-Q를 그대로 쓰나요? 아닙니다. 질문당 LLM 5.7회를 그대로 쓸 수 없어서 이름 복사와 날짜 규칙으로 호출을 줄입니다."""
    page('page-a2', 'Appendix · 관련 연구', 'Multi-hop Retrieval 관련 연구 지도', '표준 파이프라인은 없고 공통 뼈대가 있습니다. 갈래는 크게 넷이고, Weave는 둘째 갈래에 속합니다.', b, svg, notes)


# ──────────────────────────────────────────── A3 Reasoning Embedding의 역할과 추론 유형
def a3():
    b = ''
    b += '  <div class="panel" style="left:60px; top:148px; width:520px; height:462px;"></div>\n'
    b += T('st', 78, 160, '임베딩이 하는 일과 하지 않는 일', extra=' font-size:14.5px; line-height:20px;')
    svg = ''
    rows = [('Hop 1 입력', '지은이네 집들이는 언제였지?', '지은 카톡', 'talk', 190), ('Hop 2 입력', '[3/15 (일)]에 마셨던 와인은?', '와인 사진', 'gal', 258)]
    for lab, q, res, ic, y in rows:
        b += T('lane', 78, y + 10, lab)
        b += NODE('ll', 146, y, 200, 36, q)
        b += NODE('em', 372, y, 74, 36, '임베딩')
        b += BOX('', 470, y, 94, 36) + IMG(ic, 478, y + 10) + T('bt', 496, y + 10, res, 66)
        svg += ARROW(346, y + 18, 370, y + 18) + ARROW(446, y + 18, 468, y + 18)
    svg += '<path d="M516 226 L516 240 L246 240 L246 256" stroke="#8B6BFF" stroke-width="1.6" stroke-dasharray="4 3" fill="none" marker-end="url(#ah)"/>'
    b += T('tag on', 300, 243, '찾은 날짜를 넣어 질문을 다시 씁니다')
    b += T('note', 78, 302, '임베딩의 입력은 <b>질문뿐</b>입니다. 앞 기록을 기억하지 않고, 단서를 넣어 다시 쓴 질문을 받습니다.')
    b += T('note', 78, 322, '그래서 <b>튜닝한 임베딩과 질문 다시 쓰기의 이득은 더해집니다.</b>')
    b += T('th', 78, 350, '임베딩을 바꿔도 다시 쓰기의 이득은 남습니다 (Hi-Q 표 13, R@5)')
    tb = [('임베딩', '한 번 검색', 'Hi-Q를 얹으면'), ('Qwen3-Embedding-8B', '68.7', '79.0'), ('text-embedding-3-large', '74.5', '83.9'), ('NV-Embed-v2', '80.2', '88.4')]
    for i, r in enumerate(tb):
        y = 370 + i * 21
        cl = 'th' if i == 0 else 'tx'
        b += T(cl, 78, y, r[0]) + T(cl, 280, y, r[1]) + T(cl, 380, y, ('<em>%s</em>' % r[2]) if i else r[2])
    b += T('th', 78, 462, '다시 쓴 질문도 튜닝한 임베딩으로 찾습니다 (ReasonIR, BRIGHT nDCG@10)')
    b += T('tx', 78, 480, '원래 질문 <b>24.4</b> → GPT-4로 다시 쓴 질문 <em>29.9</em> → 재정렬까지 <b>36.9</b>')
    b += T('th', 78, 508, '임베딩 안에서 추론하는 연구도 입력은 질문입니다 (LaSER)')
    b += T('tx', 78, 526, '0.6B 모델 BRIGHT nDCG@10 <em>23.1</em>, 다시 쓰기 후 검색 22.4. 글을 생성하지 않습니다.')
    b += T('tx', 78, 554, '질문과 기록을 함께 넣는 MDR, GRITHopper에서는 임베딩이 직접 홉을 잇습니다.<br>Weave는 다시 쓴 질문을 화면에 보여 주는 쪽을 택했습니다.', extra=' color:#6A6474; font-size:11.5px;')

    b += '  <div class="panel" style="left:596px; top:148px; width:624px; height:462px;"></div>\n'
    b += T('st', 614, 160, '우리 시나리오의 추론 유형', extra=' font-size:14.5px; line-height:20px;')
    b += T('tx', 790, 162, 'RIR Survey 부록 B의 다섯 유형 기준', extra=' color:#6A6474; font-size:11px;')
    head = [(614, '유형'), (742, '정의 (요약)'), (1000, 'Weave에서')]
    for x, t in head:
        b += T('th', x, 188, t)
    b += '  <div class="rule" style="left:614px; top:206px; width:588px;"></div>\n'
    rows2 = [
        ('Analytical', '문서가 다단계 추론 사슬의 빈칸을 채웁니다.<br>문제를 서로 이어지는 하위 질문으로 나눕니다.', '세 시나리오의 전체 흐름<br>(개인 기록이라 가장 가까운 유형)', True),
        ('Numerical', '수치 사실과 규칙으로 값이나 결정을 정합니다.<br>시간 비교를 포함합니다.', 'UX 1의 11/3과 11/10 비교<br>임베딩이 아니라 규칙이 맡습니다', True),
        ('Deductive', '일반 원리를 적용해 특정 상황을 설명합니다.', '쓰지 않습니다', False),
        ('Analogical', '같은 풀이 전략이나 공통 기반을 공유합니다.', '쓰지 않습니다', False),
        ('Causal', '증상에서 원인으로 인과 사슬을 따라갑니다.', '쓰지 않습니다', False),
    ]
    y = 214
    for n, d, w, on in rows2:
        h = 46 if on else 28
        b += T('st', 614, y, n, extra=(' color:#6B4EFF;' if on else ' color:#A29DB2;'))
        b += T('tx', 742, y, d, extra=('' if on else ' color:#A29DB2;'))
        b += T('tx', 1000, y, w, extra=('' if on else ' color:#A29DB2;'))
        y += h
    b += '  <div class="rule" style="left:614px; top:%dpx; width:588px;"></div>\n' % (y - 2)
    y += 6
    b += T('th', 614, y, '다섯 유형에 없는 한 걸음: \'휴지 안 사 와도 돼\' → 집들이')
    b += T('tx', 614, y + 20, '글에 없는 사실을 일반 지식과 상식으로 잇습니다. 서베이의 <b>개방형 영역</b>(일반 지식과 상식, 숨은 의도 해석)에 해당하고,<br>ImpliRet의 <b>World Knowledge</b> 유형(글 속 표현을 바깥 사실과 연결)과 같은 구조입니다.<br>갈색병과 나이트 리페어의 연결도 같습니다.')
    b += T('tx', 614, y + 80, '쉬운 유형이 아닙니다. ImpliRet에서 가장 좋은 nDCG@10은 <b>14.91%</b>입니다.<br>그래서 Weave는 보낸 사람 같은 필터로 후보를 줄인 뒤 찾도록 설계합니다. 우리 모델로는 측정 전입니다.', extra=' color:#6A6474;')
    b += T('src', 62, 622, '* 출처: Wei et al., "A Survey of Reasoning-Intensive Retrieval", ACL 2026 (부록 B, §3.1.1) · Su et al., "BRIGHT", ICLR 2025 · Taghavi et al., "ImpliRet", EMNLP 2025 · Shao et al., "ReasonIR", COLM 2025')
    b += T('src', 62, 638, '   Kim et al., "Hi-Q", NeurIPS 2026 (표 13) · LaSER, SIGIR 2026 · Xiong et al., "MDR", ICLR 2021 · Erker et al., "GRITHopper", EACL 2026')
    notes = """Appendix · Reasoning Embedding. 예상 질문은 "임베딩이 앞 기록을 어떻게 기억하나요?"입니다. 답은 "임베딩은 기억하지 않습니다. 찾은 단서를 넣어 다시 쓴 질문을 받습니다."입니다.
튜닝한 임베딩과 질문 다시 쓰기는 경쟁이 아니라 더해집니다. Hi-Q 표 13에서 임베딩을 바꿔도 Hi-Q를 얹으면 R@5가 오르고 임베딩 순위는 그대로입니다.
추론 유형은 RIR 서베이 부록 B의 다섯 유형을 썼습니다. 정의는 원문을 줄인 것입니다. Analytical의 원문은 분야 지식을 말하므로 개인 기록과 완전히 같지는 않아서 "가장 가깝다"고 말합니다. BRIGHT 부록에도 Analytical 유형이 있습니다. '휴지 안 사 와도 돼'에서 집들이를 알아보는 한 걸음은 다섯 유형에 정확히 맞는 것이 없고, 서베이의 개방형 영역과 ImpliRet의 World Knowledge가 가장 가깝습니다. 이 문장 자체는 논문 예문이 아니라 우리가 만든 시나리오입니다."""
    page('page-a3', 'Appendix · Reasoning Embedding', 'Reasoning Embedding의 역할과 추론 유형', '찾는 일은 임베딩이, 잇는 일은 질문 다시 쓰기가 맡습니다.', b, svg, notes)


# ──────────────────────────────────────────── UX 상세(공통 틀)
def ux_page(name, chip, title, sub, strip, rows, foot, srcs, notes):
    b, svg = '', ''
    # 위 띠: 기록
    w = strip['w']
    x = 60
    for i, c in enumerate(strip['items']):
        ic, t1, t2, tg, on = c
        cls = 'ok' if on else 'no'
        b += BOX(cls, x, 150, w, 54)
        b += IMG(ic, x + 8, 158, 15)
        b += T('chipb', x + 28, 156, t1, extra='' if on else ' color:#8E88A0;')
        b += T('chipt', x + 8, 174, t2, extra='' if on else ' color:#A29DB2;')
        b += T('tag ' + ('on' if on else 'off'), x + 8, 186, tg)
        x += w + strip.get('gap', 8)
    # 표
    cols = [(60 + 16, '단계'), (176, '일어나는 일'), (650, '모델과 절차'), (952, '논문 근거')]
    top = 210
    rh = 43
    b += f'  <div class="panel" style="left:60px; top:{top}px; width:1160px; height:{30 + rh * len(rows) + 6}px;"></div>\n'
    for cx, t in cols:
        b += T('th', cx, top + 9, t)
    y = top + 30
    for i, (st, what, how, ev) in enumerate(rows):
        b += f'  <div class="rule" style="left:76px; top:{y - 1}px; width:1128px;"></div>\n'
        b += T('st', cols[0][0], y + 5, st.replace('\n', '<br>'))
        b += T('tx', cols[1][0], y + 5, what.replace('\n', '<br>'))
        b += T('tx', cols[2][0], y + 5, how.replace('\n', '<br>'))
        b += T('tx', cols[3][0], y + 5, ev.replace('\n', '<br>'), extra=' color:#6A6474;')
        y += rh
    y += 12
    for ln in foot:
        b += T('note', 62, y, ln, extra=' font-size:12px; line-height:17px;')
        y += 18
    y += 4
    for ln in srcs:
        b += T('src', 62, y, ln)
        y += 15
    page(name, chip, title, sub, b, svg, notes)


def a4():
    strip = dict(w=157, items=[
        ('note', '11/3 준비 회의', '제품 소개 → 데모 → Q&amp;A', '이전 안', False),
        ('mail', '11/5 민수 메일', '기술전_시연자료_v1', '날짜로 탈락', False),
        ('note', '11/6 오류 목록', '라이브 데모 오류 정리', '뜻으로 탈락', False),
        ('note', '11/10 주간 회의', '문제 상황 → 데모 → 체험', '최신 결정', True),
        ('mail', '11/12 민수 메일', 'Demo_Final.pptx', '최종 파일', True),
        ('mail', '11/13 민수 메일', '리허설 회의실 예약', '뜻으로 탈락', False),
        ('cal', '11/19 캘린더', '오후 2시, 3번 부스', '일정', True)])
    rows = [
        ('01 순간 감지', '통화 화면에서 위로 밀고 \'삼성기술전 시연 최종\'을 직접 적습니다.\n통화 내용은 듣지 않습니다. 키보드가 없는 화면의 입구입니다.', '사용자 호출', '논문 없음(설계)'),
        ('① 한 번 찾기', '11/3 회의록과 v1 파일이 올라옵니다. 답처럼 보이지만 옛 내용입니다.\n이대로 보고하면 틀립니다.', 'BM25 + Reasoning Embedding', 'IRCoT (ACL 2023), BRIGHT (ICLR 2025)'),
        ('② 나누기', '1. 언제 어디서 하지?  2. 무엇을 어떤 순서로 하지?', 'sLLM 1~2B', 'Hi-Q (NeurIPS 2026), ReasonIR (COLM 2025)'),
        ('③ 1홉', '1번은 캘린더에서, 2번은 11/3 회의록에서 찾습니다.', 'Reasoning Embedding', 'ReasonIR, ReasonEmbed (ACL 2026)'),
        ('④ 잇기', '[그 순서]를 넣어 \'그 뒤에 바뀌었나?\'로 다시 쓰고 11/3 이후로 거릅니다.', '기록에서 복사, 날짜 필터\n(날짜 비교 = Numerical Reasoning)', 'Hi-Q, IRCoT, RIR Survey (ACL 2026)'),
        ('③ 2홉', '오류 목록 말고 11/10 주간 회의를 찾습니다.\n\'기술전\'도 \'시연\'도 없는 메모입니다.', 'Reasoning Embedding', 'LongMemEval (ICLR 2025)\nKnowledge Update'),
        ('④③ 3홉', '\'민수 님이 다시 정리\'로 다시 쓰고, 민수 메일 11/10 이후에서\n회의실 메일 말고 최종본을 찾습니다.', '보낸 사람과 날짜 필터 + Reasoning Embedding', 'DER-RAG, MDR (ICLR 2021)'),
        ('⑤ 요약', '날짜순으로 세워 마지막 결정을 세 줄로 요약하고 파일을 붙입니다.\n사용자는 요약을 읽어 주고, 파일은 직접 보냅니다.', 'sLLM, 이름과 날짜 복사 검사\n전송은 사용자', 'LongMemEval (시간순 제공, Chain-of-Note)\nHi-Q (NeurIPS 2026)'),
    ]
    foot = ['<b>순서는 임베딩이 맞추지 않습니다.</b> 임베딩이 같은 일의 기록을 찾고, 메타데이터 날짜가 앞뒤를 가리고, sLLM이 마지막 결정을 읽습니다. 시간을 고려하지 않는 설계는 시간 추론 질문에서 약하다는 보고가 있습니다(LongMemEval).',
            '이 조합 전체를 시험한 논문은 없습니다. 요약 속도는 입력 500토큰, 출력 100토큰 가정으로 Qwen3-1.7B 약 2.5초, 4B 약 4.9초입니다(S26 Snapdragon 공개 측정값으로 계산, 실측 전).']
    srcs = ['* 출처: Wu et al., "LongMemEval", ICLR 2025 · Kim et al., "Hi-Q", NeurIPS 2026 · Trivedi et al., "IRCoT", ACL 2023 · Su et al., "BRIGHT", ICLR 2025 · Shao et al., "ReasonIR", COLM 2025 · Wei et al., "RIR Survey", ACL 2026']
    notes = """Appendix · UX 1 상세. 통화 중 삼성기술전 시연을 묻는 장면의 전체 절차입니다. 인포그래픽에서는 나누기를 보여 주지 않았고, 실제로는 이 표처럼 동작합니다.
핵심은 한 번 검색이 옛 회의록을 답처럼 내놓는다는 점입니다. Weave는 계획이나 결정을 찾으면 그 날짜 이후를 한 번 더 찾습니다.
LongMemEval 인용: "Naive time-agnostic memory designs perform poorly on temporal reasoning questions". 시간 인식 색인과 질의 확장으로 시간 추론 문항의 recall이 평균 11.3%(라운드 단위), 6.8%(세션 단위) 올랐습니다. 읽기 전략이 나쁘면 완벽한 검색에서도 GPT-4o 기준 최대 10포인트 떨어진다는 결과도 있어서 기록을 날짜와 함께 구조화해 넘깁니다.
시연 내용과 장소는 시나리오용 예시입니다."""
    ux_page('page-a4', 'Appendix · UX 1 상세', 'UX 1 기록 통합 검색: 단계별 모델과 근거', '재웅 선배: "프로님, 지금 보고 드려야 하는데 우리 팀이 맡은 삼성기술전 시연 최종적으로 어떻게 됐죠?"', strip, rows, foot, srcs, notes)


def a5():
    strip = dict(w=184, items=[
        ('talk', '3/15 지은 카톡', '박스 정리 다 했어! 휴지 안 사 와도 돼', '날짜 단서', True),
        ('note', '3/14 집들이 선물', '디퓨저로 결정!', '와인 얘기 없음', False),
        ('gal', '3/10 스크린샷', '와인 고르는 법', '일반 정보 글', False),
        ('gal', '3/15 19:52 사진', '식탁 사진', '뜻으로 탈락', False),
        ('gal', '3/15 20:14 사진', 'BABICH SAUVIGNON BLANC', '답', True),
        ('gal', '3/20 21:10 사진', '와인바, 다른 와인', '날짜로 탈락', False)])
    rows = [
        ('00 사전 준비', '카톡 글자와 사진을 벡터, 키워드, { date, app }로 저장합니다.', 'Reasoning Embedding, BM25, OCR', 'LongMemEval (ICLR 2025): 타임스탬프 색인'),
        ('01 순간 감지', '구글 창에 \'지은이네 집들이 때 마셨던 와인\'을 적고 실타래 버튼을 누릅니다.', '사용자 호출', '논문 없음(설계)'),
        ('① 한 번 찾기', '선물 메모, 와인 고르는 법, 3/20 와인바 사진이 올라옵니다.', 'BM25 + Reasoning Embedding', 'IRCoT (ACL 2023), BRIGHT (ICLR 2025)'),
        ('② 나누기', '1. 지은이네 집들이는 언제였지?  2. [그날] 마셨던 와인은?', 'sLLM 1~2B', 'Hi-Q (NeurIPS 2026), ReasonIR (COLM 2025)'),
        ('③ 1홉', '지은이 보낸 기록 중에서 \'휴지 안 사 와도 돼. 몸만 와\'를 집들이 초대로 찾습니다.', '보낸 사람 필터 + Reasoning Embedding\n(개방형 영역, World Knowledge)', 'ImpliRet (EMNLP 2025), RIR Survey (ACL 2026)'),
        ('④ 잇기', '[그날 → 3/15 (일)]. 카톡에 저장된 날짜를 그대로 씁니다.', '메타데이터 복사, 날짜 필터', 'Hi-Q, LongMemEval'),
        ('③ 2홉', '그날 사진 둘 중 식탁 사진 말고 와인 사진을 찾고 라벨을 읽습니다.', 'Reasoning Embedding + OCR', 'DocHop-QA (EMNLP 2026): 글 + 이미지'),
        ('⑤ 전달', '배비치 소비뇽 블랑을 출처와 함께 건넵니다. 입력은 사용자가 합니다.', 'sLLM, 이름 복사 검사', 'Hi-Q'),
    ]
    foot = ['<b>왜 이 장면이 멀티홉인가요?</b> 질문에 없는 날짜를 먼저 찾아야 사진을 고를 수 있습니다. 첫 단계를 모르면 둘째 근거는 질문과 단어도 뜻도 겹치지 않아 찾기 어렵다는 지적이 있습니다(IRCoT).',
            '<b>넘어가는 단서가 날짜입니다.</b> 이번 단서는 날짜지만, 별칭이나 맡은 일 같은 내용도 같은 방식으로 잇습니다(UX 1, UX 3).']
    srcs = ['* 출처: Trivedi et al., "IRCoT", ACL 2023 · Kim et al., "Hi-Q", NeurIPS 2026 · Taghavi et al., "ImpliRet", EMNLP 2025 · Wei et al., "RIR Survey", ACL 2026 · Wu et al., "LongMemEval", ICLR 2025 · Park et al., "DocHop-QA", EMNLP 2026']
    notes = """Appendix · UX 2 상세. How it Works에서 본 와인 장면의 모델과 근거입니다.
DocHop-QA 표 7(Qwen3-VL-8B, BLEU)에서 글과 이미지를 함께 줄 때 29.7, OCR 글자만 26.0, 이미지만 18.2입니다. 위키가 아니라 PubMed 데이터이고 Weave 성능이 아닙니다.
예상 질문: 지은 카톡을 보낸 사람으로 바로 찾으면 되지 않나요? 지은의 카톡은 많고 집들이라는 말이 없습니다. 보낸 사람은 후보를 줄이는 거름망이고, 초대를 알아보는 일은 임베딩이 맡습니다."""
    ux_page('page-a5', 'Appendix · UX 2 상세', 'UX 2 단서로 찾는 기억: 단계별 모델과 근거', '구글 검색창: "지은이네 집들이 때 마셨던 와인"', strip, rows, foot, srcs, notes)


def a6():
    strip = dict(w=184, items=[
        ('map', '현재 위치', '인천공항', '지금 상황', True),
        ('wal', '삼성 월렛 탑승권', '싱가포르 → 인천, 오늘 도착', '귀국 중', True),
        ('note', '10/31 면세점 살 것', '선크림, 립밤', '내 쇼핑 목록', False),
        ('talk', '10/14 아내 카톡', '동생이 이 갈색병 좋대. 면세점에서', '숨은 부탁', True),
        ('gal', '10/14 저장한 사진', '아내가 보낸 병 사진', '답', True),
        ('gal', '10/14 스크린샷', '면세점 화장품 쿠폰', '뜻으로 탈락', False)])
    rows = [
        ('00 사전 준비', '알림의 글자, 갤러리 사진, 월렛 탑승권을 벡터와 메타데이터로 저장합니다.', 'Reasoning Embedding, BM25, 이미지 임베딩', 'DocHop-QA (EMNLP 2026)'),
        ('01 순간 감지', '아내와 카톡 중, 위치와 탑승권이 귀국을 가리키면 실타래 버튼이 반짝입니다.\n세 신호가 맞을 때만 반짝이고, 누르지 않으면 아무것도 입력되지 않습니다.', '규칙 판단 (위치 + 탑승권 + 대화 상대)\n통화와 녹음은 쓰지 않음', '논문 없음(설계)\n삼성 S26 Now Brief의 월렛 회상이 선례'),
        ('첫 질문', '\'면세점에서 아내에게 사 갈 것은?\'을 Weave가 스스로 만듭니다.', '상황별 틀 + sLLM', '논문 없음(설계)'),
        ('② 나누기', '1. 아내가 면세점에서 사 오길 바란 건?  2. [그것]의 사진은?', 'sLLM 1~2B', 'Hi-Q (NeurIPS 2026)'),
        ('③ 1홉', '보낸 사람이 아내인 기록에서 \'이 갈색병 좋대. 면세점에서 판다더라\'를 찾습니다.\n직접 부탁하지 않은 말에서 숨은 부탁을 읽습니다.', '보낸 사람 필터 + Reasoning Embedding\n(개방형 영역: 숨은 의도)', 'RIR Survey (ACL 2026), BESPOKE, ImpliRet'),
        ('④ 잇기', '[그것 → 이 갈색병], 같은 날 저장한 사진으로 좁힙니다.', '기록에서 복사, 날짜 필터', 'Hi-Q, IRCoT (ACL 2023)'),
        ('③ 2홉', '쿠폰 캡처 말고 병 사진을 찾습니다. 라벨을 읽지 않아도 사진을 건넬 수 있습니다.', '멀티모달 임베딩', 'DocHop-QA: 글 + 이미지'),
        ('⑤ 전달', '아내 말투 그대로 보낼 말을 추천하고, 연결된 기억에 사진을 함께 둡니다.', 'sLLM, 입력과 전송은 사용자', 'Hi-Q'),
    ]
    foot = ['<b>UX 2와 다른 점:</b> UX 2는 라벨 글자를 읽어 정확한 이름을 찾고, UX 3은 지금 상황과 3주 전 부탁을 잇습니다. 강점은 찾기보다 묻기 전에 건네는 순간 감지입니다.',
            '<b>기록 범위:</b> 카카오톡 알림에서는 글자만 읽습니다. 사진은 갤러리에 저장한 경우에 읽습니다. 위치만으로는 출국, 입국, 마중을 가릴 수 없어서 탑승권을 함께 봅니다.']
    srcs = ['* 출처: Wei et al., "RIR Survey", ACL 2026 · Taghavi et al., "ImpliRet", EMNLP 2025 · Kim et al., "BESPOKE", 2025 · Kim et al., "Hi-Q", NeurIPS 2026',
            '   Park et al., "DocHop-QA", EMNLP 2026 · Samsung Newsroom, "Galaxy S26 Series" (2026. 02)']
    notes = """Appendix · UX 3 상세. 출장에서 돌아와 인천공항에 내린 순간의 절차입니다. 아내와 메시지 세 개를 주고받은 뒤 실타래 버튼이 반짝입니다.
삼성 S26 발표 각주: Now Brief의 회상 데이터는 지원 앱 알림, 메시지, Gmail, Samsung Wallet에서 옵니다. 그래서 월렛을 상황 신호로 쓰는 것은 자연스러운 확장입니다. Weave는 예약 정보만이 아니라 예약이 아닌 대화 속 부탁까지 잇습니다.
삼성월렛 공식 안내: 탑승권 알림은 탑승 3시간 전부터 도착 1시간 뒤까지 뜨고, QR은 도착 24시간 뒤 비활성화됩니다. 입국 순간에도 유효합니다.
입국장 면세점 입점은 2019년 개장 기사(SM면세점 에스티로더) 기준이라 지금은 확인하지 못했습니다. 그래서 보낼 말은 입점을 단정하지 않습니다.
예상 질문: Now Nudge와 무엇이 다른가요? Now Nudge는 화면 맥락에 따라 제안합니다. 여기서 화면에 보이는 말은 '조심히 들어와'뿐이고, 3주 전 아내 카톡과 사진을 이어야 무엇을 살지 알 수 있습니다."""
    ux_page('page-a6', 'Appendix · UX 3 상세', 'UX 3 먼저 건네는 기억: 단계별 모델과 근거', '아내 "출장 고생했어! 한국 도착했어?" → 나 "응, 방금 내렸어" → 아내 "그래, 조심히 들어와~" → 실타래 버튼이 반짝', strip, rows, foot, srcs, notes)


def a7():
    b = ''
    cols = [(76, '방식'), (236, '무엇으로 찾나'), (436, '잘하는 것'), (640, "'지은이네 집들이 때 마셨던 와인'에서 막히는 곳"), (1000, '미리 해 둘 일')]
    rows = [
        ('키워드 검색 (BM25)', '같은 단어', '이름, 숫자, 파일명', "'집들이'가 없는 초대 카톡, '집들이'가 없는 와인 사진", '단어 색인'),
        ('일반 임베딩', '가까운 뜻', '표현이 다른 같은 내용', '1위에 오른 다른 날 와인 사진', '기록 벡터'),
        ('하이브리드', '두 순위를 합친 한 번 검색', '두 방식의 장점', '처음 질문에 없는 집들이 날짜', '단어 색인과 벡터'),
        ('지식 그래프 (PDE 방식)', '미리 뽑아 둔 관계', '정해 둔 관계의 여러 단계 연결', "그래프에 없는 '휴지 안 사 와도 돼 = 집들이'", '기록의 관계 추출'),
        ('Finder, Now Nudge', '앱별 자연어 검색, 화면 맥락 제안', '앱 안의 사진과 메모, 화면 속 요청', '카톡 초대와 그날 사진을 잇는 단계', '앱별 색인'),
        ('Weave', '찾은 단서로 다시 쓴 질문', '단어가 다르고 단계가 빠진 질문', '막히지 않고 배비치 소비뇽 블랑까지', '기록 벡터와 메타데이터'),
    ]
    top, rh = 150, 54
    b += f'  <div class="panel" style="left:60px; top:{top}px; width:1160px; height:{32 + rh * len(rows) + 6}px;"></div>\n'
    for x, t in cols:
        b += T('th', x, top + 10, t)
    y = top + 32
    for i, r in enumerate(rows):
        me = r[0] == 'Weave'
        if me:
            b += f'  <div class="box ll" style="left:66px; top:{y + 2}px; width:1148px; height:{rh - 4}px;"></div>\n'
        else:
            b += f'  <div class="rule" style="left:76px; top:{y - 1}px; width:1128px;"></div>\n'
        b += T('st', cols[0][0], y + 18, r[0], extra=' color:#6B4EFF;' if me else '')
        for j in range(1, 5):
            b += T('tx', cols[j][0], y + 18, ('<b>%s</b>' % r[j]) if me else r[j])
        y += rh
    y += 14
    b += T('note', 62, y, '<b>기존 방식을 대체하지 않습니다.</b> Weave도 BM25와 임베딩, 메타데이터를 함께 쓰고, 날짜와 사람처럼 같은 값으로 잇는 일은 메타데이터와 PDE가 잘합니다. Weave는 기록 내용 속의 연결을 질문할 때 잇습니다.')
    y += 22
    b += T('note', 62, y, '<b>지식 그래프:</b> 여러 단계 연결은 오히려 강점입니다. 막히는 곳은 그래프에 없는 사실입니다. PDE의 내부 구조는 공개되지 않아, 여기서는 지식 그래프 방식의 일반 특성으로 설명합니다.')
    y += 22
    b += T('note', 62, y, '<b>Finder:</b> One UI 8.5부터 자연어 검색을 지원합니다. 공식 대상은 음성 녹음, 통화 녹음, 캘린더, 노트, 리마인더, 내 파일입니다. 여기 적은 내용은 공개 자료 기준입니다.')
    y += 30
    b += T('src', 62, y, '* 출처: Robertson & Zaragoza, "BM25 and Beyond", 2009 · Karpukhin et al., "DPR", EMNLP 2020 · Cormack et al., "Reciprocal Rank Fusion", SIGIR 2009 · Oxford Semantic Technologies, RDFox 문서')
    b += T('src', 62, y + 15, '   삼성전자 뉴스룸, "[갤럭시 언팩 2025] ①" (2025. 01) · Samsung 지원, "Understanding Finder on Galaxy phones" · Samsung Newsroom, "Galaxy S26 Series" (2026. 02)')
    notes = """Appendix · 비교. 같은 와인 질문을 방식마다 어디까지 찾는지 비교한 표입니다. 각 방식이 잘하는 것부터 말하고, 이 질문에서 막히는 곳을 말합니다.
쓰지 말아야 할 말: "PDE는 못 한다", "Finder는 키워드 검색이다", "여러 단계 개인 검색은 아무도 못 한다". Apple Siri AI도 메시지에서 이메일로 이어지는 공식 예시가 있습니다.
Weave의 차별점은 온디바이스에서 미리 정한 항목 없이 원문 기록을 이어 가는 추론 검색입니다."""
    page('page-a7', 'Appendix · 비교', '기존 검색, 삼성 기술과 무엇이 다른가요?', '같은 질문을 방식마다 어디까지 찾는지 비교했습니다.', b, '', notes)


if __name__ == '__main__':
    a1(); a2(); a3(); a4(); a5(); a6(); a7()
    print('ok')
