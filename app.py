import sys, os, shutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from db import Store
from parser import extract
FIELDS=[('name','نام مشتری'),('national_id','کد ملی'),('phone','تلفن'),('insurance','بیمه'),('doctor','پزشک'),('receipt_no','شماره فیش'),('date','تاریخ نسخه'),('tracking','کد رهگیری'),('prescription','دستور دارو'),('paid_irr','پرداختی (ریال)')]
class App(QMainWindow):
 def __init__(self):
  super().__init__(); self.store=Store(); self.setWindowTitle('CRM داروخانه'); self.resize(1150,720); self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
  if not self.store.has_password():
   p,ok=QInputDialog.getText(self,'رمز برنامه','رمز محلی جدید:',QLineEdit.EchoMode.Password)
   if not ok or not p: sys.exit(0)
   self.store.set_password(p)
  else:
   p,ok=QInputDialog.getText(self,'ورود','رمز برنامه:',QLineEdit.EchoMode.Password)
   if not ok or not self.store.verify(p): QMessageBox.critical(self,'خطا','رمز نادرست'); sys.exit(1)
  root=QWidget(); self.setCentralWidget(root); lay=QVBoxLayout(root)
  bar=QHBoxLayout(); self.query=QLineEdit(); self.query.setPlaceholderText('جست‌وجو: نام، کد ملی، فیش یا تلفن'); self.query.textChanged.connect(self.refresh); bar.addWidget(self.query)
  for text,fn in [('ثبت دستی',self.manual),('ورود PDF',self.pdf),('خروجی CSV',self.export),('پشتیبان',self.backup),('بازیابی',self.restore)]:
   b=QPushButton(text); b.clicked.connect(fn); bar.addWidget(b)
  lay.addLayout(bar); self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(['نام','کد ملی','تلفن','شماره فیش','پرداختی (ریال)']); self.table.cellDoubleClicked.connect(self.profile); lay.addWidget(self.table)
 def manual(self,values=None):
  d=QDialog(self); d.setWindowTitle('بازبینی و ثبت فیش'); form=QFormLayout(d); edits={}
  for key,label in FIELDS:
   w=QLineEdit(str((values or {}).get(key,''))); edits[key]=w; form.addRow(label,w)
  buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel); buttons.accepted.connect(d.accept); buttons.rejected.connect(d.reject); form.addRow(buttons)
  if d.exec()!=QDialog.DialogCode.Accepted:return
  data={k:w.text().strip() for k,w in edits.items()};
  try:
   if not data['paid_irr'].replace(',','').isdigit(): raise ValueError('مبلغ پرداختی را به ریال و با عدد وارد کنید')
   self.store.add_receipt(data); self.refresh()
  except Exception as e: QMessageBox.warning(self,'ثبت انجام نشد',str(e))
 def pdf(self):
  path,_=QFileDialog.getOpenFileName(self,'انتخاب فیش','','PDF (*.pdf)')
  if path:
   try:
    data,_=extract(path); self.manual(data)
   except Exception as e: QMessageBox.warning(self,'استخراج ناموفق','فایل خوانده نشد؛ اطلاعات را دستی وارد کنید.')
 def refresh(self):
  rows=self.store.search(self.query.text()); self.table.setRowCount(len(rows))
  for i,r in enumerate(rows):
   rec=self.store.receipts(r['id']); last=rec[0] if rec else None
   for j,val in enumerate([r['name'],r['national_id'],r['phone'],last['receipt_no'] if last else '',f"{last['paid_irr']:,}" if last else '']): self.table.setItem(i,j,QTableWidgetItem(str(val)))
   self.table.item(i,0).setData(Qt.ItemDataRole.UserRole,r['id'])
 def profile(self,row,col):
  cid=self.table.item(row,0).data(Qt.ItemDataRole.UserRole); recs=self.store.receipts(cid); dlg=QDialog(self); dlg.setWindowTitle('پرونده مشتری'); lay=QVBoxLayout(dlg); dates=QHBoxLayout(); start=QLineEdit(); end=QLineEdit(); start.setPlaceholderText('از تاریخ YYYY/MM/DD'); end.setPlaceholderText('تا تاریخ YYYY/MM/DD'); dates.addWidget(start); dates.addWidget(end); lay.addLayout(dates)
  label=QLabel(); lay.addWidget(label); tbl=QTableWidget(len(recs),4); tbl.setHorizontalHeaderLabels(['تاریخ','شماره فیش','رهگیری','پرداختی (ریال)'])
  for i,r in enumerate(recs):
   for j,v in enumerate([r['date'],r['receipt_no'],r['tracking'],f"{r['paid_irr']:,}"]): tbl.setItem(i,j,QTableWidgetItem(str(v)))
  lay.addWidget(tbl)
  def calc():
   total,threshold,alert=self.store.threshold(cid,start.text(),end.text()); label.setText(f'مجموع: {total:,} ریال | آستانه: {threshold:,} ریال'+(' | هشدار: آستانه رد شد' if alert else ''))
  start.textChanged.connect(calc); end.textChanged.connect(calc); calc(); dlg.resize(750,500); dlg.exec()
 def export(self):
  if QMessageBox.question(self,'تأیید خروجی','خروجی شامل اطلاعات حساس است. ادامه؟')!=QMessageBox.StandardButton.Yes:return
  p,_=QFileDialog.getSaveFileName(self,'ذخیره CSV','','CSV (*.csv)')
  if p:self.store.export_csv(p)
 def backup(self):
  p,_=QFileDialog.getSaveFileName(self,'نسخه پشتیبان','','SQLite (*.db)')
  if p:self.store.backup(p)
 def restore(self):
  p,_=QFileDialog.getOpenFileName(self,'بازیابی نسخه پشتیبان','','SQLite (*.db)')
  if p and QMessageBox.question(self,'تأیید','جایگزینی دیتابیس فعلی؟')==QMessageBox.StandardButton.Yes:
   self.store.close(); shutil.copy2(p,'pharmacy.db'); QMessageBox.information(self,'بازیابی','برنامه را دوباره اجرا کنید.')
app=QApplication(sys.argv); w=App(); w.show(); sys.exit(app.exec())
