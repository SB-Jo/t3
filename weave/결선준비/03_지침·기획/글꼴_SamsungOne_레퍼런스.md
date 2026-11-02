# 글꼴 레퍼런스: SamsungOne 패밀리 (Weave Assist 결선 덱)

작성 2026-11-02. 공개 웹 자료만 조사했고 사내 포털 위치는 추측하지 않았다.

표기
- [확인] 원문(페이지, PDF, CSS, 사진)을 직접 열어 확인
- [제3자] 공식이 아닌 출처에서만 확인
- [미검증] 원문 접근 실패 또는 근거 부족
- [추론] 확인된 사실에서 끌어낸 판단. 실기 확인 필요
- [제안] 이 문서의 권고

---

## 0. 한눈에

1. **SamsungOne**은 2016-07-22에 발표된 삼성 브랜드 서체다. Samsung이 디자인 회사 Brody Associates와 함께 만들었고, 26개 표기 체계와 400개 이상 언어, 25,000자 이상을 지원한다. [확인]
2. **역할 분담**(삼성 실제 문서에서 관찰): 영문 디스플레이는 Samsung Sharp Sans Bold/Medium, 한글은 SamsungOneKorean, 영문 본문과 각주는 SamsungOne을 쓴다. [확인: IR 덱, 지속가능경영보고서, 뉴스룸 CSS, samsung.com/sec CSS]
3. **SamsungOneKorean 600은 있다.** 삼성전자 2026년 2분기 실적발표 국문 PDF는 PowerPoint로 만들어졌고, TrueType판 SamsungOneKorean-400/500/600/700이 임베드되어 있다. InDesign으로 만든 보고서에는 CFF판 SamsungOneKoreanOTF-300~700과 콘덴스드(C)가 들어 있다. 팀 로컬 세트(400/500/700)는 그 일부다. [확인]
4. **공개된 공식 다운로드나 라이선스 경로는 없다.** design.samsung.com과 developer.samsung.com에는 소개 글과 견본 PDF만 있다. [확인]
5. **PowerPoint 임베딩.** 팀 파일(TrueType 아웃라인, fsType 8 = Editable embedding)은 "모든 문자 포함"으로 임베딩하면 받는 쪽에서도 편집할 수 있다. 기술적 허용과 라이선스 허용은 별개라서 사외 배포 전에 확인이 필요하다. CFF(OTF)판과 가변 폰트(One UI Sans)는 쓰지 않는다. [확인 + 제안]
6. **덱 세팅.** 슬라이드 마스터의 테마 글꼴에서 라틴 글꼴과 아시아 글꼴을 따로 지정한다. 영문 제목은 Sharp Sans Bold, 영문 본문은 SamsungOne 400, 국문 제목은 SamsungOneKorean 700, 국문 본문은 SamsungOneKorean 400으로 둔다. [제안]

---

## 1. 패밀리 정리

### 1.1 SamsungOne (라틴 외 다국어)

- **발표**: Samsung Newsroom "[Design Story] SamsungOne, the New Universal Typeface for Samsung", 2016-07-22. [확인]
  - "It is a family of scripts covering 26 writing systems, more than 400 languages, and over 25,000 glyphs"
- **디자인 원칙**은 Humanist, Distinctive, Universal, Expert, Legible/Scalable 다섯 가지다. [확인]
  - "SamsungOne mixes a simple, single-width stroke with more calligraphic details."
  - "Letterforms are specifically designed to work functionally at small sizes, and dynamically at large sizes."
- **제작**
  - SamMobile(2016-07-22)은 Samsung이 "teamed up with design firm Brody Associates"라고 보도했다. [확인]
  - design.samsung.com Part 2 페이지는 타이포그래퍼 Neville Brody가 디자인 과정을 설명하는 오디오를 싣고 있다. [확인]
  - Brody Associates 작업 페이지도 SamsungOne을 자사 작업으로 소개한다. [확인]
  - 개별 디자이너 크레딧 전체는 공개 자료에서 찾지 못했다. [미검증]
- **용도**: 공식 소개 페이지는 본문용인지 제목용인지 구분하지 않는다. [확인: 기재 없음] 2021 Co-branding 가이드에는 "Do not use SamsungOne for headlines"라는 규칙이 있다(1.7 참고).
- **굵기**
  - design.samsung.com Part 2: SamsungOne200, 400, 700과 각 Italic, Condensed 옵션. [확인]
  - design.samsung.com 2026 CSS의 웹 파일 선언: SamsungOneLatin 200, 300, 400, 450, 500, 600, 700, 800, 900, 1000, 1100, 콘덴스드 200C~900C, 이탤릭 200~800. [확인] 1000과 1100이 무엇을 뜻하는지는 문서가 없다.
  - 삼성 공식 PDF에 임베드된 데스크톱판: SamsungOne-300, 400, 400C, 500, 600, 700, 700C. [확인] 자세한 내용은 1.6의 표.
- **참고**: 2015년에 나온 "Samsung Sans"는 갤럭시 기기 전용 첫 UI 서체다(뉴스룸 2015-11-23 인터뷰, "Samsung Sans is our first exclusive font for Samsung mobile devices."). SamsungOne과는 다른 서체다. [확인]

### 1.2 SamsungOneKorean (한글)

