"""Fail-closed source, linked call-stack, resource and RIFF checks."""
from pathlib import Path
import sys,re,json,hashlib
from project_info import info
def strip_comments(t):
    return re.sub(r'/\*.*?\*/|//[^\n]*',lambda m:'\n'*m[0].count('\n'),t,flags=re.S)
def functions(text):
    text=strip_comments(text)
    pat=r'\b([A-Za-z_]\w*)\s*\([^{};]*\)\s*(?:__\w+\s*(?:\([^{};]*\))?\s*)*\{'
    for m in re.finditer(pat,text):
        if m[1] in ('if','while','for','switch'):continue
        depth=1;i=m.end()
        while i<len(text) and depth:
            if text[i]=='{':depth+=1
            elif text[i]=='}':depth-=1
            i+=1
        if depth:raise ValueError('Unbalanced braces')
        yield m[1],text[m.start():m.end()],text[m.end():i-1]
def parse_listing(path):
    result={}
    for l in path.read_text(encoding='utf-8-sig').splitlines():
        m=re.match(r'([0-9a-f]{8})\s+[0-9a-f]{4}\s+(\w+)\s*(.*)',l,re.I)
        if m:result[int(m[1],16)]=(m[2].upper(),m[3].split(';')[0].strip())
    if not result:raise ValueError('Empty/unsupported linked listing')
    return result
def linked_depth(program,root):
    todo=[(root,())];seen=set();peak=0
    while todo:
        pc,stack=todo.pop()
        if (pc,stack) in seen:continue
        seen.add((pc,stack))
        if pc not in program:raise ValueError(f'Unresolved executable address 0x{pc:x}')
        op,arg=program[pc];peak=max(peak,len(stack))
        if len(stack)>2:raise ValueError('Linked call nesting exceeds 2; recursion or compiler helper chain')
        if op in ('CALLA','GOTOA','FCALLA','INT'):raise ValueError('Unbounded indirect/software-interrupt flow: '+op)
        if op in ('LCALL','CALL','FCALL','LGOTO','GOTO','FGOTO'):
            m=re.match(r'0x([0-9a-f]+)',arg,re.I)
            if not m:raise ValueError('Unresolved linked call/jump: '+arg)
            todo.append((int(m[1],16),stack+(pc+1,) if 'CALL' in op else stack))
        elif op in ('RET','RETIA','RETIE'):
            if stack:todo.append((stack[-1],stack[:-1]))
        else:
            todo.append((pc+1,stack))
            if op in ('BTRSC','BTRSS','INCRSZ','DECRSZ'):todo.append((pc+2,stack))
    return peak
def check_sources(p):
    p=Path(p)
    own=sorted(set(p.glob('*.c'))|set(p.glob('*.h'))|set((p/'Modules').rglob('*.c'))|set((p/'Modules').rglob('*.h')))
    if not own:raise ValueError('No own source')
    banned=r'\b(float|double|long|printf|sprintf|snprintf|vprintf|malloc|calloc|realloc|free|memcpy|memset|strlen|strcpy|strcmp)\b'
    isrs=[]
    for source in own:
        text=source.read_text(encoding='ascii');clean=strip_comments(text)
        if re.search(banned,clean):raise ValueError('Forbidden type/library in '+str(source))
        for inc in re.findall(r'^\s*#\s*include\s*"([^"]+)"',clean,re.M):
            dest=(source.parent/inc).resolve()
            if dest.suffix.lower() in ('.c','.h') and p not in dest.parents:raise ValueError('Own include escapes project: '+str(dest))
        for name,decl,body in functions(text):
            if '__interrupt' in decl:
                isrs.append(name)
                bad=[c for c in re.findall(r'\b([A-Za-z_]\w*)\s*\(',body) if c not in ('if','for','while','switch','sizeof')]
                if bad:raise ValueError('ISR call/macro requires removal or inline proof: '+','.join(bad))
    main=p/'main.c'
    if not main.is_file() or 'CLRWDT()' not in strip_comments(main.read_text(encoding='ascii')):raise ValueError('main.c must service watchdog')
    return isrs,own

def verify(project):
    meta=info(project);p=meta['project'];stem=meta['output'];row=meta['limits']
    binary=p/(stem+'.bin');raw=binary.read_bytes()
    if len(raw)<32 or raw[:4]!=b'RIFF' or raw[8:12]!=b'NQST' or int.from_bytes(raw[4:8],'little')+8!=len(raw):raise ValueError('Invalid/truncated RIFF')
    mt=(p/(stem+'.map')).read_text(encoding='utf-8-sig')
    if any('0xFFFFFFFF' in l for l in mt.splitlines() if not l.startswith('#')):raise ValueError('Unallocated linker section')
    def sym(n):
        m=re.search(r'^'+re.escape(n)+r'\s+0x([0-9a-f]+)',mt,re.M)
        if not m:raise ValueError('Missing map symbol: '+n)
        return int(m[1],16)
    ram=sum(sym(n) for n in ('__uninit_total_size__','__share_bank_total_size__','__idata_total_size__'))
    if ram>meta['ram_budget']:raise ValueError(f'RAM exceeds budget: {ram}/{meta["ram_budget"]}')
    isrs,own=check_sources(p)
    program=parse_listing(p/(stem+'.link.lst'))
    if any(a<meta['rom_start'] or a>=meta['rom_usable_end'] for a in program):raise ValueError('Code overlaps cfg/datasheet reserved region')
    normal=linked_depth(program,meta['rom_start']);irq=linked_depth(program,8) if isrs else 0
    if irq:raise ValueError('ISR contains a linked call, including compiler helpers')
    total=normal+(1+irq if isrs else 0)
    if total>2 or total>row['stack']:raise ValueError(f'Call + interrupt stack {total} exceeds allowed/hardware stack')
    summary={'status':'ARTIFACTS_PASS','errors':0,'warnings':0,'chip':meta['chip'],'rom_words':max(program)+1-meta['rom_start'],'rom_physical_words':row['rom_words'],'rom_usable_words':meta['rom_usable_end']-meta['rom_start'],'cfg':str(meta['cfg']),'checksum_reserved_words':meta['qualification']['checksum_reserved_words'],'ram_allocated_bytes':ram,'ram_physical_bytes':row['ram_bytes'],'ram_budget_bytes':meta['ram_budget'],'hardware_stack':row['stack'],'linked_normal_call_depth':normal,'linked_isr_call_depth':irq,'worst_stack_with_interrupt':total,'own_files_checked':[str(f.relative_to(p)) for f in own],'binary':binary.name,'binary_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'scope':'Compiler/linker/static checks only; behavior and physical bench status separate'}
    (p/'Build_Verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(f'0 Errors, 0 Warnings; artifacts verified; {meta["chip"]}; ROM {summary["rom_words"]}/{row["rom_words"]}; RAM {ram}/{row["ram_bytes"]}; stack {total}/{row["stack"]}')
    return summary
if __name__=='__main__':verify(sys.argv[1])
