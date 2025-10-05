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
        Output('year-graph', 'figure'),
        Output('line-graph', 'figure'),
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
            df = df[df['収入/支出'] == '収入']  # ← 収入のみ
            all_dfs.append(df)

        if not all_dfs:
            empty_bar = px.bar(title="対象データがありません")
            empty_line = px.line(title="対象データがありません")
            return ([], None, [], 'all', [], 'all', empty_bar, empty_line)

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
            
        # --- 📊 年別・分類別の積み上げ棒グラフ ---
        df_bar = combined_df.groupby(['年', '分類'], as_index=False)['金額'].sum()
        
        # 年ごとの合計金額を計算（ラベル用）
        df_total = df_bar.groupby('年', as_index=False)['金額'].sum()

        fig_bar = px.bar(
            df_bar,
            x='年',
            y='金額',
            color='分類',
            title="年別 収入分類の内訳",
            labels={'金額': '金額（円）', '年': '年'},
            text_auto='.2s'
        )
        fig_bar.update_layout(barmode='stack', yaxis_tickformat=',', yaxis_title="金額（円）")
        
        # 各年の合計金額を上部に表示（text）
        for i, row in df_total.iterrows():
            fig_bar.add_annotation(
                x=row['年'],
                y=row['金額'],
                text=f"{int(row['金額']):,}円",
                showarrow=False,
                font=dict(size=12, color="black"),
                yshift=10
            )
        
        # 🟩 折れ線グラフ（年内の月別推移）
        monthly = (
            df_filtered.groupby('期間', as_index=False)['金額']
            .sum()
            .sort_values('期間')
        )

        fig_line = px.line(
            monthly,
            x='期間',  # ← datetimeのまま
            y='金額',
            markers=True,
            title=f'{selected_year}年の月別収入推移'
        )

        # update_layoutで年月表示や通貨表記を設定
        fig_line.update_layout(
            xaxis=dict(
                tickformat='%Y年%m月',  # ← 日本語形式
                rangeslider=dict(visible=False)
            ),
            yaxis=dict(
                tickformat=',',
                tickprefix='￥'
            ),
            xaxis_title="年月",
            yaxis_title="金額（円）"
        )
        
        return (year_options, selected_year,
                income_options, selected_income_category,
                income_suboptions, selected_income_subcategory,
                fig_bar, fig_line)