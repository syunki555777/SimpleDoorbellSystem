from flask import Flask, render_template, request, redirect, url_for, abort, jsonify

app = Flask(__name__)


# 呼び出し理由のリスト
call_reasons = ["呼び出し理由1","呼び出し理由2"]

# 管理者向けトークン
SECRET_TOKEN = "ADMINADMINADMIN"

# 呼び出し側向けトークン(共通)
STUDENT_TOKEN= "STUDENTSTUDENTSTUDENT"


# 呼び鈴の番号と理由を保存するリスト(何も入れないでください。)
called_numbers = []

@app.route('/')
def index():
    return render_template('index.html', numbers=called_numbers)

@app.route('/confirm', methods=['POST'])
def confirm_call():

    number = int(request.form['number'])
    reason = request.form['reason']
    return render_template('confirm.html', number=number, reason=reason)

@app.route('/call', methods=['POST'])
def call_bell():
    number = int(request.form['number'])
    reason = request.form['reason']
    if not any(d['number'] == number for d in called_numbers):
        called_numbers.append({'number': number, 'reason': reason})
    return redirect(url_for('index'))

@app.route('/clear/<int:number>', methods=['POST'])
def clear_number(number):
    global called_numbers
    token = request.form['token']
    if token != SECRET_TOKEN:
        abort(403)  # Forbidden
    called_numbers = [d for d in called_numbers if d['number'] != number]
    return redirect(url_for('admin', token=token))

@app.route('/admin')
def admin():
    token = request.args.get('token')
    if token != SECRET_TOKEN:
        abort(403)  # Forbidden
    return render_template('admin.html', numbers=called_numbers, token=token)

@app.route('/bell/<int:number>')
def bell(number):

    token = request.args.get('token')
    if token != STUDENT_TOKEN:
        abort(403)  # Forbidden
    return render_template('bell.html', number=number, reasons=call_reasons)

@app.route('/get_numbers')
def get_numbers():
    return jsonify(called_numbers)

if __name__ == '__main__':
    app.run(debug=True)