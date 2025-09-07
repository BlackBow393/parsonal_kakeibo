import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from dash import dash_table

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',
        assets_folder="assets"
    )

    DATA_DIR = "data"
    excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx')]

    dash_app.layout = html.Div([
        html.H3("全Excelファイルを結合して表示（Dash）"),
        dcc.Graph(id='excel-graph'), # 棒グラフ
        html.Div([
            dcc.Graph(id='pie-in-chart', style={'width': '50%'}),  # 収入の円グラフ
            dcc.Graph(id='pie-out-chart', style={'width': '50%'})  # 支出の円グラフ
        ], style={'display': 'flex'}),
        html.Div([
            # 収入テーブル
            html.Div([
                dash_table.DataTable(
                    id='income-table',
                    columns=[],
                    data=[],
                    page_action='none',
                    fixed_rows={'headers': True},  # ← ヘッダー固定
                    style_table={
                        'height': '500px',
                        'overflowY': 'auto',
                        'overflowX': 'auto',
                        'width': '100%'   # 子Divに合わせて幅100%
                    },
                    style_cell={
                        'textAlign': 'left',
                        'minWidth': '100px',
                        'width': 'auto'
                    }
                )
            ], style={'width': '50%', 'padding-right': '5px'}),  # 画面半分

            # 支出テーブル
            html.Div([
                dash_table.DataTable(
                    id='expenses-table',
                    columns=[],
                    data=[],
                    page_action='none',
                    fixed_rows={'headers': True},  # ← ヘッダー固定
                    style_table={
                        'height': '500px',
                        'overflowY': 'auto',
                        'overflowX': 'auto',
                        'width': '100%'   # 子Divに合わせて幅100%
                    },
                    style_cell={
                        'textAlign': 'left',
                        'minWidth': '100px',
                        'width': 'auto'
                    }
                )
            ], style={'width': '50%', 'padding-left': '5px'})   # 画面半分
        ], style={'display': 'flex', 'gap': '0px'})  # 横並び
    ])

    @dash_app.callback(
        Output('excel-graph', 'figure'),
        Output('pie-in-chart', 'figure'),
        Output('pie-out-chart', 'figure'),
        Output('income-table', 'columns'),
        Output('income-table', 'data'),
        Output('expenses-table', 'columns'),
        Output('expenses-table', 'data'),
        Input('excel-graph', 'id')
    )
    def update_graph(_):
        all_dfs = []

        for file in excel_files:
            path = os.path.join(DATA_DIR, file)
            df = pd.read_excel(path)

            if '期間' not in df.columns or '収入/支出' not in df.columns or '金額' not in df.columns:
                continue

            df['期間'] = pd.to_datetime(df['期間'], errors='coerce')
            df.dropna(subset=['期間'], inplace=True)
            
            # まず datetime 型で昇順にソート
            df = df.sort_values(by='期間')
            
            # テーブル用（日付フォーマット）
            df['期間_table'] = df['期間'].dt.strftime("%Y/%m/%d")
            
            # グラフ用（月ごと）
            df['期間'] = df['期間'].dt.to_period('M').astype(str)
            
            df = df[df['収入/支出'].isin(['収入', '支出'])]

            all_dfs.append(df)

        if not all_dfs:
            empty_fig = px.bar(title="対象データがありません")
            return empty_fig, px.pie(title="対象データがありません"), px.pie(title="対象データがありません"), [], [], [], []

        combined_df = pd.concat(all_dfs, ignore_index=True)

        # 棒グラフ
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
            xaxis=dict(tickformat='%Y年%m月', rangeslider=dict(visible=True)),
            yaxis=dict(tickformat=',', tickprefix='￥')
        )

        # 円グラフ
        income_df = combined_df[combined_df['収入/支出'] == '収入']
        if '分類' in income_df.columns:
            grouped_in = income_df.groupby('分類')['金額'].sum().reset_index()

            # 「その他」以外を降順にソート
            non_other = grouped_in[grouped_in['分類'] != 'その他'].sort_values('金額', ascending=False)
            other = grouped_in[grouped_in['分類'] == 'その他']

            # ソート後に「その他」を最後に追加
            grouped_in = pd.concat([non_other, other])

            # 順序をカテゴリ型にして固定
            categories = grouped_in['分類'].tolist()
            grouped_in['分類'] = pd.Categorical(grouped_in['分類'], categories=categories, ordered=True)

            fig_pie_in = px.pie(
                grouped_in,
                names='分類',
                values='金額',
                title='収入の分類割合',
                category_orders={'分類': categories}
            )
            # 時計回り
            fig_pie_in.update_traces(sort=False, direction='clockwise')
        else:
            fig_pie_in = px.pie(title="対象データがありません")

        expenses_df = combined_df[combined_df['収入/支出'] == '支出']
        if '分類' in expenses_df.columns:
            grouped_out = expenses_df.groupby('分類')['金額'].sum().reset_index()

            non_other = grouped_out[grouped_out['分類'] != 'その他'].sort_values('金額', ascending=False)
            other = grouped_out[grouped_out['分類'] == 'その他']
            grouped_out = pd.concat([non_other, other])

            categories = grouped_out['分類'].tolist()
            grouped_out['分類'] = pd.Categorical(grouped_out['分類'], categories=categories, ordered=True)

            fig_pie_out = px.pie(
                grouped_out,
                names='分類',
                values='金額',
                title='支出の分類割合',
                category_orders={'分類': categories}
            )
            fig_pie_out.update_traces(sort=False, direction='clockwise')
        else:
            fig_pie_out = px.pie(title="対象データがありません")

        # 表示したい列だけ抽出
        display_columns = ['期間_table', '資産', '分類', '小分類', '内容', 'メモ', '金額']
        income_df = income_df[display_columns]
        expenses_df = expenses_df[display_columns]

        # DataTable用
        income_columns = [{"name": i, "id": i} for i in income_df.columns] if not income_df.empty else []
        income_data = income_df.to_dict('records') if not income_df.empty else []

        expenses_columns = [{"name": i, "id": i} for i in expenses_df.columns] if not expenses_df.empty else []
        expenses_data = expenses_df.to_dict('records') if not expenses_df.empty else []

        return fig_bar, fig_pie_in, fig_pie_out, income_columns, income_data, expenses_columns, expenses_data

    return dash_app
