"""A1 덱용 00판 — 결선 How it Works (시나리오 중심 자연스러운 12장 흐름).

흐름:
1. open    : 질문의 순간 ("지은이네 집들이 때 마셨던 와인")
2. cloud   : 내 폰 속 여러 앱에 흩어진 단서들
3. fail    : 기존 단일 검색(BM25 키워드 / 단순 1-hop 임베딩)의 실패
4. step    : 패러다임 전환 — 실패 화면이 흐려지며 "Let's think step by step!" 등장
5. hybrid  : Weave의 핵심 해법 (문맥 추론 · 멀티홉 · 메타데이터 필터)
6. idx2    : 온디바이스 하이브리드 색인 구조 (원문 · 임베딩 벡터 · 메타데이터 분리 저장)
7. trig    : 01 맥락 감지 — 키보드 위 실타래 버튼 탭
8. split   : 02 질의 분해·재작성 — 하위 질문 2개로 분해
9. hop1    : 03 연쇄 탐색 (Hop 1) — 대화 문맥 추론으로 집들이 날짜(3/15) 획득
10. hop2   : 03 연쇄 탐색 (Hop 2) — 날짜 반영 재질의 + 메타데이터 필터 + 라벨 OCR
11. sum    : 03 연쇄 탐색 완료 — 2-Hop 추론 파이프라인 조감도 (100% 온디바이스 처리)
12. deliver: 04 정답 전달 — 근거 기록과 함께 제시 후 탭 한 번으로 검색창에 즉시 입력
"""
import copy

from a1_deck import SPEC as _D
from story import INK, PURPLE

SPEC = copy.deepcopy(_D)
SPEC['file'] = 'A1_덱용_집들이와인_00판'
SPEC['n_cloud'] = 18
SPEC['cloud_box'] = (430, 230, 1420, 500)
SPEC['index'] = dict(
    key='invite',
    entry_title='온디바이스 색인 구조 (Hybrid Index)',
    text='박스 정리 다 했어! 이따 올 때 휴지 안 사 와도 돼',
    pt_key=12.5,
    pt_fill=9.5,
    after_hybrid=True,
)
CP, NT = SPEC['cap'], SPEC['notes']
CP['idx2'] = dict(t=[('이를 위해 의미는 임베딩 벡터로,\n', INK), ('날짜와 앱은 메타데이터로 분리해 색인합니다', PURPLE)])
NT['idx2'] = ('이처럼 문맥 추론과 정확한 날짜 필터링이 동시에 가능한 이유는, Weave가 평소 기기 안에서 기록을 색인하는 방식에 있습니다. '
              '지은이가 보낸 카톡을 저장할 때 원문과 함께, (클릭) 문맥의 의미는 임베딩 벡터로 변환하고, '
              '(클릭) 수신 날짜와 출처 앱은 메타데이터로 분리해 구조화해 둡니다. '
              '이 색인 작업은 충전 중이나 유휴 시간에 기기 안에서 미리 수행됩니다.')
NT['deliver'] = NT['deliver'] + ' 동일한 파이프라인이 통화 중에는 실시간 브리핑으로, 메신저에서는 답장 추천으로 동작합니다.'
