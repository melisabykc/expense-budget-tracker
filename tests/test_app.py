import tempfile, unittest
from pathlib import Path
import app
class Tests(unittest.TestCase):
 def test_add(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.sqlite3'; app.add('Lunch',10,'expense','Food','2026-10-27',p); self.assertEqual(app.report(p)['expenses'],10)
if __name__=='__main__': unittest.main()
