from flask import Flask, render_template, request, redirect, url_for, abort, jsonify, send_from_directory,send_file, render_template
import os
import json
import config  # config.py をインポート
import subprocess
from threading import Thread, Lock


PDF_DIR  = os.path.join("pdf", "pdf_output")
PDF_NAME = "班別QRコード一覧.pdf"
PDF_PATH = os.path.join(PDF_DIR, PDF_NAME)

_generate_lock = Lock()
_is_generating = False   # 生成フラグ

app = Flask(__name__)

# 設定を読み込む
app.config.from_object(config)

# 必要な変数は Flask の `app.config` から参照する
title = app.config["TITLE"]
progress_data = app.config["PROGRESS_DATA"]
call_requests = app.config["CALL_REQUESTS"]
NUMBER_OF_GROUPS = app.config["NUMBER_OF_GROUPS"]
TASKS = app.config["TASKS"]
CALL_REASONS = app.config["CALL_REASONS"]

SECRET_TOKEN = app.config["SECRET_TOKEN"]
STUDENT_TOKEN = app.config["STUDENT_TOKEN"]
REMOTE_TOKEN = app.config["REMOTE_TOKEN"]


def _background_generate():
    """
    別スレッドで PDF を生成し、終了後にフラグを戻す。
    """
    global _is_generating
    try:
        subprocess.run(["python", "generatePDF.py"], check=True)
    finally:
        _is_generating = False

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

# --- API call (Tokenの設定が必要です。)

#callを指定する。
@app.route('/api/call/<int:group_id>/<reason>', methods=['GET', 'POST'])
def remote_call(group_id, reason):
    token = request.args.get('token')
    if token != REMOTE_TOKEN:
        return jsonify({"error": "Forbidden", "message": "Invalid token."}), 403
    if request.method == 'POST':
        call_requests.append({"group_id": group_id, "reason": reason})
    return jsonify({"status": "OK"})

#次のタスクを完了させる。
@app.route('/api/task/<int:group_id>', methods=['POST'])
def complete_next_task(group_id):
    token = request.args.get('token')
    if token != REMOTE_TOKEN:
        # トークンが無効な場合、JSON形式でエラーを返す
        return jsonify({"error": "Forbidden", "message": "Invalid token."}), 403

    # group_id の進捗データを取得（無ければ初期化）
    progress = progress_data.get(group_id, {})

    # 次の未完了タスクを取得
    next_tasks = [task for task in TASKS if progress.get(task) != "済み"]

    if not next_tasks:
        # 全タスクが完了済みの場合
        return jsonify({
            "status": "completed",
            "message": "All tasks for this group are already completed.",
            "group_id": group_id,
        })

    # 次のタスクを完了状態に更新
    next_task = next_tasks[0]
    if group_id not in progress_data:
        progress_data[group_id] = {}
    progress_data[group_id][next_task] = "済み"

    # 更新されたデータをJSON形式で返す
    return jsonify({
        "status": "success",
        "group_id": group_id,
        "completed_task": next_task,
        "remaining_tasks": [task for task in TASKS if progress_data[group_id].get(task) != "済み"]
    })

#タスクを取り消す(未完了に変更)
@app.route('/api/task/<int:group_id>/undo', methods=['POST'])
def undo_last_completed_task(group_id):
    token = request.args.get('token')
    if token != REMOTE_TOKEN:
        # トークンが無効な場合、JSON形式でエラーを返す
        return jsonify({"error": "Forbidden", "message": "Invalid token."}), 403

    # group_id の進捗データを取得
    progress = progress_data.get(group_id, {})
    if not progress:
        # 進捗データが存在しない場合
        return jsonify({
            "status": "error",
            "message": "No progress data found for this group.",
            "group_id": group_id
        })

    # 完了済みのタスクを逆順で取得
    completed_tasks = [task for task in reversed(TASKS) if progress.get(task) == "済み"]

    if not completed_tasks:
        # 完了済みタスクがない場合
        return jsonify({
            "status": "error",
            "message": "No completed tasks to undo.",
            "group_id": group_id
        })

    # 最後の完了済みタスクを未完了に戻す
    last_task = completed_tasks[0]
    progress_data[group_id][last_task] = "未完了"

    return jsonify({
        "status": "success",
        "group_id": group_id,
        "undone_task": last_task,
        "remaining_tasks": [task for task in TASKS if progress_data[group_id].get(task) != "済み"],
        "completed_tasks": [task for task in TASKS if progress_data[group_id].get(task) == "済み"]
    })



@app.route('/admin', methods=['GET'])
def admin():
    token = request.args.get('token')
    if token != SECRET_TOKEN:
        abort(403)  # Forbidden
    return render_template('admin.html', data=progress_data, tasks=TASKS, num_groups=NUMBER_OF_GROUPS, call_requests=call_requests, token=token,title=title)

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

@app.route('/download/pdf', methods=['GET'])
def download_pdf():
    """
    PDF ダウンロードルート:
    1) 既に PDF があれば即返却
    2) 無ければ生成開始 → 「生成中」ページを返す
    3) 生成開始済みなら「生成中」ページのみ返す
    """
    global _is_generating

    # 1. 既に PDF が存在する場合
    if os.path.exists(PDF_PATH):
        return send_file(
            PDF_PATH,
            as_attachment=True,
            download_name=PDF_NAME,
            mimetype="application/pdf"
        )

    # 2. 生成がまだ始まっていなければバックグラウンド生成を開始
    with _generate_lock:
        if not _is_generating:
            _is_generating = True
            Thread(target=_background_generate, daemon=True).start()

    # 3. 生成中ページを返す
    return render_template("generating.html")


if __name__ == '__main__':
    # --- 起動前に必要な情報を表示 ----------------------------
    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))

    print("=" * 60)
    print("🚀 Flask アプリを起動します")
    print(f"🔑 Admin URL: http://{host}:{port}/admin?token={SECRET_TOKEN}")
    print("\n📋 Config 内容（*TOKEN を除外）")
    for key, value in app.config.items():
        if key.endswith("_TOKEN"):
            continue
        print(f"  {key}: {value}")
    print("=" * 60)
    # ---------------------------------------------------------

    app.run(debug=True, host=host, port=port)

