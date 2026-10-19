"""Limited NY8 instruction model library; no vendor or physical simulation claim.
Peripherals and product scenarios belong to each project's behavior_tests.py.
Unsupported chips/instructions fail rather than silently emulate another chip.
"""
from pathlib import Path
import re
from project_info import info, ROOT
from verify_artifacts import parse_listing
from verification_contract import load_build_context

def load_symbols(path):
    result={}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        m=re.fullmatch(r'(\S+)\s+0x([0-9a-f]+)(?:\s+.*)?',line)
        if m:result[m[1]]=int(m[2],16)
    return result

class CPUModel:
    def __init__(self,project,boundary=None):
        self.meta=info(project)
        self.context, self.configuration = load_build_context(project)
        self.instruction_hz = self.context['instruction_hz']
        if self.meta['limits']['rom_word_bits']!=14 or self.meta['limits']['ram_bytes']>128 or not self.meta['model'].startswith('small'):
            raise ValueError('CPU model does not support this instruction width/RAM banking; add a verified backend')
        p=self.meta['project'];stem=self.meta['output']
        self.symbols=load_symbols(p/(stem+'.map'))
        self.program=parse_listing(p/(stem+'.link.lst'))
        self.program={a:(op,[x.strip() for x in arg.split(',')] if arg else []) for a,(op,arg) in self.program.items()}
        h=(ROOT/'00_Reference/include'/(self.meta['chip'].lower()+'.h')).read_text(encoding='ascii')
        self.bit_names={m[1]:int(m[2]) for m in re.finditer(r'__sbit\s+(\w+)\s*=\s*\w+\s*:\s*(\d+)',h)}
        bits=self.meta['qualification'].get('r_page_address_bits')
        if bits not in (6,7):raise ValueError('R-page address width needs qualification')
        self.r_mask=(1<<bits)-1
        self.r=[0]*(1<<bits);self.f={};self.s={};self.inputs={};self.acc=0;self.pc=self.meta['rom_start'];self.stack=[]
        self.gie=False;self.sleeping=False;self.maxstack=0;self.events=[]
        self.boundary=boundary
    def val(self,x):
        if x.startswith('0x'):return int(x,16)
        if x in ('C','Z'):return {'C':0,'Z':2}[x]
        if x in self.bit_names:return self.bit_names[x]
        if re.fullmatch(r'P[AB][0-7]',x):return int(x[-1])
        return self.symbols['_'+x]&self.r_mask
    def get(self,a):
        if a==0:a=self.r[4]&self.r_mask
        value=self.r[a]
        for (port,bit),level in self.inputs.items():
            if a==self.symbols.get('_'+port,-1)&self.r_mask and self.f.get('IOST'+port[-1],255)&(1<<bit):
                value=(value&~(1<<bit))|((level&1)<<bit)
        return value
    def put(self,a,v):
        if a==0:a=self.r[4]&self.r_mask
        v &= 255
        if a==15:self.r[a]&=v
        else:self.r[a]=v
    def z(self,v):self.r[3]=(self.r[3]&251)|(4 if (v&255)==0 else 0)
    def store(self,a,v,d):
        if d=='ToReg':self.put(a,v)
        else:self.acc=v&255
    def step(self):
        op,args=self.program[self.pc];self.pc+=1
        if op=='LGOTO':self.pc=self.val(args[0])
        elif op=='LCALL':
            self.stack.append(self.pc);self.maxstack=max(self.maxstack,len(self.stack));self.pc=self.val(args[0])
        elif op in ('RET','RETIE','RETIA'):
            if op=='RETIA':self.acc=self.val(args[0])
            self.pc=self.stack.pop()
            if op=='RETIE':self.gie=True
        elif op=='MOVIA':self.acc=self.val(args[0])
        elif op=='MOVAR':self.put(self.val(args[0]),self.acc)
        elif op=='MOVR':
            a=self.val(args[0]);v=self.get(a);self.store(a,v,args[1]);self.z(v)
        elif op in ('CLRR','CLRA'):
            if op=='CLRA':self.acc=0
            else:self.put(self.val(args[0]),0)
            self.z(0)
        elif op in ('INCR','DECR','INCRSZ'):
            a=self.val(args[0]);v=(self.get(a)+(1 if op!='DECR' else -1))&255
            self.store(a,v,args[1])
            if op=='INCRSZ':self.pc+=v==0
            else:self.z(v)
        elif op in ('XORAR','SUBAR','SWAPR'):
            a=self.val(args[0]);rv=self.get(a)
            if op=='SWAPR':v=((rv<<4)|(rv>>4))&255
            elif op=='XORAR':v=rv^self.acc;self.z(v)
            else:
                v=(rv-self.acc)&255
                self.r[3]=(self.r[3]&254)|(1 if rv>=self.acc else 0);self.z(v)
            self.store(a,v,args[1])
        elif op=='XORIA':self.acc^=self.val(args[0]);self.z(self.acc)
        elif op in ('BTRSC','BTRSS'):
            bit=bool(self.get(self.val(args[0])) & (1<<self.val(args[1])))
            self.pc+= bit if op=='BTRSS' else not bit
        elif op in ('BSR','BCR'):
            a=self.val(args[0]);mask=1<<self.val(args[1]);self.put(a,self.get(a)|mask if op=='BSR' else self.get(a)&~mask)
        elif op=='DISI':self.gie=False
        elif op=='ENI':self.gie=True
        elif op=='IOST':self.f[args[0]]=self.acc
        elif op=='SFUN':self.s[args[0]]=self.acc
        elif op=='SLEEP':self.sleeping=True
        elif op in ('NOP','CLRWDT'):pass
        else:raise AssertionError('Unsupported instruction '+op)
    def run(self):
        for _ in range(5000):
            self.step()
            if self.sleeping or self.pc==self.boundary:return
        raise AssertionError('CPU did not return to the main loop')
