import re
try: import pdfplumber
except ImportError: pdfplumber=None
# Fails closed to a manual review form: ambiguous values remain blank.
def extract(path):
 if not pdfplumber: raise RuntimeError('برای PDF، pdfplumber نصب کنید')
 with pdfplumber.open(path) as pdf: text='\n'.join(p.extract_text() or '' for p in pdf.pages)
 def pick(pattern):
  m=re.search(pattern,text); return m.group(1).strip() if m else ''
 # Sample exports use Latin numerals but RTL text extraction may reverse neighboring labels.
 fields={'receipt_no':'', 'national_id':pick(r'(\d{10})\s*:?\s*د\s*س'), 'tracking':'', 'date':pick(r'(\d{4}/\d{2}/\d{2})'), 'paid_irr':''}
 # Only accept a value occurring immediately with the explicit پرداختی label.
 m=re.search(r'([\d,]+)\s*:?\s*پرداختی',text)
 if m: fields['paid_irr']=m.group(1).replace(',','')
 return fields,text
