# 마무리 세 장(39~41쪽)에 쓸 사진 후보

65장이에요. 1차 26장(A~C)은 Unsplash, 2차 39장(D~F)은 Pexels와 Unsplash에서 받았어요.
Unsplash 라이선스와 Pexels 라이선스 모두 무료로 쓰고 고칠 수 있고 출처 표기 의무가 없어요.
16:9로 자르고 1920×1080으로 줄였어요. 덱의 39~41쪽은 아직 바꾸지 않았어요.

| | 주제 | 한눈에 | 39~41쪽에 대 본 모습 |
|---|---|---|---|
| 1차 (A~C) | 일상의 행복한 순간 | `후보_한눈에.jpg` | `시안_한눈에.jpg` |
| 2차 (D~F) | 연인이나 친구끼리 찍어 주는 모습, 셀카를 찍는 모습 | `후보2_한눈에.jpg` | `시안2_한눈에.jpg` |

- 다시 찍기: `python tools/closing_try.py` (2차만은 `--round 2`, 조합은 그 파일의 `TRIES1`, `TRIES2`)
- 덱에 넣을 때: `slides_new.py`의 `s_end1(photo=…)`, `s_end2(photo=…, hand=…)`, `s_end3(photo=…)`

39쪽과 41쪽은 글이 화면 한가운데에 놓여서, 가운데가 비었거나 사람이 실루엣인 사진이 맞아요(C 묶음, A5, D10, D12, E11, E12, F12, F13).
40쪽은 손글씨 '순간'만 있어서 어느 사진이든 놓을 수 있어요.

# 2차: 찍어 주는 모습과 셀카

## D. 찍어 주는 모습 (연인, 친구)

| 코드 | 장면 | 휴대폰 | 찍은 사람 | 원본 |
|---|---|---|---|---|
| D1 | 강가에서 연인을 찍어 주는 남자 (미국 뉴욕) | 화면이 보임, 기종 모름 | Samson Katt | https://www.pexels.com/photo/5225075/ |
| D2 | 산길에서 두 사람을 찍어 주는 친구 | 분홍 케이스, 작게 보임(크게 키우면 화면 위에 노치가 보임) | Gotta Be Worth It | https://www.pexels.com/photo/18528781/ |
| D3 | 물가에서 걸어오는 친구를 찍어 주는 순간 | 작게 보임 | PNW Production | https://www.pexels.com/photo/9353804/ |
| D4 | 바닷가 산책길에서 휠체어에 앉아 친구를 찍어 주는 사람 (포르투갈) | 뒷면, 기종 모름 | Kampus Production | https://www.pexels.com/photo/8777856/ |
| D5 | 다리 위에서 웃는 세 친구를 찍어 주는 사람 | 뒷면, 기종 모름 | Edmond Dantès | https://www.pexels.com/photo/8556341/ |
| D6 | 호숫가 모래밭에 선 친구들을 찍어 주는 사람 | 작게 보임 | Thirdman | https://www.pexels.com/photo/8021265/ |
| D7 | 거리에서 웃는 친구를 찍어 주는 순간. 화면에 찍히는 모습이 보임 | 기종 모름 | Marcus Aurelius | https://www.pexels.com/photo/9789383/ |
| D8 | 바위 해변을 걷는 여자를 찍어 주는 사람 | 뒷면(흐림), 기종 모름 | Yan Krukau | https://www.pexels.com/photo/7312022/ |
| D9 | 해변에서 여자를 찍어 주는 어르신 (포르투갈) | 빨간 케이스, 화면이 보임, 기종 모름 | Kampus Production | https://www.pexels.com/photo/7233006/ |
| D10 | 해 진 바다를 함께 찍는 두 사람의 뒷모습 (튀르키예 이스탄불) | 화면이 보임, 기종 모름 | fatmanur imanci | https://www.pexels.com/photo/7908554/ |
| D11 | 분홍빛 노을을 찍는 두 친구 | 뒷면, 기종 모름 | Lalu Fatoni | https://www.pexels.com/photo/773147/ |
| D12 | 노을 진 전망대에서 한 사람이 다른 사람을 찍어 주는 모습 (튀르키예 이스탄불) | 작게 보임 | Zeynep Sude Emek | https://www.pexels.com/photo/34962473/ |

