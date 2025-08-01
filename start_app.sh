#!/bin/bash

# 富士見町宿泊事業分析ツール起動スクリプト

echo "🏔️ 8weeks Fujimi Landscape - 事業分析ツール起動中..."

# 現在のディレクトリに移動
cd "$(dirname "$0")"

# 必要なモジュールの確認
echo "📦 必要モジュールの確認中..."
python3 -c "
try:
    import streamlit, numpy, pandas, plotly
    print('✅ 全モジュール正常')
except ImportError as e:
    print(f'❌ モジュールエラー: {e}')
    exit(1)
"

# ビジネスモデルの動作確認
echo "🧮 計算エンジンの確認中..."
python3 -c "
from fujimi_business_model import FujimBusinessModel
model = FujimBusinessModel()
metrics = model.calculate_total_metrics()
print(f'✅ 計算正常 - ROI: {metrics[\"overall_roi\"]:.1f}%')
"

# Streamlitアプリ起動
echo "🚀 Streamlitアプリを起動中..."
echo "📱 ブラウザで以下のURLにアクセスしてください:"
echo "   http://localhost:8501"
echo ""
echo "⚠️  終了するにはCtrl+Cを押してください"
echo ""

streamlit run streamlit_app.py --server.port 8501