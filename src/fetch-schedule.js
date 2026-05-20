const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  console.log('Loading https://www.shibuyahifi.com/hifi-schedule...');
  try {
    await page.goto('https://www.shibuyahifi.com/hifi-schedule', { waitUntil: 'domcontentloaded', timeout: 15000 });
  } catch (error) {
    console.log('⚠ Page load timeout, continuing anyway...');
  }
  await page.waitForTimeout(2000); // Wait for initial content to render

  // Click "Load More" until it's gone
  let clickCount = 0;
  let hasMoreContent = true;
  const maxClicks = 20; // Safety limit

  while (hasMoreContent && clickCount < maxClicks) {
    const loadMoreBtn = await page.locator('button:has-text("Load More")').first();
    const isVisible = await loadMoreBtn.isVisible().catch(() => false);

    if (!isVisible) {
      hasMoreContent = false;
      break;
    }

    clickCount++;
    console.log(`Clicking Load More (${clickCount})...`);
    try {
      await loadMoreBtn.click();
      await page.waitForTimeout(1500); // Wait for content to load
    } catch (error) {
      console.log(`⚠ Error clicking Load More: ${error.message}`);
      hasMoreContent = false;
    }
  }

  console.log(`✓ Loaded all content (${clickCount} clicks)`);

  // Save rendered HTML to tmp directory
  const html = await page.content();
  const tmpDir = path.join(__dirname, '..', 'tmp');
  if (!fs.existsSync(tmpDir)) {
    fs.mkdirSync(tmpDir, { recursive: true });
  }
  const outputFile = path.join(tmpDir, 'shibuya-schedule-rendered.html');
  fs.writeFileSync(outputFile, html);

  await browser.close();
  console.log(`✓ Saved rendered page to ${outputFile}`);
})();