## E. 연인의 셀카

| 코드 | 장면 | 휴대폰 | 찍은 사람 | 원본 |
|---|---|---|---|---|
| E1 | 볼을 맞대고 찍는 셀카 | 뒷면이 갤럭시 S10 계열(카메라 셋이 가로로) | Budgeron Bach | https://www.pexels.com/photo/6532804/ |
| E2 | 도심에서 팔을 뻗어 찍는 셀카 | 뒷면, 기종 모름 | Samson Katt | https://www.pexels.com/photo/5225440/ |
| E3 | 나무 사이 햇살 속에서 찍는 셀카 | 작게 보임 | Andrea Piacquadio | https://www.pexels.com/photo/3777884/ |
| E4 | 호숫가에서 해를 등지고 찍는 셀카 | 보이지 않음 | Ryland zweifel | https://www.pexels.com/photo/7071778/ |
| E5 | 강가 다리 위에서 찍는 셀카 (프랑스 파리) | 뒷면, 기종 모름 | Bethany Ferr | https://www.pexels.com/photo/5177141/ |
| E6 | 해 질 녘 발코니에서 찍는 셀카 | 보이지 않음 | Max Bvp | https://unsplash.com/photos/bwQMC8txi1Q |
| E7 | 일본 전통 옷을 입은 두 사람의 셀카 | 뒷면, 기종 모름 | Bruno Aguirre | https://unsplash.com/photos/zDpKTjg4w_U |
| E8 | 푸른 들판에서 찍는 셀카 | 뒷면, 작게 보임 | Md Ekbal Bapari | https://www.pexels.com/photo/20039590/ |
| E9 | 배가 떠 있는 강가에서 찍는 셀카 | 뒷면, 작게 보임 | Sourov sarker | https://www.pexels.com/photo/36251502/ |
| E10 | 노을 진 해변에 앉아 찍는 셀카 (알바니아 블로러) | 작게 보임 | Sabina Kallari | https://www.pexels.com/photo/28456105/ |
| E11 | 노을 속 배 위에서 찍는 셀카 (실루엣) | 실루엣 | Sami TÜRK | https://www.pexels.com/photo/30043600/ |
| E12 | 큰 노을 앞에서 찍는 셀카 (작은 실루엣) | 실루엣 | Piotrek Wilk | https://www.pexels.com/photo/9933827/ |

## F. 친구들의 셀카

