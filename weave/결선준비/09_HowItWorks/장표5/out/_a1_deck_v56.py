"""A1 덱용 — 결선 중간본의 How it Works. A1에서 결과 화면(검색어가 정확한 이름으로) 한 장만 뺌.

솔루션 장표와 표지 영상이 화면 경험을 이미 보여 주므로, 여기서는
질문 → 흩어진 기록 → 키워드·임베딩 실패 → 실타래 버튼 → 질문 다시 쓰기 → 연쇄 탐색 → 전달 → 정리까지 13장.
"""
import copy

from a1 import SPEC as _A1

SPEC = copy.deepcopy(_A1)
SPEC['file'] = 'A1_덱용_집들이와인'
SPEC['skip'] = ['result']
