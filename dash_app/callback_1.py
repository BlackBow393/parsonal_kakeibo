import pandas as pd
import plotly.express as px
from dash import Input, Output

def register_callbacks(dash_app, excel_files, DATA_DIR):
    @dash_app.callback(
        Output('year-dropdown', 'options'),
        Output('year-dropdown', 'value'),
        Output('income-category-dropdown', 'options'),
        Output('income-category-dropdown', 'value'),
        Output('expense-category-dropdown', 'options'),
        Output('expense-category-dropdown', 'value'),
        Output('excel-graph', 'figure'),
        Output('pie-in-chart', 'figure'),
        Output('pie-out-chart', 'figure'),
        Output('income-table', 'columns'),
        Output('income-table', 'data'),
        Output('expenses-table', 'columns'),
        Output('expenses-table', 'data'),
        Input('year-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('income-category-dropdown', 'value'),
        Input('expense-category-dropdown', 'value')
    )
    def update_graph(selected_year, selected_month, selected_income_category, selected_expense_category):
        # --- 元データ読み込み ---
        all_dfs = []
        for file in excel_files:
            path = f"{DATA_DIR}/{file}"
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
            return [], None, [], 'all', [], 'all', empty_fig, px.pie(title="対象データがありません"), px.pie(title="対象データがありません"), [], [], [], []

        combined_df = pd.concat(all_dfs, ignore_index=True)

        # --- 年リスト作成 ---
        years = sorted(combined_df['年'].unique())
        year_options = [{'label': str(y), 'value': y} for y in years]
        if selected_year is None:
            selected_year = years[-1]

        # 年フィルタ
        df_filtered = combined_df[combined_df['年'] == selected_year]

        # --- 月フィルタ ---
        if selected_month != 'all':
            # selected_month は 1～12 の整数
            month_str = f"{selected_year}-{int(selected_month):02d}"  # "2025-09" の形式に
            df_filtered = df_filtered[df_filtered['期間'] == month_str]

        # --- 収入カテゴリ ---
        income_categories = sorted(df_filtered[df_filtered['収入/支出']=='収入']['分類'].dropna().unique())
        income_options = [{'label':'すべて','value':'all'}] + [{'label':c,'value':c} for c in income_categories]
        if selected_income_category not in [c['value'] for c in income_options]:
            selected_income_category = 'all'
        if selected_income_category != 'all':
            df_filtered = df_filtered[df_filtered['分類'] == selected_income_category]

        # --- 支出カテゴリ ---
        expense_categories = sorted(df_filtered[df_filtered['収入/支出']=='支出']['分類'].dropna().unique())
        expense_options = [{'label':'すべて','value':'all'}] + [{'label':c,'value':c} for c in expense_categories]
        if selected_expense_category not in [c['value'] for c in expense_options]:
            selected_expense_category = 'all'
        if selected_expense_category != 'all':
            df_filtered = df_filtered[df_filtered['分類'] == selected_expense_category]

        # --- 棒グラフ作成 ---
        summary_bar = df_filtered.groupby(['期間','収入/支出'])['金額'].sum().reset_index()
        fig_bar = px.bar(summary_bar, x='期間', y='金額', color='収入/支出', barmode='group',
                         title="期間別収支分類", labels={'金額':'金額（円）','期間':'期間'},
                         color_discrete_map={
                            '収入': 'cornflowerblue',   # 収入は青
                            '支出': 'tomato'     # 支出は赤
                            }
                        )
        fig_bar.update_layout(xaxis=dict(tickformat='%Y年%m月', rangeslider=dict(visible=False)),
                              yaxis=dict(tickformat=',', tickprefix='￥'))

        # --- 円グラフ作成関数 ---
        def make_pie(df, title):
            if df.empty or '分類' not in df.columns:
                return px.pie(title="対象データがありません")
            
            grouped = df.groupby('分類')['金額'].sum().reset_index()
            non_other = grouped[grouped['分類'] != 'その他'].sort_values('金額', ascending=False)
            other = grouped[grouped['分類'] == 'その他']
            grouped = pd.concat([non_other, other])
            
            categories = grouped['分類'].tolist()
            grouped['分類'] = pd.Categorical(grouped['分類'], categories=categories, ordered=True)
            
            # その他以外はデフォルト色、その他だけ dimgray
            default_colors = px.colors.qualitative.Plotly  # デフォルトのパレット
            color_map = {}
            j = 0
            for c in categories:
                if c == 'その他':
                    color_map[c] = 'dimgray'
                else:
                    color_map[c] = default_colors[j % len(default_colors)]
                    j += 1
            
            fig = px.pie(
                grouped,
                names='分類',
                values='金額',
                title=title,
                category_orders={'分類': categories},
                color='分類',
                color_discrete_map=color_map
            )
            fig.update_traces(sort=False, direction='clockwise')
            return fig

        fig_pie_in = make_pie(df_filtered[df_filtered['収入/支出']=='収入'],'収入の分類割合')
        fig_pie_out = make_pie(df_filtered[df_filtered['収入/支出']=='支出'],'支出の分類割合')

        # --- テーブル ---
        display_cols = ['期間_table','資産','分類','小分類','内容','メモ','金額']
        income_df = df_filtered[df_filtered['収入/支出']=='収入'][display_cols] if not df_filtered.empty else pd.DataFrame()
        expenses_df = df_filtered[df_filtered['収入/支出']=='支出'][display_cols] if not df_filtered.empty else pd.DataFrame()

        income_columns = [{"name":i,"id":i} for i in income_df.columns] if not income_df.empty else []
        income_data = income_df.to_dict('records') if not income_df.empty else []

        expenses_columns = [{"name":i,"id":i} for i in expenses_df.columns] if not expenses_df.empty else []
        expenses_data = expenses_df.to_dict('records') if not expenses_df.empty else []

        return (year_options, selected_year,
                income_options, selected_income_category,
                expense_options, selected_expense_category,
                fig_bar, fig_pie_in, fig_pie_out,
                income_columns, income_data,
                expenses_columns, expenses_data)