| 코드 | 장면 | 휴대폰 | 찍은 사람 | 원본 |
|---|---|---|---|---|
| F1 | 웃으며 셀카를 찍는 세 친구 | 옆면만 보임 | Ketut Subiyanto | https://www.pexels.com/photo/4350314/ |
| F2 | 흐린 하늘 아래 두 친구의 셀카 | 뒷면에 카메라 셋이 세로로, 기종 모름 | PNW Production | https://www.pexels.com/photo/7625138/ |
| F3 | 히잡을 쓴 두 친구가 웃는 모습 | 왼쪽 끝의 휴대폰은 잘라 냄 | Bwalya Marcel Ngosa | https://www.pexels.com/photo/21822267/ |
| F4 | 히잡을 쓴 세 친구의 셀카 | 뒷면(흐림), 기종 모름 | RDNE Stock project | https://www.pexels.com/photo/4911252/ |
| F5 | 할머니들과 셀카를 찍는 여자 (인도네시아 서자바) | 작게 보임 | Andreas Suwardy | https://www.pexels.com/photo/40672256/ |
| F6 | 손을 흔들며 웃는 세 친구의 셀카 | 보이지 않음 | ANTONI SHKRABA production | https://www.pexels.com/photo/8910365/ |
| F7 | 전통 옷을 입은 세 친구의 셀카 | 작게 보임 | The Chongaiman Ace | https://www.pexels.com/photo/37786290/ |
| F8 | 홀리 축제에서 셀카를 찍는 두 사람 (인도 푸시카르) | 주황 케이스, 기종 모름 | Kerry Bian | https://www.pexels.com/photo/4937284/ |
| F9 | 가을 공원에서 팔을 높이 들어 찍는 두 친구 | 옆면만 보임 | Julio Lopez | https://www.pexels.com/photo/29763537/ |
| F10 | 산을 배경으로 셀카를 찍는 두 친구 | 작게 보임 | Nasir Javed | https://www.pexels.com/photo/13014445/ |
| F11 | 눈 오는 날 네 친구의 셀카 | 작게 보임 | fauxels | https://www.pexels.com/photo/3228731/ |
| F12 | 해 질 녘 산에서 셀카를 찍는 친구들의 뒷모습 | 작게 보임 | Helena Lopes | https://www.pexels.com/photo/4453154/ |
| F13 | 노을 앞에서 셀카봉을 든 두 친구 (실루엣, 인도) | 실루엣 | India Uttarakhand | https://www.pexels.com/photo/11554046/ |
| F14 | 옥상에서 셀카를 찍는 두 친구 (포르투갈) | 뒷면, 기종 모름 | Kampus Production | https://www.pexels.com/photo/6760907/ |
| F15 | 기차역에서 셀카를 찍는 두 여행자 | 작게 보임 | Ketut Subiyanto | https://www.pexels.com/photo/4901973/ |

# 1차: 일상의 행복한 순간

## A. 찍어 주는 순간

| 코드 | 장면 | 휴대폰 | 찍은 사람 | 원본 |
|---|---|---|---|---|
| A1 | 바닷가에서 여자를 찍어 주는 남자. 휴대폰 화면에 찍히는 모습이 보임 | 기종 모름 | Chermiti Mohamed | https://unsplash.com/photos/pUsDkxoSyls |
| A2 | 노을 지는 들판에서 휴대폰으로 사람을 찍는 모습 | 앞면에 SAMSUNG 글자가 보임 | Stefan Maass | https://unsplash.com/photos/zu68hhvQM2M |
| A3 | 돌아보며 웃는 친구를 찍어 주는 순간, 금빛 역광 | 기종 모름 | Olga Nayda | https://unsplash.com/photos/8-o97EJ3eWg |
| A4 | 분홍빛 바닷가에서 여자를 찍어 주는 남자 (크로아티아 자다르) | 작게 보임 | Partha Narasimhan | https://unsplash.com/photos/kta4cdLtNF8 |
| A5 | 붉은 노을 앞에서 한 사람이 다른 사람을 찍는 실루엣 | 작게 보임 | Tat Linh Nguyen | https://unsplash.com/photos/XIHTICJc6Q8 |
| A6 | 노을 아래 휴대폰을 들어 올린 아이들 (캄보디아) | 작게 보임 | Chheun Ly | https://unsplash.com/photos/BFXq6k6y0Rw |
| A7 | 팔로 하트를 만든 두 사람과 그 모습을 찍는 사람 | 카메라 | Derek Lee | https://unsplash.com/photos/WX80LrTECKU |
| A8 | 언덕에서 노을을 찍는 친구들 | 작게 보임 | Bambi Corro | https://unsplash.com/photos/o3lefLTghaM |

## B. 얼굴이 보이는 행복한 순간

