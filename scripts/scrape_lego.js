import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

puppeteer.use(StealthPlugin());

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SETS_JSON_PATH = path.join(__dirname, '../src/data/sets.json');
const IMAGES_DIR = path.join(__dirname, '../public/images'); 

async function downloadImage(url, destPath) {
    if (!url) return false;
    try {
        const response = await axios({
            url,
            method: 'GET',
            responseType: 'stream',
            timeout: 10000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        });
        const writer = fs.createWriteStream(destPath);
        response.data.pipe(writer);
        return new Promise((resolve, reject) => {
            writer.on('finish', resolve);
            writer.on('error', reject);
        });
    } catch (e) {
        console.error(`Failed to download image ${url}:`, e.message);
        return false;
    }
}

async function run(limit = null) {
    let sets = JSON.parse(fs.readFileSync(SETS_JSON_PATH, 'utf-8'));
    
    if (!fs.existsSync(IMAGES_DIR)) {
        fs.mkdirSync(IMAGES_DIR, { recursive: true });
    }

    console.log("Launching browser in visible mode. If you see a Cloudflare Captcha, PLEASE SOLVE IT manually in the browser window.");
    const browser = await puppeteer.launch({ 
        headless: false, // Make it visible so user can solve captchas
        args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    });
    
    const page = await browser.newPage();
    const setsToProcess = limit ? sets.slice(0, limit) : sets;

    for (let i = 0; i < setsToProcess.length; i++) {
        const set = setsToProcess[i];
        console.log(`\nProcessing ${i+1}/${setsToProcess.length}: ${set.id}`);
        
        try {
            await page.goto(`https://www.lego.com/en-us/search?q=${set.id}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
            
            // Wait to see if Cloudflare is blocking
            let pageTitle = await page.title();
            if (pageTitle.includes("Just a moment") || pageTitle.includes("Cloudflare")) {
                console.log("⚠️ Cloudflare challenge detected! Please solve it in the browser window...");
                // Wait until the title changes
                while(pageTitle.includes("Just a moment") || pageTitle.includes("Cloudflare")) {
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    pageTitle = await page.title();
                }
                console.log("✅ Cloudflare passed!");
            }

            // Also check for Lego cookie banner and click "Continue" or "Accept All" if present
            try {
                const acceptBtn = await page.$('button[data-test="cookie-accept-all"]');
                if (acceptBtn) await acceptBtn.click();
            } catch(e) {}

            await new Promise(resolve => setTimeout(resolve, 4000));

            let url = page.url();
            
            if (!url.includes('/product/')) {
                const productHref = await page.evaluate(() => {
                    const links = Array.from(document.querySelectorAll('a'));
                    const productLink = links.find(a => a.href.includes('/product/') && !a.href.includes('review') && !a.href.includes('questions'));
                    return productLink ? productLink.href : null;
                });

                if (productHref) {
                    await page.goto(productHref, { waitUntil: 'domcontentloaded', timeout: 60000 });
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    url = page.url();
                }
            }

            if (url.includes('/product/')) {
                // Extract Data
                const data = { images: [] };
                
                try {
                    const titleEl = await page.$('h1 span');
                    if (titleEl) data.name = await page.evaluate(el => el.textContent.trim(), titleEl);
                } catch (e) {}

                try {
                    const attrs = await page.$$eval('[data-test="product-details-value"]', els => els.map(el => el.textContent.trim()));
                    if (attrs.length >= 2) {
                        data.age = attrs[0];
                        data.pieces = parseInt(attrs[1].replace(/\D/g, '')) || 0;
                    }
                } catch (e) {}

                try {
                    const imgUrls = await page.$$eval('img', imgs => imgs.map(img => img.src).filter(src => src && src.includes('lego.com') && src.includes('/assets/')));
                    const uniqueImages = [...new Set(imgUrls)].filter(url => !url.includes('?width=50')).map(url => {
                        const urlObj = new URL(url);
                        urlObj.search = '?width=800'; 
                        return urlObj.toString();
                    });
                    data.images = uniqueImages.slice(0, 5); 
                } catch (e) {}

                // Save data
                if (data.name && data.name !== `Set ${set.id}`) set.name = data.name;
                if (data.pieces > 0) set.pieces = data.pieces;
                if (data.age) set.age = data.age;
                
                const setImgDir = path.join(IMAGES_DIR, set.id);
                if (!fs.existsSync(setImgDir)) fs.mkdirSync(setImgDir, { recursive: true });

                const localImages = [];
                for (let j = 0; j < data.images.length; j++) {
                    const imgUrl = data.images[j];
                    const localFilename = `${j}.png`;
                    const destPath = path.join(setImgDir, localFilename);
                    console.log(`   Downloading image ${j+1}/${data.images.length}...`);
                    await downloadImage(imgUrl, destPath);
                    localImages.push(`/images/${set.id}/${localFilename}`);
                }

                if (localImages.length > 0) {
                    set.thumbnail = localImages[0];
                    set.images = localImages;
                }

                const fullSetsIndex = sets.findIndex(s => s.id === set.id);
                if (fullSetsIndex !== -1) {
                    sets[fullSetsIndex] = set;
                    fs.writeFileSync(SETS_JSON_PATH, JSON.stringify(sets, null, 2));
                }
            } else {
                console.log(`   Failed to land on product page.`);
            }
        } catch (e) {
            console.error(`   Error processing ${set.id}:`, e.message);
        }

        if (i < setsToProcess.length - 1) {
            console.log(`   Waiting 4 seconds to avoid rate limits...`);
            await new Promise(resolve => setTimeout(resolve, 4000));
        }
    }

    await browser.close();
    console.log('\nScraping complete!');
}

const args = process.argv.slice(2);
const limit = args[0] ? parseInt(args[0]) : null;

run(limit).catch(console.error);
