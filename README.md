# 🏔️ 8weeks Fujimi Landscape - 事業分析ツール

富士見町宿泊事業の包括的な事業分析・投資シミュレーションツールです。

## 🌟 主要機能

### 📊 インタラクティブ事業分析アプリ（Streamlit）
- **感応度分析**: 稼働率・客単価・物件数の変化による影響をリアルタイム分析
- **シナリオ比較**: 楽観・基本・悲観・最悪シナリオの詳細比較
- **リスクファクター分析**: 売上・費用面の主要リスクと影響度の定量化
- **損益分岐点分析**: 現金ベースでの損益分岐稼働率と安全余裕の算出
- **詳細財務データ**: 自社所有・賃貸物件別の詳細収益構造
- **計算前提ドキュメント**: 全ての計算ロジックと前提条件の透明化

### 🎨 投資家向けピッチサイト（HTML）
- **レスポンシブデザイン**: PC・タブレット・スマートフォン対応
- **インタラクティブシミュレーター**: 基本的な収益計算
- **ビジュアル表現**: Chart.jsによるデータビジュアライゼーション

## 🛠️ 技術構成

### Streamlitアプリ
- **Python 3.8+**: メインプログラミング言語
- **Streamlit**: Webアプリケーションフレームワーク
- **Plotly**: インタラクティブグラフ
- **Pandas/NumPy**: データ分析・計算処理

### ピッチサイト
- **HTML5**: セマンティックマークアップ
- **CSS3**: モダンデザイン・アニメーション
- **JavaScript**: インタラクティブ機能
- **Chart.js**: データビジュアライゼーション

## 🚀 デプロイ方法

### 📊 Streamlitアプリのデプロイ（推奨）

#### Streamlit Cloudを使用
1. [Streamlit Cloud](https://streamlit.io/cloud)でアカウント作成
2. GitHubリポジトリを連携
3. `streamlit_app.py`をメインファイルに指定
4. 自動デプロイ開始

#### その他のプラットフォーム
- **Heroku**: `Procfile`を追加し、`web: streamlit run streamlit_app.py --server.port=$PORT`
- **Railway**: Gitリポジトリを連携し、自動検出
- **Render**: Webサービスとして`streamlit run streamlit_app.py`を指定

### 🎨 ピッチサイト（HTML）のデプロイ

#### Netlifyを使用
1. [Netlify](https://netlify.com)でアカウント作成
2. フォルダをドラッグ&ドロップでアップロード
3. `index.html`が自動的にメインページに設定

#### Vercelを使用
1. [Vercel](https://vercel.com)でアカウント作成
2. GitHubリポジトリを連携
3. 自動ビルド・デプロイ

### 🔗 GitHub連携の手順

```bash
# 1. Gitリポジトリの初期化
git init

# 2. ファイルの追加
git add .

# 3. 初回コミット
git commit -m "Initial commit: 8weeks Fujimi Landscape事業分析ツール"

# 4. リモートリポジトリの追加
git remote add origin https://github.com/[username]/fujimi-business-analysis.git

# 5. プッシュ
git push -u origin main
```

## 📁 ファイル構成

```
├── streamlit_app.py              # Streamlitメインアプリ
├── fujimi_business_model.py      # 事業モデル計算クラス
├── requirements.txt              # Python依存関係
├── .streamlit/
│   └── config.toml              # Streamlit設定
├── index.html                   # HTMLピッチサイト
├── styles.css                   # CSSスタイル
├── script.js                    # JavaScript機能
├── netlify.toml                 # Netlify設定
└── README.md                    # このファイル
```

### 🔧 主要ファイルの説明

- **`streamlit_app.py`**: メインのStreamlitアプリケーション
- **`fujimi_business_model.py`**: 事業分析の計算ロジック
- **`requirements.txt`**: デプロイ時の依存関係管理
- **`.streamlit/config.toml`**: アプリの外観・動作設定

## カスタマイズ

### 連絡先情報の更新
`index.html`の以下の部分を実際の情報に更新してください：

```html
<p>📧 contact@fujimi-stay.jp</p>
<p>📱 0266-XX-XXXX</p>
```

### 財務データの調整
`script.js`の`updateCalculator`関数で計算ロジックを調整できます。

### デザインの変更
`styles.css`でカラーパレット、フォント、レイアウトを変更できます。

## ライセンス

このプロジェクトは富士見町宿泊事業用に作成されました。商用利用については事前にご相談ください。

---
作成日: 2025年7月30日
作成者: Claude Code