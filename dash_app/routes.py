from flask import Blueprint, jsonify
import os
import time
import win32com.client
import pythoncom

routes_bp = Blueprint("routes", __name__)
SAVE_DIR = r"C:\Users\t9374\OneDrive\デスクトップ\家計簿保存先"

@routes_bp.route("/refresh", methods=["POST"])
def update_mail():
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)

        pythoncom.CoInitialize()
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6)  # 6 = 受信トレイ

        saved_files = []
        messages = None

        # 最大3回リトライ
        for attempt in range(3):
            messages = inbox.Items.Restrict("[Unread] = true")
            messages.Sort("[ReceivedTime]", True)  # 新しい順にソート

            if messages.Count > 0:
                break
            else:
                time.sleep(2)  # 待ってから再取得

        if messages and messages.Count > 0:
            for msg in list(messages):  # list()で確定
                try:
                    if "家計簿" in (msg.Subject or ""):
                        _ = msg.Body  # 本文アクセスで強制ロード

                        for att in msg.Attachments:
                            save_path = os.path.join(SAVE_DIR, att.FileName)

                            # 添付保存リトライ（最大3回）
                            for s_attempt in range(3):
                                try:
                                    att.SaveAsFile(save_path)
                                    saved_files.append(save_path)
                                    break
                                except Exception as save_err:
                                    if s_attempt < 2:
                                        time.sleep(5)
                                    else:
                                        saved_files.append(
                                            f"error saving {att.FileName}: {save_err}"
                                        )

                        msg.UnRead = False

                except Exception as inner_e:
                    saved_files.append(f"error processing mail: {str(inner_e)}")

        pythoncom.CoUninitialize()

        return jsonify({"status": "success", "files": saved_files})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
