import pandas as pd
import plotly.express as px
from dash import Input, Output
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
        Output('income-category-dropdown', 'options'),
        Output('income-category-dropdown', 'value'),
        Output('income-subcategory-dropdown', 'options'),
        Output('income-subcategory-dropdown', 'value'),
        Input('year-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('income-category-dropdown', 'value'),
        Input('income-subcategory-dropdown', 'value')
    )
    def update_graph(selected_year, selected_month, selected_income_category, selected_income_subcategory):
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
            if '期間' not in df.columns or '収入/支出' not in df.columns or '金額' not in df.columns:
                continue
            df['期間'] = pd.to_datetime(df['期間'], errors='coerce')
            df.dropna(subset=['期間'], inplace=True)
            df['年'] = df['期間'].dt.year
            df['期間_table'] = df['期間'].dt.strftime("%Y/%m/%d")
            df['期間'] = df['期間'].dt.to_period('M').astype(str)
            df = df[df['収入/支出'].isin(['収入', '支出'])]
            all_dfs.append(df)

        if not all_dfs:
            empty_fig = px.bar(title="対象データがありません")
            empty_pie = px.pie(title="対象データがありません")
            return ([], None, [], 'all', [], 'all', empty_fig, empty_pie, empty_pie, [], [], [], [])

        combined_df = pd.concat(all_dfs, ignore_index=True)

        # 以下は既存のグラフ・テーブル生成コードをそのまま使用
        # 年リスト作成、月・カテゴリフィルタ、棒グラフ、円グラフ、テーブル生成
        years = sorted(combined_df['年'].unique())
        year_options = [{'label': str(y), 'value': y} for y in years]
        if selected_year is None:
            selected_year = years[-1]

        df_filtered = combined_df[combined_df['年'] == selected_year]

        if selected_month != 'all':
            month_str = f"{selected_year}-{int(selected_month):02d}"
            df_filtered = df_filtered[df_filtered['期間'] == month_str]

        # 収入カテゴリ
        income_categories = sorted(df_filtered[df_filtered['収入/支出']=='収入']['分類'].dropna().unique())
        income_options = [{'label':'すべて','value':'all'}] + [{'label':c,'value':c} for c in income_categories]
        if selected_income_category not in [c['value'] for c in income_options]:
            selected_income_category = 'all'
        if selected_income_category != 'all':
            df_filtered = df_filtered[df_filtered['分類'] == selected_income_category]

        # 収入サブカテゴリ
        income_subcategories = sorted(df_filtered[df_filtered['収入/支出']=='収入']['小分類'].dropna().unique())
        income_suboptions = [{'label':'すべて','value':'all'}] + [{'label':c,'value':c} for c in income_subcategories]
        if selected_income_subcategory not in [c['value'] for c in income_suboptions]:
            selected_income_subcategory = 'all'
        if selected_income_subcategory != 'all':
            df_filtered = df_filtered[df_filtered['小分類'] == selected_income_subcategory]

        return (year_options, selected_year,
                income_options, selected_income_category,
                income_suboptions, selected_income_subcategory)