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
        Output('assets-category-dropdown', 'options'),
        Output('assets-category-dropdown', 'value'),
        Output('loan-graph', 'figure'),
        Output('total-debt-value', 'children'),
        Output('total-debt-rate', 'children'),
        Output('year-debt-rate', 'children'),
        Input('year-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('assets-category-dropdown', 'value')
    )
    def update_graph(selected_year, selected_month, selected_assets_category):

        # ==============================
        # データ読み込み
        # ==============================
        config = load_config()
        DATA_DIR = config.get("folder_path")

        dfs = []
        for file in os.listdir(DATA_DIR):
            if file.endswith(".xlsx"):
                df = pd.read_excel(os.path.join(DATA_DIR, file))
                if {'期間','収入/支出','金額','資産'}.issubset(df.columns):
                    df['期間'] = pd.to_datetime(df['期間'], errors='coerce')
                    df.dropna(subset=['期間'], inplace=True)
                    df['期間'] = df['期間'].dt.to_period('M').dt.to_timestamp()
                    dfs.append(df)

        if not dfs:
            empty = px.area(title="対象データがありません")
            return ([], None, [], 'all', empty, empty, empty, empty, empty)

        df_tx = pd.concat(dfs, ignore_index=True)

        # ==============================
        # 初期資産
        # ==============================
        initial_assets = [
            ("JAバンク", 75948),
            ("楽天銀行", 169187),
            ("楽天カード", -7000),
            ("現金", 30944),
            ("シェルカード", -11516),
            ("manaca", 119),
            ("PayPayマネー", 19177),
            ("岡崎信用金庫", 541002),
            ("楽天証券NISA", 103395),
            ("碧海信用金庫", 140323),
            ("労働信用金庫", 234827),
        ]
        initial_map = dict(initial_assets)

        # ==============================
        # 符号付き金額
        # ==============================
        df_tx['符号付き金額'] = df_tx.apply(
            lambda r: r['金額'] if r['収入/支出'] in ['収入','預け入れ','残高収入'] else -r['金額'],
            axis=1
        )

        # ==============================
        # 資産グループ
        # ==============================
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
        }
        df_tx['資産グループ'] = df_tx['資産'].map(group_map)
        
        # ★ カード・ローンを除外
        exclude_groups = ['現金', '電子マネー', '銀行', 'カード']
        df_tx = df_tx[~df_tx['資産グループ'].isin(exclude_groups)]

        # ==============================
        # ★ 全期間 × 全資産（ここが核心）
        # ==============================
        all_months = pd.date_range(
            df_tx['期間'].min(),
            df_tx['期間'].max(),
            freq='MS'
        )

        assets = df_tx[['資産','資産グループ']].drop_duplicates()

        base = (
            assets.assign(key=1)
            .merge(pd.DataFrame({'期間': all_months, 'key': 1}), on='key')
            .drop('key', axis=1)
        )

        tx_monthly = (
            df_tx
            .groupby(['資産グループ','資産','期間'])['符号付き金額']
            .sum()
            .reset_index()
        )

        summary = (
            base
            .merge(tx_monthly, on=['資産グループ','資産','期間'], how='left')
            .fillna({'符号付き金額': 0})
            .sort_values(['資産','期間'])
        )

        # ==============================
        # 累計 + 初期資産
        # ==============================
        summary['累計金額'] = summary.groupby('資産')['符号付き金額'].cumsum()
        summary['累計金額'] += summary['資産'].map(initial_map).fillna(0)

        # ==============================
        # フィルタ
        # ==============================
        years = sorted(summary['期間'].dt.year.unique())
        year_options = [{'label':'すべて','value':'all'}] + [{'label':str(y),'value':y} for y in years]

        if selected_year is None:
            selected_year = 'all'

        df_view = summary.copy()
        if selected_year != 'all':
            df_view = df_view[df_view['期間'].dt.year == selected_year]

        if selected_month != 'all':
            df_view = df_view[df_view['期間'].dt.month == int(selected_month)]

        assets_options = (
            [{'label':'すべて','value':'all'}] +
            [{'label':a,'value':a} for a in sorted(df_view['資産'].unique())]
        )

        if selected_assets_category is None:
            selected_assets_category = 'all'
        
        if selected_assets_category != 'all':
            df_view = df_view[df_view['資産'] == selected_assets_category]

        # ==============================
        # グラフ生成
        # ==============================
        target_groups = ['ローン・奨学金']
        df_combined = df_view[df_view['資産グループ'].isin(target_groups)]
        
        fig_combined = px.area(
            df_combined,
            x='期間',
            y='累計金額',
            color='資産',              # ← 資産ごとに積み上げ
            title='資産残高推移（現金・電子マネー・銀行）'
        )
        
        fig_combined.update_layout(
            xaxis_tickformat='%Y年%m月',
            yaxis_tickformat=',',
            yaxis_tickprefix='￥',
            legend_title_text='負債'
        )
        
        # ==============================
        # 総資産・成長率・前年比
        # ==============================

        df_total = df_view.copy()

        if df_total.empty:
            total_debt = 0
            growth_rate = None
            yoy_rate = None
        else:
            df_total = df_total.sort_values('期間')

            first_month = df_total['期間'].min()
            latest_month = df_total['期間'].max()
            prev_year_month = latest_month - pd.DateOffset(years=1)

            # 初期月の総資産
            first_debt = (
                df_total[df_total['期間'] == first_month]
                .groupby('資産')['累計金額']
                .last()
                .sum()
            )

            # 最新月の総資産
            total_debt = (
                df_total[df_total['期間'] == latest_month]
                .groupby('資産')['累計金額']
                .last()
                .sum()
            )

            # 前年同月の総資産
            prev_year_debt = (
                df_total[df_total['期間'] == prev_year_month]
                .groupby('資産')['累計金額']
                .last()
                .sum()
            )

            # 成長率
            growth_rate = (
                (total_debt - first_debt) / first_debt * 100
                if first_debt < 0 else None
            )

            # 前年比
            yoy_rate = (
                (total_debt - prev_year_debt) / prev_year_debt * 100
                if prev_year_debt < 0 else None
            )

        return (
            year_options, selected_year,
            assets_options, selected_assets_category,
            fig_combined,
            f"￥{int(total_debt):,}",
            None if growth_rate is None else f"{growth_rate:+.1f}%",
            None if yoy_rate is None else f"{yoy_rate:+.1f}%"
        )
