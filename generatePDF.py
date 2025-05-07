import os
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import config  # config.py をインポート

OUTPUT_DIR = "pdf/pdf_output"  # PDF保存先フォルダ
QR_CODE_DIR = "pdf/qr_codes"  # QRコード画像保存先フォルダ
FONT_DIR = "pdf/font"  # フォント保存フォルダ（同じディレクトリ内）
FONT_FILE = "MPLUSRounded1c-ExtraBold.ttf"  # 使用するフォント
IMAGE_PATH = "pdf/image/introduction.png"  # QRコードの下に追加する画像

# 日本語フォント登録名
FONT_NAME = "MPLUSRounded1c"


# PDF作成メイン関数
def create_group_qr_pdf():
    # フォントのパス
    font_path = os.path.join(FONT_DIR, FONT_FILE)

    # 日本語フォントを登録
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"フォントファイル '{font_path}' が見つかりません。正しいパスを確認してください。")
    pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))

    # 保存先ディレクトリを確認＆作成
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(QR_CODE_DIR):
        os.makedirs(QR_CODE_DIR)

    # 追加する画像ファイルが存在するかチェック
    if not os.path.exists(IMAGE_PATH):
        raise FileNotFoundError(f"画像ファイル '{IMAGE_PATH}' が見つかりません。正しいパスを確認してください。")

    # PDFの保存パス
    pdf_file_path = os.path.join(OUTPUT_DIR, "班別QRコード一覧.pdf")

    # 新しいPDFを作成
    c = canvas.Canvas(pdf_file_path, pagesize=letter)
    width, height = letter  # PDFのページサイズ

    # 各班のQRコードを作成し、その班用ページに描画
    for group_id in range(1, config.NUMBER_OF_GROUPS + 1):
        # 各班のURLを生成
        group_url = f"{config.SERVER_URL}/group/{group_id}?token={config.STUDENT_TOKEN}"

        # QRコード画像を生成
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(group_url)
        qr.make(fit=True)
        qr_img_path = os.path.join(QR_CODE_DIR, f"group_{group_id}.png")
        qr_img = qr.make_image(fill="black", back_color="white")
        qr_img.save(qr_img_path)

        # 班番号タイトルを描画（日本語フォントを使用）
        c.setFont(FONT_NAME, 24)  # 日本語用フォントで大きめの文字サイズ
        c.drawString(inch, height - inch, f"班 {group_id} のQRコード")

        # QRコードを描画
        qr_width = 3 * inch  # QRコードの幅（インチ単位）
        qr_height = 3 * inch  # QRコードの高さ（インチ単位）
        x_position = (width - qr_width) / 2  # QRコードをページ中央に配置
        y_position = height - 2 * inch - qr_height  # QRコードのY座標

        c.drawImage(qr_img_path, x_position, y_position, qr_width, qr_height)

        # URLをQRコード下部に描画（日本語フォント）
        c.setFont(FONT_NAME, 12)  # 通常サイズの日本語フォント
        url_y_position = y_position - 0.5 * inch  # QRコードより少し下

        # QRコード下に画像を描画 (画像サイズ比率を考慮)
        img_orig_width, img_orig_height = 2000, 2816  # 画像オリジナル解像度
        max_img_width = width - 2 * inch  # 左右1インチずつ余白
        max_img_height = height / 3  # ページ3分の1ほどの高さに制限

        # 縦横比を維持してリサイズ
        img_width, img_height = max_img_width, max_img_width * (img_orig_height / img_orig_width)
        if img_height > max_img_height:
            img_height = max_img_height
            img_width = max_img_height * (img_orig_width / img_orig_height)

        # 画像の描画位置を計算 (中央揃えで下方向に配置)
        img_x_position = (width - img_width) / 2
        img_y_position = url_y_position - img_height - 0.5 * inch

        c.drawImage(IMAGE_PATH, img_x_position, img_y_position, img_width, img_height)



        # 班ごとに新しいページを追加
        c.showPage()

    # タイトル
    c.setFont(FONT_NAME, 24)
    c.drawString(inch, height - inch, "管理者専用ページ (外部公開禁止)")

    # 管理者 URL と QR コード
    admin_url = f"{config.SERVER_URL}/admin?token={config.SECRET_TOKEN}"
    admin_qr_img_path = os.path.join(QR_CODE_DIR, "admin.png")
    admin_qr = qrcode.QRCode(version=1, box_size=10, border=4)
    admin_qr.add_data(admin_url)
    admin_qr.make(fit=True)
    admin_qr_img = admin_qr.make_image(fill="black", back_color="white")
    admin_qr_img.save(admin_qr_img_path)

    # QR を中央配置
    qr_size = 4 * inch
    x_qr = (width - qr_size) / 2
    y_qr = height - 2 * inch - qr_size
    c.drawImage(admin_qr_img_path, x_qr, y_qr, qr_size, qr_size)

    # URL と注意書き
    c.setFont(FONT_NAME, 12)
    c.drawCentredString(width / 2, y_qr - 0.4 * inch, f"管理者ページ: {admin_url}")

    c.setFont(FONT_NAME, 10)
    warn_text = "※この QR は関係者のみ使用可。外部に共有しないでください。"
    c.drawCentredString(width / 2, y_qr - 0.8 * inch, warn_text)



    # PDFファイルを保存
    c.save()
    print(f"PDFファイル『{pdf_file_path}』を作成しました！")


if __name__ == "__main__":
    create_group_qr_pdf()