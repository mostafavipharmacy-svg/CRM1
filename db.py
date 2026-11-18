import sqlite3, hashlib, hmac, os, csv, shutil
from datetime import date

class Store:
 def __init__(self,path='pharmacy.db'):
  self.path=path; self.db=sqlite3.connect(path); self.db.row_factory=sqlite3.Row
  self.db.execute('PRAGMA foreign_keys=ON')
  self.db.executescript("""CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
  CREATE TABLE IF NOT EXISTS customers(id INTEGER PRIMARY KEY,name TEXT NOT NULL DEFAULT '',national_id TEXT NOT NULL DEFAULT '',phone TEXT NOT NULL DEFAULT '',threshold INTEGER);
  CREATE TABLE IF NOT EXISTS receipts(id INTEGER PRIMARY KEY,customer_id INTEGER NOT NULL REFERENCES customers(id),insurance TEXT,doctor TEXT,receipt_no TEXT NOT NULL,date TEXT NOT NULL,tracking TEXT,prescription TEXT,paid_irr INTEGER NOT NULL CHECK(paid_irr>=0), UNIQUE(receipt_no));"""); self.db.commit()
 def set_password(self,pw):
  salt=os.urandom(16); digest=hashlib.pbkdf2_hmac('sha256',pw.encode(),salt,250000)
  self.db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('auth',salt.hex()+':'+digest.hex())); self.db.commit()
 def has_password(self): return self.db.execute("SELECT 1 FROM settings WHERE key='auth'").fetchone() is not None
 def verify(self,pw):
  row=self.db.execute("SELECT value FROM settings WHERE key='auth'").fetchone()
  if not row:return False
  salt,digest=row[0].split(':'); return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',pw.encode(),bytes.fromhex(salt),250000).hex(),digest)
 def add_receipt(self,d):
  if not d.get('receipt_no','').strip(): raise ValueError('شماره فیش الزامی است')
  if not d.get('date','').strip(): raise ValueError('تاریخ الزامی است')
  paid=int(d.get('paid_irr') or 0)
  if paid<0: raise ValueError('مبلغ نامعتبر است')
  c=self.db.execute('SELECT id FROM customers WHERE national_id=?',(d.get('national_id',''),)).fetchone() if d.get('national_id') else None
  if c: cid=c['id']; self.db.execute('UPDATE customers SET name=?,phone=? WHERE id=?',(d.get('name',''),d.get('phone',''),cid))
  else:
   cur=self.db.execute('INSERT INTO customers(name,national_id,phone) VALUES(?,?,?)',(d.get('name',''),d.get('national_id',''),d.get('phone',''))); cid=cur.lastrowid
  cur=self.db.execute('INSERT INTO receipts(customer_id,insurance,doctor,receipt_no,date,tracking,prescription,paid_irr) VALUES(?,?,?,?,?,?,?,?)',(cid,d.get('insurance',''),d.get('doctor',''),d['receipt_no'],d['date'],d.get('tracking',''),d.get('prescription',''),paid)); self.db.commit(); return cur.lastrowid
 def search(self,q):
  q='%'+q+'%'; return self.db.execute('SELECT DISTINCT c.*,r.receipt_no FROM customers c LEFT JOIN receipts r ON r.customer_id=c.id WHERE c.name LIKE ? OR c.national_id LIKE ? OR c.phone LIKE ? OR r.receipt_no LIKE ? ORDER BY c.id DESC',(q,q,q,q)).fetchall()
 def receipts(self,cid): return self.db.execute('SELECT * FROM receipts WHERE customer_id=? ORDER BY date DESC,id DESC',(cid,)).fetchall()
 def total(self,cid,start='',end=''):
  return self.db.execute('SELECT COALESCE(SUM(paid_irr),0) FROM receipts WHERE customer_id=? AND (? IS NULL OR date>=?) AND (? IS NULL OR date<=?)',(cid,start or None,start,end or None,end)).fetchone()[0]
 def threshold(self,cid,start='',end=''):
  row=self.db.execute('SELECT threshold FROM customers WHERE id=?',(cid,)).fetchone(); t=row[0] if row and row[0] is not None else int(self.db.execute("SELECT COALESCE((SELECT value FROM settings WHERE key='threshold'),'0')").fetchone()[0]); total=self.total(cid,start,end); return total,t,total>t and t>0
 def delete_receipt(self,rid): self.db.execute('DELETE FROM receipts WHERE id=?',(rid,)); self.db.commit()
 def export_csv(self,path):
  rows=self.db.execute('SELECT c.name,c.national_id,c.phone,r.insurance,r.doctor,r.receipt_no,r.date,r.tracking,r.prescription,r.paid_irr FROM receipts r JOIN customers c ON c.id=r.customer_id').fetchall()
  with open(path,'w',newline='',encoding='utf-8-sig') as f:
   w=csv.writer(f); w.writerow(['نام','کد ملی','تلفن','بیمه','پزشک','شماره فیش','تاریخ','رهگیری','دستور دارو','پرداختی (ریال)']); w.writerows([tuple(x) for x in rows])
 def backup(self,path): self.db.commit(); dest=sqlite3.connect(path); self.db.backup(dest); dest.close()
 def close(self): self.db.close()