- **제작 주체와 연도**: 공개 자료에서 찾지 못했다. [미검증] 뉴스룸 국문 기사 "삼성원폰트, 한글 타이포그래피 포스터로 변신하다"(2016-10-08)는 삼성원폰트로 만든 한글 포스터 3종을 소개한다. [확인: 피드 본문]
- **웹 굵기**(design.samsung.com 2026 CSS): 200, 300, 400, 400C, 500, 600, 700, 700C. [확인]
- **문서용 데스크톱판 정황** [확인]
  - TrueType판: SamsungOneKorean-400/500/600/700. PowerPoint로 만든 IR 덱에 들어 있다.
  - CFF판: SamsungOneKoreanOTF-300/400/400C/500/500C/600/600C/700/700C. InDesign으로 만든 보고서에 들어 있다.
- **질문에 대한 답**: SamsungOneKorean 600은 삼성 공식 문서에서 쓰이고 있다. 팀 로컬(400/500/700)에는 없다.
- **웹 파일 버전 흔적**: samsung.com 포르투갈 CSS의 파일명이 `SamsungOneKorean-500_v1.2_20190628.woff`다. [확인] 2019-06-28에 빌드된 v1.2라는 해석은 [추론].

### 1.3 Samsung Sharp Sans (영문 디스플레이)

- **제작**: Sharp Type 사례 페이지는, 2014년 Galaxy 브랜드용으로 Sharp Sans Display No.1을 커스터마이즈해 x-height를 높이고 일부 글자 구조를 고쳤다고 설명한다. [미검증: 페이지가 429와 보안 체크로 열리지 않아 검색 요약만 봤다]
- **굵기**: Regular, Medium, Bold. [확인: design.samsung.com CSS, Co-branding 가이드, 지속가능경영보고서] 팀 로컬에는 Regular와 Bold만 있고 Medium은 없다.
- **한글**: 글리프가 없는 것으로 보인다. [추론] 근거는 두 가지다. samsung.com/sec CSS가 `'SamsungSharpSans'` 다음에 `'SamsungOneKorean'`을 폴백으로 두고, 삼성 IR 덱에서도 한글은 SamsungOneKorean으로 출력된다. 로컬 파일로 직접 확인하기를 권한다.

### 1.4 Samsung Sharp Sans KR (Head/Body), 새로 보이는 정황

- design.samsung.com 2026 CSS에 웹 파일 `SamsungSSHeadKR-Light/Regular/Medium/Bold`와 `SamsungSSBodyKR-Light/Regular/Medium/Bold`가 선언되어 있다. CSS 선언 수로는 사이트에서 가장 많이 쓰이는 패밀리다(제목 클래스의 Head KR Bold 규칙이 약 440개). [확인: CSS]
- 공식 발표나 배포 정보는 찾지 못했다. "2026년 4월에 Sharp Sans 한글 자형 Head 4종, Body 4종이 나왔다"는 취지의 커뮤니티 글은 검색 요약으로만 봤다. [미검증]
- **덱 적용**: 사내에서 데스크톱판을 정식으로 받을 수 있다면 국문 헤드라인 후보로 볼 만하다. 받을 수 없으면 SamsungOneKorean 700을 유지한다. [제안]

### 1.5 One UI Sans (갤럭시 시스템 UI 서체)

- One UI 6(2023)부터 시스템 기본 서체다.
  - Samsung 보도자료(2023-08-11, One UI 6 베타)에 "the impactful new default font"라는 표현이 있다. [확인]
  - "One UI Sans"라는 이름은 SamMobile(2023-11-01) 기사로 확인했다. 기사는 이전 기본값이 Roboto였고 One UI Sans는 "slightly rounder and wider"라고 설명한다. [확인]
- **가변 폰트**: 개발자 블로그(dev.to, 2024-01-09)는 시스템 폰트 파일명이 `OneUISans-VF.ttf`, `OneUISansKR-VF.ttf`이고 패밀리 이름이 "One UI Sans APP VF"라고 보고했다. [제3자, 비공식]
- **덱 적용**: 쓰지 않는다. 공개 배포가 없고, PowerPoint의 가변 폰트 지원도 불안정하다(3.3 참고). One UI Sans는 UI 화면 캡처 안의 글자로만 등장하게 둔다. [제안]

### 1.6 Windows와 PowerPoint의 메뉴 이름: 증거 표

삼성이 공개한 PDF를 내려받아 pypdf로 임베드 폰트를 나열했다. PDF 원본은 /tmp에서만 다뤘다. [확인]

| 문서 (생성일) | 제작 도구 | 임베드된 Samsung 폰트 (PostScript 이름) | 아웃라인 |
|---|---|---|---|
| 삼성전자 2026년 2분기 실적발표 국문 (2026-07-29) | Microsoft PowerPoint LTSC | SamsungOneKorean-400/500/600/700, SamsungOne-400/700, SamsungSharpSans-Bold (그 밖에 맑은 고딕, Calibri, Arial) | TrueType |
| 3Q 2026 Earnings Call 영문 (2026-10-28) | Microsoft PowerPoint 2016 | SamsungOneKorean-400/700 (그 밖에 Calibri, Arial) | TrueType |
| 지속가능경영보고서 2026 국문 (2026-06-26) | Adobe InDesign | SamsungOneKoreanOTF-300/400/400C/500/500C/600/700, SamsungOne-400C/500/700C, SamsungSharpSans-Bold/Medium | 한글은 CFF, 나머지는 TrueType |
| 지속가능경영보고서 2025 국문 (2025-06-27) | Adobe InDesign | SamsungOneKoreanOTF-300/400/400C/500/500C/600/600C/700/700C, SamsungOne-300/400C/500/600/700C, SamsungSharpSans-Bold | 위와 같음 |
| Samsung Co-branding Guidelines v1.1 (2021-10-20) | Adobe InDesign | SamsungOne-400/400C/700, SamsungSharpSans-Bold/Medium | TrueType |

