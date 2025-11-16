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
        Output('expense-category-dropdown', 'options'),
        Output('expense-category-dropdown', 'value'),
        Output('expense-subcategory-dropdown', 'options'),
        Output('expense-subcategory-dropdown', 'value'),
        Output('expense-graph', 'figure'),
        Input('year-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('expense-category-dropdown', 'value'),
        Input('expense-subcategory-dropdown', 'value')
    )
    def update_graph(selected_year, selected_month, selected_expense_category, selected_expense_subcategory):
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
            df = df[df['収入/支出'] == '支出']  # ← 収入のみ
            all_dfs.append(df)

        if not all_dfs:
            empty_bar = px.bar(title="対象データがありません")
            empty_line = px.line(title="対象データがありません")
            empty_pie = px.pie(title="対象データがありません")
            empty_scatter = px.scatter(title="対象データがありません")
            return ([], None, [], 'all', [], 'all', empty_line, empty_bar, empty_pie, empty_scatter)

        combined_df = pd.concat(all_dfs, ignore_index=True)

        # 以下は既存のグラフ・テーブル生成コードをそのまま使用
        # 年リスト作成、月・カテゴリフィルタ、棒グラフ、円グラフ、テーブル生成
        years = sorted(combined_df['年'].unique())
        year_options = [{'label':'すべて','value':'all'}] + [{'label': str(y), 'value': y} for y in years]
        if selected_year is None:
            selected_year = years[-1]
        
        if selected_year != 'all':
            # 特定の年 → その年だけを使う
            df_filtered = combined_df[combined_df['年'] == selected_year]

            # 月単位のままでもOK
            df_bar = df_filtered.groupby(['年', '分類'], as_index=False)['金額'].sum()

        else:
            # すべて選択 → 月単位をまとめて年単位に集約
            df_filtered = combined_df.copy()
            df_bar = df_filtered.groupby(['年', '分類'], as_index=False)['金額'].sum()

        if selected_month != 'all':
            month_str = f"{selected_year}-{int(selected_month):02d}"
            df_filtered = df_filtered[df_filtered['期間'] == month_str]

        # 収入カテゴリ
        expense_categories = sorted(df_filtered[df_filtered['収入/支出']=='支出']['分類'].dropna().unique())
        expense_options = [{'label':'すべて','value':'all'}] + [{'label':c,'value':c} for c in expense_categories]
        if selected_expense_category not in [c['value'] for c in expense_options]:
            selected_expense_category = 'all'
        if selected_expense_category != 'all':
            df_filtered = df_filtered[df_filtered['分類'] == selected_expense_category]

        # 収入サブカテゴリ
        expense_subcategories = sorted(df_filtered[df_filtered['収入/支出']=='支出']['小分類'].dropna().unique())
        expense_suboptions = [{'label':'すべて','value':'all'}] + [{'label':c,'value':c} for c in expense_subcategories]
        if selected_expense_subcategory not in [c['value'] for c in expense_suboptions]:
            selected_expense_subcategory = 'all'
        if selected_expense_subcategory != 'all':
            df_filtered = df_filtered[df_filtered['小分類'] == selected_expense_subcategory]
            
        # --- 年別の折れ線グラフ ---
        df_line = (
            combined_df.groupby(['年'], as_index=False)['金額']
            .sum()
            .sort_values('年')
        )
        
        # 年ごとの合計金額を計算（ラベル用）
        df_total = df_line.groupby('年', as_index=False)['金額'].sum()
        
        fig_line = px.line(
            df_line,
            x='年',
            y='金額',
            title="支出金額推移",
            labels={'金額': '金額（円）', '年': '年'},
            color_discrete_map={'その他': 'dimgray'} 
        )
        fig_line.update_layout(
            barmode='stack', 
            yaxis=dict(tickformat=',', tickprefix='￥'),
            yaxis_title="金額（円）",
            xaxis=dict(
                tickmode='array',              # 目盛りを手動指定
                tickvals=sorted(df_line['年'].unique()),  # 年（整数）のみを表示
                ticktext=[str(y) for y in sorted(df_line['年'].unique())]  # 表示文字列
            )
        )
        
        # 各年の合計金額を上部に表示（text）
        for i, row in df_total.iterrows():
            fig_line.add_annotation(
                x=row['年'],
                y=row['金額'],
                text=f"{int(row['金額']):,}円",
                showarrow=False,
                font=dict(size=12, color="black"),
                yshift=10
            )
        
        return (year_options, selected_year,
                expense_options, selected_expense_category,
                expense_suboptions, selected_expense_subcategory,
                fig_line)