// touch-tap.svg → touch-tap.png (투명, 8배)
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: '/home/jaeung/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args: ['--no-sandbox', '--force-color-profile=srgb'] });
  const p = await b.newPage({ viewport: { width: 656, height: 928 }, deviceScaleFactor: 1 });
  await p.goto(pathToFileURL(path.join(__dirname, 'touch-tap.svg')).href);
  await p.locator('svg').first().screenshot({ path: path.join(__dirname, 'touch-tap.png'), omitBackground: true });
  await b.close();
})();