- InDesign PDF의 FontFamily 문자열은 "SamsungOne 400", "SamsungOne 700", "SamsungOne 400C", "SamsungOneKoreanOTF 600", "Samsung Sharp Sans Bold"처럼 굵기가 패밀리 이름 안에 들어 있다. [확인] 팀 로컬의 "SamsungOne 400", "SamsungOneKorean 400/500/700"과 같은 체계다.
- Windows 글꼴 메뉴에 실제로 어떻게 표시되는지는 공개 자료로 직접 확인할 수 없다. [미검증] 위 정황으로 보면 "SamsungOneKorean 600"처럼 굵기별 항목으로 표시될 가능성이 높다. [추론]
- 팀 로컬의 "SamsungOneLatin"(400~700이 한 패밀리 이름을 공유)은 웹 빌드 명명과 일치한다(design.samsung.com 파일명 `SamsungOneLatin-400`, 뉴스룸 파일명 `SamsungOneLatinWeb-400`). 이 이름은 공식 문서 PDF에 나오지 않는다. [확인] 그래서 PowerPoint에서는 굵기별 패밀리(SamsungOne 400/700)를 쓰는 편이 안전하다. [추론, 3.5 참고]
- 공식 데스크톱판에는 팀 로컬에 없는 굵기가 있다(300, 600, 콘덴스드, Sharp Sans Medium). [확인]

### 1.7 삼성 가이드에 적힌 위계: Co-branding Guidelines (Samsung Mobile, 2021-10, v1.1)

**주의**: 이 문서 매 쪽에 "Samsung proprietary and confidential"이 찍혀 있다. Getty Images 자산 URL로 공개 접근되기는 하지만, 사내 공식본으로 다시 확인하고 덱이나 외부 자료에 인용하지 않기를 권한다. 원래 마케팅 광고와 공동 브랜딩용 문서라 발표 덱에는 참고 수준으로 쓴다.

- 헤드라인: "Headlines are set in Samsung Sharp Sans Bold." 헤드라인 트래킹은 10(“Tracking is set at 10 point in headlines”). [확인]
- 부제와 본문: Samsung Sharp Sans Medium, "Use auto leading with no tracking." [확인]
- SamsungOne의 쓰임: "SamsungOne can be used only in body copy in digital environment (dotcom, GUI, CDM, etc.) and text-heavy collaterals where text legibility is highly required." [확인]
- 법적 고지: SamsungOne 400C, 10pt 이하, 행간 +1pt, 트래킹 −5. [확인]
- 크기 비율: 부제는 헤드라인 캡하이트의 60%, 본문은 부제의 50%. [확인]
- Do Nots [확인]
  - "Do not use SamsungOne for headlines."
  - "Do not use title case."
  - "Do not accent any type with color."
  - "Do not use colored copy."
  - "Do not use type with gradients."
  - "Do not overly track out type."
- 보조 컬러 팔레트 이름에 "Lavender"가 들어 있다(Sky Blue, Sea Blue, Teal, Lavender, Clover, Saffron, Coral). 색상 값은 텍스트로 추출되지 않았다. [확인]

---

## 2. 공식 입수와 라이선스 (공개 정보만)

- **design.samsung.com SamsungOne 페이지**: 소개 글과 견본 PDF(`OneFont_eng.pdf`, `OneFont_kor.pdf`)만 있다. 폰트 파일 다운로드 링크나 라이선스 문구는 없다. [확인] 영문 견본 PDF는 10MB를 넘어 내용을 열지 못했다. [미검증]
- **developer.samsung.com/design-system/font**: SamsungOne 소개만 있고 다운로드와 라이선스 정보는 없다. [확인]
- **Samsung Developers 포럼의 "How to download samsung one UI font for web" 스레드**: 현재 404라서 공식 답변을 확인하지 못했다. [미검증]
- **공개 CSS에 보이는 폰트 URL**(뉴스룸, samsung.com, design.samsung.com)은 사이트 렌더링용이다. 팀 로컬 파일의 이름 테이블에는 "All rights of this font software are reserved by Samsung Electronics Co.,LTD. Any unauthorized use or distribution is expressly prohibited."라는 문구가 있다(팀 제공 정보).
- **제3자 '무료 다운로드' 사이트**(bestfonts.pro, onlinewebfonts.com, cufonfonts 등)에도 SamsungOne, Sharp Sans, "SamsungOneKorean-600C" 같은 파일이 올라와 있다. 공식 경로가 아니므로 쓰지 않는다. [제3자, 제안]
- **결론**: 공개된 공식 배포와 라이선스 경로는 확인되지 않는다. 사내 브랜드나 디자인 담당 경로로 데스크톱판(가능하면 TrueType판)을 받을 수 있는지 확인해야 한다. 내부 포털 위치는 추측하지 않았다.

---

## 3. PowerPoint 실무

