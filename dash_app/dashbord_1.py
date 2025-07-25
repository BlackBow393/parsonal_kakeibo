import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',
    )

    DATA_DIR = "data"
    excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx')]

    dash_app.layout = html.Div([
        html.H3("全Excelファイルを結合して表示（Dash）"),
        dcc.Graph(id='excel-graph'), #棒グラフ
        dcc.Graph(id='pie-in-chart'),  # 収入の円グラフ
        dcc.Graph(id='pie-out-chart')  # 収入の円グラフ
    ])

    @dash_app.callback(
        Output('excel-graph', 'figure'),
        Output('pie-in-chart', 'figure'),
        Output('pie-out-chart', 'figure'),
        Input('excel-graph', 'id')  # トリガー用（何かしら必要）
    )
    def update_graph(_):
        all_dfs = []

        for file in excel_files:
            path = os.path.join(DATA_DIR, file)
            df = pd.read_excel(path)

            if '期間' not in df.columns or '収入/支出' not in df.columns or '金額' not in df.columns:
                continue  # 想定外の構成はスキップ

            df['期間'] = pd.to_datetime(df['期間'], errors='coerce')
            df.dropna(subset=['期間'], inplace=True)
            df['期間'] = df['期間'].dt.to_period('M').astype(str)
            df = df[df['収入/支出'].isin(['収入', '支出'])]

            all_dfs.append(df)

        if not all_dfs:
            empty_fig = px.bar(title="対象データがありません")
            return empty_fig, px.pie(title="対象データがありません")

        combined_df = pd.concat(all_dfs, ignore_index=True)

        # 棒グラフ用データ
        summary_bar = combined_df.groupby(['期間', '収入/支出'])['金額'].sum().reset_index()

        fig_bar = px.bar(
            summary_bar,
            x='期間',
            y='金額',
            color='収入/支出',
            barmode='group',
            title="期間別収支分類",
            labels={'金額': '金額（円）', '期間': '期間'}
        )

        fig_bar.update_layout(
            xaxis=dict(
                tickformat='%Y年%m月',
                rangeslider=dict(visible=True)
            ),
            yaxis=dict(
                tickformat=',',
                tickprefix='￥'
            )
        )

        # 円グラフ用データ（収入だけ）
        income_df = combined_df[combined_df['収入/支出'] == '収入']
        if '分類' in income_df.columns:
            summary_pie_in = income_df.groupby('分類')['金額'].sum().reset_index()
            fig_pie_in = px.pie(
                summary_pie_in,
                names='分類',
                values='金額',
                title='収入の分類割合',
                labels={'金額': '金額（円）'}
            )
        else:
            fig_pie_in = px.pie(title="対象データがありません")
        
        # 円グラフ用データ（支出だけ）
        expenses_df = combined_df[combined_df['収入/支出'] == '支出']
        if '分類' in expenses_df.columns:
            summary_pie_out = expenses_df.groupby('分類')['金額'].sum().reset_index()
            fig_pie_out = px.pie(
                summary_pie_out,
                names='分類',
                values='金額',
                title='支出の分類割合',
                labels={'金額': '金額（円）'}
            )
        else:
            fig_pie_out = px.pie(title="対象データがありません")

        return fig_bar, fig_pie_in, fig_pie_out

    return dash_app
