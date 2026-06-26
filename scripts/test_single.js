import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

async function run() {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

  const id = '6289699';
  console.log(`Loading ${id}...`);
  await page.goto(`https://www.lego.com/en-us/pick-and-build/pick-a-brick?icmp=PAB_All_Pieces&query=${id}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  
  console.log('Waiting for button...');
  try {
    await page.waitForSelector('[data-test="pab-item-button"]', { timeout: 30000 });
    console.log('Button found!');
    
    const clicked = await page.evaluate(() => {
      const btn = document.querySelector('[data-test="pab-item-button"]');
      if (btn) {
        btn.click();
        return true;
      }
      return false;
    });
    console.log(`Clicked: ${clicked}`);

    if (clicked) {
      await page.waitForSelector('[role="dialog"], [data-test="pab-item-color-select"]', { timeout: 15000 });
      await new Promise(r => setTimeout(r, 1000));
      
      const data = await page.evaluate(async () => {
        let colorName = null;
        const colorSelect = document.querySelector('[data-test="pab-item-color-select"], select');
        if (colorSelect && colorSelect.options && colorSelect.selectedIndex >= 0) {
          colorName = colorSelect.options[colorSelect.selectedIndex].text.trim();
        } else {
           const spans = Array.from(document.querySelectorAll('span, p, div'));
           const colorLabel = spans.find(s => s.innerText && s.innerText.trim() === 'Color');
           if (colorLabel && colorLabel.nextElementSibling) {
              colorName = colorLabel.nextElementSibling.innerText.trim();
           }
        }
        return colorName;
      });
      console.log(`Extracted color: ${data}`);
    }
  } catch (err) {
    console.log(`Error: ${err.message}`);
    await page.screenshot({path: 'error_screenshot.png'});
  }

  await browser.close();
}

run().catch(console.error);
