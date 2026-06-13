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

const missingIds = [
    "60320", "60205", "60485", "60401", "42669", "42687", "42692", "42662", 
    "42644", "30721", "31172", "11508", "11506", "21355", "10980", "31209"
];

async function downloadImage(url, destPath) {
    if (!url) return false;
    try {
        const response = await axios({
            url,
            method: 'GET',
            responseType: 'stream',
            timeout: 10000,
            headers: { 'User-Agent': 'Mozilla/5.0' }
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

async function run() {
    let sets = JSON.parse(fs.readFileSync(SETS_JSON_PATH, 'utf-8'));
    
    if (!fs.existsSync(IMAGES_DIR)) {
        fs.mkdirSync(IMAGES_DIR, { recursive: true });
    }

    console.log("Launching fallback scraper for Brickset...");
    const browser = await puppeteer.launch({ 
        headless: 'new', // Brickset is less strict than Lego.com
        args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    });
    
    const page = await browser.newPage();
    // Block unnecessary requests
    await page.setRequestInterception(true);
    page.on('request', request => {
        if (['font', 'media'].includes(request.resourceType())) request.abort();
        else request.continue();
    });

    for (let i = 0; i < missingIds.length; i++) {
        const setId = missingIds[i];
        console.log(`\nProcessing ${i+1}/${missingIds.length}: ${setId}`);
        
        try {
            // Usually sets have a -1 suffix on Brickset
            await page.goto(`https://brickset.com/sets/${setId}-1`, { waitUntil: 'domcontentloaded', timeout: 30000 });
            
            // Check if page not found
            const pageTitle = await page.title();
            if (pageTitle.includes('Page not found') || pageTitle.includes('Search')) {
                console.log(`   Set not found directly, trying search...`);
                await page.goto(`https://brickset.com/sets?query=${setId}`, { waitUntil: 'domcontentloaded' });
                // Click first result if available
                try {
                    const firstResult = await page.$('.set');
                    if (firstResult) {
                        const link = await firstResult.$eval('h1 a', el => el.href);
                        if (link) await page.goto(link, { waitUntil: 'domcontentloaded' });
                    }
                } catch(e) {}
            }

            // Extract Data
            const data = { images: [] };
            
            try {
                const titleEl = await page.$('h1');
                if (titleEl) {
                    const fullText = await page.evaluate(el => el.textContent.trim(), titleEl);
                    // Usually "60320: Fire Station"
                    data.name = fullText.split(':').slice(1).join(':').trim() || fullText;
                }
            } catch (e) {}

            try {
                // Feature list usually has Pieces, Minifigs, Age, etc
                const dlText = await page.evaluate(() => {
                    const dl = document.querySelector('.featurebox dl');
                    if (!dl) return '';
                    return dl.innerText;
                });
                
                // Parse the DL text
                const lines = dlText.split('\n');
                for (let j = 0; j < lines.length; j++) {
                    if (lines[j].toLowerCase().includes('pieces') && lines[j+1]) {
                        data.pieces = parseInt(lines[j+1].replace(/\D/g, '')) || 0;
                    }
                    if (lines[j].toLowerCase().includes('age range') && lines[j+1]) {
                        data.age = lines[j+1].trim();
                    }
                }
            } catch (e) {}

            try {
                // Get main image
                const mainImg = await page.$('.mainimg img');
                if (mainImg) {
                    let src = await page.evaluate(el => el.src, mainImg);
                    if (src) data.images.push(src);
                }
                
                // Try to get alternate images from thumbnail gallery
                const altImgs = await page.$$eval('.pic a', els => els.map(el => el.href).filter(href => href.match(/\.(jpg|png)$/i)));
                if (altImgs && altImgs.length > 0) {
                    data.images.push(...altImgs);
                }
            } catch (e) {}

            const uniqueImages = [...new Set(data.images)].slice(0, 5);

            // Save data
            const targetSet = sets.find(s => s.id === setId);
            if (!targetSet) continue;

            if (data.name && data.name !== `Set ${setId}`) targetSet.name = data.name;
            if (data.pieces > 0) targetSet.pieces = data.pieces;
            if (data.age) targetSet.age = data.age;
            
            const setImgDir = path.join(IMAGES_DIR, setId);
            if (!fs.existsSync(setImgDir)) fs.mkdirSync(setImgDir, { recursive: true });

            const localImages = [];
            for (let j = 0; j < uniqueImages.length; j++) {
                const imgUrl = uniqueImages[j];
                const localFilename = `${j}.jpg`;
                const destPath = path.join(setImgDir, localFilename);
                console.log(`   Downloading image ${j+1}/${uniqueImages.length}...`);
                await downloadImage(imgUrl, destPath);
                localImages.push(`/images/${setId}/${localFilename}`);
            }

            if (localImages.length > 0) {
                targetSet.thumbnail = localImages[0];
                targetSet.images = localImages;
            } else {
                console.log(`   No images found on Brickset.`);
            }

            fs.writeFileSync(SETS_JSON_PATH, JSON.stringify(sets, null, 2));
            
        } catch (e) {
            console.error(`   Error processing ${setId}:`, e.message);
        }

        if (i < missingIds.length - 1) {
            console.log(`   Waiting 2 seconds...`);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }

    await browser.close();
    console.log('\nFallback scraping complete!');
}

run().catch(console.error);
