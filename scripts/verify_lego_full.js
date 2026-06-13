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
const STATUS_FILE = '/Users/navneet/.gemini/antigravity-ide/brain/8417abfc-9a07-4510-a57f-c6bae378b12e/verification_status.md';

const ORIGINAL_IDS = [
    "30719", "60488", "60500", "60320", "60454", "60435", "60452", "60304", "60375", "60337", "60316", "60330", "60386", "60491", "60469", "60481", "60482", "60483", "60484", "60205", "60487", "60404", "60384", "60485", "60350", "60401", "60453", "60434", "42641", "42669", "41736", "42605", "42623", "42604", "42674", "42687", "42699", "42689", "42671", "41759", "30722", "30697", "42635", "42649", "42655", "42691", "42692", "41754", "42618", "42612", "42642", "42666", "42653", "42614", "41727", "42646", "42610", "42695", "42648", "42662", "42670", "42652", "42665", "42644", "42680", "30721", "42659", "41743", "42663", "31172", "31155", "31134", "40713", "31160", "31169", "31148", "31174", "31384", "31156", "40953", "31147", "30689", "31149", "31141", "40619", "43271", "10349", "10329", "10344", "30701", "11508", "11506", "21355", "21345", "21353", "40817", "40815", "40719", "11042", "11039", "10980", "40886", "11370", "21058", "21060", "30735", "42179", "31209", "10359"
];

async function downloadImage(url, destPath) {
    if (!url) return false;
    try {
        const response = await axios({
            url, method: 'GET', responseType: 'stream', timeout: 10000,
            headers: { 'User-Agent': 'Mozilla/5.0' }
        });
        const writer = fs.createWriteStream(destPath);
        response.data.pipe(writer);
        return new Promise((resolve, reject) => {
            writer.on('finish', resolve);
            writer.on('error', reject);
        });
    } catch (e) {
        return false;
    }
}

const START_INDEX = parseInt(process.argv[2]) || 0;

