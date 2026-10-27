import argparse, json, sqlite3
from pathlib import Path
DB=Path(__file__).with_name('data.sqlite3')
def connect(path=DB):
 c=sqlite3.connect(str(path)); c.row_factory=sqlite3.Row; c.execute('CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY, description TEXT NOT NULL, amount REAL NOT NULL, kind TEXT NOT NULL, category TEXT NOT NULL, date TEXT NOT NULL)'); return c
def add(description,amount,kind,category,date,path=DB):
 amount=float(amount)
 if amount<0 or kind not in ('income','expense'): raise ValueError('amount must be nonnegative and kind must be income or expense')
 with connect(path) as c: cur=c.execute('INSERT INTO transactions(description,amount,kind,category,date) VALUES(?,?,?,?,?)',(description,amount,kind,category,date)); return cur.lastrowid
def listing(path=DB):
 with connect(path) as c:return [dict(r) for r in c.execute('SELECT * FROM transactions ORDER BY id DESC')]
def report(path=DB):
 rows=listing(path); return {'records':len(rows),'income':sum(r['amount'] for r in rows if r['kind']=='income'),'expenses':sum(r['amount'] for r in rows if r['kind']=='expense')}
def main():
 p=argparse.ArgumentParser(description='Expense and budget tracker'); s=p.add_subparsers(dest='cmd',required=True); a=s.add_parser('add'); a.add_argument('--description',required=True); a.add_argument('--amount',required=True,type=float); a.add_argument('--kind',choices=['income','expense'],required=True); a.add_argument('--category',required=True); a.add_argument('--date',required=True); s.add_parser('list'); s.add_parser('report'); x=p.parse_args()
 if x.cmd=='add': print(json.dumps({'id':add(x.description,x.amount,x.kind,x.category,x.date)}))
 elif x.cmd=='list': print(json.dumps(listing(),indent=2))
 else: print(json.dumps(report(),indent=2))
if __name__=='__main__': main()
