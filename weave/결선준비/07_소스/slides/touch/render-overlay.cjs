// out/<name>.svg → out/<name>.png (투명 배경, SVG에 적힌 8배 크기 그대로)
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: '/home/jaeung/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args: ['--no-sandbox', '--force-color-profile=srgb'] });
  for (const name of process.argv.slice(2)) {
    const svg = path.join(__dirname, 'out', name + '.svg');
    const m = fs.readFileSync(svg, 'utf8').match(/width="([\d.]+)" height="([\d.]+)"/);
    const p = await b.newPage({ viewport: { width: Math.ceil(+m[1]), height: Math.ceil(+m[2]) }, deviceScaleFactor: 1 });
    await p.goto(pathToFileURL(svg).href);
    await p.locator('svg').first().screenshot({ path: path.join(__dirname, 'out', name + '.png'), omitBackground: true });
    await p.close();
  }
  await b.close();
})();
