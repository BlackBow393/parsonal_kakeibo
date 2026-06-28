from flask import Blueprint, jsonify
import base64
import json
import os
import re
import requests
import msal

routes_bp = Blueprint("routes", __name__)

CONFIG_FILE = "config.json"
TOKEN_CACHE_FILE = "graph_token_cache.bin"
GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name)


def load_cache():
    cache = msal.SerializableTokenCache()

    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
            cache.deserialize(f.read())

    return cache


def save_cache(cache):
    if cache.has_state_changed:
        with open(TOKEN_CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(cache.serialize())


def get_access_token(config):
    client_id = config["graph_client_id"]
    authority = config.get(
        "graph_authority",
        "https://login.microsoftonline.com/consumers",
    )
    scopes = config.get(
        "graph_scopes",
        ["User.Read", "Mail.ReadWrite"],
    )

    cache = load_cache()

    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=authority,
        token_cache=cache,
    )

    accounts = app.get_accounts()
    result = None

    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])

    if not result:
        flow = app.initiate_device_flow(scopes=scopes)

        if "user_code" not in flow:
            raise RuntimeError(f"Device code flow開始に失敗しました: {flow}")

        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)

    save_cache(cache)

    if "access_token" not in result:
        raise RuntimeError(f"アクセストークン取得失敗: {result}")

    return result["access_token"]


def graph_get(url, token, params=None):
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def graph_patch(url, token, payload):
    response = requests.patch(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()


def save_attachments(message_id, token, folder_path):
    attachments_url = f"{GRAPH_BASE}/me/messages/{message_id}/attachments"
    data = graph_get(attachments_url, token)

    saved_files = []

    for attachment in data.get("value", []):
        if attachment.get("@odata.type") != "#microsoft.graph.fileAttachment":
            continue

        filename = sanitize_filename(attachment.get("name", "attachment.bin"))
        content_bytes = attachment.get("contentBytes")

        if not content_bytes:
            continue

        save_path = os.path.join(folder_path, filename)

        with open(save_path, "wb") as f:
            f.write(base64.b64decode(content_bytes))

        saved_files.append(save_path)

    return saved_files


@routes_bp.route("/refresh", methods=["POST"])
def update_mail():
    try:
        print("===== refresh開始 =====")
        
        config = load_config()

        folder_path = config.get("folder_path")
        subject_keyword = config.get("subject_keyword", "家計簿")

        if not folder_path:
            return jsonify({
                "status": "error",
                "message": "保存先フォルダが設定されていません。",
            })

        os.makedirs(folder_path, exist_ok=True)

        token = get_access_token(config)

        messages_url = f"{GRAPH_BASE}/me/mailFolders/inbox/messages"

        params = {
            "$filter": "isRead eq false",
            "$select": "id,subject,receivedDateTime,hasAttachments,isRead",
            "$orderby": "receivedDateTime desc",
            "$top": "25",
        }

        data = graph_get(messages_url, token, params=params)
        messages = data.get("value", [])

        saved_files = []

        for msg in messages:
            subject = msg.get("subject") or ""
            message_id = msg["id"]

            print(f"メール確認: {subject}")

            if subject_keyword and subject_keyword not in subject:
                continue

            if msg.get("hasAttachments"):
                saved = save_attachments(message_id, token, folder_path)
                saved_files.extend(saved)

            graph_patch(
                f"{GRAPH_BASE}/me/messages/{message_id}",
                token,
                {"isRead": True},
            )

        print("===== refresh終了 =====")

        return jsonify({
            "status": "success",
            "files": saved_files,
            "count": len(saved_files),
        })

    except Exception as e:
        print("致命的エラー:", str(e))

        return jsonify({
            "status": "error",
            "message": str(e),
        })