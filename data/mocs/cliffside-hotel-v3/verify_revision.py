"""Validate repeatability, allocations, evidence, and freshness of review artifacts."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,argparse,csv
from hotel import author
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((H/name).read_text())

def run(pdf_dir):
    model=read('model.json');snapshot=read('inventory-snapshot.json')
    generated,roof=author()
    assert len(generated.pieces)<=3500,'Exceeds the user-approved piece ceiling'
    assert not any(q.get('hinge_parent') or q.get('pose_type')=='pitched_roof_panel' for q in generated.pieces),'Old hinged roof remains'
    assert generated.pieces==model['pieces'],'Placement regeneration differs'
    assert roof==model['roof'],'Roof metadata differs'
    used=Counter(q['element'] for q in model['pieces'])
    bom=read('bom.json');allocation=read('allocation.json')
    for name,rows in [('parts-list.csv',bom),('donor-picking-list.csv',allocation)]:
        with (H/name).open(newline='') as file:csv_rows=list(csv.DictReader(file))
        assert len(csv_rows)==len(rows),'Stale CSV: '+name
        for csv_row,row in zip(csv_rows,rows):
            assert all(csv_row[k]==str(row.get(k,'')) for k in csv_row),'CSV differs: '+name
    assert {r['element']:r['required'] for r in bom}==dict(used)
    allocated=Counter();by_source=Counter()
    for r in allocation:
        allocated[r['element']]+=r['quantity']
        by_source[r['element'],r['set'],r['copy']]+=r['quantity']
    assert allocated==used
    for (element,donor,copy),quantity in by_source.items():
        available=next(r['quantity'] for r in snapshot['parts'][element]['sources'] if r['set']==donor and r['copy']==copy)
        assert quantity<=available,(element,donor,copy)
    for p,digest in snapshot['input_sha256'].items():
        assert sha(H.parents[2]/p)==digest,'Inventory source changed: '+p
    mesh=read('geometry-verification.json');connections=read('verification.json')
    assert connections['model_sha256']==mesh['model_sha256']==sha(H/'model.json')
    assert connections['digital_checks_pass']
    assert not mesh['bounds_errors'] and not mesh['strict_surface_crossings']
    for name in ['hotel-preview','hotel-preview-rear']:
        render=read(name+'.render.json')
        assert render['input_sha256']==sha(H/'hotel.ldr'),'Stale render: '+name
    ldr=(H/'hotel.ldr').read_text()
    assert len([line for line in ldr.splitlines() if line.startswith('1 ')])==len(model['pieces'])
    evidence=read('verified-donor-quantities.json');verified=0
    if pdf_dir:
        import pymupdf
        documents={s:pymupdf.open(pdf_dir/d['file']) for s,d in evidence['source_documents'].items()}
        for s,d in evidence['source_documents'].items():assert sha(pdf_dir/d['file'])==d['sha256']
        for r in evidence['rows']:
            text=documents[r['set']][r['printed_page']-1].get_text()
            assert (str(r['quantity']),r['element']) in re.findall(r'(\d+)x\s+(\d{5,8})',text),r
            verified+=1
    result=dict(piece_count=len(model['pieces']),exact_elements=len(used),donor_sets=len({r['set'] for r in allocation}),
                allocation_rows=len(allocation),deterministic_placements=True,allocation_pass=True,
                current_digital_reports_pass=True,current_render_hashes_pass=True,
                instruction_quantity_rows_verified=verified,model_sha256=sha(H/'model.json'),ldr_sha256=sha(H/'hotel.ldr'),
                visual_status='Review draft; taller cliff, turning stairs and stud-connected hip roofs; roof texture remains stylized',
                physical_build_tested=False)
    (H/'reproducibility.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pdf-dir',type=Path)
    run(parser.parse_args().pdf_dir)
