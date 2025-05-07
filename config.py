import os, json

# --- 既存設定 ---

TITLE  = os.getenv("TITLE", "進捗管理システム")
NUMBER_OF_GROUPS = int(os.getenv("NUMBER_OF_GROUPS", "5"))
TASKS        = json.loads(os.getenv("TASKS", '["課題1", "課題2"]'))
CALL_REASONS = json.loads(os.getenv("CALL_REASONS", '["質問", "ヘルプ"]'))

SECRET_TOKEN  = os.getenv("SECRET_TOKEN",  "ADMINADMIN")
STUDENT_TOKEN = os.getenv("STUDENT_TOKEN", "STUDENTSTUDENT")
REMOTE_TOKEN  = os.getenv("REMOTE_TOKEN",  "REMOTEREMOTE")

# --- ここを追加 --------------------------------------
# PDF に QR コードを貼り付けるときなどに使用するサービス URL
# Render では環境変数 SERVER_URL に https://xxxx.onrender.com をセットすると上書きできます
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5000")
# ----------------------------------------------------

# インメモリストレージ
PROGRESS_DATA = {}
CALL_REQUESTS = []