"""Relocate only copied/generated project paths; never touch firmware sources."""
from pathlib import Path
import os,re,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
def repair(project,base=ROOT):
    p=Path(project).resolve();base=Path(base).resolve()
    if base not in p.parents:raise ValueError('Project must be inside base')
    mk=p/'Makefile';s=mk.read_text(encoding='utf-8-sig')
    relative=os.path.relpath(base,p).replace('\\','/')
    s=re.sub(r'^BASE_ROOT\s*\??=.*\n','',s,flags=re.M)
    s='BASE_ROOT ?= '+relative+'\n'+s
    s=re.sub(r'^CC_PATH\s*:?=.*$',r'CC_PATH := $(BASE_ROOT)/00_Reference/Tools/NYC_NY8/app',s,flags=re.M)
    s=re.sub(r'-I"[^"\n]*00_Reference/include"',r'-I"$(BASE_ROOT)/00_Reference/include"',s)
    mk.write_text(s,encoding='ascii')
    for f in p.glob('*.naprj'):
        tree=ET.parse(f);root=tree.getroot()
        for key,sub in [('CCompilerInstallDir','00_Reference/Tools/NYC_NY8/app'),('NYASMInstallDir','00_Reference/Tools/NYASM/app'),('IncludePath','00_Reference/include')]:
            e=root.find('./PropertyGroup/'+key)
            if e is None:e=ET.SubElement(root.find('PropertyGroup'),key)
            e.text=str(base/sub)
        for e in root.iter('ApplicationDefinition'):
            old=e.get('Include','')
            if old.lower().endswith('.h'):e.set('Include',str(base/'00_Reference/include'/Path(old.replace('\\','/')).name))
        tree.write(f,encoding='utf-8',xml_declaration=True)
    return p

def validate(project):
    p=Path(project).resolve();s=(p/'Makefile').read_text(encoding='utf-8-sig')
    for old in re.findall(r'[A-Za-z]:[/\\][^"\r\n]*00_Reference[^"\r\n]*',s):
        if not old.replace('\\','/').lower().startswith(str(ROOT).replace('\\','/').lower()+'/'):
            raise ValueError('Stale Makefile base path; run Repair-ProjectPaths.ps1: '+old)
    for f in p.glob('*.naprj'):
        root=ET.parse(f)
        for key,sub in [('CCompilerInstallDir','00_Reference/Tools/NYC_NY8/app'),('NYASMInstallDir','00_Reference/Tools/NYASM/app'),('IncludePath','00_Reference/include')]:
            value=root.findtext('./PropertyGroup/'+key)
            if value and Path(value).resolve()!=ROOT/sub:
                raise ValueError('Project tool/include path differs from current base; run Repair-ProjectPaths.ps1: '+key)
if __name__=='__main__':
    if sys.argv[1]=='repair':repair(sys.argv[2])
    elif sys.argv[1]=='check':validate(sys.argv[2])
    else:raise SystemExit('Use repair/check PROJECT')
