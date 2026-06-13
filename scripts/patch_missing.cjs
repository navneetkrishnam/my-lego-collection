const fs = require('fs');
const path = require('path');

const SETS_JSON_PATH = path.join(__dirname, '../src/data/sets.json');

const updates = {
  "60320": { name: "LEGO City Fire Station", pieces: 540 },
  "60205": { name: "LEGO City Tracks", pieces: 20 },
  "60485": { name: "LEGO City Hot Rod", pieces: 0 },
  "60401": { name: "LEGO Construction Steamroller", pieces: 78 },
  "42669": { name: "LEGO Friends Beekeepers' House and Flower Garden", pieces: 1161 },
  "42687": { name: "LEGO Friends Liann's Family House", pieces: 946 },
  "42692": { name: "LEGO Friends Ice Cream & Balloon Stand", pieces: 107 },
  "42662": { name: "LEGO Friends Hair Salon and Accessories Store", pieces: 347 },
  "42644": { name: "LEGO Friends Heartlake City Ice Cream Truck", pieces: 92 },
  "30721": { name: "LEGO City Set 30721", pieces: 0 },
  "31172": { name: "LEGO Creator 3-in-1 Record Player with Flowers", pieces: 366 },
  "11508": { name: "LEGO Set 11508", pieces: 0 },
  "11506": { name: "LEGO Botanicals Rocking Plants", pieces: 0 },
  "21355": { name: "LEGO Ideas The Evolution of STEM", pieces: 0 },
  "10980": { name: "LEGO DUPLO Green Building Plate", pieces: 1 },
  "31209": { name: "LEGO Art The Amazing Spider-Man", pieces: 2099 }
};

let sets = JSON.parse(fs.readFileSync(SETS_JSON_PATH, 'utf-8'));

sets.forEach(set => {
  if (updates[set.id]) {
    set.name = updates[set.id].name;
    if (updates[set.id].pieces > 0) set.pieces = updates[set.id].pieces;
    
    const bricklinkImage = `https://img.bricklink.com/ItemImage/SN/0/${set.id}-1.png`;
    set.thumbnail = bricklinkImage;
    set.images = [bricklinkImage];
  }
});

fs.writeFileSync(SETS_JSON_PATH, JSON.stringify(sets, null, 2));
console.log("Patched 16 missing sets.");