### 3.1 임베딩 켜는 법

- **Windows**: File > Options > Save > "Preserve fidelity when sharing this presentation" > "Embed fonts in the file"을 켜고 "Embed all characters (best for editing by other people)"를 고른다. [확인: Microsoft 지원 문서]
- **Mac**: "PowerPoint for Microsoft 365 for Mac, PowerPoint 2024 for Mac, and PowerPoint 2021 for Mac"에서 임베딩할 수 있다. [확인]
- **웹판**: 지원 문서에 언급이 없다. [미검증]

### 3.2 팀 파일은 임베딩되는가

- **형식**: Microsoft는 "Use OpenType (.OTF) or TrueType (.TTF), if possible.", "Avoid PostScript fonts (.PFB, .PFM)."라고 안내한다. Adobe PostScript Type 1과 AAT 폰트는 임베딩할 수 없다. [확인]
- **권한**: OpenType OS/2 스펙의 fsType 값 8은 "Editable embedding: the font may be embedded, and may be temporarily loaded on other systems … editing is permitted, including ability to format new text using the embedded font, and changes may be saved."이다. 임시로 로드한 폰트는 문서를 닫을 때 지워야 한다. [확인] Windows 글꼴 제어판의 "Font embeddability"가 Editable이나 Installable이면 임베딩할 수 있다. [확인: Microsoft]
- **결론**: 팀의 TrueType + fsType 8 파일은 기술적으로 임베딩할 수 있고, 받는 쪽에서도 편집할 수 있다. 다만 임베딩하면 폰트 데이터가 파일과 함께 나가므로, 사외 공유 전에는 위 라이선스 문구를 기준으로 확인해야 한다. [판단]
- **CFF판 주의**: 나중에 SamsungOneKoreanOTF(CFF)를 받게 될 경우의 근거는 둘 다 제3자다. [제3자] 그러니 TrueType판을 쓴다. [제안]
  - pptfaq(2020 갱신): "PowerPoint can only embed TrueType data."
  - Microsoft Q&A의 자원봉사 모더레이터(2024-04): "Office works better with TrueType flavor."
- **용량**
  - 임베딩하면 파일이 커지고 일부 PC에서는 여는 속도가 느려질 수 있다. [확인: Microsoft, 요지]
  - "Embed only the characters used"를 고르면 용량은 줄지만 "limits editing of the file using the same font". [확인]
- **한글 웹폰트는 서브셋일 수 있다.** 글자 수를 줄인 웹 빌드라면 덱의 드문 음절이 다른 글꼴로 대체될 수 있으니 전 문구를 확인한다. [추론]

### 3.3 가변 폰트

- 가변 폰트의 Office 지원을 다룬 Microsoft 공식 문서는 찾지 못했다.
- OpenType name 스펙에는 "Applications that assume a four-style family grouping based on name IDs 1 and 2 are likely to provide a poor user experience with variable fonts."라는 문장이 있다. [확인]
- Dalton Maag 호환표: Word와 PowerPoint의 pre-defined instances는 "Yes, but PDF generation and some printer drivers are currently unreliable"이고, additional variations는 "No"다. [확인, 페이지에 날짜 없음]
- TLC Creative(2025-03-12)는 "it is better to steer clear of using variable fonts in PowerPoint presentations."라고 권한다. [확인]
- 따라서 One UI Sans 같은 가변 폰트는 덱 텍스트에 쓰지 않는다. [제안]

### 3.4 받는 PC에 폰트가 없을 때

- Microsoft 설명 [확인]
  - 임베딩하지 않았거나 임베딩이 빠지면 "a different font is substituted".
  - 임베딩하면 "special characters won't turn into meaningless rectangles".
- **덱에 주는 영향** [추론]: 대체 글꼴은 글자 폭과 행간이 달라 줄바꿈이 바뀐다. 그러면 Morph 장면에서 같은 이름의 텍스트 상자 크기와 위치가 달라져 전환이 어긋날 수 있다.
- **확인 방법**: 홈 > 바꾸기 > 글꼴 바꾸기 목록에서 덱에 쓰인 글꼴을 확인한다. [제3자 설명] 폰트가 없는 PC(또는 폰트를 지운 계정)에서 슬라이드 쇼로 끝까지 돌려 본다. [제안]
- **알려진 버그**: PowerPoint for Windows 2410(2024-11)에서 다시 연 파일의 임베딩 폰트가 대체 폰트로 바뀌는 사례가 Glyphs 포럼에 보고됐다. TTF와 OTF 모두였다. [제3자, 지금도 그런지는 미확인]
- **발표 PC 대비**: 폰트 설치, 임베딩, PDF나 영상 백업을 모두 준비한다. [제안]

### 3.5 굵기 선택과 국문/영문 분리

- **굵기별 패밀리**(SamsungOneKorean 400/500/700 등): 굵기는 글꼴 목록에서 해당 패밀리를 직접 골라 바꾼다. 같은 패밀리에 Bold 스타일이 연결되어 있지 않으면 B(굵게) 버튼이 합성 볼드를 만들 수 있다. [추론, 실기 확인 권장]
- **한 패밀리 이름을 4개 넘는 굵기가 공유하는 경우**("SamsungOneLatin" 400~700)
  - OpenType 스펙에 따르면 name ID 1은 "should be shared among at most four fonts"이고, 기존 앱은 Regular, Italic, Bold, Bold Italic 네 개만 가정한다. [확인: 스펙]
  - 그래서 PowerPoint 목록에서 일부 굵기가 안 보이거나 섞일 수 있다. 같은 PC에 "SamsungOne 400/700"과 함께 설치했을 때 충돌하는지도 확인해야 한다. [추론]
