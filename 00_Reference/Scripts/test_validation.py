"""Regression tests for the general validator, including negative gates."""
from pathlib import Path
import unittest,tempfile,shutil,sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_artifacts import verify,functions,linked_depth,check_sources
from project_info import ROOT,info
class Gates(unittest.TestCase):
 def test_isr_brace_matching(self):
  fs=list(functions('void irq(void) __interrupt(0) { if (1) { flag=1; } } void Unrelated(void) { x(); }'))
  self.assertEqual([f[0] for f in fs],['irq','Unrelated']);self.assertIn('__interrupt',fs[0][1]);self.assertNotIn('x()',fs[0][2])
 def test_two_calls(self):self.assertEqual(linked_depth({0:('LCALL','0x3'),1:('RET',''),3:('LCALL','0x5'),4:('RET',''),5:('RET','')},0),2)
 def test_helper_third_call(self):
  with self.assertRaisesRegex(ValueError,'nesting'):linked_depth({0:('LCALL','0x3'),1:('RET',''),3:('LCALL','0x5'),4:('RET',''),5:('LCALL','0x7'),6:('RET',''),7:('RET','')},0)
 def test_recursion(self):
  with self.assertRaises(ValueError):linked_depth({0:('LCALL','0x0'),1:('RET','')},0)
 def test_indirect_call(self):
  with self.assertRaisesRegex(ValueError,'Unbounded'):linked_depth({0:('CALLA','')},0)
 def test_all_own_headers_and_modules(self):
  for name,content,expected in [('Modules/PWM_Extra.c','unsigned char a; float hidden;','Forbidden'),('extra.h','void helper(void); /* 中文 */','ascii')]:
   with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp);(p/'Modules').mkdir()
    (p/'main.c').write_text('void main(void) { CLRWDT(); }',encoding='ascii')
    (p/name).write_text(content,encoding='utf-8')
    with self.assertRaises((ValueError,UnicodeDecodeError)):check_sources(p)
 def test_unknown_stack(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)
   (p/'Makefile').write_text('ICBODY := NY8A050D\nOUT_NAME := Fixture\nMODEL := small\n')
   (p/'fixture.naprj').write_text('<Project><PropertyGroup><ChipId>NY8A050D</ChipId></PropertyGroup></Project>')
   with self.assertRaisesRegex(ValueError,'stack pending'):info(p)
if __name__=='__main__':unittest.main(verbosity=2)
