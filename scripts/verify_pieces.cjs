const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

const SETS_JSON_PATH = path.join(__dirname, '../src/data/sets.json');

async function run() {
    let sets = JSON.parse(fs.readFileSync(SETS_JSON_PATH, 'utf-8'));
    console.log(`Verifying piece counts for sets (with rate limit handling)...`);

    let updatedCount = 0;

    for (let i = 0; i < sets.length; i++) {
        const set = sets[i];
        
        let success = false;
        let attempts = 0;

        while (!success && attempts < 3) {
            attempts++;
            try {
                let url = `https://brickset.com/sets/${set.id}-1`;
                let response = await axios.get(url, {
                    headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' },
                    validateStatus: false
                });

                if (response.status === 429) {
                    console.log(`[${set.id}] Rate limited (429). Waiting 10 seconds...`);
                    await new Promise(r => setTimeout(r, 10000));
                    continue; // Retry
                }

                if (response.status === 404) {
                    url = `https://brickset.com/sets/${set.id}`;
                    response = await axios.get(url, {
                        headers: { 'User-Agent': 'Mozilla/5.0' },
                        validateStatus: false
                    });
                }

                if (response.status === 200) {
                    const $ = cheerio.load(response.data);
                    
                    let newPieces = null;
                    $('.featurebox dl dt').each((idx, el) => {
                        const term = $(el).text().toLowerCase();
                        if (term.includes('pieces')) {
                            const val = $(el).next('dd').text().trim();
                            const num = parseInt(val.replace(/\D/g, ''));
                            if (!isNaN(num) && num > 0) {
                                newPieces = num;
                            }
                        }
                    });

                    if (newPieces && newPieces !== set.pieces) {
                        console.log(`[${set.id}] Updated pieces: ${set.pieces} -> ${newPieces}`);
                        set.pieces = newPieces;
                        updatedCount++;
                    } else if (!newPieces) {
                        console.log(`[${set.id}] No piece count found. Current: ${set.pieces}`);
                    } else {
                        console.log(`[${set.id}] Pieces already correct: ${set.pieces}`);
                    }
                    success = true;
                } else {
                    console.log(`[${set.id}] Failed to load Brickset page (Status: ${response.status})`);
                    success = true; // Stop retrying on 404/500
                }
            } catch (e) {
                console.error(`[${set.id}] Error: ${e.message}`);
                await new Promise(r => setTimeout(r, 5000));
            }
        }

        // Save progress every 10 updates so we don't lose data
        if (updatedCount > 0 && updatedCount % 10 === 0) {
            fs.writeFileSync(SETS_JSON_PATH, JSON.stringify(sets, null, 2));
        }

        // Polite delay of 3 seconds to avoid 429s
        if (i < sets.length - 1) {
            await new Promise(r => setTimeout(r, 3000));
        }
    }

    fs.writeFileSync(SETS_JSON_PATH, JSON.stringify(sets, null, 2));
    console.log(`\nSuccessfully updated ${updatedCount} piece counts!`);
}

run();
