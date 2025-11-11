# 🚀 AgentPsyAssessment - クイックスタートガイド v1.0

## 📋 目次
- [システム概要](#システム概要)
- [環境設定](#環境設定)
- [クイックインストール](#クイックインストール)
- [5分間体験](#5分間体験)
- [統一評価スキルシステム](#統一評価スキルシステム)
- [基本使用法](#基本使用法)
- [API設定](#api設定)
- [サポートされる評価タイプ](#サポートされる評価タイプ)
- [よくある問題](#よくある問題)
- [トラブルシューティング](#トラブルシューティング)

## 🎯 システム概要

AgentPsyAssessmentは、複数の精神測定モデル（ビッグファイブ、MBTI、認知機能）とAI駆動の分析機能を組み合わせた、ポータブルで包括的な心理評価フレームワークです。

### ⚠️ 重要：評価システムと分析システムの分離

- **📝 評価システム** (`llm_assessment/`)：AIが生成する心理質問票回答
- **🎯 分析システム** (`production_pipelines/`)：回答の科学的スコアリングと分析
- **🧠 統一スキルシステム** (`.claude/skills/unified-assessment-system/`)：設定駆動型評価フレームワーク

### 🆕 新機能（v1.0）
- ✨ **統一評価スキルシステム**：6つの専門評価タイプをサポートする設定駆動型アーキテクチャ
- 🤖 **インテリジェントタイプ検出**：手動設定不要の自動評価タイプ識別
- 📊 **可視化レポート**：Chart.jsデータ可視化付きインタラクティブHTMLレポート
- 🌍 **多言語サポート**：バイリンガルインターフェースとコンテンツ（中国語/英語/日本語）
- 🎭 **16 MBTI パーソナリティ**：詳細なパーソナリティタイプ分析とマッピング

## 🔧 環境設定

### システム要件
- **Python**：3.8+
- **メモリ**：4GB+（8GB+推奨）
- **ストレージ**：2GB+の利用可能なスペース
- **システム**：Windows 10/11、macOS 10.15+、Linux

## ⚡ クイックインストール

### 1. プロジェクトをクローン
```bash
# プロジェクトをクローン
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2. Python環境設定
```bash
# 仮想環境を作成（推奨）
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# 依存関係をインストール
pip install -r requirements.txt  # 利用可能な場合
pip install ollama requests numpy pandas
```

### 3. 環境変数を設定
```bash
# プロバイダーを設定（localまたはcloud）
export PROVIDER="local"  # または "cloud"

# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-openai-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-key"

# macOS/Linux
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 4. インストールを検証
```bash
# 統一評価システムテストを実行
cd .claude/skills/unified-assessment-system
python test_runner.py

# 期待される出力：🎉 ALL TESTS PASSED!
```

## 🎯 5分間体験

### 方法1：クイックテスト体験
```bash
# 1. 質問票生成を体験
python llm_assessment/run_assessment_unified.py \
    --model_name def \
    --test_file llm_assessment/test_files/single_test_question_10.json \
    --role_name def \
    --tmpr 0.7

# 2. バッチ分析を体験
python production_pipelines/local_batch_production/cli.py \
    assess --model gpt-4o --role def

# 3. 結果を確認
ls results/
```

### 方法2：ローカルモデル体験
```bash
# Ollamaを起動（ローカルモデルを使用する場合）
ollama serve

# モデルをダウンロード
ollama pull llama3.1

# ローカル評価を実行
python llm_assessment/run_assessment_unified.py \
    --model llama3.1 \
    --role a1 \
    --provider local
```

### 方法3：スキルデモ体験
```bash
# スキルデモを実行
python skills_demo_chinese_questionnaire.py

# 生成されたHTMLレポートを確認
ls html/
```

## 🧠 統一評価スキルシステム

### システムアーキテクチャ
```
.claude/skills/unified-assessment-system/
├── 📋 config_validator.py           # 設定バリデーター
├── 🔍 assessment_detector.py        # 評価タイプ検出器
├── 🏗️ skill_base.py                 # スキルベースアーキテクチャ
├── 📝 unified_questionnaire_responder.py    # 統一質問票レスポンダー
├── 📊 unified_psychological_analyzer.py    # 統一心理分析者
├── 📄 unified_report_generator.py          # 統一レポート生成者
└── 📁 configs/                       # 設定ファイルディレクトリ
    ├── big_five_personality.json     # ビッグファイブ人格評価
    ├── citizenship_knowledge.json   # 市民知識評価
    ├── financial_professional.json  # 金融専門評価
    ├── legal_knowledge.json         # 法知識評価
    ├── motivation_psychology.json   # 動機心理学評価
    └── political_literacy.json      # 政治リテラシー評価
```

### サポートされる評価タイプ
1. **ビッグファイブ人格評価** - OCEAN5次元 + MBTIマッピング
2. **市民知識評価** - 市民権利義務、政治システム認識
3. **金融専門評価** - 金融専門知識、リスク識別能力
4. **法知識評価** - 法的基礎知識、実務運用能力
5. **動機心理学評価** - 達成動機、権力動機、親和動機
6. **政治リテラシー評価** - 政治制度認識、批判的思考

### 統一スキルシステムの使用
```bash
# 統一評価システムをテスト
cd .claude/skills/unified-assessment-system
python test_runner.py

# 期待される出力：
# ✅ PASS Configuration System (6/6 configs loaded)
# ✅ PASS Assessment Detection (2/2 detections successful)
# ✅ PASS Questionnaire Response (Generated 2 responses)
# ✅ PASS Psychological Analysis (Big Five + MBTI analysis)
# ✅ PASS Report Generation (HTML report generated)
# 🎉 ALL TESTS PASSED!
```

## 🌐 デプロイメント

### オプション1：ローカルデプロイメント（初心者推奨）

#### 1. Ollamaをインストール
```bash
# Windows（Chocolatey推奨）
choco install ollama

# Linux（curl使用）
curl -fsSL https://ollama.ai/install.sh | sh

# macOS（Homebrew使用）
brew install ollama
```

#### 2. Ollamaサービスを起動
```bash
# Ollamaサービスを起動
ollama serve

# 新しいターミナルを開き、推奨モデルをダウンロード
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

### オプション2：クラウドデプロイメント（専門家推奨）

#### 1. APIキーを取得

**Alibaba Cloud Tongyi Qianwen (DashScope)**
```bash
# 登録：https://bailian.console.aliyun.com/
# APIキーを取得
export DASHSCOPE_API_KEY=sk-your-api-key-here
```

**Anthropic Claude**
```bash
# 登録：https://console.anthropic.com/
# APIキーを取得
export ANTHROPIC_API_KEY=sk-ant-api-key-here
```

**OpenAI GPT**
```bash
# 登録：https://platform.openai.com/
# APIキーを取得
export OPENAI_API_KEY=sk-openai-key-here
```

#### 2. 環境変数設定
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-your-api-key"
$env:ANTHROPIC_API_KEY="sk-ant-api-key"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-your-api-key"
export ANTHROPIC_API_KEY="sk-ant-api-key"
export OPENAI_API_KEY="sk-openai-key"
```

## 🚀 基本使用法

### 1. 個別評価
```bash
# 基本評価
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name enfj \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json

# 出力ファイルの場所
# results/assessment_<timestamp>_<model>_<role>.json
```

### 2. バッチ評価
```bash
# 複数のロールをバッチ処理
python production_pipelines/local_batch_production/run_batch_suite.py \
    --model llama3.1 \
    --roles a1,a2,b1

# バッチ結果を確認
python production_pipelines/local_batch_production/cli.py analyze \
    --input results/latest_batch.json
```

### 3. 高度な設定
```bash
# 温度とパラメータを設定
python llm_assessment/run_assessment_unified.py \
    --model_name claude-3-5-sonnet \
    --role_name intj \
    --temperature 0.2 \
    --max_tokens 1000

# 特定の設定ファイルを使用
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --config_path configs/custom_assessment.json
```

## 🎨 サポートされる評価タイプ

### 1. ビッグファイブ人格
```bash
# ファイルパターンマッチング：*big_five*, *personality*, *ocean*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-big-five-50-complete2.json
```

### 2. 市民知識
```bash
# ファイルパターンマッチング：*citizenship*, *公民*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-citizenship-test.json
```

### 3. 金融専門
```bash
# ファイルパターンマッチング：*financial*, *金融*, *bank*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-fund-management-test.json
```

### 4. 法知識
```bash
# ファイルパターンマッチング：*legal*, *law*, *法律*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-legal-test.json
```

### 5. 動機心理学
```bash
# ファイルパターンマッチング：*motivation*, *动机*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-motivation-test.json
```

### 6. 政治リテラシー
```bash
# ファイルパターンマッチング：*political*, *政治*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-political-test.json
```

## 🔧 クイックコマンドリファレンス

### 基本コマンド
```bash
# システムステータスを確認
python test_end_to_end_complete.py

# クイックテストを実行
python run_local_batch.py --quick

# 利用可能なモデルを表示
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_available_models.py
```

### レポート生成
```bash
# HTMLレポートを生成
python generate_all_html_reports.py

# 最新レポートを確認
ls html/ | tail -1
```

### トラブルシューティング
```bash
# 依存関係を確認
pip check

# 設定を確認
python -c "import llm_assessment; print('✅ インポート成功')"

# API接続をテスト
python quick_cloud_test.py
```

## ❓ よくある質問

### Q1：適切なモデルを選ぶには？
**A**：
- **ローカルモデル**：`llama3.1`、`mistral` - 高速、無料、テストに適している
- **クラウドモデル**：`gpt-4o`、`claude-3-5-sonnet` - 高品質、APIキーが必要
- **推奨**：開発にはローカルモデル、本番にはクラウドモデルを使用

### Q2：評価結果はどこに保存されますか？
**A**：
- 生結果：`results/readonly-original/`
- 処理済み結果：`results/ok/evaluated/`
- HTMLレポート：`html/`
- バッチ分析：`results/final-*-batch-analysis/`

### Q3：新しい評価タイプを追加するには？
**A**：
1. `.claude/skills/questionnaire-responder/configs/`に新しいJSON設定を追加
2. `python test_runner.py`を実行して設定を検証
3. システムが自動的に新しい評価タイプを検出

### Q4：メモリ不足の場合の対処法は？
**A**：
```bash
# 同時リクエストを制限
export MAX_CONCURRENT_REQUESTS=1

# 小さなモデルを使用
python llm_assessment/run_assessment_unified.py --model mistral

# バッチで処理
python final_batch_processor.py --limit 5
```

### Q5：APIコール失敗の対処法は？
**A**：
```bash
# APIキーを確認
echo $OPENAI_API_KEY

# 接続をテスト
python quick_cloud_test.py

# ローカルバックアップを使用
export PROVIDER=local
```

## 🎯 次のステップ

### 📚 深い学習
- 📖 [完全ユーザーマニュアル](../../USER_MANUAL.md)
- 🏗️ [システムアーキテクチャドキュメント](ARCHITECTURE.md)
- 🔧 [APIリファレンスドキュメント](API_REFERENCE.md)

### 🚀 高度な機能
- 🔌 [プラグイン開発ガイド](PLUGIN_DEVELOPMENT.md)
- 📊 [バッチ処理チュートリアル](BATCH_PROCESSING.md)
- 🌐 [クラウドデプロイメントガイド](CLOUD_DEPLOYMENT.md)

### 🤝 コミュニティサポート
- 🐛 [問題フィードバック](https://github.com/your-repo/issues)
- 💬 [ディスカッションエリア](https://github.com/your-repo/discussions)
- 📧 [メールサポート](mailto:support@example.com)

## 🎉 成功チェックリスト

以下のステップを完了して、設定成功を示してください：

- [ ] ✅ 環境設定完了（Python 3.8+）
- [ ] ✅ プロジェクト依存関係が正常にインストールされた
- [ ] ✅ 環境変数が正しく設定された
- [ ] ✅ テスト合格（`python test_runner.py`）
- [ ] ✅ 最初の評価結果が生成された
- [ ] ✅ HTMLレポートが表示された
- [ ] ✅ 異なる評価タイプを試した

**🎊 おめでとうございます！AgentPsyAssessmentの基本使用をマスターしました！**

---

**バージョン**：v1.0.0
**更新日**：2025-01-08
**作成者**：AgentPsyAssessment Team