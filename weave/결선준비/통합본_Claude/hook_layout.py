"""6쪽(수많은 기록)의 휴대폰 벽: 어느 자리에 어느 앱 화면이 놓이는지. slides_new.py(불이 켜지는 화면)와 tools/hook_assets.py(어두운 벽 그림)가 함께 쓴다.

좌표는 1280×720 px. 짝수 열은 가운데 줄이 화면 한가운데에 오고, 홀수 열은 반 칸 내려와 벽돌처럼 어긋난다.
한가운데 칸은 '검색 결과가 없습니다' 화면(큰 화면이 줄어들어 놓이는 자리)이라 불이 켜지지 않는다.
불은 앱마다 두 화면에만 켜진다(LIT). 클릭할 때마다 그 앱의 두 화면이 켜지고 앞 앱의 화면은 꺼진다.
"""
PW, PH = 124, 268                 # 휴대폰 한 대(360×780 화면)
GAP = 16
RADIUS = 14
APPS = ['talk', 'gallery', 'note', 'cal', 'mail']       # 불이 켜지는 차례("카톡 대화, 사진, 메모, 일정, 메일까지")
# (열, 줄): (앱, 화면 이름). 줄은 짝수 열에서 -1 위, 0 가운데, 1 아래 / 홀수 열에서 -1 위, 0 아래. 같은 앱이 이웃하지 않게 놓음
CELLS = {
    (0, -1): ('talk', 'talk4'), (0, 0): ('gallery', 'gal1'), (0, 1): ('cal', 'cal1'),
    (1, -1): ('note', 'note1'), (1, 0): ('mail', 'mail1'),
    (2, -1): ('cal', 'cal3'), (2, 0): ('talk', 'talk1'), (2, 1): ('gallery', 'gal3'),
    (3, -1): ('mail', 'mail2'), (3, 0): ('note', 'note2'),
    (4, -1): ('gallery', 'gal2'), (4, 0): (None, 'find'), (4, 1): ('talk', 'talk4'),
    (5, -1): ('cal', 'cal2'), (5, 0): ('gallery', 'gal4'),
    (6, -1): ('talk', 'talk3'), (6, 0): ('mail', 'mail3'), (6, 1): ('note', 'note3'),
    (7, -1): ('gallery', 'gal1'), (7, 0): ('cal', 'cal1'),
    (8, -1): ('note', 'note1'), (8, 0): ('talk', 'talk2'), (8, 1): ('mail', 'mail1'),
}
# 불이 켜지는 칸: 앱마다 두 곳, 온전히 보이는 칸에서 서로 떨어진 자리로
LIT = {'talk': [(2, 0), (8, 0)], 'gallery': [(5, 0), (0, 0)], 'note': [(1, -1), (3, 0)], 'cal': [(5, -1), (7, 0)], 'mail': [(3, -1), (6, 0)]}
# 홀수 열의 위아래 끝에 조금만 보이는 화면(불은 켜지지 않음)
EDGE = {(1, -2): 'cal2', (1, 1): 'talk2', (3, -2): 'gal4', (3, 1): 'cal3', (5, -2): 'note2', (5, 1): 'mail2', (7, -2): 'mail3', (7, 1): 'gal2'}


def pos(c, r):
    """칸 (c, r)의 왼쪽 위 자리(px)."""
    x = 640 + (c - 4) * (PW + GAP) - PW / 2
    y = 360 - PH / 2 + r * (PH + GAP) + ((PH + GAP) / 2 if c % 2 else 0)
    return x, y


def lit():
    """불이 켜지는 화면: [(앱, 화면 이름, x, y)] — 앱 차례대로(LIT)."""
    out = []
    for app in APPS:
        for c, r in LIT[app]:
            assert CELLS[c, r][0] == app, (app, c, r)
            out.append((app, CELLS[c, r][1], *pos(c, r)))
    return out
