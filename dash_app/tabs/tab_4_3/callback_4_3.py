import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output
import os, json

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def register_callbacks_4_3(dash_app):
    @dash_app.callback(
        Output('year-dropdown3', 'options'),
        Output('year-dropdown3', 'value'),
        Output('expense-category-dropdown3', 'options'),
        Output('expense-category-dropdown3', 'value'),
        Output('expense-subcategory-dropdown3', 'options'),
        Output('expense-subcategory-dropdown3', 'value'),
        Output('expense-subcategory-graph3', 'figure'),
        Output('refueling-graph1', 'figure'),
        Output('count-pareto-graph3', 'figure'),
        Input('year-dropdown3', 'value'),
        Input('month-dropdown3', 'value'),
        Input('expense-category-dropdown3', 'value'),
        Input('expense-subcategory-dropdown3', 'value')
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
            df = df[df['分類'] == '🚖 交通/車']  # ← 車交通のみ
            all_dfs.append(df)

        if not all_dfs:
            empty_bar = px.bar(title="対象データがありません")
            empty_line = px.line(title="対象データがありません")
            empty_pie = px.pie(title="対象データがありません")
            empty_scatter = px.scatter(title="対象データがありません")
            return ([], None, [], 'all', [], 'all', empty_bar, empty_bar, empty_bar)

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

        else:
            # すべて選択 → 月単位をまとめて年単位に集約
            df_filtered = combined_df.copy()

        if selected_month != 'all':
            month_str = f"{selected_year}-{int(selected_month):02d}"
            df_filtered = df_filtered[df_filtered['期間'] == month_str]

        # 収入カテゴリ
        expense_categories = sorted(df_filtered[df_filtered['収入/支出']=='支出']['分類'].dropna().unique())
        expense_options = [{'label':c,'value':c} for c in expense_categories]
        selected_expense_category = '🚖 交通/車'

        # 収入サブカテゴリ
        expense_subcategories = sorted(df_filtered[df_filtered['収入/支出']=='支出']['小分類'].dropna().unique())
        expense_suboptions = [{'label':'すべて','value':'all'}] + [{'label':c,'value':c} for c in expense_subcategories]
        if selected_expense_subcategory not in [c['value'] for c in expense_suboptions]:
            selected_expense_subcategory = 'all'
        if selected_expense_subcategory != 'all':
            df_filtered = df_filtered[df_filtered['小分類'] == selected_expense_subcategory]
            
        # 分類別の棒グラフ
        df_bar_subcategory = df_filtered.groupby(['小分類'], as_index=False)['金額'].sum()
        
        # 金額の大きい順に並び替え
        df_bar_subcategory = df_bar_subcategory.sort_values('金額', ascending=False)
        
        x = df_bar_subcategory['小分類']
        y = df_bar_subcategory['金額']
        
        # タイトルを条件で切り替える
        if selected_year == 'all':
            title_text_bar = '全年 小分類別支出金額'
        else:
            title_text_bar = f'{selected_year}年 小分類別支出金額'
        
        fig_bar_subcategory = px.bar(
            df_bar_subcategory,
            x='小分類',
            y='金額',
            color='小分類',
            title=title_text_bar,
            color_discrete_map={'その他': 'dimgray'} 
        )
        
        fig_bar_subcategory.update_layout(
            barmode='stack', 
            yaxis=dict(tickformat=',', tickprefix='￥'),
            yaxis_title="金額（円）"
        )
        
        # --- 内容別の給油の分類の棒グラフ ---
        refueling_subcategory = '⛽️ガソリン'
        df_refueling = df_filtered[df_filtered['小分類'] == refueling_subcategory]
        # 件数（count）と平均値（mean）も集計
        df_bar_refueling = (
            df_refueling
            .groupby(['内容'], as_index=False)
            .agg(
                金額合計=('金額', 'sum'),
                件数=('金額', 'count'),
                平均金額=('金額', 'mean')
            )
        )
        df_bar_refueling = df_bar_refueling.sort_values('金額合計', ascending=False)
        
        # タイトルを条件で切り替える
        if selected_year == 'all':
            title_text_bar2 = '全年 給油金額と回数'
        else:
            title_text_bar2 = f'{selected_year}年 給油金額と回数'
            
        # --- 棒グラフ（給油金額） ---
        fig_bar_mix = px.bar(
            df_bar_refueling,
            x='内容',
            y='金額合計', 
            title=title_text_bar2,
            color='内容',
            hover_data={
                '件数': True,
                '平均金額': ':.0f',
                '金額合計': ':.0f'
            },
            color_discrete_map={'その他': 'dimgray'}
        )

        # --- 折れ線グラフ（給油回数：第2軸）を追加 ---
        fig_bar_mix.add_trace(
            go.Scatter(
                x=df_bar_refueling['内容'],
                y=df_bar_refueling['件数'],
                mode='lines+markers',
                name='給油回数（回）',
                yaxis='y2'  # ← 第2軸を使う
            )
        )

        # --- レイアウト設定（第2軸を追加） ---
        fig_bar_mix.update_layout(
            yaxis=dict(
                title='金額（円）',
                tickformat=',',
                tickprefix='￥'
            ),
            yaxis2=dict(
                title='給油回数（回）',
                overlaying='y',      # ← 第1軸と重ねる
                side='right',        # ← 右側に配置
                tickformat=','
            ),
            showlegend=False
        )
        
        # --内容別のパレート図--
        df_bar_pareto = df_filtered.groupby(['内容'], as_index=False)['金額'].sum()
        df_bar_pareto = df_bar_pareto.sort_values('金額', ascending=False).head(10)
        
        # タイトルを条件で切り替える
        if selected_year == 'all':
            title_text_bar3 = '全年 内容別支出金額上位１０位'
        else:
            title_text_bar3 = f'{selected_year}年 内容別支出金額上位１０位'
            
        fig_bar_pareto = px.bar(
            df_bar_pareto,
            x='内容',
            y='金額',
            color='内容',
            title=title_text_bar3,
            color_discrete_map={'その他': 'dimgray'} 
        )
        
        fig_bar_pareto.update_layout(
            barmode='stack', 
            yaxis=dict(tickformat=',', tickprefix='￥'),
            yaxis_title="金額（円）",
            showlegend=False
        )
        
        return (year_options, selected_year,
                expense_options, selected_expense_category,
                expense_suboptions, selected_expense_subcategory,
                fig_bar_subcategory,fig_bar_mix,fig_bar_pareto)