| 코드 | 장면 | 휴대폰 | 찍은 사람 | 원본 |
|---|---|---|---|---|
| B1 | 휴대폰을 보며 웃는 두 어르신 (탄자니아 다르에스살람) | 기종 모름 | Ali Mkumbwa | https://unsplash.com/photos/YJCU26w-iaA |
| B2 | 잔디에 누워 웃는 두 친구 | 뒷면이 갤럭시 A 계열로 보임(글자는 읽히지 않음) | Muhamad Iqbal Akbar | https://unsplash.com/photos/JlOm3kz6S1I |
| B3 | 역광 속에서 웃는 두 친구 (호주 멜버른) | 없음 | Khiem Nguyen | https://unsplash.com/photos/yOqKUlVnPiY |
| B4 | 셀카를 찍는 두 친구 (태그로는 네팔 카트만두) | 뒷면이 갤럭시 S8 계열 | v2osk | https://unsplash.com/photos/-7aCbFKRj28 |
| B5 | 할머니들과 휴대폰을 함께 보는 사람 | 뒷면이 갤럭시 S8 계열 | Valentin Lacoste | https://unsplash.com/photos/wyNeEBQWKMc |
| B6 | 노을 앞에서 손으로 하트를 만드는 친구들 | 없음 | Noorulabdeen Ahmad | https://unsplash.com/photos/MW_2Osq-yIE |
| B7 | 머리를 맞대고 웃는 두 사람 | 없음 | Cord Allman | https://unsplash.com/photos/tYbv4T2B4q0 |
| B8 | 해 질 녘 길가에 앉은 세 사람 | 없음 | Sipho Ngondo | https://unsplash.com/photos/wUtpte0kyVU |

## C. 해 질 녘의 가족과 친구

| 코드 | 장면 | 찍은 사람 | 원본 |
|---|---|---|---|
| C1 | 금빛 해변을 걷는 가족 | Merve Kalafat Yılmaz | https://unsplash.com/photos/dc8Yoc2lDTA |
| C2 | 물가를 걷는 아빠와 아이, 아기를 안은 엄마 | Galih Jelih | https://unsplash.com/photos/p6gB5tEc1dA |
| C3 | 노을 앞에서 함께 뛰어오르는 사람들 (멕시코 부세리아스) | Ty Downs | https://unsplash.com/photos/R4yH3gu7JFs |
| C4 | 해변에서 춤추는 두 사람 (미국 말리부) | Nathan Dumlao | https://unsplash.com/photos/rV9fZwhE1ak |
| C5 | 노을을 바라보는 사람들 (미국 블레인) | Herry Sutanto | https://unsplash.com/photos/dXtE8EA75Ko |
| C6 | 노을 아래 춤추는 두 사람 | Borcila Dorinel photography | https://unsplash.com/photos/sJczsYJD6i8 |
| C7 | 광안리 바닷가의 두 사람 (부산) | Luke Ow | https://unsplash.com/photos/lWHMPZLwfAU |
| C8 | 손을 잡고 선 사람들 (멕시코 부세리아스) | Ty Downs | https://unsplash.com/photos/P4InE2tswBs |
| C9 | 노을 진 해변을 걷는 네 사람 | Ashley Hunt | https://unsplash.com/photos/85bH6ORfRjM |
| C10 | 바닷가에 선 여자와 아이 (태그로는 미국 샌디에이고) | Christopher Ruel | https://unsplash.com/photos/7ReknBtEp8E |

# 고른 방법

- 1차: Unsplash에서 서른한 가지 검색어로 사진 469장을 모아 미리보기로 보고 골랐어요.
- 2차: Pexels 서른세 가지, Unsplash 열여섯 가지 검색어로 찾은 사진 가운데 주제에 맞는 290여 장을 미리보기로 보고 골랐어요. 1차에서 본 Unsplash 사진은 뺐어요.
- 술이 보이는 사진, 실내 사진, 카메라로 찍는 사진은 뺐어요.
- 휴대폰은 크게 키워서 봤어요. 아이폰의 카메라 화면이나 뒷면 카메라가 뚜렷한 사진은 뺐어요.
- 찍은 사람과 라이선스는 사진마다 원본 쪽에서 확인했어요. Unsplash 28장은 "Free to use under the Unsplash License", Pexels 37장은 "Free"로 적혀 있어요.
