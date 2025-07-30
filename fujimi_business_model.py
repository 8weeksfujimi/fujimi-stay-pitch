#!/usr/bin/env python3
"""
8weeks Fujimi Landscape - インタラクティブ事業モデル分析ツール
リアルタイムで感応度分析・シナリオ分析が可能
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import Slider
import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

class FujimBusinessModel:
    """8weeks Fujimi Landscape 事業モデルクラス"""
    
    def __init__(self):
        # 基本パラメータ
        self.params = {
            'owned_initial_investment': 18_900_000,  # 自社所有物件初期投資
            'rental_initial_investment': 5_500_000,  # 賃貸物件初期投資
            'base_occupancy_rate': 0.33,             # 基本稼働率
            'average_price_per_night': 25_000,       # 平均客単価
            'owned_properties': 15,                   # 自社所有物件数
            'rental_properties': 15,                  # 賃貸物件数
            'depreciation_years': 7,                  # 減価償却年数
            'monthly_rent': 70_000,                   # 月額賃料
        }
        
        # 固定費（年間・物件あたり）
        self.fixed_costs = {
            'owned': {
                'operations_fixed': 400_000,    # 固定運営費
                'utilities_fixed': 80_000,      # 基本光熱費・通信費
                'insurance': 60_000,            # 保険・雑費
            },
            'rental': {
                'rent': 840_000,                # 年間賃料
                'operations_fixed': 900_000,    # 固定運営費
                'utilities_fixed': 60_000,      # 基本光熱費・通信費
                'insurance': 40_000,            # 保険・雑費
            }
        }
        
        # 変動費（稼働率に連動・年間・物件あたり）
        self.variable_costs = {
            'owned': {
                'operations_variable': 240_000 * 0.33,  # 稼働率33%時の変動運営費
                'utilities_variable': 68_000 * 0.33,    # 稼働率33%時の変動光熱費
                'cleaning_maintenance': 120_000 * 0.33, # 清掃・メンテナンス費
            },
            'rental': {
                'operations_variable': 594_000 * 0.33,  # 稼働率33%時の変動運営費
                'utilities_variable': 55_000 * 0.33,    # 稼働率33%時の変動光熱費
                'cleaning_maintenance': 150_000 * 0.33, # 清掃・メンテナンス費
            }
        }
    
    def calculate_annual_revenue(self, occupancy_rate, price_per_night, num_properties):
        """年間売上計算"""
        days_per_year = 365
        return occupancy_rate * price_per_night * days_per_year * num_properties
    
    def calculate_variable_costs(self, occupancy_rate, property_type, num_properties):
        """稼働率に応じた変動費計算"""
        base_occupancy = 0.33  # 基準稼働率33%
        
        # 稼働率に応じて変動費を計算（線形比例）
        occupancy_factor = occupancy_rate / base_occupancy
        
        variable_costs_per_property = self.variable_costs[property_type]
        total_variable_costs = 0
        
        for cost_type, base_cost in variable_costs_per_property.items():
            # 稼働率に比例して変動費を計算
            actual_cost = base_cost * occupancy_factor
            total_variable_costs += actual_cost
        
        return total_variable_costs * num_properties
    
    def calculate_owned_property_metrics(self, occupancy_rate=None, price_per_night=None, num_properties=None):
        """自社所有物件の収益計算"""
        occupancy_rate = occupancy_rate or self.params['base_occupancy_rate']
        price_per_night = price_per_night or self.params['average_price_per_night']
        num_properties = num_properties or self.params['owned_properties']
        
        # 年間売上
        annual_revenue = self.calculate_annual_revenue(occupancy_rate, price_per_night, num_properties)
        
        # 固定費（NOI計算用 - 減価償却費除外）
        fixed_operations_cost = self.fixed_costs['owned']['operations_fixed'] * num_properties
        fixed_utilities_cost = self.fixed_costs['owned']['utilities_fixed'] * num_properties
        insurance_cost = self.fixed_costs['owned']['insurance'] * num_properties
        
        # 変動費（稼働率に連動）
        total_variable_costs = self.calculate_variable_costs(occupancy_rate, 'owned', num_properties)
        
        # NOI計算用の営業費用（減価償却費除外）
        operating_costs = fixed_operations_cost + fixed_utilities_cost + insurance_cost + total_variable_costs
        
        # NOI（Net Operating Income - 減価償却前営業利益）
        noi = annual_revenue - operating_costs
        
        # 減価償却費（参考値として保持）
        depreciation = (self.params['owned_initial_investment'] * num_properties) / self.params['depreciation_years']
        
        # 総費用（会計上の総費用、減価償却含む）
        total_costs = operating_costs + depreciation
        
        # 投資回収期間
        total_investment = self.params['owned_initial_investment'] * num_properties
        payback_period = total_investment / noi if noi > 0 else float('inf')
        
        # ROI
        roi = (noi / total_investment) * 100 if total_investment > 0 else 0
        
        return {
            'annual_revenue': annual_revenue,
            'noi': noi,
            'total_investment': total_investment,
            'payback_period': payback_period,
            'roi': roi,
            'total_costs': total_costs,
            'operating_costs': operating_costs,
            'depreciation': depreciation,
            'variable_costs': total_variable_costs
        }
    
    def calculate_rental_property_metrics(self, occupancy_rate=None, price_per_night=None, num_properties=None):
        """賃貸物件の収益計算"""
        occupancy_rate = occupancy_rate or self.params['base_occupancy_rate']
        price_per_night = price_per_night or self.params['average_price_per_night']
        num_properties = num_properties or self.params['rental_properties']
        
        # 年間売上
        annual_revenue = self.calculate_annual_revenue(occupancy_rate, price_per_night, num_properties)
        
        # 固定費
        rent_cost = self.fixed_costs['rental']['rent'] * num_properties
        fixed_operations_cost = self.fixed_costs['rental']['operations_fixed'] * num_properties
        fixed_utilities_cost = self.fixed_costs['rental']['utilities_fixed'] * num_properties
        insurance_cost = self.fixed_costs['rental']['insurance'] * num_properties
        
        total_fixed_costs = rent_cost + fixed_operations_cost + fixed_utilities_cost + insurance_cost
        
        # 変動費（稼働率に連動）
        total_variable_costs = self.calculate_variable_costs(occupancy_rate, 'rental', num_properties)
        
        # 総費用
        total_costs = total_fixed_costs + total_variable_costs
        
        # 営業利益
        operating_profit = annual_revenue - total_costs
        
        # 投資回収期間
        total_investment = self.params['rental_initial_investment'] * num_properties
        payback_period = total_investment / operating_profit if operating_profit > 0 else float('inf')
        
        # ROI
        roi = (operating_profit / total_investment) * 100 if total_investment > 0 else 0
        
        return {
            'annual_revenue': annual_revenue,
            'operating_profit': operating_profit,
            'total_investment': total_investment,
            'payback_period': payback_period,
            'roi': roi,
            'total_costs': total_costs,
            'fixed_costs': total_fixed_costs,
            'variable_costs': total_variable_costs
        }
    
    def calculate_total_metrics(self, occupancy_rate=None, price_per_night=None):
        """全体の収益計算"""
        owned_metrics = self.calculate_owned_property_metrics(occupancy_rate, price_per_night)
        rental_metrics = self.calculate_rental_property_metrics(occupancy_rate, price_per_night)
        
        total_revenue = owned_metrics['annual_revenue'] + rental_metrics['annual_revenue']
        total_profit = owned_metrics['noi'] + rental_metrics['operating_profit']
        total_investment = owned_metrics['total_investment'] + rental_metrics['total_investment']
        
        overall_payback = total_investment / total_profit if total_profit > 0 else float('inf')
        overall_roi = (total_profit / total_investment) * 100 if total_investment > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'total_investment': total_investment,
            'overall_payback': overall_payback,
            'overall_roi': overall_roi,
            'owned_metrics': owned_metrics,
            'rental_metrics': rental_metrics
        }
    
    def sensitivity_analysis(self, param_name, min_val, max_val, steps=10):
        """感応度分析"""
        values = np.linspace(min_val, max_val, steps)
        results = []
        
        for val in values:
            if param_name == 'occupancy_rate':
                metrics = self.calculate_total_metrics(occupancy_rate=val)
            elif param_name == 'price_per_night':
                metrics = self.calculate_total_metrics(price_per_night=val)
            else:
                # その他のパラメータの場合は一時的に変更
                original_val = self.params.get(param_name)
                self.params[param_name] = val
                metrics = self.calculate_total_metrics()
                self.params[param_name] = original_val
            
            results.append({
                param_name: val,
                'total_profit': metrics['total_profit'],
                'overall_roi': metrics['overall_roi'],
                'overall_payback': metrics['overall_payback']
            })
        
        return pd.DataFrame(results)
    
    def scenario_analysis(self):
        """シナリオ分析"""
        scenarios = {
            '楽観': {'occupancy_rate': 0.50, 'price_per_night': 30_000},
            '基本': {'occupancy_rate': 0.33, 'price_per_night': 25_000},
            '悲観': {'occupancy_rate': 0.25, 'price_per_night': 22_000},
            '最悪': {'occupancy_rate': 0.20, 'price_per_night': 20_000},
        }
        
        results = []
        for scenario_name, params in scenarios.items():
            metrics = self.calculate_total_metrics(
                occupancy_rate=params['occupancy_rate'],
                price_per_night=params['price_per_night']
            )
            results.append({
                'シナリオ': scenario_name,
                '稼働率': f"{params['occupancy_rate']:.0%}",
                '客単価': f"¥{params['price_per_night']:,}",
                '年間売上': f"¥{metrics['total_revenue']:,.0f}",
                '年間利益': f"¥{metrics['total_profit']:,.0f}",
                'ROI': f"{metrics['overall_roi']:.1f}%",
                '投資回収期間': f"{metrics['overall_payback']:.1f}年"
            })
        
        return pd.DataFrame(results)

class InteractiveModelAnalyzer:
    """インタラクティブ分析ツール"""
    
    def __init__(self, model):
        self.model = model
        self.setup_widgets()
    
    def setup_widgets(self):
        """ウィジェット設定"""
        style = {'description_width': '150px'}
        layout = widgets.Layout(width='400px')
        
        self.occupancy_slider = widgets.FloatSlider(
            value=33, min=15, max=70, step=1,
            description='稼働率 (%):',
            style=style, layout=layout
        )
        
        self.price_slider = widgets.IntSlider(
            value=25000, min=15000, max=40000, step=1000,
            description='客単価 (円):',
            style=style, layout=layout
        )
        
        self.owned_properties_slider = widgets.IntSlider(
            value=15, min=5, max=30, step=1,
            description='自社所有物件数:',
            style=style, layout=layout
        )
        
        self.rental_properties_slider = widgets.IntSlider(
            value=15, min=5, max=30, step=1,
            description='賃貸物件数:',
            style=style, layout=layout
        )
        
        # 結果表示用
        self.output = widgets.Output()
        
        # ウィジェットの変更時に更新
        for widget in [self.occupancy_slider, self.price_slider, 
                      self.owned_properties_slider, self.rental_properties_slider]:
            widget.observe(self.update_analysis, names='value')
    
    def update_analysis(self, change=None):
        """分析結果更新"""
        with self.output:
            clear_output(wait=True)
            
            # パラメータ取得
            occupancy_rate = self.occupancy_slider.value / 100
            price_per_night = self.price_slider.value
            self.model.params['owned_properties'] = self.owned_properties_slider.value
            self.model.params['rental_properties'] = self.rental_properties_slider.value
            
            # 計算実行
            metrics = self.model.calculate_total_metrics(occupancy_rate, price_per_night)
            
            # 結果表示
            self.display_results(metrics, occupancy_rate, price_per_night)
            self.plot_sensitivity_analysis()
    
    def display_results(self, metrics, occupancy_rate, price_per_night):
        """結果表示"""
        print("=" * 60)
        print("📊 8weeks Fujimi Landscape - 事業分析結果")
        print("=" * 60)
        print(f"📈 稼働率: {occupancy_rate:.1%} | 客単価: ¥{price_per_night:,}")
        print(f"🏠 物件数: 自社{self.model.params['owned_properties']}軒 + 賃貸{self.model.params['rental_properties']}軒")
        print("-" * 60)
        print(f"💰 年間売上:     ¥{metrics['total_revenue']:>15,.0f}")
        print(f"💵 年間利益:     ¥{metrics['total_profit']:>15,.0f}")
        print(f"💎 総投資額:     ¥{metrics['total_investment']:>15,.0f}")
        print(f"📊 ROI:         {metrics['overall_roi']:>16.1f}%")
        print(f"⏰ 投資回収期間: {metrics['overall_payback']:>16.1f}年")
        print("-" * 60)
        
        # 物件タイプ別詳細
        owned = metrics['owned_metrics']
        rental = metrics['rental_metrics']
        
        print("\n🏘️ 物件タイプ別詳細:")
        print(f"自社所有 - 利益: ¥{owned['noi']:,.0f} | ROI: {owned['roi']:.1f}% | 回収: {owned['payback_period']:.1f}年")
        print(f"賃貸     - 利益: ¥{rental['operating_profit']:,.0f} | ROI: {rental['roi']:.1f}% | 回収: {rental['payback_period']:.1f}年")
    
    def plot_sensitivity_analysis(self):
        """感応度分析グラフ"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 稼働率感応度
        occupancy_df = self.model.sensitivity_analysis('occupancy_rate', 0.15, 0.70, 12)
        ax1.plot(occupancy_df['occupancy_rate'] * 100, occupancy_df['overall_roi'], 'b-o', linewidth=2)
        ax1.set_xlabel('稼働率 (%)')
        ax1.set_ylabel('ROI (%)')
        ax1.set_title('稼働率 vs ROI')
        ax1.grid(True, alpha=0.3)
        
        # 客単価感応度
        price_df = self.model.sensitivity_analysis('price_per_night', 15_000, 40_000, 12)
        ax2.plot(price_df['price_per_night'] / 1000, price_df['overall_roi'], 'r-o', linewidth=2)
        ax2.set_xlabel('客単価 (千円)')
        ax2.set_ylabel('ROI (%)')
        ax2.set_title('客単価 vs ROI')
        ax2.grid(True, alpha=0.3)
        
        # 投資回収期間（稼働率）
        ax3.plot(occupancy_df['occupancy_rate'] * 100, occupancy_df['overall_payback'], 'g-o', linewidth=2)
        ax3.set_xlabel('稼働率 (%)')
        ax3.set_ylabel('投資回収期間 (年)')
        ax3.set_title('稼働率 vs 投資回収期間')
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim(0, min(15, occupancy_df['overall_payback'].max()))
        
        # 年間利益（客単価）
        ax4.bar(price_df['price_per_night'] / 1000, price_df['total_profit'] / 1_000_000, alpha=0.7, color='orange')
        ax4.set_xlabel('客単価 (千円)')
        ax4.set_ylabel('年間利益 (百万円)')
        ax4.set_title('客単価 vs 年間利益')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.show()
    
    def display_widgets(self):
        """ウィジェット表示"""
        display(widgets.VBox([
            widgets.HTML("<h2>🏔️ 8weeks Fujimi Landscape - インタラクティブ事業分析</h2>"),
            self.occupancy_slider,
            self.price_slider,
            self.owned_properties_slider,
            self.rental_properties_slider,
            self.output
        ]))
        
        # 初期表示
        self.update_analysis()

