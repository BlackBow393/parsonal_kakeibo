from flask import Blueprint, jsonify
import os
import time
import win32com.client
import pythoncom
import json

routes_bp = Blueprint("routes", __name__)

CONFIG_FILE = "config.json"

# =========================
# 設定ファイル読み込み
# =========================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# =========================
# メール更新
# =========================
@routes_bp.route("/refresh", methods=["POST"])
def update_mail():

    try:
        print("===== refresh開始 =====")

        config = load_config()
        SAVE_DIR = config.get("folder_path")

        if not SAVE_DIR:
            return jsonify({
                "status": "error",
                "message": "保存先が設定されていません。"
            })

        os.makedirs(SAVE_DIR, exist_ok=True)

        saved_files = []

        pythoncom.CoInitialize()

        try:
            print("Outlook接続開始")

            outlook = win32com.client.Dispatch(
                "Outlook.Application"
            ).GetNamespace("MAPI")

            print("受信トレイ取得")

            inbox = outlook.GetDefaultFolder(6)

            messages = None

            # =========================
            # 未読メール取得（最大3回）
            # =========================
            for attempt in range(3):

                print(f"未読検索 {attempt+1}回目")

                messages = inbox.Items.Restrict(
                    "[Unread] = true"
                )

                messages.Sort(
                    "[ReceivedTime]",
                    True
                )

                print(
                    f"未読件数: {messages.Count}"
                )

                if messages.Count > 0:
                    break

                time.sleep(2)

            # =========================
            # メール処理
            # =========================
            if messages and messages.Count > 0:

                for i in range(
                    messages.Count,
                    0,
                    -1
                ):

                    try:

                        msg = messages.Item(i)

                        subject = msg.Subject or ""

                        print(
                            f"メール処理: {subject}"
                        )

                        if "家計簿" not in subject:
                            continue

                        _ = msg.Body

                        attachment_count = msg.Attachments.Count

                        print(
                            f"添付数: {attachment_count}"
                        )

                        for j in range(
                            1,
                            attachment_count + 1
                        ):

                            att = msg.Attachments.Item(j)

                            save_path = os.path.join(
                                SAVE_DIR,
                                att.FileName
                            )

                            print(
                                f"保存開始: {save_path}"
                            )

                            for retry in range(3):

                                try:

                                    att.SaveAsFile(
                                        save_path
                                    )

                                    saved_files.append(
                                        save_path
                                    )

                                    print(
                                        f"保存成功: {save_path}"
                                    )

                                    break

                                except Exception as save_err:

                                    print(
                                        f"保存失敗({retry+1}/3): {save_err}"
                                    )

                                    if retry < 2:
                                        time.sleep(5)
                                    else:
                                        saved_files.append(
                                            f"ERROR: {att.FileName} - {save_err}"
                                        )

                        msg.UnRead = False
                        msg.Save()

                    except Exception as mail_err:

                        error_msg = (
                            f"メール処理失敗: {mail_err}"
                        )

                        print(error_msg)

                        saved_files.append(error_msg)

        finally:

            pythoncom.CoUninitialize()

            print("Outlook終了")

        print("===== refresh終了 =====")

        return jsonify({
            "status": "success",
            "files": saved_files
        })

    except Exception as e:

        print("致命的エラー:", str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        })