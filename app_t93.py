from flask import Flask, render_template, jsonify
from dash_app.routes import routes_bp
from dash_app.dashbord_1 import create_dash_app
from dash_app.dashbord_2 import create_dash_app2
from dash_app.dashbord_3 import create_dash_app3
from dash_app.dashbord_4 import create_dash_app4
from dash_app.dashbord_4_2 import create_dash_app4_2
from dash_app.folder_selecter import choose_folder
import os, json

#print("実際に動いているファイル:", __file__)
#print("現在のカレントディレクトリ:", os.getcwd())

app = Flask(__name__)
app.register_blueprint(routes_bp)  # ← Blueprintを登録

create_dash_app(app)
create_dash_app2(app)
create_dash_app3(app)
create_dash_app4(app)
create_dash_app4_2(app)

CONFIG_FILE = "config.json"

# 設定ファイル読み込み
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 設定ファイル保存
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/asset')
def asset():
    return render_template('asset.html')

@app.route('/income')
def income():
    return render_template('income.html')

@app.route('/expense')
def expense():
    return render_template('expense_1.html')

@app.route('/setting')
def setting():
    config = load_config()
    folder_path = config.get("folder_path", "")  # 保存済みフォルダパスを取得
    return render_template('setting.html', folder_path=folder_path)

@app.route("/select_folder", methods=["GET"])
def select_folder():
    # メインスレッドで Tkinter を呼ぶ
    folder_path = choose_folder()
    if folder_path:
        config = load_config()
        config["folder_path"] = folder_path
        save_config(config)
    return jsonify({"folderPath": folder_path if folder_path else ""})

if __name__ == "__main__":
    # threaded=False にすることでリクエストもメインスレッドで処理
    app.run(debug=True, threaded=False, port=5050)
