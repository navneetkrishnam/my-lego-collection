// Exercise the offline guide's data/filter/pagination logic without a browser UI.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const html=fs.readFileSync(path.join(here,'guide.html'),'utf8');
const payload=html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
const data=JSON.parse(payload),saved=JSON.parse(fs.readFileSync(path.join(here,'model.json'),'utf8'));
assert.deepEqual(data.model,saved);
const nodes=new Map();
function element(id){if(!nodes.has(id))nodes.set(id,{value:'',textContent:'',innerHTML:'',children:[],listeners:{},add(o){this.children.push(o)},addEventListener(k,f){this.listeners[k]=f}});return nodes.get(id)}
element('data').textContent=payload;
element('tabs').children=['placements','parts','donors'].map(mode=>({dataset:{mode},classList:{toggle(){}}}));
const context=vm.createContext({document:{getElementById:element},Option:class{constructor(text,value){this.text=text;this.value=value}}});
new vm.Script(script).runInContext(context);
assert.match(element('count').textContent,/2,188 placements/);
assert.equal((element('rows').innerHTML.match(/<tr>/g)||[]).length,60);
element('next').onclick();assert.ok(element('rows').innerHTML.includes(data.model.pieces[60].key));
let staged=0;
for(const s of data.model.steps){element('stage').value=String(s.number);element('stage').listeners.change();const n=data.model.pieces.filter(p=>p.step===s.number).length;assert.ok(element('count').textContent.startsWith(n.toLocaleString()+' placements'));staged+=n}
assert.equal(staged,data.model.pieces.length);
element('stage').value='';element('stage').listeners.change();
element('search').value='H00001';element('search').listeners.input();assert.ok(element('count').textContent.startsWith('1 placements'));
element('search').value='does-not-exist';element('search').listeners.input();assert.ok(element('count').textContent.startsWith('0 placements'));assert.equal(element('rows').innerHTML,'');
element('search').value='';element('search').listeners.input();
for(const mode of ['parts','donors']){const button=element('tabs').children.find(b=>b.dataset.mode===mode);element('tabs').listeners.click({target:button});assert.equal((element('rows').innerHTML.match(/<tr>/g)||[]).length,60)}
assert.ok(element('count').textContent.includes('1557 table rows'));
let links=0;
for(const match of html.split('<script id="data"')[0].matchAll(/(?:src|href)="([^"]+)"/g)){const target=match[1];if(/^https?:/.test(target)||target.startsWith('#'))continue;assert.ok(fs.existsSync(path.join(here,target)),`Missing local link: ${target}`);links++}
const report={guide_matches_model:true,placements_checked:data.model.pieces.length,stages_checked:data.model.steps.length,picking_elements:data.bom.length,donor_rows:data.allocation.length,local_links_checked:links,script_syntax_and_execution:true,filtering_and_pagination:true,browser_visual_check:false,browser_visual_check_reason:'No browser available through the computer-use tool.'};
fs.writeFileSync(path.join(here,'guide-verification.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
