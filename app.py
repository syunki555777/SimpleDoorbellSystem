from flask import Flask, render_template, request, redirect, url_for, abort, jsonify, send_from_directory
import os
import json

app = Flask(__name__)

# 管理者向けトークン ここを変更してください。
SECRET_TOKEN = "ADMIN"

# 呼び出し側向けトークン(共通) ここを変更してください。
STUDENT_TOKEN = "STUDENT"

# 班ごとの進捗を保存する辞書
progress_data = {}

# 班ごとの呼び出しリクエストを保存するリスト
call_requests = []

# 班と進捗の設定
NUMBER_OF_GROUPS = 14
TASKS = ["課題1","課題2"]

# 呼び出し理由のリスト
CALL_REASONS = ["呼び出し理由1","呼び出し理由2","呼び出し理由3"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
def group_progress(group_id):
    token = request.args.get('token')
    if token != STUDENT_TOKEN:
        abort(403)  # Forbidden
    if request.method == 'POST':
        if 'call' in request.form:
            reason = request.form['reason']
            return redirect(url_for('confirm_call', group_id=group_id, reason=reason, token=token))
        else:
            task = request.form['task']
            return redirect(url_for('confirm_task', group_id=group_id, task=task, token=token))
    progress = progress_data.get(group_id, {})
    next_tasks = [task for task in TASKS if task not in progress or progress[task] != "済み"]
    return render_template('group.html', group_id=group_id, progress=progress, tasks=next_tasks, token=token, call_reasons=CALL_REASONS)

@app.route('/confirm/<int:group_id>/<task>', methods=['GET', 'POST'])
def confirm_task(group_id, task):
    token = request.args.get('token')
    if token != STUDENT_TOKEN:
        abort(403)  # Forbidden
    if request.method == 'POST':
        if group_id not in progress_data:
            progress_data[group_id] = {}
        progress_data[group_id][task] = "済み"
        return redirect(url_for('group_progress', group_id=group_id, token=token))
    return render_template('confirm.html', group_id=group_id, task=task, token=token)

@app.route('/confirm_call/<int:group_id>/<reason>', methods=['GET', 'POST'])
def confirm_call(group_id, reason):
    token = request.args.get('token')
    if token != STUDENT_TOKEN:
        abort(403)  # Forbidden
    if request.method == 'POST':
        call_requests.append({"group_id": group_id, "reason": reason})
        return redirect(url_for('group_progress', group_id=group_id, token=token))
    return render_template('confirm_call.html', group_id=group_id, reason=reason, token=token)

@app.route('/admin', methods=['GET'])
def admin():
    token = request.args.get('token')
    if token != SECRET_TOKEN:
        abort(403)  # Forbidden
    return render_template('admin.html', data=progress_data, tasks=TASKS, num_groups=NUMBER_OF_GROUPS, call_requests=call_requests, token=token)

@app.route('/update_progress', methods=['POST'])
def update_progress():
    token = request.form.get('token')
    if token != SECRET_TOKEN:
        abort(403)  # Forbidden
    group_id = int(request.form['group_id'])
    task = request.form['task']
    if group_id not in progress_data:
        progress_data[group_id] = {}
    progress_data[group_id][task] = request.form['status']
    return jsonify({"status": "success"})

@app.route('/clear_progress/<int:group_id>', methods=['POST'])
def clear_progress(group_id):
    token = request.form.get('token')
    if token != SECRET_TOKEN:
        abort(403)  # Forbidden
    progress_data.pop(group_id, None)
    return jsonify({"status": "success"})

@app.route('/get_progress')
def get_progress():
    return jsonify(progress_data)

@app.route('/get_call_requests')
def get_call_requests():
    return jsonify(call_requests)

@app.route('/complete_call_request', methods=['POST'])
def complete_call_request():
    token = request.form.get('token')
    if token != SECRET_TOKEN:
        abort(403)  # Forbidden
    group_id = int(request.form['group_id'])
    reason = request.form['reason']
    global call_requests
    call_requests = [req for req in call_requests if not (req['group_id'] == group_id and req['reason'] == reason)]
    return jsonify({"status": "success"})

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('audio', filename)

if __name__ == '__main__':
    app.run(debug=True)
