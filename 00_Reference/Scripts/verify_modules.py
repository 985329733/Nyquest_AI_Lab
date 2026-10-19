"""Compile every reference block in its own copied vendor project."""
from pathlib import Path
import shutil,subprocess,json,hashlib,os,sys,xml.etree.ElementTree as ET
from datetime import datetime
from project_paths import repair,ROOT
from verify_artifacts import verify
from toolchain import resolve_tools
CASES={
'Key_Scan_Debounce':('Key_Reset();','Key_Scan_10ms();'),
'Sleep_Wakeup_LowPower':('','LowPower_Sleep();'),
'PWM_SoftStart':('PWM_Init(); pwm_target = 100;','PWM_Ramp_10ms();'),
'ADC_Battery_LowPower':('Battery_Init(); battery_cut_limit=80; battery_warn_limit=96; battery_recover_limit=112; battery_confirm_samples=3; battery_configured=1;','Battery_10ms();'),
'Charge_Status':('Charge_Init();','Charge_10ms();'),
'Motor_MultiSpeed':('PWM_Init(); motor_mode=1; Motor_SelectMode(); Motor_Timer2Start();','Motor_SelectMode(); PWM_Ramp_10ms();'),
'LED_Patterns':('LED_Init(); led_mode=3;','LED_10ms();'),
'Buzzer_Alerts':('Buzzer_Init(); buzzer_ticks=50;','Buzzer_10ms();'),
'MultiKey_Combo':('MultiKey_Init();','MultiKey_10ms();'),
'Protection_Overcurrent':('Protection_Reset(); protection_limit=100; protection_hard_limit=200; protection_confirm_ticks=3; protection_configured=1; protection_sensor_fault=0; protection_current=0; protection_fresh=1; Protection_Arm();','protection_fresh=1; Protection_10ms();')}
def main():
 template=ROOT/'00_Reference/Templates/NY8B062D_Validated'
 dest=ROOT/'00_Reference/Validation'/('Module_Builds_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
 dest.mkdir(exist_ok=True);reports=[]
 env=os.environ.copy();env['PATH']=str(ROOT/'00_Reference/Tools/NYC_NY8/app/bin')+';'+str(ROOT/'00_Reference/Tools/NYASM/app')+';'+env['PATH']
 for name,(init,tick) in CASES.items():
  p=dest/name
  if p.exists():raise ValueError('Existing evidence preserved; use a new run directory: '+str(p))
  p.mkdir();(p/'OBJ').mkdir();(p/'Modules').mkdir()
  for f in ('Makefile','ThreeModeDemo.cb','ThreeModeDemo.naprj'):shutil.copy2(template/f,p/f)
  source=ROOT/'01_Modules'/(name+'.c');shutil.copy2(source,p/'Modules'/source.name)
  if name=='Motor_MultiSpeed':shutil.copy2(ROOT/'01_Modules/PWM_SoftStart.c',p/'Modules/PWM_SoftStart.c')
  (p/'main.c').write_text('/* Compile-only fixture. Untimed calls. Do not flash this harness. */\n#define LED_ON 0\n#define MOTOR_ON 1\n#include <ny8.h>\n#include "Modules/'+name+'.c"\nvoid main(void)\n{\n DISI(); PORTA=0; PORTB=7; IOSTA=255; IOSTB=255;\n PACON=0; APHCON=254; ABPLCON=255; BPHCON=255; PCON=0x98;\n '+init+'\n while(1) { CLRWDT(); '+tick+' }\n}\n',encoding='ascii')
  repair(p)
  result=subprocess.run([str(resolve_tools()['make']),'-B','all','SHOW_CMD=1','BASE_ROOT='+ROOT.as_posix()],cwd=p,env=env,capture_output=True,text=True,errors='replace')
  (p/'build.log').write_text(result.stdout+result.stderr,encoding='utf-8')
  if result.returncode or 'msg {' in result.stdout+result.stderr:raise ValueError('Compiler diagnostic: '+str(p)+'\n'+result.stdout+result.stderr)
  report=verify(p);report['module']=name;report['module_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();report['scope']='Independent real compile/link and artifact checks only; no timed behavior or bench acceptance'
  reports.append(report)
 (dest/'Module_Compilation_Report.json').write_text(json.dumps(reports,indent=2),encoding='utf-8');print('Compiled and checked',len(reports),'modules')
if __name__=='__main__':main()