- **라틴 글꼴과 아시아 글꼴은 칸이 따로 있다**
  - PowerPoint의 Font 개체에는 아시아 글꼴 이름을 담는 `NameFarEast`가 따로 있다("Returns or sets the Asian font name"). [확인: Microsoft Learn]
  - think-cell KB는 "Asian and Western character fonts are defined separately and must both be set"이라며, 슬라이드 마스터의 "Create New Theme Fonts"에서 제목과 본문의 동아시아 글꼴을 지정하라고 권한다. [확인] 한국어 UI의 메뉴 명칭은 확인하지 않았다.
- **삼성 IR 국문 덱에서 본 것**: 같은 문단 안에서 한글은 SamsungOneKorean, 라틴 문자와 숫자는 Samsung Sharp Sans Bold로 출력된다. 라틴 칸과 아시아 칸을 나눠 쓴 결과로 보인다. [관찰 + 추론] 본문에서는 이 방식이 굵기 차이를 만들 수 있다(예: 한글 500 + 라틴 Bold). 그래서 본문의 라틴 칸은 SamsungOne으로 두기를 권한다. [제안]

### 3.6 체크리스트 [제안]

1. 테마 글꼴 설정: 라틴 제목 Samsung Sharp Sans Bold, 라틴 본문 SamsungOne 400, 아시아 제목 SamsungOneKorean 700, 아시아 본문 SamsungOneKorean 400.
2. "SamsungOneLatin" 대신 "SamsungOne 400/700"을 쓴다. 가능하면 둘 중 하나만 설치한다.
3. 가변 폰트(One UI Sans)는 쓰지 않는다. 맑은 고딕이나 Calibri가 남아 있는지 글꼴 바꾸기 목록에서 확인한다.
4. 저장 옵션: 글꼴 포함, 모든 문자 포함.
5. 폰트가 없는 PC에서 Morph 전환까지 리허설한다.
6. PDF와 영상 백업을 만든다.
7. 사외 공유 전에 라이선스를 확인한다.

---

## 4. 공부할 레퍼런스 10개

각 항목은 URL, 직접 확인한 것, 볼 것, 연라벤더 미니멀 덱에 적용할 점 순서다. 다크 무대 화면은 밝게 뒤집어 적용한다.

### R1. 삼성전자 2026년 2분기 실적발표 국문 덱 (PowerPoint)

- URL: https://images.samsung.com/kdp/ir/events/2026/2026_2Q_conference_kor.pdf
- 확인한 것(폰트 추출, 슬라이드 크기 20×11.25in) [확인]
  - 제목: SamsungOneKorean 700, 52pt
  - 목차 항목: 600, 28pt
  - KPI 숫자(“171.5 조원”): 700, 75pt
  - 본문 불릿: 400, 18pt
  - 각주: SamsungOne/SamsungOneKorean 400, 약 10.6pt
  - 영문 사업부 타이틀("S.LSI / Foundry", "MX / NW")과 증감률("+130%"): Samsung Sharp Sans Bold
  - 표지 "삼성전자"와 일부 섹션 라벨은 맑은 고딕으로 출력된다(의도인지는 불명).
- 볼 것: 같은 제목 자리에서 국문은 SamsungOneKorean 700, 영문 고유명은 Sharp Sans Bold로 바꿔 쓰는 방식. 600을 목차와 라벨에 쓰는 방식.
- 적용
  - 표준 16:9(13.33in)로 환산하면(×0.667) 제목 약 35pt, 목차 약 19pt, 본문 약 12pt, 각주 약 7pt다.
  - 결선은 무대 투사라 본문은 이보다 크게 잡는 편이 안전하다. [제안]

### R2. 3Q 2026 Earnings Call 영문 덱 (PowerPoint 2016)

- URL: https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2026_3Q_conference_eng.pdf
- 확인한 것: 영문 덱인데 SamsungOneKorean 400/700만 쓴다(SamsungOneKorean에 들어 있는 라틴 글리프). 제목 52pt, KPI "195.3T" 75pt, 본문 24~32pt. [확인]
- 볼 것: 패밀리 하나로 국문과 영문의 높이와 굵기를 맞추는 단순한 전략.
- 적용: "Query Rewriting"처럼 국문과 영문이 섞인 짧은 라벨은 SamsungOneKorean 하나로 처리하면 기준선과 굵기가 어긋나지 않는다. [제안]

### R3. 삼성전자 지속가능경영보고서 2026 국문 (InDesign)

- URL: https://download.semiconductor.samsung.com/resources/others/Samsung_Electronics_Sustainability_Report_2026_KOR.pdf
- 확인한 것 [확인]
  - 표지: "A Journey Towards a Sustainable Future"는 Sharp Sans Bold, "2026"은 Sharp Sans Medium, 국문 "삼성전자 지속가능경영보고서"는 SamsungOneKoreanOTF 600.
  - 섹션 오프너: "Our Company"를 Sharp Sans Medium 88pt로.
  - 장 제목: "Sustainability Performance"(Sharp Sans Bold 30pt) 아래에 국문 "분야별 주요성과"(SamsungOneKorean 700, 13pt).
  - 큰 숫자(75.0, 99.3 등): SamsungOneKoreanOTF 300(Light), 31pt. 단위와 라벨은 500.
  - 본문: 300, 9pt. 내비게이션: SamsungOne 400C/700C, 8pt.
