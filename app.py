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
def ui_main():
    import streamlit as st
    import pandas as pd
    title="Gelir-Gider Takibi"; table="transactions"
    choices={"status":["todo","in_progress","done"] if table=="tasks" else ["pending","processing","shipped","delivered","cancelled"] if table=="orders" else ["open","in_progress","resolved","closed"] if table=="tickets" else [],"kind":["income","expense"],"priority":["low","medium","high","urgent"]}
    st.set_page_config(page_title=title,page_icon="📊",layout="wide"); st.title(title)
    st.caption("Kayıt ekle, kayıtlarını görüntüle ve CSV olarak indir.")
    with connect() as db: fields=[dict(r) for r in db.execute("PRAGMA table_info("+table+")") if r["name"]!="id"]
    t1,t2,t3=st.tabs(["➕ Yeni kayıt","📋 Kayıtlar","ℹ️ Hakkında"])
    with t1:
        with st.form("new_record",clear_on_submit=True):
            values={}; cols=st.columns(2)
            for i,f in enumerate(fields):
                k,typ=f["name"],f["type"].upper()
                with cols[i%2]:
                    if k in choices and choices[k]: values[k]=st.selectbox(k.replace("_"," ").title(),choices[k])
                    elif "INT" in typ: values[k]=st.number_input(k.replace("_"," ").title(),min_value=0,step=1)
                    elif any(x in typ for x in ("REAL","FLOAT","DOUBLE","NUMERIC")) or k in ("amount","value","total","unit_price"): values[k]=st.number_input(k.replace("_"," ").title(),min_value=0.0,step=1.0)
                    else: values[k]=st.text_input(k.replace("_"," ").title())
            if st.form_submit_button("Kaydı ekle",type="primary"):
                if any(str(v).strip()=="" for k,v in values.items() if k!="url"): st.error("Lütfen gerekli alanları doldur.")
                else:
                    try:
                        with connect() as db: db.execute(f"INSERT INTO {table} ({', '.join(values)}) VALUES ({', '.join(['?']*len(values))})",tuple(values.values()))
                        st.success("Kayıt eklendi.")
                    except Exception as e: st.error(f"Kayıt eklenemedi: {e}")
    with t2:
        with connect() as db: rows=[dict(r) for r in db.execute(f"SELECT * FROM {table} ORDER BY id DESC")]
        if rows:
            st.metric("Toplam kayıt",len(rows)); df=pd.DataFrame(rows); st.dataframe(df,use_container_width=True,hide_index=True)
            st.download_button("CSV olarak indir",df.to_csv(index=False).encode("utf-8-sig"),file_name=table+".csv",mime="text/csv")
        else: st.info("Henüz kayıt yok.")
    with t3:
        st.write("Python, SQLite ve Streamlit ile hazırlanmıştır.")
        st.code("pip install -r requirements.txt\nstreamlit run app.py",language="bash")
if __name__ == "__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1] in ("add","list","report"): main()
    else: ui_main()