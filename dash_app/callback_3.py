import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
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
        Output('pie-in-chart', 'figure'),
        Output('pie-in-subchart', 'figure'),
        Output('income-graph', 'figure'),
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
            empty_pie = px.pie(title="対象データがありません")
            return ([], None, [], 'all', [], 'all', empty_bar, empty_line, empty_pie, empty_pie,empty_bar)

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
        df_bar = df_filtered.groupby(['年', '分類'], as_index=False)['金額'].sum()
        
        # 年ごとの合計金額を計算（ラベル用）
        df_total = df_bar.groupby('年', as_index=False)['金額'].sum()

        fig_bar = px.bar(
            df_bar,
            x='年',
            y='金額',
            color='分類',
            title="年別 収入分類の内訳",
            labels={'金額': '金額（円）', '年': '年'},
            color_discrete_map={'その他': 'dimgray'} 
        )
        fig_bar.update_layout(
            barmode='stack', 
            yaxis=dict(tickformat=',', tickprefix='￥'),
            yaxis_title="金額（円）",
            xaxis=dict(
                tickmode='array',              # 目盛りを手動指定
                tickvals=sorted(df_bar['年'].unique()),  # 年（整数）のみを表示
                ticktext=[str(y) for y in sorted(df_bar['年'].unique())]  # 表示文字列
            )
        )
        
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

        # タイトルを条件で切り替える
        if selected_year == 'all':
            title_text_line = '全年 分類別収入金額'
        else:
            title_text_line = f'{selected_year}年 分類別収入金額'

        fig_line = px.line(
            monthly,
            x='期間',  # ← datetimeのまま
            y='金額',
            markers=True,
            title=title_text_line
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

        fig_pie_in = make_pie(df_filtered[df_filtered['収入/支出']=='収入'], '収入の分類割合')
        
        # 小分類の円グラフ作成
        def make_pie(df, title):
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

        fig_pie_in_sub = make_pie(df_filtered[df_filtered['収入/支出']=='収入'], '収入の小分類割合')
        
        # --- 📊 年別・年収棒グラフ ---
        # 分類が「給与」のデータだけ抽出
        df_bar_income = combined_df[combined_df['分類'] == '💰 給料']
        df_bar_income = df_bar_income.groupby(['年', '分類'], as_index=False)['金額'].sum()
        
        # 回帰直線を計算（線形近似）
        # 年を数値型に変換（polyfitは数値でないと動かない）
        x = df_bar_income['年'].astype(int)
        y = df_bar_income['金額']
        
        # 1次式で近似（y = a*x + b）
        a, b = np.polyfit(x, y, 1)
        
        # --- 🔹 来年を外挿して追加 ---
        next_year = x.max() + 1
        y_next = a * next_year + b  # 来年の予測値
        
        y_fit = a * x + b
        
        # 元データ + 来年の予測点をプロット用にまとめる
        x_extended = np.append(x, next_year)
        y_fit_extended = np.append(y_fit, y_next)

        fig_bar_income = px.bar(
            df_bar_income,
            x='年',
            y='金額',
            color='分類',
            title="年収推移",
            labels={'金額': '金額（円）', '年': '年'},
            color_discrete_map={'💰 給料': 'cornflowerblue'} 
        )
        
        # 回帰直線を追加
        fig_bar_income.add_trace(
            go.Scatter(
                x=x_extended,
                y=y_fit_extended,
                mode='lines',
                name='年収予測線',
                line=dict(color='red', width=2, dash='dash')
            )
        )
        
        # 来年の予測点を強調表示（オプション）
        fig_bar_income.add_trace(
            go.Scatter(
                x=[next_year],
                y=[y_next],
                mode='markers+text',
                name='来年予測',
                text=[f"{int(next_year)}年\n予測: {y_next:,.0f}円"],
                textposition='top center',
                marker=dict(color='red', size=10, symbol='diamond')
            )
        )
        
        fig_bar_income.update_layout(
            barmode='stack', 
            yaxis=dict(tickformat=',', tickprefix='￥'),
            yaxis_title="金額（円）",
            xaxis=dict(
                tickmode='array',              # 目盛りを手動指定
                tickvals=sorted(list(x) + [next_year]),  # 年（整数）のみを表示
                ticktext=[str(y) for y in sorted(list(x) + [next_year])]  # 表示文字列
            )
        )
        
        return (year_options, selected_year,
                income_options, selected_income_category,
                income_suboptions, selected_income_subcategory,
                fig_bar, fig_line, fig_pie_in, fig_pie_in_sub,fig_bar_income)