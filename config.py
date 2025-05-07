## 必要であればこの内容を編集してください。
## setup.pyでこのコンフィグは上書きされます。
import os, json

# タイトル
TITLE = os.getenv("TITLE", "進捗管理システム")

# 班数などの数値系は int に変換
NUMBER_OF_GROUPS = int(os.getenv("NUMBER_OF_GROUPS", "5"))

# リスト系は JSON 文字列で受け取り、パースする
TASKS = json.loads(os.getenv("TASKS", '["課題1", "課題2"]'))
CALL_REASONS = json.loads(os.getenv("CALL_REASONS", '["質問", "ヘルプ"]'))

# トークン（必須なのでデフォルトは空文字列）
SECRET_TOKEN  = os.getenv("SECRET_TOKEN",  "")
STUDENT_TOKEN = os.getenv("STUDENT_TOKEN", "")
REMOTE_TOKEN  = os.getenv("REMOTE_TOKEN",  "")

# インメモリで進捗を保持
PROGRESS_DATA = {}
CALL_REQUESTS = []