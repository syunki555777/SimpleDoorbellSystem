import os
import random
import string

CONFIG_FILE = "config.py"


# ランダムなトークンを生成する関数
def generate_random_token(length=32):
    """指定された長さのランダムな英数字トークンを生成"""
    characters = string.ascii_letters + string.digits  # 英字＋数字
    return ''.join(random.choice(characters) for _ in range(length))


# 設定を対話的にユーザーから取得する
def interactive_setup():
    print("=== 設定ウィザード ===")
    print("以下の質問に答えて、アプリ設定を構成してください。\n")

    # トークンの長さを選択
    try:
        token_length = int(input("生成するトークンの長さを入力してください (デフォルト: 32): ").strip() or 32)
    except ValueError:
        token_length = 32

    # 管理者向けトークン
    secret_token = input("管理者向けトークンを入力してください (未入力の場合は自動生成されます): ").strip()
    if not secret_token:
        secret_token = generate_random_token(token_length)
        print(f"生成された管理者向けトークン: {secret_token}")

    # 呼び出し側向けトークン
    student_token = input("呼び出し側向けトークン (共通) を入力してください (未入力の場合は自動生成されます): ").strip()
    if not student_token:
        student_token = generate_random_token(token_length)
        print(f"生成された呼び出し側向けトークン: {student_token}")

    # 外部API用トークン
    remote_token = input("外部API用トークンを入力してください (未入力の場合は自動生成されます): ").strip()
    if not remote_token:
        remote_token = generate_random_token(token_length)
        print(f"生成された外部API用トークン: {remote_token}")

    # アプリケーションのタイトル
    title = input("アプリケーションのタイトルを入力してください (例: 進捗管理システム): ").strip() or "進捗管理システム"

    # 班数
    try:
        number_of_groups = int(input("班の総数を入力してください (例: 14): ").strip() or 14)
    except ValueError:
        number_of_groups = 14

    # タスク
    tasks_input = input("タスク名をカンマ (,) 区切りで入力してください (例: 課題1,課題2): ").strip()
    tasks = tasks_input.split(",") if tasks_input else ["課題1", "課題2"]

    # 呼び出し理由
    reasons_input = input(
        "呼び出し理由をカンマ (,) 区切りで入力してください (例: 呼び出し理由1,呼び出し理由2): ").strip()
    call_reasons = reasons_input.split(",") if reasons_input else ["呼び出し理由1", "呼び出し理由2", "呼び出し理由3"]

    # サーバー URL の入力
    server_url = input("サーバーの URL を入力してください (デフォルト: http://localhost:5000): ").strip()
    if not server_url:
        server_url = "http://localhost:5000"

    # 入力された設定を辞書に格納
    settings = {
        "SECRET_TOKEN": secret_token,
        "STUDENT_TOKEN": student_token,
        "REMOTE_TOKEN": remote_token,
        "TITLE": title,
        "NUMBER_OF_GROUPS": number_of_groups,
        "TASKS": tasks,
        "CALL_REASONS": call_reasons,
        "SERVER_URL": server_url,  # 新規追加項目
    }

    return settings


# 設定を config.py に書き込む
def save_to_config_file(settings):
    with open(CONFIG_FILE, "w") as f:
        f.write(f"# 自動生成された設定ファイル\n\n")
        for key, value in settings.items():
            if isinstance(value, str):
                # 文字列の場合
                f.write(f'{key} = "{value}"\n')
            elif isinstance(value, list):
                # リストの場合
                f.write(f'{key} = {value}\n')
            else:
                # その他の型 (整数など)
                f.write(f"{key} = {value}\n")
        f.write(f"\n\n")
        f.write(f"# 班ごとの進捗を保存するデフォルト辞書\n"
                    "PROGRESS_DATA = {}\n"
                    "# 班ごとの呼び出しリクエストを保存するリスト\n"
                    "CALL_REQUESTS = []\n")
    print(f"\n設定を {CONFIG_FILE} に保存しました！")


# メイン関数
def main():
    print("Flask アプリケーションの設定を行います。")
    print("既存の設定を上書きしますか？")

    if os.path.exists(CONFIG_FILE):
        overwrite = input(f"{CONFIG_FILE} が既に存在します。上書きしますか？ (y/N): ").strip().lower()
        if overwrite != "y":
            print("設定の変更をキャンセルしました。")
            return

    # 対話形式で設定を取得
    settings = interactive_setup()

    # config.py に保存
    save_to_config_file(settings)


if __name__ == "__main__":
    main()