- 볼 것: 영문 디스플레이 한 줄에 작은 국문 부제를 짝짓는 방식. 큰 숫자를 Light로 가볍게 처리하는 방식.
- 적용: 단계 제목을 "On-device Index"(Sharp Sans Bold)와 "기기 안 색인"(SamsungOneKorean 700, 작게)으로 짝짓는다. Light가 없으니 큰 숫자는 400으로 대신한다. [제안]

### R4. Galaxy Unpacked 2026 무대 화면

- URL
  - 하이라이트(Samsung Newsroom, 2026-02-26): https://news.samsung.com/global/galaxy-unpacked-2026-highlights
  - 공식 리플레이(2026-02-27, YouTube ID SA93zbnoR4U): https://news.samsung.com/in/heres-the-official-replay-of-galaxy-unpacked-february-2026
- 확인한 것(기사 사진을 직접 봄) [확인]
  - "Agentic AI phone": 짧은 영문 헤드라인 한 줄. 짙은 보랏빛 배경에 흰색에서 라벤더로 넘어가는 글자.
  - "Galaxy AI" 큰 제목 아래에 타일 모자이크 큐브가 있고, Moments / Personal Data Engine / Private Access Token 라벨이 붙어 있다.
  - Now Nudge 데모: 연라벤더 배경에 대화 UI를 크게 확대했다("Can you send me the pics we took last Saturday?"에 이어 "Share photos" 칩).
- 서체: 헤드라인은 Sharp Sans 계열로 보이지만 육안 판단이다. [미검증]
- 볼 것: 2~3단어 헤드라인, 화면 하나에 메시지 하나, UI를 크게 확대하는 카메라.
- 적용: 우리 덱(연라벤더, 확대)과 문법이 같다. Personal Data Engine은 지식 그래프 기반이므로 개념은 빌리지 않고 시각만 참고한다(00단계 레퍼런스 문서 B9 참고).

### R5. Samsung Newsroom 타이포 체계 (CSS 빌드 2026-09-07)

- URL: 글로벌 https://news.samsung.com/global/ , 국문 https://news.samsung.com/kr/
- 확인한 것 [확인]
  - 글로벌: 기본 패밀리 "SamsungOne"(SamsungOneLatinWeb 400/700). 기사 제목과 캐러셀 제목은 SamsungSharpSans 700, 기사 제목 24px, 자간 0.
  - 국문: 같은 패밀리 이름 "SamsungOne"에 SamsungOneKoreanOTF 400/500/700을 연결했다. 기사 제목 규칙은 700, 24px, 자간 −0.045rem(약 −3%), 행간 32px이고 글꼴은 기본 패밀리를 물려받는다.
- 볼 것: 영문 제목은 Sharp Sans, 국문 제목은 SamsungOneKorean 700에 음수 자간.
- 적용: 국문 제목 자간을 −1%에서 −3% 사이로 둔다. PowerPoint 문자 간격은 pt 단위라서 글자 크기에 비율을 곱한다(32pt × 3% ≈ 1pt 좁게). [제안]

### R6. design.samsung.com (2026 개편)과 SamsungOne 소개 페이지

- URL: https://design.samsung.com/kr/main/ , http://design.samsung.com/global/contents/samsungone/ , http://www.design.samsung.com/global/contents/samsungone_part2/
- 확인한 것 [확인]
  - 국문 키비주얼 제목: Samsung Sharp Sans Head KR Bold, 70px, 행간 1.17.
  - 기본 제목: Head KR Medium 26px와 20px.
  - 본문: Body KR Regular 20px(행간 1.3), 30px(행간 1.6).
  - SamsungOne 견본 클래스: 자간 −0.015em.
  - SamsungOne 페이지: 다섯 가지 원칙과 언어별 견본.
- 볼 것: 제목 패밀리와 본문 패밀리의 분리, 큰 제목의 촘촘한 행간.
- 적용: 큰 제목 행간은 1.1~1.2, 본문 행간은 1.3~1.5. [제안]

### R7. samsung.com/sec (삼성닷컴 국문)

- URL: https://www.samsung.com/sec/static/_css/mig/sec.css
- 확인한 것 [확인]
  - 제목 스택: `'SamsungSharpSans', 'SamsungOneKorean', …`(bold). 주석 "영문 title 부분 폰트 재정의"가 달려 있다.
  - 영문 타이틀 크기: 56~60px.
  - 본문: `'SamsungOneKorean', …`.
- 적용: PowerPoint에서 라틴 칸과 아시아 칸을 나누는 것과 같은 구조다.

### R8. Samsung Co-branding Guidelines v1.1 (2021-10)

- URL: https://assets.gettyimages.com/bf-boulder-whitelabelbucket-getty-prod/qwbqch8624nt824q5cxtfxh/v/1012694872/original/Samsung_CoBrandingGuidelines_Version1.1_10202021.pdf.pdf
- 확인한 것: 1.7 참고. 기밀 표기가 있는 문서다.
- 볼 것: 헤드라인, 부제, 본문의 크기 비율과 Do Nots.
- 적용: 보라 텍스트는 키워드 하나 정도로 제한하고, 그라데이션 글자는 쓰지 않으며, 영문은 sentence case로 쓴다. 광고용 가이드이므로 참고 수준이다. [제안]

