#!/usr/bin/env python3
"""
8weeks Fujimi Landscape - Streamlit Web App
ブラウザ上で動作するインタラクティブ事業分析ツール
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

# 同じディレクトリのfujimi_business_model.pyをインポート
sys.path.append(os.path.dirname(__file__))
from fujimi_business_model import FujimBusinessModel

# ページ設定
st.set_page_config(
    page_title="8weeks Fujimi Landscape - 事業分析",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #2E3440;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #5E81AC;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2E3440;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_model():
    """モデルをキャッシュ付きで読み込み"""
    return FujimBusinessModel()

def main():
    # ヘッダー
    st.markdown('<h1 class="main-header">🏔️ 8weeks Fujimi Landscape</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #4C566A;">インタラクティブ事業分析ツール</p>', unsafe_allow_html=True)
    
    # モデル読み込み
    model = load_model()
    
    # サイドバー - パラメータ調整
    st.sidebar.markdown('<p class="sidebar-header">📊 パラメータ調整</p>', unsafe_allow_html=True)
    
    # 基本パラメータ
    occupancy_rate = st.sidebar.slider(
        "稼働率 (%)",
        min_value=15, max_value=70, value=33, step=1,
        help="年間の稼働率を設定します"
    ) / 100
    
    price_per_night = st.sidebar.slider(
        "客単価 (円)",
        min_value=15000, max_value=40000, value=25000, step=1000,
        help="1泊あたりの平均料金を設定します"
    )
    
    # 物件数
    st.sidebar.markdown("### 🏠 物件構成")
    owned_properties = st.sidebar.slider(
        "自社所有物件数",
        min_value=5, max_value=30, value=15, step=1
    )
    
    rental_properties = st.sidebar.slider(
        "賃貸物件数",
        min_value=5, max_value=30, value=15, step=1
    )
    
    # モデルパラメータ更新
    model.params['owned_properties'] = owned_properties
    model.params['rental_properties'] = rental_properties
    
    # 計算実行
    metrics = model.calculate_total_metrics(occupancy_rate, price_per_night)
    
    # メイン画面 - 結果表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "年間売上",
            f"¥{metrics['total_revenue']:,.0f}",
            delta=f"物件数: {owned_properties + rental_properties}"
        )
    
    with col2:
        st.metric(
            "年間利益",
            f"¥{metrics['total_profit']:,.0f}",
            delta=f"利益率: {(metrics['total_profit']/metrics['total_revenue'])*100:.1f}%"
        )
    
    with col3:
        st.metric(
            "ROI",
            f"{metrics['overall_roi']:.1f}%",
            delta="年間投資利益率"
        )
    
    with col4:
        st.metric(
            "投資回収期間",
            f"{metrics['overall_payback']:.1f}年",
            delta=f"総投資額: ¥{metrics['total_investment']:,.0f}"
        )
    
    # タブ表示
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 感応度分析", "📊 シナリオ比較", "🎯 損益分析", "📋 詳細データ", "📚 ドキュメント"])
    
    with tab1:
        st.subheader("感応度分析")
        
        # 感応度分析実行
        occupancy_df = model.sensitivity_analysis('occupancy_rate', 0.15, 0.70, 20)
        price_df = model.sensitivity_analysis('price_per_night', 15000, 40000, 20)
        
        # グラフ作成
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('稼働率 vs ROI', '客単価 vs ROI', '稼働率 vs 投資回収期間', '客単価 vs 年間利益'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 稼働率 vs ROI
        fig.add_trace(
            go.Scatter(x=occupancy_df['occupancy_rate']*100, y=occupancy_df['overall_roi'], 
                      mode='lines+markers', name='ROI', line=dict(color='#5E81AC', width=3)),
            row=1, col=1
        )
        
        # 客単価 vs ROI
        fig.add_trace(
            go.Scatter(x=price_df['price_per_night']/1000, y=price_df['overall_roi'],
                      mode='lines+markers', name='ROI', line=dict(color='#BF616A', width=3),
                      showlegend=False),
            row=1, col=2
        )
        
        # 稼働率 vs 投資回収期間
        payback_capped = occupancy_df['overall_payback'].clip(upper=15)  # 15年でキャップ
        fig.add_trace(
            go.Scatter(x=occupancy_df['occupancy_rate']*100, y=payback_capped,
                      mode='lines+markers', name='回収期間', line=dict(color='#D08770', width=3),
                      showlegend=False),
            row=2, col=1
        )
        
        # 客単価 vs 年間利益
        fig.add_trace(
            go.Bar(x=price_df['price_per_night']/1000, y=price_df['total_profit']/1000000,
                   name='年間利益', marker_color='#A3BE8C', showlegend=False),
            row=2, col=2
        )
        
        fig.update_xaxes(title_text="稼働率 (%)", row=1, col=1)
        fig.update_xaxes(title_text="客単価 (千円)", row=1, col=2)
        fig.update_xaxes(title_text="稼働率 (%)", row=2, col=1)
        fig.update_xaxes(title_text="客単価 (千円)", row=2, col=2)
        
        fig.update_yaxes(title_text="ROI (%)", row=1, col=1)
        fig.update_yaxes(title_text="ROI (%)", row=1, col=2)
        fig.update_yaxes(title_text="投資回収期間 (年)", row=2, col=1)
        fig.update_yaxes(title_text="年間利益 (百万円)", row=2, col=2)
        
        fig.update_layout(height=700, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("シナリオ比較")
        
        # シナリオ分析
        scenarios = {
            '楽観': {'occupancy_rate': 0.50, 'price_per_night': 30000, 'color': '#A3BE8C'},
            '基本': {'occupancy_rate': 0.33, 'price_per_night': 25000, 'color': '#5E81AC'},
            '悲観': {'occupancy_rate': 0.25, 'price_per_night': 22000, 'color': '#D08770'},
            '最悪': {'occupancy_rate': 0.20, 'price_per_night': 20000, 'color': '#BF616A'},
        }
        
        scenario_results = []
        for name, params in scenarios.items():
            scenario_metrics = model.calculate_total_metrics(
                params['occupancy_rate'], params['price_per_night']
            )
            scenario_results.append({
                'シナリオ': name,
                '稼働率': params['occupancy_rate'],
                '客単価': params['price_per_night'],
                'ROI': scenario_metrics['overall_roi'],
                '年間利益': scenario_metrics['total_profit'],
                '投資回収期間': scenario_metrics['overall_payback'],
                'color': params['color']
            })
        
        scenario_df = pd.DataFrame(scenario_results)
        
        # レーダーチャート
        fig_radar = go.Figure()
        
        metrics_radar = ['ROI', '年間利益', '投資回収期間']
        
        for _, row in scenario_df.iterrows():
            # 値を正規化（0-100スケール）
            roi_norm = min(row['ROI'] * 2, 100)  # ROI*2で正規化
            profit_norm = min((row['年間利益'] / 100000000) * 100, 100)  # 1億円=100として正規化
            payback_norm = max(100 - (row['投資回収期間'] * 10), 0)  # 回収期間は逆数的に正規化
            
            fig_radar.add_trace(go.Scatterpolar(
                r=[roi_norm, profit_norm, payback_norm],
                theta=metrics_radar,
                fill='toself',
                name=row['シナリオ'],
                line_color=row['color']
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="シナリオ別パフォーマンス比較",
            height=500
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # シナリオ詳細テーブル
            display_df = scenario_df[['シナリオ', '稼働率', '客単価', 'ROI', '年間利益', '投資回収期間']].copy()
            display_df['稼働率'] = display_df['稼働率'].apply(lambda x: f"{x:.0%}")
            display_df['客単価'] = display_df['客単価'].apply(lambda x: f"¥{x:,}")
            display_df['ROI'] = display_df['ROI'].apply(lambda x: f"{x:.1f}%")
            display_df['年間利益'] = display_df['年間利益'].apply(lambda x: f"¥{x:,.0f}")
            display_df['投資回収期間'] = display_df['投資回収期間'].apply(lambda x: f"{x:.1f}年")
            
            st.dataframe(display_df.set_index('シナリオ'), use_container_width=True)
        
        # リスクファクター分析
        st.markdown("---")
        st.subheader("🎯 主要リスクファクター分析")
        
        # リスクファクターの定義
        risk_factors = {
            "売上面リスク": {
                "稼働率低下": {
                    "要因": "競合激化、観光需要減少、経済情勢悪化",
                    "ダウンサイド": {"稼働率": 0.20, "客単価": 22000},
                    "アップサイド": {"稼働率": 0.55, "客単価": 28000},
                    "base_impact": 0
                },
                "価格競争": {
                    "要因": "類似施設増加、価格競争激化",
                    "ダウンサイド": {"稼働率": 0.28, "客単価": 18000},
                    "アップサイド": {"稼働率": 0.40, "客単価": 32000},
                    "base_impact": 0
                }
            },
            "費用面リスク": {
                "光熱費高騰": {
                    "要因": "エネルギー価格上昇、円安影響",
                    "ダウンサイド": "光熱費1.5倍",
                    "アップサイド": "光熱費0.8倍",
                    "base_impact": 0
                },
                "人件費上昇": {
                    "要因": "最低賃金上昇、人手不足",
                    "ダウンサイド": "運営費1.3倍",
                    "アップサイド": "運営費0.9倍（効率化）",
                    "base_impact": 0
                },
                "賃料上昇": {
                    "要因": "不動産価格上昇、契約更新",
                    "ダウンサイド": "賃料1.2倍",
                    "アップサイド": "賃料0.95倍（交渉成功）",
                    "base_impact": 0
                }
            }
        }
        
        # 基準シナリオ（現在の設定値）
        base_metrics = model.calculate_total_metrics(occupancy_rate, price_per_night)
        
        # リスクシナリオの計算
        st.markdown("### 📊 売上面リスクの影響度")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔻 稼働率・価格低下リスク**")
            
            # 稼働率低下シナリオ
            downside_metrics = model.calculate_total_metrics(0.20, 20000)
            profit_impact = ((downside_metrics['total_profit'] - base_metrics['total_profit']) / base_metrics['total_profit']) * 100
            roi_impact = downside_metrics['overall_roi'] - base_metrics['overall_roi']
            
            st.markdown(f"""
            **主要リスク要因:**
            - 競合施設の増加
            - 観光需要の低迷
            - 経済情勢の悪化
            
            **影響度:**
            - 年間利益: {profit_impact:+.1f}%
            - ROI: {roi_impact:+.1f}%ポイント
            - 投資回収期間: {downside_metrics['overall_payback']:.1f}年
            """)
            
        with col2:
            st.markdown("**🔺 稼働率・価格上昇機会**")
            
            # アップサイドシナリオ
            upside_metrics = model.calculate_total_metrics(0.55, 32000)
            profit_impact_up = ((upside_metrics['total_profit'] - base_metrics['total_profit']) / base_metrics['total_profit']) * 100
            roi_impact_up = upside_metrics['overall_roi'] - base_metrics['overall_roi']
            
            st.markdown(f"""
            **主要機会要因:**
            - 観光需要の増加
            - プレミアム化の成功
            - マーケティング強化効果
            
            **影響度:**
            - 年間利益: {profit_impact_up:+.1f}%
            - ROI: {roi_impact_up:+.1f}%ポイント
            - 投資回収期間: {upside_metrics['overall_payback']:.1f}年
            """)
        
        st.markdown("### 💸 費用面リスクの影響度")
        
        # 費用増加シナリオの計算（モデルを一時的に変更）
        original_fixed_costs = model.fixed_costs.copy()
        original_variable_costs = model.variable_costs.copy()
        
        # 光熱費・運営費高騰シナリオ
        model.fixed_costs['owned']['utilities_fixed'] *= 1.4
        model.fixed_costs['rental']['utilities_fixed'] *= 1.4
        model.variable_costs['owned']['utilities_variable'] *= 1.5
        model.variable_costs['rental']['utilities_variable'] *= 1.5
        model.fixed_costs['owned']['operations_fixed'] *= 1.25
        model.fixed_costs['rental']['operations_fixed'] *= 1.25
        model.variable_costs['owned']['operations_variable'] *= 1.3
        model.variable_costs['rental']['operations_variable'] *= 1.3
        model.fixed_costs['rental']['rent'] *= 1.15
        
        cost_risk_metrics = model.calculate_total_metrics(occupancy_rate, price_per_night)
        cost_profit_impact = ((cost_risk_metrics['total_profit'] - base_metrics['total_profit']) / base_metrics['total_profit']) * 100
        cost_roi_impact = cost_risk_metrics['overall_roi'] - base_metrics['overall_roi']
        
        # 費用削減シナリオ
        model.fixed_costs = original_fixed_costs.copy()
        model.variable_costs = original_variable_costs.copy()
        
        model.fixed_costs['owned']['utilities_fixed'] *= 0.85
        model.fixed_costs['rental']['utilities_fixed'] *= 0.85
        model.variable_costs['owned']['utilities_variable'] *= 0.8
        model.variable_costs['rental']['utilities_variable'] *= 0.8
        model.fixed_costs['owned']['operations_fixed'] *= 0.92
        model.fixed_costs['rental']['operations_fixed'] *= 0.92
        model.variable_costs['owned']['operations_variable'] *= 0.9
        model.variable_costs['rental']['operations_variable'] *= 0.9
        model.fixed_costs['rental']['rent'] *= 0.97
        
        cost_savings_metrics = model.calculate_total_metrics(occupancy_rate, price_per_night)
        cost_savings_impact = ((cost_savings_metrics['total_profit'] - base_metrics['total_profit']) / base_metrics['total_profit']) * 100
        cost_savings_roi_impact = cost_savings_metrics['overall_roi'] - base_metrics['overall_roi']
        
        # 元の値に戻す
        model.fixed_costs = original_fixed_costs
        model.variable_costs = original_variable_costs
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔻 費用上昇リスク**")
            st.markdown(f"""
            **主要リスク要因:**
            - エネルギー価格上昇 (+50%光熱費)
            - 人件費・運営費上昇 (+25-30%)
            - 不動産価格上昇 (+15%賃料)
            
            **影響度:**
            - 年間利益: {cost_profit_impact:+.1f}%
            - ROI: {cost_roi_impact:+.1f}%ポイント
            - 投資回収期間: {cost_risk_metrics['overall_payback']:.1f}年
            """)
            
        with col2:
            st.markdown("**🔺 費用削減機会**")
            st.markdown(f"""
            **主要機会要因:**
            - 省エネ設備導入 (-15-20%光熱費)
            - 運営効率化 (-8-10%運営費)
            - 賃料交渉成功 (-3%賃料)
            
            **影響度:**
            - 年間利益: {cost_savings_impact:+.1f}%
            - ROI: {cost_savings_roi_impact:+.1f}%ポイント
            - 投資回収期間: {cost_savings_metrics['overall_payback']:.1f}年
            """)
        
        # リスク影響度サマリー
        st.markdown("### 📈 リスク影響度サマリー")
        
        risk_summary_data = {
            'リスク要因': [
                '売上激減（稼働20%・単価2万円）',
                '売上好調（稼働55%・単価3.2万円）', 
                '費用上昇（光熱費+50%等）',
                '費用削減（省エネ化等）'
            ],
            '年間利益への影響': [
                f'{profit_impact:+.1f}%',
                f'{profit_impact_up:+.1f}%',
                f'{cost_profit_impact:+.1f}%',
                f'{cost_savings_impact:+.1f}%'
            ],
            'ROIへの影響': [
                f'{roi_impact:+.1f}%pt',
                f'{roi_impact_up:+.1f}%pt',
                f'{cost_roi_impact:+.1f}%pt',
                f'{cost_savings_roi_impact:+.1f}%pt'
            ],
            'リスク確率': ['低', '中', '中', '高'],
            '対策可能性': ['部分的', '積極策で可能', '部分的', '高い']
        }
        
        risk_summary_df = pd.DataFrame(risk_summary_data)
        st.dataframe(risk_summary_df, use_container_width=True)
        
        st.markdown("""
        **🎯 リスク管理のポイント:**
        - **売上リスク**: 多様な集客チャネルの確保、差別化戦略
        - **費用リスク**: 省エネ設備投資、運営効率化、契約交渉
        - **モニタリング**: 月次での実績管理と早期対策
        """)
    
    with tab3:
        st.subheader("損益分岐点分析")
        
        # 固定費計算（損益分岐点分析では減価償却費除外）
        fixed_cost_owned = (model.fixed_costs['owned']['operations_fixed'] + 
                           model.fixed_costs['owned']['utilities_fixed'] + 
                           model.fixed_costs['owned']['insurance']) * owned_properties
        
        fixed_cost_rental = (model.fixed_costs['rental']['rent'] + 
                            model.fixed_costs['rental']['operations_fixed'] + 
                            model.fixed_costs['rental']['utilities_fixed'] + 
                            model.fixed_costs['rental']['insurance']) * rental_properties
        
        # 損益分岐点は現金ベース（減価償却費除外）
        total_fixed_costs = fixed_cost_owned + fixed_cost_rental
        
        # 損益分岐点計算
        total_properties = owned_properties + rental_properties
        daily_revenue_potential = price_per_night * total_properties
        breakeven_days = total_fixed_costs / daily_revenue_potential
        breakeven_occupancy = (breakeven_days / 365) * 100
        
        # 損益分岐点グラフ
        occupancy_range = np.linspace(10, 70, 100)
        revenues = (occupancy_range / 100) * daily_revenue_potential * 365
        costs = np.full_like(revenues, total_fixed_costs)
        
        fig_breakeven = go.Figure()
        
        fig_breakeven.add_trace(go.Scatter(
            x=occupancy_range, y=revenues/1000000,
            mode='lines', name='年間売上', line=dict(color='#A3BE8C', width=3)
        ))
        
        fig_breakeven.add_trace(go.Scatter(
            x=occupancy_range, y=costs/1000000,
            mode='lines', name='固定費', line=dict(color='#BF616A', width=3, dash='dash')
        ))
        
        fig_breakeven.add_vline(
            x=breakeven_occupancy, line_dash="dot", line_color="orange", line_width=3,
            annotation_text=f"損益分岐点: {breakeven_occupancy:.1f}%"
        )
        
        fig_breakeven.add_vline(
            x=occupancy_rate*100, line_dash="solid", line_color="blue", line_width=2,
            annotation_text=f"現在稼働率: {occupancy_rate*100:.1f}%"
        )
        
        fig_breakeven.update_layout(
            title="損益分岐点分析",
            xaxis_title="稼働率 (%)",
            yaxis_title="金額 (百万円)",
            height=500
        )
        
        st.plotly_chart(fig_breakeven, use_container_width=True)
        
        # 損益分岐点情報
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("損益分岐稼働率", f"{breakeven_occupancy:.1f}%")
        with col2:
            st.metric("安全余裕", f"{occupancy_rate*100 - breakeven_occupancy:.1f}%ポイント")
        with col3:
            st.metric("固定費総額", f"¥{total_fixed_costs:,.0f}")
    
    with tab4:
        st.subheader("詳細財務データ")
        
        # 物件タイプ別詳細
        owned_metrics = metrics['owned_metrics']
        rental_metrics = metrics['rental_metrics']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏠 自社所有物件")
            owned_data = {
                '項目': ['年間売上', 'NOI', '総投資額', 'ROI', '投資回収期間'],
                '金額・値': [
                    f"¥{owned_metrics['annual_revenue']:,.0f}",
                    f"¥{owned_metrics['noi']:,.0f}",
                    f"¥{owned_metrics['total_investment']:,.0f}",
                    f"{owned_metrics['roi']:.1f}%",
                    f"{owned_metrics['payback_period']:.1f}年"
                ]
            }
            st.dataframe(pd.DataFrame(owned_data), use_container_width=True)
        
        with col2:
            st.markdown("#### 🏢 賃貸物件")
            rental_data = {
                '項目': ['年間売上', '営業利益', '総投資額', 'ROI', '投資回収期間'],
                '金額・値': [
                    f"¥{rental_metrics['annual_revenue']:,.0f}",
                    f"¥{rental_metrics['operating_profit']:,.0f}",
                    f"¥{rental_metrics['total_investment']:,.0f}",
                    f"{rental_metrics['roi']:.1f}%",
                    f"{rental_metrics['payback_period']:.1f}年"
                ]
            }
            st.dataframe(pd.DataFrame(rental_data), use_container_width=True)
        
        # コスト内訳
        st.markdown("#### 💰 コスト内訳")
        
        # 変動費を計算
        owned_variable_costs = model.calculate_variable_costs(occupancy_rate, 'owned', owned_properties)
        rental_variable_costs = model.calculate_variable_costs(occupancy_rate, 'rental', rental_properties)
        
        cost_breakdown = {
            '自社所有物件': [
                f"固定運営費: ¥{model.fixed_costs['owned']['operations_fixed'] * owned_properties:,.0f}",
                f"基本光熱費: ¥{model.fixed_costs['owned']['utilities_fixed'] * owned_properties:,.0f}",
                f"変動費(稼働率連動): ¥{owned_variable_costs:,.0f}",
                f"保険等: ¥{model.fixed_costs['owned']['insurance'] * owned_properties:,.0f}",
                f"減価償却(非現金): ¥{(model.params['owned_initial_investment'] * owned_properties / model.params['depreciation_years']):,.0f}"
            ],
            '賃貸物件': [
                f"賃料: ¥{model.fixed_costs['rental']['rent'] * rental_properties:,.0f}",
                f"固定運営費: ¥{model.fixed_costs['rental']['operations_fixed'] * rental_properties:,.0f}",
                f"基本光熱費: ¥{model.fixed_costs['rental']['utilities_fixed'] * rental_properties:,.0f}",
                f"変動費(稼働率連動): ¥{rental_variable_costs:,.0f}",
                f"保険等: ¥{model.fixed_costs['rental']['insurance'] * rental_properties:,.0f}"
            ]
        }
        
        col1, col2 = st.columns(2)
        with col1:
            for cost in cost_breakdown['自社所有物件']:
                st.text(cost)
        with col2:
            for cost in cost_breakdown['賃貸物件']:
                st.text(cost)
    
    with tab5:
        st.subheader("📚 計算前提とドキュメント")
        
        # 基本前提
        st.markdown("### 🏗️ 事業モデルの基本前提")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📊 基本パラメータ**
            - **基準稼働率**: 33%（年間120日稼働）
            - **平均客単価**: ¥25,000/泊
            - **自社所有物件**: 15軒
            - **賃貸物件**: 15軒
            - **減価償却年数**: 7年
            """)
            
        with col2:
            st.markdown("""
            **💰 初期投資額**
            - **自社所有物件**: ¥18,900,000/軒
                - 物件取得費
                - 改装・設備投資費
            - **賃貸物件**: ¥5,500,000/軒
                - 敷金・保証金
                - 改装・設備投資費
            """)
        
        # 費用構造
        st.markdown("### 💸 費用構造の詳細")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🏠 自社所有物件（年間・物件あたり）**
            
            **固定費（稼働率に関係なく発生）:**
            - 固定運営費: ¥400,000
                - 基本管理費、システム利用料
            - 基本光熱費: ¥80,000
                - 最低契約料金、基本料金
            - 保険・雑費: ¥60,000
                - 損害保険、税金等
            
            **変動費（稼働率33%時の基準額）:**
            - 変動運営費: ¥79,200
                - 清掃費、消耗品費（稼働日数に比例）
            - 変動光熱費: ¥22,440
                - 使用量分の電気・ガス・水道代
            - 清掃・メンテナンス: ¥39,600
                - 利用後清掃、定期メンテナンス
            """)
            
        with col2:
            st.markdown("""
            **🏢 賃貸物件（年間・物件あたり）**
            
            **固定費（稼働率に関係なく発生）:**
            - 年間賃料: ¥840,000
                - 月額¥70,000の固定賃料
            - 固定運営費: ¥900,000
                - 基本管理費、システム利用料
            - 基本光熱費: ¥60,000
                - 最低契約料金、基本料金
            - 保険・雑費: ¥40,000
                - 損害保険等
            
            **変動費（稼働率33%時の基準額）:**
            - 変動運営費: ¥196,020
                - 清掃費、消耗品費（稼働日数に比例）
            - 変動光熱費: ¥18,150
                - 使用量分の電気・ガス・水道代
            - 清掃・メンテナンス: ¥49,500
                - 利用後清掃、定期メンテナンス
            """)
        
        # 計算ロジック
        st.markdown("### 🧮 計算ロジックの説明")
        
        st.markdown("""
        **📈 変動費の計算方法**
        
        変動費は稼働率に比例して変化します：
        
        ```
        実際の変動費 = 基準変動費 × (実際の稼働率 ÷ 基準稼働率33%)
        ```
        
        **例：** 稼働率が50%の場合
        - 変動費倍率 = 50% ÷ 33% = 約1.52倍
        - 実際の変動費 = 基準変動費 × 1.52
        
        **📊 主要指標の計算式**
        
        1. **年間売上**
           ```
           年間売上 = 稼働率 × 客単価 × 365日 × 物件数
           ```
        
        2. **NOI（Net Operating Income）**
           ```
           NOI = 年間売上 - 営業費用
           営業費用 = 固定費 + 変動費
           ※減価償却費は除外（非現金項目のため）
           ```
        
        3. **ROI（投資利益率）**
           ```
           ROI = (NOI ÷ 初期投資額) × 100
           ```
        
        4. **投資回収期間**
           ```
           投資回収期間 = 初期投資額 ÷ NOI
           ```
        
        5. **損益分岐稼働率**
           ```
           損益分岐稼働率 = 固定費 ÷ (客単価 × 365日 × 物件数)
           ※変動費は稼働率ゼロ時点での計算のため除外
           ```
        """)
        
        # 重要な注意点
        st.markdown("### ⚠️ 重要な注意点")
        
        st.markdown("""
        **📝 計算の前提条件**
        
        - **NOI計算**: 減価償却費は含まない（現金ベース）
        - **損益分岐点**: 現金ベースで計算（減価償却費除外）
        - **変動費**: 稼働率に完全比例すると仮定
        - **客単価**: 季節変動は考慮しない平均値
        - **稼働率**: 年間を通じて一定と仮定
        
        **🎯 モデルの限界**
        
        - 実際の運営では季節変動がある
        - 競合状況の変化は考慮しない
        - 大規模修繕費は含まない
        - 人件費の詳細は運営費に含む
        - 税金・融資コストは含まない
        
        **💡 使用上の注意**
        
        - このモデルは事業計画の参考用途
        - 実際の投資判断には詳細な市場調査が必要
        - 定期的なパラメータ見直しを推奨
        """)

if __name__ == "__main__":
    main()