"""Verify the PDF placement rows, page bounds and exact cover render."""
import json
from pathlib import Path
import re
import pymupdf
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
pdf=ROOT/'output/pdf/fern-and-steam-courtyard-build-draft.pdf'
doc=pymupdf.open(pdf)
text='\n'.join(page.get_text() for page in doc)
keys=[p['key'] for p in json.loads((HERE/'model.json').read_text())['pieces']]
bad={k:n for k in keys if (n:=len(re.findall(r'(?m)^'+k+r'$',text)))!=1}
clipped=[]
for i,page in enumerate(doc):
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<0 or y0<0 or x1>page.rect.width or y1>page.rect.height:
                    clipped.append([i+1,span['text']])
preview=Image.open(HERE/'preview.png').convert('RGB')
cover_matches=False
for image in doc[0].get_images(full=True):
    pix=pymupdf.Pixmap(doc,image[0])
    if (pix.width,pix.height)==preview.size and pix.n==3:
        cover_matches=pix.samples==preview.tobytes()
report={'pages':len(doc),'placement_rows_checked':len(keys),'missing_or_duplicated_rows':bad,
        'clipped_text':clipped,'cover_matches_current_preview':cover_matches}
(HERE/'guide-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if bad or clipped or not cover_matches:raise SystemExit(1)
