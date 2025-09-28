import pandas as pd
import plotly.express as px
from dash import Input, Output, html, dcc
import os, json

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def register_callbacks(dash_app):
    @dash_app.callback(
        Output('year-dropdown', 'options'),
        Output('year-dropdown', 'value'),
        Output('assets-category-dropdown', 'options'),
        Output('assets-category-dropdown', 'value'),
        Output('cash-graph', 'figure'),
        Output('cashles-graph', 'figure'),
        Output('bank-graph', 'figure'),
        Output('loan-graph', 'figure'),
        Output('card-graph', 'figure'),
        Input('year-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('assets-category-dropdown', 'value')
    )
    def update_graph(selected_year, selected_month, selected_assets_category):
        # --- 最新の設定を取得 ---
        config = load_config()
        DATA_DIR = config.get("folder_path")

        # ここから先は通常のデータ読み込み・グラフ生成処理
        all_dfs = []
        for file in os.listdir(DATA_DIR):
            if not file.endswith('.xlsx'):
                continue
            path = os.path.join(DATA_DIR, file)
            df = pd.read_excel(path)
            if '期間' not in df.columns or '収入/支出' not in df.columns or '金額' not in df.columns or '資産' not in df.columns:
                continue
            df['期間'] = pd.to_datetime(df['期間'], errors='coerce')
            df.dropna(subset=['期間'], inplace=True)
            df['年'] = df['期間'].dt.year
            df['期間_table'] = df['期間'].dt.strftime("%Y/%m/%d")
            df['期間'] = df['期間'].dt.to_period('M').astype(str)
            all_dfs.append(df)

        if not all_dfs:
            empty_fig = px.area(title="対象データがありません")
            return ([], None, [], 'all', empty_fig, empty_fig, empty_fig, empty_fig, empty_fig)

        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        # --- 初期資産リストを DataFrame に変換 ---
        initial_assets_list = [
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "JAバンク", "収入/支出": "収入", "金額": 75948},
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "楽天銀行", "収入/支出": "収入", "金額": 169187},
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "楽天カード", "収入/支出": "支出", "金額": 7000},
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "現金", "収入/支出": "収入", "金額": 30944},
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "シェルカード", "収入/支出": "支出", "金額": 11516},
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "manaca", "収入/支出": "収入", "金額": 119},
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "PayPayマネー", "収入/支出": "収入", "金額": 19177},
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "岡崎信用金庫", "収入/支出": "収入", "金額": 541002},
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "楽天証券NISA", "収入/支出": "収入", "金額": 103395},
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "碧海信用金庫", "収入/支出": "収入", "金額": 140323},
            {"期間": "2023-12-31", "年": 2023, "月": 12, "資産": "労働信用金庫", "収入/支出": "収入", "金額": 234827}
        ]
        df_initial_assets = pd.DataFrame(initial_assets_list)
        df_initial_assets['期間'] = pd.to_datetime(df_initial_assets['期間'])

        # --- Excel データと結合 ---
        combined_df = pd.concat([combined_df, df_initial_assets], ignore_index=True)

        # 年リスト作成
        years = sorted(combined_df['年'].unique())
        year_options = [{'label': str(y), 'value': y} for y in years]
        if selected_year is None:
            selected_year = years[-1]

        df_filtered = combined_df[combined_df['年'] == selected_year]

        if selected_month != 'all':
            month_str = f"{selected_year}-{int(selected_month):02d}"
            df_filtered = df_filtered[df_filtered['期間'] == month_str]

        # 資産カテゴリ
        assets_categories = sorted(df_filtered['資産'].dropna().unique())
        assets_options = [{'label': 'すべて', 'value': 'all'}] + [{'label': c, 'value': c} for c in assets_categories]
        if selected_assets_category not in [c['value'] for c in assets_options]:
            selected_assets_category = 'all'
        if selected_assets_category != 'all':
            df_filtered = df_filtered[df_filtered['資産'] == selected_assets_category]

        # 符号付き金額（収入・預け入れは加算、支出・引き出しは減算）
        df_balance = combined_df.copy()
        df_balance['符号付き金額'] = df_balance.apply(
            lambda row: row['金額'] if row['収入/支出'] in ['収入', '預け入れ'] else -row['金額'],
            axis=1
        )

        # グループ定義
        group_map = {
            "GR86ローン": "ローン・奨学金",
            "学部生奨学金": "ローン・奨学金",
            "院生奨学金": "ローン・奨学金",
            "楽天カード": "カード",
            "シェルカード": "カード",
            "PayPayマネー": "電子マネー",
            "manaca": "電子マネー",
            "現金": "現金",
            "JAバンク": "銀行",
            "労働信用金庫": "銀行",
            "岡崎信用金庫": "銀行",
            "碧海信用金庫": "銀行",
            "楽天銀行": "銀行",
            "楽天証券NISA": "銀行",
            "岡崎信用金庫定期": "銀行"
        }
        df_balance['資産グループ'] = df_balance['資産'].map(group_map)

        # 累計グラフ用（全期間）
        df_cumsum = df_balance.copy()  # 全期間を使う

        figs = {}
        
        # X軸の表示範囲を決める
        x_range = None
        if selected_year is not None:
            if selected_month == 'all':
                # 年だけ指定 → その年の1月〜12月
                x_range = [f"{selected_year}-01", f"{selected_year}-12"]
            else:
                # 年＋月指定 → その月のみ
                month_str = f"{selected_year}-{int(selected_month):02d}"
                x_range = [month_str, month_str]
        
        for group_name in ["ローン・奨学金", "カード", "現金", "電子マネー", "銀行"]:
            df_group = df_cumsum[df_cumsum['資産グループ'] == group_name].copy()
            if df_group.empty:
                figs[group_name] = px.area(title=f"{group_name} の対象データがありません")
                continue

            summary_area = df_group.groupby(['期間', '資産'])['符号付き金額'].sum().reset_index()
            summary_area = summary_area.sort_values(['資産', '期間'])
            summary_area['累計金額'] = summary_area.groupby('資産')['符号付き金額'].cumsum()

            fig = px.area(
                summary_area,
                x='期間',
                y='累計金額',
                color='資産',
                title=f"{group_name} の残高推移（累計・全期間）",
                labels={'累計金額': '残高（円）', '期間': '期間'}
            )
            fig.update_layout(
                xaxis=dict(tickformat='%Y年%m月', rangeslider=dict(visible=False),range=x_range),
                yaxis=dict(tickformat=',', tickprefix='￥')
            )
            figs[group_name] = fig

        return (year_options, selected_year,
                assets_options, selected_assets_category,
                figs["現金"], figs["電子マネー"], figs["銀行"], figs["ローン・奨学金"], figs["カード"])
