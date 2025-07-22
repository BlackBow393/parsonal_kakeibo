import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',  # DashのURLルート
    )

    DATA_DIR = "data"
    excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx')]

    dash_app.layout = html.Div([
        html.H3("Excelファイルのグラフ表示（Dash）"),
        dcc.Dropdown(
            id='file-dropdown',
            options=[{'label': f, 'value': f} for f in excel_files],
            placeholder="Excelファイルを選択",
        ),
        dcc.Graph(id='excel-graph')
    ])

    @dash_app.callback(
        Output('excel-graph', 'figure'),
        Input('file-dropdown', 'value')
    )
    def update_graph(file_name):
        if file_name is None:
            return {}

        df = pd.read_excel(os.path.join("data", file_name))

        # 列チェック
        if '期間' not in df.columns or '収入/支出' not in df.columns or '金額' not in df.columns:
            return {}

        # 期間を文字列や日付に変換（必要に応じて）
        df['期間'] = pd.to_datetime(df['期間'])
        df['期間'] = df['期間'].dt.to_period('M').astype(str)  # 月単位にする場合
        df = df[df['収入/支出'].isin(['収入','支出'])]

        # 区分ごとに期間別集計
        summary = df.groupby(['期間', '収入/支出'])['金額'].sum().reset_index()

        # グラフ作成
        fig = px.bar(
            summary,
            x='期間',
            y='金額',
            color='収入/支出',
            barmode='group',
            title=f"{file_name} の期間別収支分類",
            labels={'金額': '金額（円）', '期間': '期間'}
        )
        
        fig.update_layout(
            xaxis=dict(
                tickformat='%Y/%m/%d'
            ),
            yaxis=dict(
                tickformat=',',
                tickprefix='￥'
            )
        )
        
        return fig

    return dash_app
