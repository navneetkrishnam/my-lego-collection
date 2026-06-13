import fs from 'fs';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

const DATA_FILE = './src/data/sets.json';
const START_INDEX = process.argv[2] ? parseInt(process.argv[2], 10) : 0;

async function run() {
    console.log(`Starting theme verification from index ${START_INDEX}...`);
    let sets = [];
    try {
        sets = JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));
    } catch (e) {
        console.error("Failed to read sets.json");
        process.exit(1);
    }

    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    // Block unnecessary resources for speed
    await page.setRequestInterception(true);
    page.on('request', (req) => {
        const type = req.resourceType();
        if (['image', 'stylesheet', 'font', 'media'].includes(type)) {
            req.abort();
        } else {
            req.continue();
        }
    });

    for (let i = START_INDEX; i < sets.length; i++) {
        const set = sets[i];
        console.log(`[${i+1}/${sets.length}] Verifying Theme for Set ${set.id} - ${set.name}...`);
        
        try {
            await page.goto(`https://www.lego.com/en-us/product/-${set.id}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
            
            // Wait briefly for breadcrumbs to render
            await new Promise(r => setTimeout(r, 1500));
            
            const theme = await page.evaluate(() => {
                const el = document.querySelector('[data-test="breadcrumb-1"]');
                if (el) return el.textContent.trim();
                
                // Fallback: sometimes the theme is in a product overview link
                const overviewLink = document.querySelector('[data-test^="product-overview-category-"]');
                if (overviewLink) return overviewLink.textContent.trim();
                
                return null;
            });
            
            if (theme) {
                console.log(`   -> Theme found: ${theme}`);
                sets[i].theme = theme;
                // Save incrementally
                fs.writeFileSync(DATA_FILE, JSON.stringify(sets, null, 2));
            } else {
                console.log(`   -> WARNING: No theme found for ${set.id}`);
            }
            
        } catch (e) {
            console.error(`   -> ERROR processing ${set.id}: ${e.message}`);
        }
        
        // Random delay to avoid rate limiting
        await new Promise(r => setTimeout(r, 1000 + Math.random() * 2000));
    }

    console.log("Completed Theme Verification!");
    await browser.close();
}

run();
