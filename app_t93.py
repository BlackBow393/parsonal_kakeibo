from flask import Flask, render_template
from dash_app.dashbord_1 import create_dash_app
import os
print("実際に動いているファイル:", __file__)
print("現在のカレントディレクトリ:", os.getcwd())

app = Flask(__name__)
create_dash_app(app)

@app.route('/')
def home():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True, port=5050)
