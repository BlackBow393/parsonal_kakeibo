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
        all_dfs = []

        for file in excel_files:
            path = f"{DATA_DIR}/{file}"
            df = pd.read_excel(path)

            if '期間' not in df.columns or '収入/支出' not in df.columns or '金額' not in df.columns:
                continue

            df['期間'] = pd.to_datetime(df['期間'], errors='coerce')
            df.dropna(subset=['期間'], inplace=True)

            # 年列を追加
            df['年'] = df['期間'].dt.year

            # datetime 型で昇順にソート
            df = df.sort_values(by='期間')

            # テーブル用（日付フォーマット）
            df['期間_table'] = df['期間'].dt.strftime("%Y/%m/%d")

            # グラフ用（月ごと）
            df['期間'] = df['期間'].dt.to_period('M').astype(str)

            df = df[df['収入/支出'].isin(['収入', '支出'])]
            all_dfs.append(df)

        if not all_dfs:
            empty_fig = px.bar(title="対象データがありません")
            return [], None, [], 'all', [], 'all', empty_fig, px.pie(title="対象データがありません"), px.pie(title="対象データがありません"), [], [], [], []

        combined_df = pd.concat(all_dfs, ignore_index=True)

        # 年のリストを作成
        years = sorted(combined_df['年'].unique())
        options = [{'label': str(y), 'value': y} for y in years]
        if selected_year is None:
            selected_year = years[-1]  # 最新年をデフォルト

        # 年でフィルタリング
        combined_df = combined_df[combined_df['年'] == selected_year]

        # 月でフィルタリング
        if selected_month != 'all':
            combined_df = combined_df[
                combined_df['期間'].str.startswith(f"{selected_year}-{int(selected_month):02d}")
            ]

        # 収入分類
        income_categories = sorted(combined_df[combined_df['収入/支出'] == '収入']['分類'].dropna().unique())
        category_options_income = [{'label': 'すべて', 'value': 'all'}] + [{'label': c, 'value': c} for c in income_categories]

        if selected_income_category is None or selected_income_category not in [c['value'] for c in category_options_income]:
            selected_income_category = 'all'

        if selected_income_category != 'all':
            combined_df = combined_df[combined_df['分類'] == selected_income_category]

        # 支出分類
        expense_categories = sorted(combined_df[combined_df['収入/支出'] == '支出']['分類'].dropna().unique())
        category_options_expense = [{'label': 'すべて', 'value': 'all'}] + [{'label': c, 'value': c} for c in expense_categories]

        if selected_expense_category is None or selected_expense_category not in [c['value'] for c in category_options_expense]:
            selected_expense_category = 'all'

        if selected_expense_category != 'all':
            combined_df = combined_df[combined_df['分類'] == selected_expense_category]

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
            xaxis=dict(tickformat='%Y年%m月', rangeslider=dict(visible=False)),
            yaxis=dict(tickformat=',', tickprefix='￥')
        )

        # 円グラフ
        income_df = combined_df[combined_df['収入/支出'] == '収入']
        expenses_df = combined_df[combined_df['収入/支出'] == '支出']

        # 円グラフ関数
        def make_pie(df, title):
            if df.empty or '分類' not in df.columns:
                return px.pie(title="対象データがありません")
            grouped = df.groupby('分類')['金額'].sum().reset_index()
            non_other = grouped[grouped['分類'] != 'その他'].sort_values('金額', ascending=False)
            other = grouped[grouped['分類'] == 'その他']
            grouped = pd.concat([non_other, other])
            categories = grouped['分類'].tolist()
            grouped['分類'] = pd.Categorical(grouped['分類'], categories=categories, ordered=True)
            fig = px.pie(grouped, names='分類', values='金額', title=title, category_orders={'分類': categories})
            fig.update_traces(sort=False, direction='clockwise')
            return fig

        fig_pie_in = make_pie(income_df, '収入の分類割合')
        fig_pie_out = make_pie(expenses_df, '支出の分類割合')

        # テーブル用
        display_columns = ['期間_table', '資産', '分類', '小分類', '内容', 'メモ', '金額']
        income_df = income_df[display_columns] if not income_df.empty else pd.DataFrame()
        expenses_df = expenses_df[display_columns] if not expenses_df.empty else pd.DataFrame()

        income_columns = [{"name": i, "id": i} for i in income_df.columns] if not income_df.empty else []
        income_data = income_df.to_dict('records') if not income_df.empty else []

        expenses_columns = [{"name": i, "id": i} for i in expenses_df.columns] if not expenses_df.empty else []
        expenses_data = expenses_df.to_dict('records') if not expenses_df.empty else []

        return (
            options, selected_year,
            category_options_income, selected_income_category,
            category_options_expense, selected_expense_category,
            fig_bar, fig_pie_in, fig_pie_out,
            income_columns, income_data,
            expenses_columns, expenses_data
        )
