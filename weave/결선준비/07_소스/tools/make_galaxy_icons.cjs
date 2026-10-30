// 갤럭시(One UI) 앱 아이콘 만들기 — 2026-09-28 요청 '아이폰 아이콘 → 갤럭시 아이콘'
//   samsung-calendar.png, samsung-email.png : 갤럭시 스토어 공식 아이콘(512×512) 그대로
//     캘린더  https://img.samsungapps.com/productNew/000009036099/ENG/IconImage_20260922090309765_NEW_WAP_ICON_512_512.png
//     이메일  https://img.samsungapps.com/productNew/000009282129/ENG/IconImage_20260923092453153_NEW_WAP_ICON_512_512.png
//   samsung-gallery.png, samsung-phone.png : 시스템 앱이라 스토어 웹에서 받을 수 없어 SVG로 그림(gallery.svg, phone.svg)
//     → 공식 캘린더 아이콘의 윤곽(투명도)으로 잘라 네 아이콘의 모서리 모양을 똑같게 함
// 사용: node tools/make_galaxy_icons.cjs
const path = require('node:path');
const NM = process.env.NM || '/tmp/claude-weave-0927/node_modules';
const sharp = require(path.join(NM, 'sharp'));
const DIR = path.resolve(__dirname, '..', 'assets', 'icons', 'galaxy');
(async () => {
  const m = await sharp(path.join(DIR, 'samsung-calendar.png')).ensureAlpha().extractChannel(3).raw().toBuffer();   // 공식 윤곽
  for (const name of ['gallery', 'phone']) {
    const art = await sharp(path.join(DIR, `${name}.svg`), { density: 72 }).resize(512, 512).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
    const px = art.data;                                     // RGBA, 알파에 윤곽을 곱함
    for (let i = 0; i < 512 * 512; i++) px[i * 4 + 3] = Math.round(px[i * 4 + 3] * m[i] / 255);
    await sharp(px, { raw: { width: 512, height: 512, channels: 4 } }).png().toFile(path.join(DIR, `samsung-${name}.png`));
    console.log('wrote', `samsung-${name}.png`);
  }
})().catch((e) => { console.error(e); process.exit(1); });
