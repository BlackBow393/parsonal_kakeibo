import pandas as pd
import plotly.express as px
from dash import Input, Output
import os, json, requests

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def register_callbacks_4_1(dash_app):
    @dash_app.callback(
        Output('year-dropdown1', 'options'),
        Output('year-dropdown1', 'value'),
        Output('expense-category-dropdown1', 'options'),
        Output('expense-category-dropdown1', 'value'),
        Output('expense-subcategory-dropdown1', 'options'),
        Output('expense-subcategory-dropdown1', 'value'),
        Output('expense-graph1', 'figure'),
        Output('expense-category-graph', 'figure'),
        Output('pie-ex-chart', 'figure'),
        Output('expense-frequency-graph', 'figure'),
        Input('year-dropdown1', 'value'),
        Input('month-dropdown1', 'value'),
        Input('expense-category-dropdown1', 'value'),
        Input('expense-subcategory-dropdown1', 'value'),
        Input('refresh-btn', 'n_clicks')  # 🔴ここ追加
    )
    def update_graph(selected_year, selected_month, selected_expense_category, selected_expense_subcategory, n_clicks):
        # --- 最新の設定を取得 ---
        from dash import callback_context
        
        ctx = callback_context

        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_id == "refresh-btn":
                try:
                    # 🔴 Flaskの更新処理を呼ぶ
                    requests.post("http://localhost:5050/refresh")
                except:
                    print("refresh失敗")
        
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
        df_category_only = combined_df.copy()

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
        expense_options = [{'label':'すべて','value':'all'}] + [{'label':c,'value':c} for c in expense_categories]
        if selected_expense_category not in [c['value'] for c in expense_options]:
            selected_expense_category = 'all'
        if selected_expense_category != 'all':
            df_filtered = df_filtered[df_filtered['分類'] == selected_expense_category]
            df_category_only = df_category_only[df_category_only['分類'] == selected_expense_category]

        # 収入サブカテゴリ
        expense_subcategories = sorted(df_filtered[df_filtered['収入/支出']=='支出']['小分類'].dropna().unique())
        expense_suboptions = [{'label':'すべて','value':'all'}] + [{'label':c,'value':c} for c in expense_subcategories]
        if selected_expense_subcategory not in [c['value'] for c in expense_suboptions]:
            selected_expense_subcategory = 'all'
        if selected_expense_subcategory != 'all':
            df_filtered = df_filtered[df_filtered['小分類'] == selected_expense_subcategory]
            df_category_only = df_category_only[df_category_only['小分類'] == selected_expense_subcategory]
            
        # --- 年別の折れ線グラフ ---
        df_line = (
            df_category_only.groupby(['年'], as_index=False)['金額']
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
            yaxis=dict(tickformat=',', tickprefix='￥', rangemode='tozero'),
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
        
        # 分類別の棒グラフ
        df_bar_category = df_filtered.groupby(['分類'], as_index=False)['金額'].sum()
        
        # 金額の大きい順に並び替え
        df_bar_category = df_bar_category.sort_values('金額', ascending=False)
        
        x = df_bar_category['分類']
        y = df_bar_category['金額']
        
        # タイトルを条件で切り替える
        if selected_year == 'all':
            title_text_bar = '全年 分類別支出金額'
        else:
            title_text_bar = f'{selected_year}年 分類別支出金額'
        
        fig_bar_category = px.bar(
            df_bar_category,
            x='分類',
            y='金額',
            color='分類',
            title=title_text_bar,
            color_discrete_map={'その他': 'dimgray'} 
        )
        
        fig_bar_category.update_layout(
            barmode='stack', 
            yaxis=dict(tickformat=',', tickprefix='￥'),
            yaxis_title="金額（円）",
            showlegend=False
        )
        
        # 分類の円グラフ作成
        def make_pie(df, title):
            if df.empty or '分類' not in df.columns:
                return px.pie(title="対象データがありません")
            grouped = df.groupby('分類')['金額'].sum().reset_index()
            non_other = grouped[grouped['分類'] != 'その他'].sort_values('金額', ascending=False)
            other = grouped[grouped['分類'] == 'その他']
            grouped = pd.concat([non_other, other])
            categories = grouped['分類'].tolist()
            grouped['分類'] = pd.Categorical(grouped['分類'], categories=categories, ordered=True)
            default_colors = px.colors.qualitative.Plotly
            color_map = {}
            j = 0
            for c in categories:
                if c == 'その他':
                    color_map[c] = 'dimgray'
                else:
                    color_map[c] = default_colors[j % len(default_colors)]
                    j += 1
            fig = px.pie(grouped, names='分類', values='金額', title=title,
                         category_orders={'分類': categories}, color='分類', color_discrete_map=color_map)
            fig.update_traces(sort=False, direction='clockwise')
            return fig
        
        # 小分類の円グラフ作成
        def make_pie_sub(df, title):
            if df.empty or '小分類' not in df.columns:
                return px.pie(title="対象データがありません")
            # --- 🟢 小分類が空（NaNや空文字）のものを「その他」に置き換え ---
            df['小分類'] = df['小分類'].replace('', pd.NA)
            df['小分類'] = df['小分類'].fillna('その他')
            sub_grouped = df.groupby('小分類')['金額'].sum().reset_index()
            non_other_sub = sub_grouped[sub_grouped['小分類'] != 'その他'].sort_values('金額', ascending=False)
            other_sub = sub_grouped[sub_grouped['小分類'] == 'その他']
            sub_grouped = pd.concat([non_other_sub, other_sub])
            sub_categories = sub_grouped['小分類'].tolist()
            sub_grouped['小分類'] = pd.Categorical(sub_grouped['小分類'], categories=sub_categories, ordered=True)
            default_colors = px.colors.qualitative.Plotly
            color_map = {}
            j = 0
            for c in sub_categories:
                if c == 'その他':
                    color_map[c] = 'dimgray'
                else:
                    color_map[c] = default_colors[j % len(default_colors)]
                    j += 1
            fig = px.pie(sub_grouped, names='小分類', values='金額', title=title,
                         category_orders={'小分類': sub_categories}, color='小分類', color_discrete_map=color_map)
            fig.update_traces(sort=False, direction='clockwise')
            return fig

        df_expense = df_filtered[df_filtered['収入/支出'] == '支出']
        
        if selected_expense_category == 'all':
            # 分類ごとの円グラフを描画
            fig_pie_ex = make_pie(df_expense, '支出の分類割合')
        else:
            # 特定分類 → 小分類の円グラフを描画
            df_selected = df_expense[df_expense['分類'] == selected_expense_category]
            fig_pie_ex = make_pie_sub(df_selected, f"{selected_expense_category} の小分類割合")
            
        # 支出金額と頻度の散布図作成
        
        df_scatter = (
            df_expense
            .groupby('内容', as_index=False)
            .agg(
                回数=('金額', 'count'),
                合計金額=('金額', 'sum')
            )
        )
        
        fig_scatter = px.scatter(
            df_scatter,
            x='回数',
            y='合計金額',
            size='合計金額',
            color='内容',
            title='支出金額と発生回数の関係',
            hover_name='内容'
        )

        # 見た目の微調整
        fig_scatter.update_traces(
            marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey')),
            hovertemplate=(
                '内容: %{hovertext}<br>' +
                '回数: %{x:,}回<br>' +
                '合計金額: %{y:,}円<br>' +
                '<extra></extra>'
            )
        )
        fig_scatter.update_layout(
            xaxis_title='回数', 
            yaxis=dict(tickformat=',', tickprefix='￥'),
            yaxis_title='金額（円）'
        )
        
        return (year_options, selected_year,
                expense_options, selected_expense_category,
                expense_suboptions, selected_expense_subcategory,
                fig_line,fig_bar_category, fig_pie_ex, fig_scatter)