async function run() {
    let sets = [];
    if (fs.existsSync(SETS_JSON_PATH)) {
        sets = JSON.parse(fs.readFileSync(SETS_JSON_PATH, 'utf-8'));
    }
    
    // Create map for easy lookup
    let setsMap = {};
    for (const s of sets) {
        setsMap[s.id] = s;
    }

    if (!fs.existsSync(IMAGES_DIR)) fs.mkdirSync(IMAGES_DIR, { recursive: true });

    let statusLog = `# Lego.com Verification Status\n\n`;
    statusLog += `| Set ID | Name | Pieces | Age | Images | Status |\n`;
    statusLog += `|--------|------|--------|-----|--------|--------|\n`;
    fs.writeFileSync(STATUS_FILE, statusLog);

    console.log("Launching visible browser. Solving Cloudflare automatically if possible...");
    const browser = await puppeteer.launch({ 
        headless: false, 
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800'] 
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    for (let i = START_INDEX; i < ORIGINAL_IDS.length; i++) {
        const id = ORIGINAL_IDS[i];
        console.log(`\nVerifying [${i+1}/${ORIGINAL_IDS.length}]: Set #${id}`);
        
        let existingSet = setsMap[id] || { id, name: `Set ${id}`, pieces: 0, age: 'N/A', theme: 'Misc', status: 'Not Started', history: [] };
        let statusMsg = "Success";

        try {
            await page.goto(`https://www.lego.com/en-us/product/-${id}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
            
            // Wait to bypass Cloudflare
            let pageTitle = await page.title();
            if (pageTitle.includes("Just a moment") || pageTitle.includes("Cloudflare")) {
                console.log("   Cloudflare challenge detected...");
                while(pageTitle.includes("Just a moment") || pageTitle.includes("Cloudflare")) {
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    pageTitle = await page.title();
                }
            }

            // Handle Age Gate Modal ("LEGO.com" vs "Play Zone")
            try {
                const ageGateBtn = await page.waitForSelector('button[data-test="age-gate-grown-up-cta"], [data-test="age-gate-grown-up-cta"]', { timeout: 3000 });
                if (ageGateBtn) {
                    await ageGateBtn.click();
                    await new Promise(resolve => setTimeout(resolve, 1500));
                }
            } catch(e) {
                // Fallback to text search
                try {
                    await page.evaluate(() => {
                        const buttons = Array.from(document.querySelectorAll('button, a'));
                        const continueBtn = buttons.find(b => b.textContent && b.textContent.trim() === 'Continue');
                        if (continueBtn) continueBtn.click();
                    });
                    await new Promise(resolve => setTimeout(resolve, 1000));
                } catch(err) {}
            }

            // Cookie banner
            try {
                const acceptBtn = await page.$('button[data-test="cookie-accept-all"]');
                if (acceptBtn) await acceptBtn.click();
            } catch(e) {}

            await new Promise(resolve => setTimeout(resolve, 3000));

            let url = page.url();
            if (url.includes('/product/')) {
                // Extract Name
                try {
                    const titleEl = await page.$('h1 span');
                    if (titleEl) existingSet.name = await page.evaluate(el => el.textContent.trim(), titleEl);
                } catch (e) {}

                // Extract exact details mapping labels to values robustly
                const details = await page.evaluate(() => {
                    let res = { pieces: 0, age: 'N/A' };
                    
                    // Try the new Lego.com DOM
                    let ageVal = document.querySelector('[data-test="ages-value"]')?.textContent.trim();
                    let piecesVal = document.querySelector('[data-test="pieces-value"]')?.textContent.trim();
                    
                    if (ageVal) res.age = ageVal;
                    if (piecesVal) res.pieces = parseInt(piecesVal.replace(/\D/g, '')) || 0;

                    // Fallback to old mapping
                    if (res.age === 'N/A' || res.pieces === 0) {
                        const labels = Array.from(document.querySelectorAll('[data-test="product-details-label"]'));
                        labels.forEach(labelNode => {
                            const labelText = labelNode.textContent.trim().toLowerCase();
                            let valNode = labelNode.parentElement ? labelNode.parentElement.querySelector('[data-test="product-details-value"]') : null;
                            if (!valNode && labelNode.nextElementSibling) valNode = labelNode.nextElementSibling;

                            if (valNode) {
                                const valueText = valNode.textContent.trim();
                                if ((labelText === 'age' || labelText === 'ages') && res.age === 'N/A') res.age = valueText;
                                if (labelText === 'pieces' && res.pieces === 0) res.pieces = parseInt(valueText.replace(/\D/g, '')) || 0;
                            }
                        });
                    }
                    return res;
                });

                if (details.pieces > 0) existingSet.pieces = details.pieces;
                if (details.age !== 'N/A') existingSet.age = details.age;

                // Extract Images
                try {
                    const imgUrls = await page.$$eval('img', imgs => imgs.map(img => img.src).filter(src => src && src.includes('lego.com') && src.includes('/assets/')));
                    const uniqueImages = [...new Set(imgUrls)].filter(url => !url.includes('?width=50')).map(url => {
                        const urlObj = new URL(url);
                        urlObj.search = '?width=800'; 
                        return urlObj.toString();
                    });
                    
                    let imageList = uniqueImages.slice(0, 5);
                    const setImgDir = path.join(IMAGES_DIR, id);
                    if (!fs.existsSync(setImgDir)) fs.mkdirSync(setImgDir, { recursive: true });

                    const localImages = [];
                    for (let j = 0; j < imageList.length; j++) {
                        const imgUrl = imageList[j];
                        const localFilename = `${j}.png`;
                        const destPath = path.join(setImgDir, localFilename);
                        await downloadImage(imgUrl, destPath);
                        localImages.push(`/images/${id}/${localFilename}`);
                    }

                    if (localImages.length > 0) {
                        existingSet.thumbnail = localImages[0];
                        existingSet.images = localImages;
                    }
                } catch (e) {}

            } else {
                statusMsg = "Redirected / Retired Set";
                console.log(`   Page redirected. Likely a retired set.`);
            }
        } catch (e) {
            statusMsg = `Failed: ${e.message.split('\\n')[0]}`;
            console.error(`   Error processing ${id}:`, e.message);
        }

        setsMap[id] = existingSet;
        
        // Write status to artifact
        let imgCount = existingSet.images ? existingSet.images.length : 0;
        let line = `| ${existingSet.id} | ${existingSet.name} | ${existingSet.pieces} | ${existingSet.age} | ${imgCount} | ${statusMsg} |\n`;
        fs.appendFileSync(STATUS_FILE, line);

        // Save JSON incrementally
        let finalSets = ORIGINAL_IDS.map(mappedId => setsMap[mappedId]);
        fs.writeFileSync(SETS_JSON_PATH, JSON.stringify(finalSets, null, 2));

        if (i < ORIGINAL_IDS.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }

    await browser.close();
    console.log('\nFull Verification Complete!');
}

run().catch(console.error);
