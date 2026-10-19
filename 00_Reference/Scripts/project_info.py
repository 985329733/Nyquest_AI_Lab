"""Project identity and verified chip resource limits; no model defaults."""
from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
def assignments(path):
    return dict(re.findall(r'^\s*(\w+)\s*:?=\s*([^\n#]*)',path.read_text(encoding='utf-8-sig'),re.M))
def info(project):
    p=Path(project).resolve();mk=assignments(p/'Makefile');projects=list(p.glob('*.naprj'))
    xmlchip=ET.parse(projects[0]).findtext('.//ChipId') if len(projects)==1 else None
    chip=(mk.get('ICBODY') or xmlchip or '').strip().upper()
    if not re.fullmatch(r'NY8[A-Z0-9]+',chip):raise ValueError('Missing chip identity')
    if xmlchip and xmlchip.upper()!=chip:raise ValueError('Makefile/.naprj chip mismatch')
    rows=json.loads((ROOT/'00_Reference/Chip_Config/chips.json').read_text(encoding='utf-8-sig'))
    row=next((r for r in rows if r['chip']==chip),None)
    if row is None:raise ValueError('Missing chips.json entry: '+chip)
    if not isinstance(row.get('stack'),int) or row['stack']<1:raise ValueError(chip+': hardware stack pending verification; add datasheet evidence first')
    q=json.loads((ROOT/'00_Reference/Chip_Config/qualifications.json').read_text(encoding='utf-8-sig')).get(chip)
    if not q or q.get('stack')!=row['stack']:raise ValueError(chip+': missing qualification/reserved-space evidence')
    doc=ROOT/q['datasheet']
    if not doc.is_file() or hashlib.sha256(doc.read_bytes()).hexdigest()!=q['datasheet_sha256']:raise ValueError('Datasheet missing/changed: '+str(doc))
    model=mk.get('MODEL','').strip()
    if not model:raise ValueError('Makefile MODEL must be explicit')
    cfg=ROOT/'00_Reference/Tools/NYC_NY8/app/cfg'/('small' if 'small' in model else 'bankram')/(chip+'.cfg')
    m=re.search(r'\bprogram\s*:\s*start=\$([0-9a-f]+),\s*size=\$([0-9a-f]+)',cfg.read_text(),re.I)
    if not m:raise ValueError('Unrecognized cfg program region')
    word_bytes=(row['rom_word_bits']+7)//8;start=int(m[1],16)//word_bytes
    capacity=min(int(m[2],16)//word_bytes,row['rom_words']);reserved=q.get('checksum_reserved_words')
    if not isinstance(reserved,int) or reserved<0 or reserved>=capacity:raise ValueError('Missing checksum reserved words')
    output=mk.get('OUT_NAME_U',mk.get('OUT_NAME','')).strip()
    if not re.fullmatch(r'[A-Za-z0-9_]+',output):raise ValueError('Output name must be explicit English identifier')
    return dict(project=p,chip=chip,limits=row,qualification=q,cfg=cfg,model=model,output=output,rom_start=start,rom_end=start+capacity,rom_usable_end=start+capacity-reserved,ram_budget=min(row['ram70_bytes'],row['ram_bytes']*7//10),make=mk)
