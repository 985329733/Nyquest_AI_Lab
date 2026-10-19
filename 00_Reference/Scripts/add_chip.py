"""Generic, evidence-gated onboarding of an exact chip from its vendor project."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys,xml.etree.ElementTree as ET
from datetime import datetime
from project_paths import ROOT,repair

def pdf_pages(path):
    candidates=[Path(os.environ.get('NYQUEST_PDF_PYTHON',sys.executable))]
    code='import json,sys;from pypdf import PdfReader;print(json.dumps([p.extract_text() for p in PdfReader(sys.argv[1]).pages]))'
    for exe in candidates:
        if not exe.is_file():continue
        r=subprocess.run([str(exe),'-c',code,str(path)],capture_output=True,text=True,encoding='utf-8',errors='replace',env={**os.environ,'PYTHONIOENCODING':'utf-8'})
        if r.returncode==0:return json.loads(r.stdout)
    raise ValueError('Install pypdf with requirements.txt, or select its Python runtime with NYQUEST_PDF_PYTHON')

def onboard(chip,evidence=None,inspect=False):
    chip=chip.upper()
    if not re.fullmatch(r'NY8[A-Z0-9]+',chip):raise ValueError('Use exact chip identifier')
    target=ROOT/'00_Reference/Templates'/(chip+'_Validated')
    if target.exists() and not inspect:raise ValueError('Template exists; preserved without overwrite: '+str(target))
    family='NY8A' if chip.startswith('NY8A') else 'NY8B' if chip.startswith('NY8B') else None
    source=ROOT/'00_Reference/Templates/Official_C'/str(family)/chip
    projects=sorted(source.rglob('*.naprj')) if source.exists() else []
    gpio=[p for p in projects if p.stem.upper()=='GPIO']
    selected=gpio[0] if len(gpio)==1 else projects[0] if len(projects)==1 else None
    h=ROOT/'00_Reference/include'/(chip.lower()+'.h')
    registry=ROOT/'00_Reference/Chip_Config/chips.json';rows=json.loads(registry.read_text(encoding='utf-8-sig'));row=next((r for r in rows if r['chip']==chip),None)
    ev=Path(evidence).resolve() if evidence else ROOT/'00_Reference/Chip_Config/Chip_Evidence'/(chip+'.json')
    missing=[]
    if not selected:missing.append('An unambiguous complete official project (prefer GPIO) for this exact chip')
    if not h.is_file():missing.append('Matching C header: '+str(h))
    if row is None:missing.append('chips.json ROM/RAM entry')
    if not ev.is_file():missing.append('Datasheet + evidence JSON: '+str(ev))
    if missing:raise ValueError('Chip onboarding stopped; missing:\n- '+'\n- '.join(missing))
    e=json.loads(ev.read_text(encoding='utf-8-sig'))
    for key in ('datasheet','datasheet_sha256','stack','stack_page','reserved_page','rom_words','ram_bytes','checksum_reserved_words','r_page_address_bits','model','gpio_input_masks','quotes','adc','pwm'):
        if key not in e:missing.append('Evidence field: '+key)
    if e.get('chip')!=chip:missing.append('Evidence chip identity mismatch')
    doc=ROOT/e.get('datasheet','__missing__')
    if not doc.is_file():missing.append('Official datasheet file')
    if missing:raise ValueError('Chip onboarding stopped; missing:\n- '+'\n- '.join(missing))
    if hashlib.sha256(doc.read_bytes()).hexdigest()!=e['datasheet_sha256']:raise ValueError('Datasheet SHA256 mismatch')
    pages=pdf_pages(doc)
    normalize=lambda s:re.sub(r'\s+','',s)
    for q in e['quotes']:
        if normalize(q['text']) not in normalize(pages[q['page']-1]):raise ValueError('Datasheet quote/page mismatch: '+q['text'])
    stack_text=pages[e['stack_page']-1]
    stack_match=re.search(r'(\d+)\s*(?:層|级|[- ]level)',stack_text,re.I)
    if not stack_match or int(stack_match[1])!=e['stack']:raise ValueError('Hardware stack value is not supported by the cited page')
    reserved_text=pages[e['reserved_page']-1]
    reserved_ranges=re.findall(r'0x([0-9a-f]+)\s*[~～–-]\s*0x([0-9a-f]+)\b',reserved_text,re.I)
    if not any(int(start,16)==e['rom_words']-e['checksum_reserved_words'] and int(end,16)==e['rom_words']-1 for start,end in reserved_ranges):raise ValueError('Final reserved range is not supported by the cited page')
    if not e['quotes'] or not isinstance(e['stack'],int) or e['stack']<1:raise ValueError('Verified stack evidence required')
    if e.get('rom_words')!=row['rom_words'] or e.get('ram_bytes')!=row['ram_bytes']:raise ValueError('Datasheet/registry ROM/RAM mismatch')
    sdk=ROOT/'00_Reference/Tools/NYC_NY8/app';model=e['model']
    cfg=sdk/'cfg'/('small' if 'small' in model else 'bankram')/(chip+'.cfg')
    for path in [cfg,sdk/'inc'/(chip.lower()+'.inc'),sdk/'lib/startup'/(model+'.a'),sdk/'lib'/(chip.lower()+'.a')]:
        if not path.is_file():missing.append('Required toolchain file: '+str(path))
    header=h.read_text(encoding='ascii')
    for port,mask in e['gpio_input_masks'].items():
        if not re.fullmatch(r'PORT[A-Z]',port) or not isinstance(mask,int) or not 0<=mask<=255 or not re.search(r'\b'+port+r'\b',header):missing.append('Verified GPIO mask for '+port)
    if missing:raise ValueError('Chip onboarding stopped; missing:\n- '+'\n- '.join(missing))
    if inspect:return {'chip':chip,'official_project':str(selected),'datasheet':str(doc),'ready_for_compile':True}
    work=ROOT/'00_Reference/Validation/Chip_Onboarding'/(chip+'_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    work.mkdir(parents=True);shutil.copytree(selected.parent,work,dirs_exist_ok=True)
    # Retain the complete vendor input separately; alter only the working copy.
    snapshots=work/'Vendor_Original';shutil.copytree(selected.parent,snapshots)
    stem='Qualification_'+chip
    old=work/selected.name;tree=ET.parse(old);g=tree.getroot().find('PropertyGroup')
    for key,value in {'ChipId':chip,'AssemblyName':stem,'RootNamespace':stem,'InitializeBss':'True','Bank0Only':'True','ReservedRam':'8','ReservedInterruptRam':'2'}.items():
        node=g.find(key)
        if node is None:node=ET.SubElement(g,key)
        node.text=value
    cb=next(work.glob('*.cb'));original_cb_sha=hashlib.sha256(cb.read_bytes()).hexdigest();newcb=work/(stem+'.cb');cb.rename(newcb)
    for node in tree.getroot().iter():
        include=node.get('Include')
        if include:
            if include.lower().endswith('.cb'):node.set('Include',newcb.name)
            elif include.startswith('Config Block:'):node.set('Include','Config Block: '+newcb.name)
    old.unlink();tree.write(work/(stem+'.naprj'),encoding='utf-8',xml_declaration=True)
    solution=selected.parent.parent/(selected.stem+'.NySln')
    if solution.is_file():
        text=solution.read_text(encoding='utf-8-sig').replace(selected.stem+'\\'+selected.name,stem+'.naprj').replace(selected.stem,stem)
        (work/(stem+'.NySln')).write_text(text,encoding='utf-8-sig')
    vendor=(ROOT/'00_Reference/Templates/Vendor_Makefile/makefile_ny8C.template').read_text()
    values={'ICBody':chip,'ClientName':'AI_Base','ConfigBlockSp':newcb.name,'HostTool':'NYIDE','CFiles':'main.c','ProjectName':stem,'ProjectNameDealWithSpace':stem,'NYC_NY8_Path':'$(BASE_ROOT)/00_Reference/Tools/NYC_NY8/app','LinkLib':model,'InitBss':'1','MapFlag':'--mapfile','ListFlag':'--disasm','DebugFlag':'-g','DebugFlag_C':'--debug','CInit':'--cinit','ProgramChecksum':'--programchecksum','IncludePath':'-I"$(BASE_ROOT)/00_Reference/include"','ReservedRamFlag':'--stack-size 8','ReservedInterruptRamFlag':'--backup-stk 2','CodeOptimizationFlag':'--opt-code-size','CultureString':'--lang en-us'}
    (work/'Makefile').write_text(re.sub(r'%%(\w+)%%',lambda m:values.get(m[1],''),vendor),encoding='ascii')
    code=['/* Chip qualification idle probe only. Not a finished product. */','#define LED_ON 0','#include <ny8.h>','volatile unsigned char qualification_counter;','void main(void)','{','    DISI();']
    for port in e['gpio_input_masks']:code.append('    '+port+' = 0;')
    for port,mask in e['gpio_input_masks'].items():code.append('    IOST'+port[-1]+' = '+str(mask)+';')
    for reg in ['APHCON','BPHCON','BPLCON','ABPLCON']:
        if re.search(r'\b'+reg+r'\b',header):code.append('    '+reg+' = 255;')
    code+=['    PCONbits.WDTEN = 1;','    qualification_counter = 0;','    while (1) {','        CLRWDT();','        ++qualification_counter;','    }','}']
    (work/'main.c').write_text('\n'.join(code)+'\n',encoding='ascii')
    shutil.copy2(ROOT/'00_Reference/Templates/Idle_Probe_Behavior.py',work/'behavior_tests.py')
    qualpath=ROOT/'00_Reference/Chip_Config/qualifications.json';oldreg=registry.read_bytes();oldqual=qualpath.read_bytes();qual=json.loads(oldqual)
    qual[chip]=e;row['stack']=e['stack'];row['adc']=e['adc'];row['pwm']=e['pwm']
    try:
        registry.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');qualpath.write_text(json.dumps(qual,ensure_ascii=False,indent=2),encoding='utf-8')
        repair(work)
        inspect_cfg=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'00_Reference/Scripts/Inspect-Configuration.ps1'),'-ProjectDir',str(work)],capture_output=True,text=True,errors='replace')
        if inspect_cfg.returncode:raise ValueError('Configuration gate: '+inspect_cfg.stdout+inspect_cfg.stderr)
        from verification_contract import read_json, write_json
        actual=read_json(work/'Configuration_Readback.json')
        checks=['Counter initialized','Watchdog enabled in software','Counter wraps as an 8-bit value','Hardware stack bound respected']
        for port in e['gpio_input_masks']:
            checks += [port+' safe latch',port+' direction']
        write_json(work/'Project_Profile.json', {'schema_version':1,'chip':chip,'configuration':{k:v for k,v in actual.items() if k not in ('schema_version','cb_sha256')},'clock':{'oscillator_hz':4000000,'instruction_divider':4},'behavior':{'required_checks':checks}})
        result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'Build.ps1'),'-Project',str(work)],capture_output=True,text=True,errors='replace')
        print(result.stdout)
        if result.returncode:raise ValueError('Onboarding build/model failed: '+result.stderr)
        if hashlib.sha256(newcb.read_bytes()).hexdigest()!=original_cb_sha:raise ValueError('Original configuration bytes changed')
        report={'status':'PASS','chip':chip,'source_project':str(selected.relative_to(ROOT)),'datasheet':e['datasheet'],'reason':e.get('reason','Evidence available'),'scope':'Independent compiler/linker/static gates and idle instruction-model smoke only; not product/bench acceptance','firmware_sha256':hashlib.sha256((work/(stem+'.bin')).read_bytes()).hexdigest()}
        (work/'Qualification_Verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        (work/'README_For_Engineer.md').write_text('# '+chip+' 芯片接入母版\n\n这是未接产品负载的资格测试母版，不是成品功能。复制自对应官方完整GPIO工程，原件副本在Vendor_Original，官方文件原目录未改。\n\n引脚：'+str(e['gpio_input_masks'])+'；各PORT先写0，再按上述输入掩码设置方向，其余脚为低输出，只适用于未连接外部驱动的资格夹具。新产品先填写需求表，重做引脚和有效电平。\n\n状态：上电初始化后8位counter循环递增；主循环喂狗，无ISR、无产品定时器。没有设置产品关机时间。\n\n配置继承对应型号的官方cb，具体值见Configuration_Readback.json。当前配置不代表实际产品供电/LVR、复位脚或负载要求已经确认，开发产品前必须重新核对，不能把062D配置套用。\n\n编译、资源、自建模型通过；实板未测。请参考基地00_Reference/Templates/Bench_Test_Checklist.md，产品实测回填项目Bench_Results.md。\n',encoding='utf-8')
        shutil.copytree(work,target,ignore=shutil.ignore_patterns('OBJ','__pycache__'));repair(target)
        specs=ROOT/'00_Reference/Chip_Specs.md';lines=specs.read_text(encoding='utf-8').splitlines()
        for i,line in enumerate(lines):
            if line.startswith('| '+chip+' |'):
                fields=line.split('|');fields[5]=' '+str(e['stack'])+' ';fields[6]=' '+e['adc']+' ';fields[7]=' '+e['pwm']+' ';lines[i]='|'.join(fields)
        lines+=['','## '+chip+' 接入补证','',f'官方手册：`{e["datasheet"]}`，堆栈第{e["stack_page"]}页、保留区第{e["reserved_page"]}页；ROM/RAM与配置数据库一致。资格证据：`Templates/{chip}_Validated/Qualification_Verification.json`。只是编译与空闲探针验证，未替用户选型、未实板验收。']
        specs.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        return report
    except Exception:
        registry.write_bytes(oldreg);qualpath.write_bytes(oldqual)
        raise
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('chip');parser.add_argument('--evidence');parser.add_argument('--inspect',action='store_true');a=parser.parse_args()
    print(json.dumps(onboard(a.chip,a.evidence,a.inspect),ensure_ascii=False,indent=2))
