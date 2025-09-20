from flask import Flask, render_template
from flask import request, jsonify
from dash_app.routes import routes_bp
from dash_app.dashbord_1 import create_dash_app
import os
print("実際に動いているファイル:", __file__)
print("現在のカレントディレクトリ:", os.getcwd())

app = Flask(__name__)
app.register_blueprint(routes_bp)  # ← Blueprintを登録

create_dash_app(app)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/asset')
def asset():
    return render_template('asset.html')

@app.route('/setting')
def setting():
    return render_template('setting.html')

@app.route("/get_fullpath", methods=["POST"])
def get_fullpath():
    data = request.json
    relative_path = data.get("relativePath", "")

    # Flaskの実行ディレクトリから見たフルパスを作成
    full_path = os.path.abspath(relative_path)

    return jsonify({"fullPath": full_path})

if __name__ == '__main__':
    app.run(debug=True, port=5050)
