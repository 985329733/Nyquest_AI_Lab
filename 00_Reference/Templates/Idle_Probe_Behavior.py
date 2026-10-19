"""Per-chip idle qualification scenarios; not a product functional test."""
from pathlib import Path
import sys,json
PROJECT=Path(__file__).resolve().parent
ROOT=next(p for p in PROJECT.parents if (p/'00_Reference/Scripts/cpu_model.py').is_file())
sys.path.insert(0,str(ROOT/'00_Reference/Scripts'))
from cpu_model import CPUModel
from verification_contract import BehaviorSuite
cpu=CPUModel(PROJECT)
cpu.boundary=next(a for a,(op,_) in cpu.program.items() if op=='CLRWDT')
cpu.run()
suite=BehaviorSuite(PROJECT, 'Linked instruction model: chip idle qualification')
ok=suite.check
index=cpu.symbols['_qualification_counter']&cpu.r_mask
ok('Counter initialized',cpu.r[index]==0)
ok('Watchdog enabled in software',cpu.get(cpu.symbols['_PCON']&cpu.r_mask)&128)
for n in range(260):cpu.run()
ok('Counter wraps as an 8-bit value',cpu.r[index]==4)
ok('Hardware stack bound respected',cpu.maxstack<=2 and cpu.maxstack<=cpu.meta['limits']['stack'])
for port,mask in cpu.meta['qualification']['gpio_input_masks'].items():
    ok(port+' safe latch',cpu.get(cpu.symbols['_'+port]&cpu.r_mask)==0)
    ok(port+' direction',cpu.f['IOST'+port[-1]]==mask)
suite.finish(max_observed_stack=cpu.maxstack)
