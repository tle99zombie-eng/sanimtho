from flask import Flask, render_template_string, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)

# --- 1. Connect Firebase ---
c_path = 'serviceAccountKey.json'
if not firebase_admin._apps:
    cred = credentials.Certificate(c_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- 2. CSS ---
CSS = '''
<style>
    body{background:#0f172a;color:#fff;font-family:sans-serif;padding:10px;margin:0}
    .container{max-width:800px; margin:auto}
    .add-box{background:#1e293b; padding:15px; border-radius:12px; margin-bottom:20px; text-align:center; border:1px solid #334155}
    .grid{
        display: grid;
        grid-template-rows: repeat(10, 1fr); 
        grid-template-columns: repeat(3, 1fr); 
        grid-auto-flow: column; 
        gap: 8px; width: 100%;
    }
    .card{background:#1e293b;padding:10px 5px;border-radius:10px;text-align:center;border:1px solid #334155}
    .card.booked{border-color:#f59e0b;background:#78350f}
    .card h2{margin:0;font-size:16px}
    .status{font-size:10px;margin:3px 0;color:#94a3b8}
    .btn{display:block;width:90%;padding:5px 0;border-radius:6px;border:none;font-weight:bold;cursor:pointer;text-decoration:none;margin:4px auto;font-size:10px;text-align:center}
    .btn-book{background:#f59e0b;color:#fff}
    .btn-clear{background:#ef4444;color:#fff}
    .btn-add{background:#3b82f6;color:#fff; width:auto; padding:8px 15px; display:inline-block}
    input{width:85%; font-size:10px; padding:4px; margin-bottom:4px; border-radius:4px; border:1px solid #334155; background:#0f172a; color:#fff}
</style>
'''

@app.route('/')
def index():
    docs = db.collection('tables').stream()
    tables = {d.id: d.to_dict() for d in docs}
    
    html = CSS + '<div class="container">'
    html += '<div class="add-box"><form action="/add_t" method="POST">'
    html += '<input type="text" name="t_id" placeholder="พิมพ์เลขโต๊ะที่จะเพิ่ม" style="width:150px" required>'
    html += '<button type="submit" class="btn btn-add">เพิ่มโต๊ะ</button></form></div>'
    html += '<div class="grid">'
    
    sorted_keys = sorted(tables.keys(), key=lambda x: int(x) if x.isdigit() else x)
    
    for t_id in sorted_keys:
        t = tables[t_id]
        status = t.get('status', 'ว่าง')
        cls = 'booked' if status == 'จองแล้ว' else ''
        
        html += f'<div class="card {cls}"><h2>โต๊ะ {t_id}</h2>'
        if status == 'จองแล้ว':
            html += f'<div class="status">👤 {t.get("n","")}<br>📞 {t.get("p","")}</div>'
            html += f'<a href="/del/{t_id}" class="btn btn-clear">ยกเลิก/ว่าง</a>'
        else:
            html += f'<div class="status">ว่าง</div>'
            html += f'<form action="/res/{t_id}" method="POST">'
            html += '<input type="text" name="n" placeholder="ชื่อ" required>'
            html += '<input type="text" name="p" placeholder="เบอร์" required>'
            html += '<button class="btn btn-book">จอง</button></form>'
        html += '</div>'
        
    return html + '</div></div>'

@app.route('/add_t', methods=['POST'])
def add_t():
    t_id = request.form.get('t_id')
    if t_id: db.collection('tables').document(t_id).set({'status': 'ว่าง'})
    return redirect('/')

@app.route('/res/<t_id>', methods=['POST'])
def res(t_id):
    db.collection('tables').document(t_id).update({'status': 'จองแล้ว', 'n': request.form.get('n'), 'p': request.form.get('p')})
    return redirect('/')

@app.route('/del/<t_id>')
def del_t(t_id):
    db.collection('tables').document(t_id).update({'status': 'ว่าง', 'n': '', 'p': ''})
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