### R9. One UI 디자인 가이드

- URL: https://developer.samsung.com/one-ui/structure/visual-depth.html , https://developer.samsung.com/one-ui/accessibility/layout-and-typo.html
- 확인한 것 [확인]
  - blur와 dim으로 위계를 만든다. "Instead of using blur alone, use it together with the dim effect to enhance readability."
  - 그림자는 "should not be seen as having 3D depth"이고, 효과를 겹치지 말라고 한다.
  - 접근성: 텍스트를 200%까지 키울 수 있어야 한다.
  - 서체 이름이나 크기 규정은 없다.
- 적용: Morph로 확대할 때 주변 기록은 흐리게 하고 옅은 딤으로 뒤로 보낸다. 그림자는 아주 옅게 둔다. [제안]

### R10. Samsung AI Forum (Samsung Research)

- URL
  - 2026 행사 페이지: https://research.samsung.com/saif (2026-09-30, "On-Device AI Platform of Samsung" 세션 포함)
  - 2025 세션 재생목록: https://www.youtube.com/playlist?list=PL7PfK8Mp1rLGZm6zhh0F4KnFioRvPIkiA (Samsung Developers 2025-10-15 공지)
- 확인한 것: 세션 목록과 재생목록이 있다. [확인] 슬라이드 서체는 확인하지 못했다. [미검증]
- 볼 것: 연구 발표 슬라이드의 도식 밀도. 특히 "Unlocking On-Device LLMs: Models and SDKs for Phones, TVs, and Home Appliances".
- 참고: SDC24 Korea(2024-11-21, 온라인, 기술 세션 29개 이상) 페이지에는 슬라이드 링크가 없어 레퍼런스에서 뺐다. [확인]

---

## 5. 결선 덱 적용안

크기는 13.33×7.5in 기준 제안값이다. 03_지침·기획/디자인_규칙.md와 충돌하면 그 문서를 따른다(이번 조사에서는 그 문서를 열어 보지 않았다).

| 역할 | 라틴 칸 | 한글 칸 | 크기 [제안] | 근거 |
|---|---|---|---|---|
| 표지·섹션 영문 디스플레이 | Samsung Sharp Sans Bold | (영문만) | 40~60pt | R3, R4, R8 |
| 슬라이드 제목 | Sharp Sans Bold(영문 고유명) 또는 SamsungOne 700 | SamsungOneKorean 700, 자간 −1~−3% | 28~36pt | R1, R5 |
| 소제목·라벨 | SamsungOne 700 | SamsungOneKorean 500 (600 수령 시 600) | 18~22pt | R1 |
| 확대 장면 옆 짧은 캡션 | SamsungOne 400/700 | SamsungOneKorean 500 | 16~20pt | R4, R9 |
| 본문 | SamsungOne 400 | SamsungOneKorean 400 | 14~18pt | R1, R2 |
| 큰 숫자 | SamsungOne 400 또는 700 | 같은 칸 | 48~60pt | R1, R3 |
| 각주·출처 | SamsungOne 400 | SamsungOneKorean 400 | 9~10pt | R1 |

