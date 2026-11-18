import unittest,tempfile,os
from db import Store
class Tests(unittest.TestCase):
 def setUp(self): self.t=tempfile.TemporaryDirectory(); self.s=Store(os.path.join(self.t.name,'x.db'))
 def tearDown(self): self.s.close(); self.t.cleanup()
 def add(self,no='12',paid=500): return self.s.add_receipt(dict(name='علی',national_id='0012345678',receipt_no=no,date='1405/01/02',paid_irr=paid))
 def test_total_period_threshold(self):
  self.add('1',800); self.add('2',400); cid=self.s.search('علی')[0]['id']; self.assertEqual(self.s.total(cid),1200); self.assertEqual(self.s.total(cid,'1405/01/02','1405/01/02'),1200)
  self.s.db.execute("UPDATE customers SET threshold=1000 WHERE id=?",(cid,)); self.assertTrue(self.s.threshold(cid)[2])
 def test_duplicate_and_search(self):
  self.add('22'); self.assertTrue(self.s.search('0012345678')); self.assertTrue(self.s.search('22'))
  with self.assertRaises(Exception): self.add('22')
 def test_auth(self): self.s.set_password('secret'); self.assertTrue(self.s.verify('secret')); self.assertFalse(self.s.verify('bad'))
if __name__=='__main__': unittest.main()
