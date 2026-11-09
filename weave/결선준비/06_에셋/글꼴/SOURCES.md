# Samsung font sources · 2026-09-26

The fonts below were downloaded from publicly served Samsung website assets for the user's Samsung concept teaser. Their names were verified from the font metadata. No open-source license was established in this task, and this note does not grant a redistribution or commercial-use license; confirm the applicable Samsung/internal brand permissions before external reuse.

- `SamsungSharpSans-Regular.woff2`: https://www.samsung.com/sec/static/_font/SamsungSharpSans.woff2
- `SamsungSharpSans-Bold.woff2`: https://www.samsung.com/sec/static/_font/SamsungSharpSans-Bold.woff2
- Removed after the user rejected the Medium trial: `SamsungSharpSans-Medium.woff`, originally downloaded from https://d3unf4s5rp9dfh.cloudfront.net/public/fonts/SamsungSharpSans-Medium.woff . Font metadata was Samsung Sharp Sans / Medium (fontconfig weight 100, CSS 500). The active title remains Bold. The unused Medium file was moved to trash with the rejected images; this entry records provenance only.
- `SamsungOneKorean-400.woff2`: https://www.samsung.com/sec/static/_font/SamsungOneKorean-400.woff2
- `SamsungOneKorean-500.woff`: https://design.samsung.com/kr/contents/samsungone_part2/font/SamsungOneKorean-500.woff
- `SamsungOneLatin-600.woff2`: https://design.samsung.com/global/font/SamsungOneLatin-600.woff2 — declared in https://design.samsung.com/kr/css/webfont.css ; verified as SamsungOne Latin 600 in the font metadata. Used in the v16 trial only; the user selected Samsung Sharp Sans Bold for the final version.
- `SamsungOne-400.woff2`: https://www.samsung.com/etc.clientlibs/samsung/clientlibs/consumer/global/clientlib-common/resources/fonts/SamsungOne-400.woff2 — downloaded and verified as SamsungOne 400 while checking English options; not applied to the final headline.

The first three URLs are declared in https://www.samsung.com/sec/static/_css/common.css . The last URL is declared in https://design.samsung.com/kr/contents/samsungone_part2/css/page.css . Samsung's official typeface overview: https://developer.samsung.com/design-system/font .

## 2026-10-29 추가 (결선 인트로 영상 v3)

- `SamsungOneKorean-700.woff`: https://design.samsung.com/kr/contents/samsungone_part2/font/SamsungOneKorean-700.woff — 한글 11,172자 전부 포함(fontTools로 확인)
- `SamsungOneLatin-400.woff2`, `-500.woff2`, `-700.woff2`: https://design.samsung.com/global/font/SamsungOneLatin-{400,500,700}.woff2
- 위와 같은 주의가 그대로 적용됩니다: 사내 발표용으로만 쓰고, 외부 재배포 전에는 삼성 브랜드 사용 권한을 확인하세요.

## 2026-11-02 저장소에서 뺌 (공개 저장소)

GitHub 저장소(gnueaj/t3)는 공개로 유지하므로 삼성 글꼴 파일은 올리지 않습니다(`결선준비/.gitignore`). 앞서 두 커밋(10/30, 11/02)에 들어갔던 글꼴은 기록을 다시 써서 뺐습니다.

- 로컬에는 그대로 있습니다: `06_에셋/글꼴`, `07_소스/teaser/assets/fonts`, `08_인트로영상/소스/assets/fonts`, `10_표지영상/소스/assets/fonts`.
- 다른 컴퓨터에서 영상을 다시 렌더하려면 위 주소에서 받아 같은 이름으로 넣습니다.
- PowerPoint용 TTF(SamsungOneKorean 400·500·700, SamsungOne 400, Samsung Sharp Sans)는 웹 글꼴을 변환해 `~/.cache/weave-tools/fonts`에 두고, Windows 사용자 글꼴로 설치했습니다. 이것도 저장소 밖입니다.

## 2026-11-09 추가 (글꼴 시안: 한글 Korean Sans + 영문 Sharp Sans)

- `SamsungKoreanSans-Medium.woff2`, `SamsungKoreanSans-Bold.woff2`: https://www.samsung.com/sec/static/_font/_kor_sans/SamsungKoreanSans-Medium.woff2 , https://www.samsung.com/sec/static/_font/_kor_sans/SamsungKoreanSans-Bold.woff2
  - https://www.samsung.com/sec/static/_css/common.css 에 'Samsung Korea Sans'로 선언돼 있어요(주석 "21-11-01 NEW KOR font"). `.kor-sans`가 'Samsung Korea Sans', 'Samsung Sharp Sans' 순서로 써요.
  - 글꼴 정보: Samsung Korean Sans Medium·Bold, Copyright © 2021 Yoondesigngroup, 한글 2,350자, 영문 알파벳은 없어요(fontTools로 확인).
- `SamsungSharpSans-Medium.woff`: 위(2026-09-26)의 cloudfront 주소에서 다시 받았어요. 보통 굵기 글에서 Korean Sans Medium과 굵기를 맞추는 데 써요.
- PowerPoint용 파일은 `~/.cache/weave-tools/fonts`에 두고 Windows 사용자 글꼴로 설치했어요.
  - `SamsungKoreanSans-Medium.ttf`, `SamsungKoreanSans-Bold.ttf`: Windows 가족 이름을 'Samsung Korean Sans' 하나로 묶었어요(Medium = 보통, Bold = 굵게).
  - `SamsungSharpSans-Medium.otf`: Windows 가족 이름은 'Samsung Sharp Sans Medium'이에요.
- 위와 같은 주의가 그대로 적용돼요. 사내 발표용으로만 쓰고 저장소에는 올리지 않아요(`결선준비/.gitignore`).
