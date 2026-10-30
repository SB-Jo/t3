# Members — 17 / END

`통합.pptx`와 같은 밝은 라벤더 배경·중앙 제목 체계로 만든 Members 1장입니다. 사용자의 요청에 따라 `0921/통합_claude0927_반영본.pptx`의 기존 19장을 유지하고, 이 페이지를 20번째로 추가했습니다. 기존 `added_0926/통합.pptx`는 수정하지 않았습니다.

## 현재 파일

- `index.html`: 최종 편집 원본. 1280×720, Inter / Noto Sans KR.
- `members-preview.png`: 최종 HTML의 2560×1440 미리보기.
- `members.pptx`: 편집 가능한 텍스트와 개별 인물 이미지가 있는 PowerPoint.
- `members.pdf`: 동일 HTML의 PDF 내보내기.
- `members.png`: 동일 HTML의 PNG 내보내기.
- `assets/portraits-final-v5/`: 최종 원형 배치 이미지. 인물 원본은 `assets/portraits-v5/`.
- `slide-spec.json`: 이름·소속·디저트·배치 기준.
- `character-lineup-v5.prompt.txt`, `churro-tip-v5.prompt.txt`: 최종 채택 인물과 츄러스 끝부분 수정 프롬프트.
- `layout-validation.json`, `export-validation.json`: HTML / 내보내기 검사 결과.
- `pptx-render-check.png`: 글꼴을 지정한 LibreOffice에서 PPTX를 다시 열어 렌더링한 확인 이미지.
- `DOWNLOADS.md`: 24시간 유효한 온라인 미리보기·내보내기 링크.
- `append-members-slide.py`: 기존 장을 재생성하지 않고 새 Members 장과 필요한 이미지·서식만 추가하는 스크립트.
- `merged-deck-validation.json`: 기존 19장 순서·슬라이드 XML과 기존 이미지 등 132개 패키지 구성 요소의 바이트 단위 보존 확인.
- `backups/통합_claude0927_반영본_before-members-20_20260927.pptx`: 삽입 전 19장 통합본 백업.

## 마지막 수정

- 사용자가 가장 자연스럽다고 선택한 **v5**를 기준으로 했습니다. 재웅·성빈 두 명만 어깨가 너무 좁아 보이지 않도록 imagegen으로 보완했습니다. 다른 세 명의 최종 원형 이미지는 변경하지 않았습니다. 원형은 184px로 유지하고 상반신 하단을 자연스럽게 크롭했습니다.
- 시나리오 만화의 귀여운 3D 그림체를 기준으로 사용했습니다. 실제 사진에서는 헤어스타일·안경·눈매·얼굴형 특징을 참고했습니다.
- 두 남성의 헤어스타일·표정·디저트는 v5를 기준으로 유지하도록 편집했습니다. 프롬프트는 `male-shoulders-v5.prompts.json`, 편집 원본은 `assets/male-shoulder-refinement/`에 있습니다.
- 양서윤의 츄러스는 코코아색 반죽을 유지하고, 끝부분에 진하고 매끈한 초콜릿 코팅을 추가했습니다. imagegen 수정 결과의 해당 부분만 합성했으며 수정 마스크 밖 변경 픽셀은 0개입니다. `assets/portraits-v5/churro-tip-validation.json` 참조.
- 인물·이름·소속을 직전 버전보다 20px 위로, 하단 문구를 24px 위로 이동했습니다. 마지막 텍스트 박스 아래 여백은 44px에서 68px로 늘렸습니다.
- 감사 문구는 Noto Sans KR **24px / 700**, 아래 문구는 **22px / 400**입니다. 기본 색상은 #5B5866, 아래 문구의 보라색 강조는 유지합니다. 문구 영역 위치와 배경은 그대로입니다.
- 😊는 감사 문구 옆에 있는 Microsoft Fluent Emoji 컬러 이미지입니다. 글꼴 대체로 흑백 기호가 되는 것을 피했습니다.

## 제작·참고 자료

- 원본 사진과 `characters/ref1.jpg`, `ref2.png`; `overview-comic/art/panel-01-art.png`의 시나리오 그림체.
- 그림 생성/수정: 내장 imagegen. 최종 프롬프트는 `character-lineup-v5.prompt.txt`와 `churro-tip-v5.prompt.txt`.
- 원형 크롭·배치: `layout-v1-portraits.cjs v5`. 츄러스 수정 부위의 합성·보존 검사: `compose-churro-tip.cjs`. 캐릭터 본체는 생성 이미지이며 도형/텍스트로 대체하지 않았습니다.
- 내보내기: Presenton. PPTX·PDF·PNG는 동일한 최종 HTML을 사용합니다.
- [파리바게뜨 공식 초코쫀득츄러스](https://www.paris.co.kr/product/chocolate-chewy-churros/) — 형태 참고. 공식 제품 사진을 슬라이드에 직접 넣지는 않았습니다.
- [Microsoft Fluent Emoji](https://github.com/microsoft/fluentui-emoji) — 😊 이미지. MIT 라이선스는 `assets/FLUENT-EMOJI-LICENSE.txt`에 있습니다.
- 실제 프로필 사진은 공개 이미지 업로드에 사용하지 않았습니다. 공개 HTML에는 생성된 캐릭터 이미지와 컬러 이모지만 연결됩니다.

## 글꼴

- [Inter](https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap)
- [Noto Sans KR](https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap)

위 글꼴은 PPTX·PDF·PNG 공통입니다. PPTX는 텍스트 편집이 가능하므로 다른 PC에서 열 때 두 글꼴이 설치되어 있어야 모양이 유지됩니다. 저장소의 기존 글꼴 파일은 `../../ppt/assets/fonts/`에 있습니다. 이미지/PDF는 해당 PC의 글꼴 설치 여부에 영향을 받지 않습니다.

HTML의 이미지·웹폰트·Tailwind를 처음 로드하려면 인터넷 연결이 필요합니다. 로컬 그림 파일도 함께 남겨 두었습니다.