- 텍스트 기본색은 짙은 회색이나 검정으로 두고, 보라(#6B4EFF 계열)는 슬라이드당 키워드 하나로 제한한다. [제안, R8 Do Nots 참고]

---

## 6. 미검증과 주의 목록

- Sharp Type 사례(2014, Sharp Sans Display No.1 기반): 페이지 접근에 실패해 검색 요약만 봤다.
- SamsungOneKorean의 제작 주체와 연도: 확인하지 못했다.
- Samsung Sharp Sans KR(Head/Body): CSS 정황만 있고 공식 발표는 확인하지 못했다.
- One UI Sans가 가변 폰트라는 점과 그 이름: 제3자 블로그 출처다.
- Windows 글꼴 메뉴의 표기 자체: 공개 자료로 직접 확인할 수 없다.
- 합성 볼드, 4스타일 충돌, 한글 서브셋: 추론이라 실기 확인이 필요하다.
- Unpacked 무대 화면의 서체: 육안 판단이다.
- Co-branding 가이드: 기밀 표기 문서이고 2021년 기준이다.
- design.samsung.com 영문 견본 PDF: 10MB를 넘어 열지 못했다.

---

## 출처

삼성 공식
- Samsung Newsroom, [Design Story] SamsungOne (2016-07-22): https://news.samsung.com/global/design-story-samsungone-the-new-universal-typeface-for-samsung
- design.samsung.com SamsungOne: http://design.samsung.com/global/contents/samsungone/ , Part 2: http://www.design.samsung.com/global/contents/samsungone_part2/ , 국문: http://design.samsung.com/kr/contents/samsungone/
- design.samsung.com 2026 메인과 CSS: https://design.samsung.com/kr/main/ , https://design.samsung.com/assets/css/common_module_rn2026_v1.css , https://design.samsung.com/assets/css/components_rn2026_v1.css
- Samsung Developers, Font: https://developer.samsung.com/design-system/font
- Samsung Newsroom, JiEun Kim 인터뷰(Samsung Sans, 2015-11-23): https://news.samsung.com/global/create-the-face-of-galaxy-devices-font-designer-jieun-kim
- Samsung Newsroom KR 태그 피드 "삼성원폰트": https://news.samsung.com/kr/tag/%ec%82%bc%ec%84%b1%ec%9b%90%ed%8f%b0%ed%8a%b8/feed
- Samsung Mobile Press, One UI 6 Beta (2023-08-11): https://www.samsungmobilepress.com/press-releases/samsungs-one-ui-6-beta-program-offers-galaxy-s23-series-users-a-sneak-peek-at-new-enhancements
- 실적발표 2Q 2026 국문: https://images.samsung.com/kdp/ir/events/2026/2026_2Q_conference_kor.pdf
- 3Q 2026 Earnings Call 영문: https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2026_3Q_conference_eng.pdf
- 지속가능경영보고서 2026 국문: https://download.semiconductor.samsung.com/resources/others/Samsung_Electronics_Sustainability_Report_2026_KOR.pdf
- 지속가능경영보고서 2025 국문: https://images.samsung.com/kdp/ir/annual-reports/sustainability_report_2025_kr.pdf
- Co-branding Guidelines v1.1 (기밀 표기): https://assets.gettyimages.com/bf-boulder-whitelabelbucket-getty-prod/qwbqch8624nt824q5cxtfxh/v/1012694872/original/Samsung_CoBrandingGuidelines_Version1.1_10202021.pdf.pdf
- Samsung Newsroom CSS: https://news.samsung.com/global/wp-content/themes/newsroom/style.css?ver=1.5.7 , https://news.samsung.com/kr/wp-content/themes/newsroom/style.css?ver=1.2.3
- samsung.com/sec CSS: https://www.samsung.com/sec/static/_css/mig/sec.css
- samsung.com 포르투갈 CSS: https://www.internet.apps.samsung.com/pt/css/fonts-critical.css
- Samsung US 지원 시뮬레이터 CSS (SamsungOne 400/500/600/700, SamsungSharpSans 700): https://pages.samsung.com/us/support/simulators/assets/v7/global.css
- Galaxy Unpacked 2026 하이라이트: https://news.samsung.com/global/galaxy-unpacked-2026-highlights , 리플레이: https://news.samsung.com/in/heres-the-official-replay-of-galaxy-unpacked-february-2026
- One UI 가이드: https://developer.samsung.com/one-ui/index.html , https://developer.samsung.com/one-ui/structure/visual-depth.html , https://developer.samsung.com/one-ui/accessibility/layout-and-typo.html
- Samsung AI Forum: https://research.samsung.com/saif , https://developer.samsung.com/sdp/news/en/2025/10/16/catch-13-insightful-sessions-from-samsung-ai-forum-2025-on-youtube
- SDC24 Korea: https://developer.samsung.com/sdp/events/en/2024/11/21/samsung-developer-conference-korea-2024-sdc24-korea

Microsoft
- Embed fonts in documents or presentations: https://support.microsoft.com/en-us/office/embed-fonts-in-documents-or-presentations-cb3982aa-ea76-4323-b008-86670f222dbc
- Some of your fonts can't be saved with the presentation: https://support.microsoft.com/en-us/office/some-of-your-fonts-can-t-be-saved-with-the-presentation-2ba26947-5d18-4eb3-b5a9-67a58629e1b8
- OpenType OS/2 (fsType): https://learn.microsoft.com/en-us/typography/opentype/spec/os2
- OpenType name (name ID 1/2/16/17): https://learn.microsoft.com/en-us/typography/opentype/spec/name
- PowerPoint Font.NameFarEast: https://learn.microsoft.com/en-us/office/vba/api/powerpoint.font.namefareast
- Morph transition: Tips and tricks: https://support.microsoft.com/en-us/office/morph-transition-tips-and-tricks-bc7f48ff-f152-4ee8-9081-d3121788024f
- Microsoft Q&A (TrueType flavor, 2024-04): https://learn.microsoft.com/en-us/answers/a/11723704

제3자
- SamMobile, SamsungOne 발표 (2016-07-22): https://www.sammobile.com/2016/07/22/samsung-takes-the-wraps-off-its-official-universal-typeface/
- Brody Associates, Samsung One: https://www.brody-associates.com/work/samsung-one
- Sharp Type, Samsung Sharp Sans (직접 열람 실패): https://sharptype.co/case-studies/samsung-sharp-sans
- SamMobile, One UI 6 font (2023-11-01): https://www.sammobile.com/news/one-ui-6-new-font-not-looking-good-switch-back-old-one/
- dev.to, One UI Sans on web (2024-01-09): https://dev.to/reinhart1010/how-to-use-one-ui-sans-on-your-website-1m1i
- think-cell KB0038: https://www.thinkcell.com/en/resources/kb/0038
- pptfaq, Embedding fonts (2020 갱신): https://www.rdpslides.com/pptfaq/FAQ00076_Embedding_fonts.htm
- Glyphs 포럼, PowerPoint PC embedding bug (2024-11): https://forum.glyphsapp.com/t/powerpoint-pc-embedding-bug/32030
- Dalton Maag, Using Variable Fonts: https://daltonmaag.com/help/using-variable-fonts.html
- TLC Creative, Variable Fonts and PowerPoint (2025-03-12): https://thepowerpointblog.com/2025/03/12/