def create_comprehensive_analysis():
    """包括的分析レポート生成"""
    model = FujimBusinessModel()
    
    print("🏔️ 8weeks Fujimi Landscape - 包括的事業分析レポート")
    print("=" * 80)
    
    # シナリオ分析
    print("\n📊 シナリオ分析:")
    scenario_df = model.scenario_analysis()
    print(scenario_df.to_string(index=False))
    
    # 感応度分析可視化
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 稼働率感応度
    occupancy_df = model.sensitivity_analysis('occupancy_rate', 0.15, 0.70, 15)
    axes[0,0].plot(occupancy_df['occupancy_rate'] * 100, occupancy_df['overall_roi'], 'b-o', linewidth=2)
    axes[0,0].set_title('稼働率 vs ROI', fontsize=12, fontweight='bold')
    axes[0,0].set_xlabel('稼働率 (%)')
    axes[0,0].set_ylabel('ROI (%)')
    axes[0,0].grid(True, alpha=0.3)
    
    # 客単価感応度
    price_df = model.sensitivity_analysis('price_per_night', 15_000, 40_000, 15)
    axes[0,1].plot(price_df['price_per_night'] / 1000, price_df['overall_roi'], 'r-o', linewidth=2)
    axes[0,1].set_title('客単価 vs ROI', fontsize=12, fontweight='bold')
    axes[0,1].set_xlabel('客単価 (千円)')
    axes[0,1].set_ylabel('ROI (%)')
    axes[0,1].grid(True, alpha=0.3)
    
    # 投資回収期間ヒートマップ
    occupancy_range = np.arange(0.2, 0.71, 0.05)
    price_range = np.arange(20000, 35001, 2500)
    payback_matrix = np.zeros((len(occupancy_range), len(price_range)))
    
    for i, occ in enumerate(occupancy_range):
        for j, price in enumerate(price_range):
            metrics = model.calculate_total_metrics(occ, price)
            payback_matrix[i,j] = min(metrics['overall_payback'], 15)  # 15年でキャップ
    
    im = axes[0,2].imshow(payback_matrix, cmap='RdYlGn_r', aspect='auto')
    axes[0,2].set_title('投資回収期間ヒートマップ', fontsize=12, fontweight='bold')
    axes[0,2].set_xlabel('客単価')
    axes[0,2].set_ylabel('稼働率')
    axes[0,2].set_xticks(range(0, len(price_range), 2))
    axes[0,2].set_xticklabels([f'{p//1000}k' for p in price_range[::2]])
    axes[0,2].set_yticks(range(0, len(occupancy_range), 4))
    axes[0,2].set_yticklabels([f'{o:.0%}' for o in occupancy_range[::4]])
    plt.colorbar(im, ax=axes[0,2], label='投資回収期間 (年)')
    
    # 物件数別収益
    property_counts = range(10, 51, 5)
    total_profits = []
    for count in property_counts:
        model.params['owned_properties'] = count // 2
        model.params['rental_properties'] = count - (count // 2)
        metrics = model.calculate_total_metrics()
        total_profits.append(metrics['total_profit'] / 1_000_000)
    
    axes[1,0].bar(property_counts, total_profits, alpha=0.7, color='green')
    axes[1,0].set_title('物件数 vs 年間利益', fontsize=12, fontweight='bold')
    axes[1,0].set_xlabel('総物件数')
    axes[1,0].set_ylabel('年間利益 (百万円)')
    axes[1,0].grid(True, alpha=0.3, axis='y')
    
    # リスク・リターン散布図
    scenarios = [
        {'name': '最悪', 'occ': 0.20, 'price': 20000},
        {'name': '悲観', 'occ': 0.25, 'price': 22000},
        {'name': '基本', 'occ': 0.33, 'price': 25000},
        {'name': '楽観', 'occ': 0.50, 'price': 30000},
    ]
    
    model.params['owned_properties'] = 15
    model.params['rental_properties'] = 15
    
    risks = []
    returns = []
    labels = []
    
    for scenario in scenarios:
        metrics = model.calculate_total_metrics(scenario['occ'], scenario['price'])
        # リスク = 稼働率の低さ（100% - 稼働率）
        risk = (1 - scenario['occ']) * 100
        returns.append(metrics['overall_roi'])
        risks.append(risk)
        labels.append(scenario['name'])
    
    scatter = axes[1,1].scatter(risks, returns, s=200, alpha=0.7, c=['red', 'orange', 'blue', 'green'])
    axes[1,1].set_title('リスク・リターン分析', fontsize=12, fontweight='bold')
    axes[1,1].set_xlabel('リスク指標 (100% - 稼働率)')
    axes[1,1].set_ylabel('ROI (%)')
    axes[1,1].grid(True, alpha=0.3)
    
    for i, label in enumerate(labels):
        axes[1,1].annotate(label, (risks[i], returns[i]), xytext=(5, 5), textcoords='offset points')
    
    # 損益分岐点分析（現金ベース - 減価償却費除外）
    occupancy_breakeven = []
    fixed_cost_total = (model.fixed_costs['owned']['operations_fixed'] + 
                       model.fixed_costs['owned']['utilities_fixed'] + 
                       model.fixed_costs['owned']['insurance']) * 15
    fixed_cost_total += (model.fixed_costs['rental']['rent'] + 
                        model.fixed_costs['rental']['operations_fixed'] + 
                        model.fixed_costs['rental']['utilities_fixed'] + 
                        model.fixed_costs['rental']['insurance']) * 15
    
    # 損益分岐点は現金ベースで計算（減価償却費除外）
    total_fixed_costs = fixed_cost_total
    
    price_per_night = 25000
    properties_total = 30
    daily_revenue_potential = price_per_night * properties_total
    
    breakeven_days = total_fixed_costs / daily_revenue_potential
    breakeven_occupancy = (breakeven_days / 365) * 100
    
    occupancy_range_be = np.linspace(10, 70, 100)
    revenues = occupancy_range_be / 100 * daily_revenue_potential * 365
    costs = np.full_like(revenues, total_fixed_costs)
    profits = revenues - costs
    
    axes[1,2].plot(occupancy_range_be, revenues / 1_000_000, 'g-', linewidth=2, label='年間売上')
    axes[1,2].axhline(y=total_fixed_costs / 1_000_000, color='r', linestyle='--', linewidth=2, label='固定費')
    axes[1,2].axvline(x=breakeven_occupancy, color='orange', linestyle=':', linewidth=2, label=f'損益分岐点({breakeven_occupancy:.1f}%)')
    axes[1,2].fill_between(occupancy_range_be, revenues / 1_000_000, total_fixed_costs / 1_000_000, 
                          where=(revenues >= total_fixed_costs), alpha=0.3, color='green', label='利益ゾーン')
    axes[1,2].set_title('損益分岐点分析', fontsize=12, fontweight='bold')
    axes[1,2].set_xlabel('稼働率 (%)')
    axes[1,2].set_ylabel('金額 (百万円)')
    axes[1,2].legend()
    axes[1,2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 重要指標サマリー
    print(f"\n🎯 重要指標サマリー:")
    print(f"損益分岐稼働率: {breakeven_occupancy:.1f}%")
    print(f"現在稼働率での安全余裕: {33 - breakeven_occupancy:.1f}%ポイント")
    
    base_metrics = model.calculate_total_metrics()
    print(f"基本シナリオROI: {base_metrics['overall_roi']:.1f}%")
    print(f"基本シナリオ投資回収期間: {base_metrics['overall_payback']:.1f}年")

# 実行例
if __name__ == "__main__":
    # 基本分析
    print("🚀 基本分析モードで実行中...")
    create_comprehensive_analysis()
    
    # インタラクティブモード（Jupyter環境で使用）
    print("\n💡 インタラクティブモードを使用するには:")
    print("model = FujimBusinessModel()")
    print("analyzer = InteractiveModelAnalyzer(model)")
    print("analyzer.display_widgets()")