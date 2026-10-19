"""Product-specific three-mode scenarios; limited software model only."""
from pathlib import Path
import sys,json
PROJECT=Path(__file__).resolve().parent
ROOT=next(p for p in PROJECT.parents if (p/'00_Reference/Scripts/cpu_model.py').is_file())
sys.path.insert(0,str(ROOT/'00_Reference/Scripts'))
from cpu_model import CPUModel
from verification_contract import BehaviorSuite

class CPU(CPUModel):
    def __init__(self,key=1):
        super().__init__(PROJECT)
        self.key=key
        self.boundary=next(a for a,(op,_) in self.program.items() if op=='CLRWDT')
        self.run()
    @property
    def key(self):return self.inputs.get(('PORTA',0),1)
    @key.setter
    def key(self,value):self.inputs[('PORTA',0)]=value
    def tick(self,key=None):
        if key is not None and key!=self.key:
            self.key=key
            if self.sleeping and self.r[21]&1 and self.r[14]&2:
                self.r[15]|=2;self.sleeping=False;self.run()
        if not self.sleeping:
            assert self.s.get('T1CR1',0)&1 and self.r[14]&8 and self.gie
            self.r[15]|=8;self.stack.append(self.pc);self.maxstack=max(self.maxstack,len(self.stack))
            self.gie=False;self.pc=8;self.run()
            if self.r[self.symbols['_ticks_pending']&127] and not self.sleeping:self.run()
            self.events.append(self.r[self.symbols['_key_event']&127])
        return self.mode
    @property
    def mode(self):return self.r[self.symbols['_mode']&127]
    def ticks(self,n,key=None):
        for _ in range(n):self.tick(key)
    def press(self):self.ticks(3,0)
    def release(self):self.ticks(3,1)

suite=BehaviorSuite(PROJECT, 'Linked instruction model: three-mode reference')
ok=suite.check

c=CPU();c.ticks(3,1)
ok('Boot off enters sleep after stable release',c.sleeping and c.mode==0 and c.r[6]&7==7)
ok('Sleep leaves PA0 pullup and disables PWM ADC comparator RFC WDT',c.f['APHCON']==254 and c.r[12]==255 and c.r[11]==255 and c.r[8]==24 and c.r[16]==0 and c.r[26]==0 and c.r[27]==0 and all(c.s[x]==0 for x in ['T1CR1','T2CR1','T3CR1','BZ1CR','BZ2CR','BZ3CR','IRCR']))
for mode,lights in [(1,6),(2,5),(3,3),(0,7)]:
    c.press();ok(f'Press selects mode {mode} and LED mask {lights}',c.mode==mode and c.r[6]&7==lights)
    c.ticks(200,0);ok(f'Hold in mode {mode} causes no repeat',c.mode==mode)
    c.release()
ok('Fourth press sleeps only after release',c.sleeping)
c.press();ok('Wake press selects mode 1 without a second press',c.mode==1)

c=CPU(0);c.ticks(150,0)
ok('Key held at boot does not turn on',c.mode==0 and not c.sleeping)
c.release();c.press();ok('Boot held key works after a stable release',c.mode==1)
c.release()
for _ in range(10):c.tick(0);c.tick(1)
ok('Alternating bounce shorter than 30 ms does not switch',c.mode==1)
c.press();ok('Stable press after bounce switches once',c.mode==2)
c.tick(1);c.tick(0);c.ticks(10,0)
ok('Release bounce cannot rearm a held key',c.mode==2)
c.release()

c=CPU();c.ticks(3);c.press()
ok('Timer1 is exactly 625 counts and prescaler 16',c.s['TMR1']==0x70 and c.r[25]&0x30==0x20 and c.s['T1CR2']==3 and c.context['instruction_hz']==1000000)
c.release();c.ticks(29996)
ok('At 299.99 seconds mode remains on',c.mode==1 and not c.sleeping)
c.tick();ok('At 300.00 seconds auto-off enters sleep',c.mode==0 and c.sleeping)
c.press();c.release();c.ticks(20000);c.press();c.release();c.ticks(10000)
ok('An operation resets the full five-minute timeout',c.mode==2)
c.ticks(19997);ok('Five minutes after the last operation shuts down',c.mode==0 and c.sleeping)
ok('Application plus interrupt stack depth remains at most two',c.maxstack<=2)

# The scan module must report one LONG and no SHORT for a long hold.
d=CPU();d.ticks(3);d.events=[];d.press();d.ticks(150,0);d.release()
ok('Long press emits one PRESS and one LONG, no SHORT',sum(bool(e&1) for e in d.events)==1 and sum(bool(e&4) for e in d.events)==1 and not any(e&2 for e in d.events))
d.events=[];d.press();d.ticks(10,0);d.release()
ok('Short press emits one PRESS and SHORT with UP',sum(bool(e&1) for e in d.events)==1 and sum(bool(e&2) for e in d.events)==1 and any(e==10 for e in d.events))

# Interrupt a live Key_Scan call to exercise context restore and stack depth.
e=CPU();e.ticks(3);e.press();e.release()
e.r[15]|=8;e.stack.append(e.pc);e.gie=False;e.pc=8;e.run()
for _ in range(200):
    e.step()
    if e.pc==e.symbols['_Key_Scan_10ms']+3:break
else:raise AssertionError('Did not reach live key function')
saved=(e.pc,e.acc,e.r[3],e.r[4],e.r[10])
e.r[15]|=8;e.stack.append(e.pc);e.maxstack=max(e.maxstack,len(e.stack));e.gie=False;e.pc=8
for _ in range(200):
    e.step()
    if e.pc==saved[0] and e.gie:break
else:raise AssertionError('ISR did not return')
ok('ISR restores ACC STATUS FSR PCHBUF inside a live key function',(e.pc,e.acc,e.r[3],e.r[4],e.r[10])==saved)
ok('Observed main-call plus interrupt uses exactly two stack levels',e.maxstack==2)

suite.finish(max_observed_stack=max(c.maxstack,d.maxstack,e.maxstack))
