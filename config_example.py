# config.py

# 管理者向けトークン (変更してください)
SECRET_TOKEN = "ADMIN"

# 呼び出し側向けトークン (共通, 変更してください)
STUDENT_TOKEN = "STUDENT"

# 外部API用トークン (変更してください)
REMOTE_TOKEN = "REMOTE"

# アプリケーションのタイトル
TITLE = "進捗管理システム"

# 班ごとの進捗を保存するデフォルト辞書
PROGRESS_DATA = {}

# 班ごとの呼び出しリクエストを保存するリスト
CALL_REQUESTS = []

# 班と進捗の設定
NUMBER_OF_GROUPS = 14
TASKS = ["課題1", "課題2"]

# 呼び出し理由のリスト
CALL_REASONS = ["呼び出し理由1", "呼び出し理由2", "呼び出し理由3"]