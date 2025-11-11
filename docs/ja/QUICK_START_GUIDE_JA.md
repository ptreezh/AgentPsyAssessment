# 🚀 AgentPsyAssessment クイックスタートガイド

## 📋 目次
- [システム概要](#システム概要)
- [環境設定](#環境設定)
- [インストールとデプロイ](#インストールとデプロイ)
- [クイック使用](#クイック使用)
- [API設定](#api設定)
- [完全な例](#完全な例)
- [トラブルシューティング](#トラブルシューティング)

## 🎯 システム概要

AgentPsyAssessmentは、AI大規模言語モデルを使用して性格評価分析を行うポータブル心理評価フレームワークです。

### ⚠️ 重要：評価システムvs分析システムの分離

- **📝 評価システム** (`llm_assessment/`): AIが心理質問紙回答を生成
- **🎯 分析システム** (`production_pipelines/.../transparent_pipeline.py`): 回答の科学的スコアリング

## 🔧 環境設定

### システム要件
- **Python**: 3.8+
- **メモリ**: 8GB+（16GB+推奨）
- **システム**: Windows/Linux/macOS

### 1. プロジェクトをクローン
```bash
# Gitを使用してプロジェクトをクローン
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment

# またはZIPパッケージを直接ダウンロード
# 訪問: https://github.com/ptreezh/AgentPsyAssessment
# 「Code」→「Download ZIP」をクリック
```

### 2. Python環境管理
```bash
# 仮想環境を使用することを推奨
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# 依存関係をインストール
pip install -r requirements.txt  # 存在する場合
pip install ollama requests numpy pandas
```

## 🌐 インストールとデプロイ

### オプション1：ローカルデプロイ（初心者推奨）

#### 1. Ollamaをインストール
```bash
# Windows（Chocolatey推奨）
choco install ollama

# Linux（curl使用）
curl -fsSL https://ollama.ai/install.sh | sh

# macOS（Homebrew使用）
brew install ollama
```

#### 2. Ollamaサービスを開始
```bash
# Ollamaサービスを開始
ollama serve

# 新しいターミナルを開き、推奨モデルをダウンロード
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

### オプション2：クラウドデプロイ（プロフェッショナルユーザー推奨）

#### 1. APIキーを取得

**Alibaba Cloud Qwen (DashScope)**
```bash
# 登録: https://bailian.console.aliyun.com/
# APIキーを取得
export DASHSCOPE_API_KEY=sk-あなたのAPIキーをここに
```

**Anthropic Claude**
```bash
# 登録: https://console.anthropic.com/
# APIキーを取得
export ANTHROPIC_API_KEY=sk-ant-APIキーをここに
```

**OpenAI GPT**
```bash
# 登録: https://platform.openai.com/
# APIキーを取得
export OPENAI_API_KEY=sk-openaiキーをここに
```

#### 2. 環境変数設定
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-あなたのAPIキー"
$env:ANTHROPIC_API_KEY="sk-ant-APIキー"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-あなたのAPIキー"
export ANTHROPIC_API_KEY="sk-ant-APIキー"
export OPENAI_API_KEY="sk-openaiキー"
```

## 🚀 クイック使用

### ステップ1：心理質問紙回答を生成（評価システム）

```bash
# 基本使用 - デフォルトモデルを使用
python llm_assessment/run_assessment_unified.py

# モデルと役割を指定
python llm_assessment/run_assessment_unified.py \
    --model_name deepseek-r1:8b \
    --role_name enfj \
    --tmpr 0.7

# 中国語質問紙を使用
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name def \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

**出力例**:
```
🎯 AI評価完了！
モデル: deepseek-r1:8b
役割: enfj
出力ファイル: results/assessment_result_20250108_123456.json
```

### ステップ2：科学的スコアリング分析（分析システム）

```python
# 評価スクリプトevaluate_result.pyを作成
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser
import json

# 評価パイプラインを初期化（クラウドモデル + 適応的コンセンサスアルゴリズム）
pipeline = TransparentPipeline(use_cloud=True)

# 回答を解析
parser = InputParser()
questions = parser.parse_assessment_json('results/assessment_result_20250108_123456.json')

# 最初の質問を評価
question = questions[0]
result = pipeline.process_single_question(question, 0)

# 結果を出力
print(f"✅ 評価完了！")
print(f"最終スコア: {result['final_adjusted_scores']}")
print(f"全体信頼性: {result['confidence_metrics']['overall_reliability']:.3f}")
print(f"使用モデル数: {len(result['models_used'])}")
print(f"コンセンサス方法: {result['confidence_metrics']['consensus_method']}")
```

評価を実行：
```bash
python evaluate_result.py
```

## 🔑 API設定詳細

### モデル設定ファイル
`llm_assessment/config/ollama_config.json`を編集：

```json
{
  "models": {
    "deepseek-r1:8b": {
      "provider": "ollama",
      "api_base": "http://localhost:11434",
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "qwen3:8b": {
      "provider": "ollama",
      "api_base": "http://localhost:11434",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  },
  "evaluators": {
    "primary": ["deepseek-r1:8b", "qwen3:8b"],
    "dispute": ["mistral-nemo:latest"]
  }
}
```

### クラウドモデル設定
`production_pipelines/local_batch_production/single_report_pipeline/config.yaml`を編集：

```yaml
cloud_models:
  primary:
    - deepseek-v3.1:671b-cloud
    - gpt-oss:120b-cloud
    - qwen3-vl:235b-cloud

  dispute:
    - qwen3-vl:235b-cloud
    - gpt-oss:120b-cloud

api_keys:
  dashscope: "${DASHSCOPE_API_KEY}"
  anthropic: "${ANTHROPIC_API_KEY}"
  openai: "${OPENAI_API_KEY}"
```

## 📚 完全な例

### 例1：完全な評価ワークフロー

```bash
# 1. 回答を生成
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name enfj \
    --tmpr 0.7

# 2. 評価スクリプトを作成
cat > complete_evaluation.py << 'EOF'
from transparent_pipeline import TransparentPipeline
from input_parser import InputParser

# クラウド評価システムを初期化
pipeline = TransparentPipeline(use_cloud=True)
parser = InputParser()

# 回答を解析
questions = parser.parse_assessment_json('results/latest_assessment.json')

# バッチ評価
all_results = []
for i, question in enumerate(questions):
    print(f"質問 {i+1}/{len(questions)} を評価中: {question.get('question_id', 'Unknown')}")
    result = pipeline.process_single_question(question, i)
    all_results.append(result)

# 要約レポートを生成
print("\n🎉 評価完了！")
print(f"総質問数: {len(all_results)}")
print(f"平均信頼性: {sum(r['confidence_metrics']['overall_reliability'] for r in all_results) / len(all_results):.3f}")

# 結果を保存
import json
with open('evaluation_results.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
EOF

# 3. 評価を実行
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../../../complete_evaluation.py
```

### 例2：複数役割のバッチ処理

```bash
# 複数役割の回答を生成
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py \
        --model_name qwen3:8b \
        --role_name $role \
        --tmpr 0.7
    echo "✅ $role 役割評価完了"
done

# バッチ評価
python batch_evaluation.py
```

## 🛠️ 高度な機能

### 1. カスタム役割設定
`llm_assessment/roles/enfj.json`を編集：
```json
{
  "name": "ENFJ - 主人公",
  "description": "温かく、理想的で、共感的な性格タイプ",
  "traits": {
    "extraversion": 0.7,
    "intuition": 0.8,
    "feeling": 0.9,
    "judging": 0.8
  },
  "communication_style": "温かく、励まし、洞察に富む"
}
```

### 2. バッチ処理スクリプト
```bash
# バッチスクリプトを作成
cat > batch_assess.sh << 'EOF'
#!/bin/bash
ROLES=("enfj" "intj" "estp" "istj" "infp" "entj")
MODEL="qwen3:8b"

for role in "${ROLES[@]}"; do
    echo "🎯 役割を処理中: $role"
    python llm_assessment/run_assessment_unified.py \
        --model_name $MODEL \
        --role_name $role \
        --tmpr 0.7
    sleep 2  # API制限を回避
done

echo "✅ バッチ評価完了！"
EOF

chmod +x batch_assess.sh
./batch_assess.sh
```

### 3. 結果の可視化
```python
# 可視化スクリプトを作成
import matplotlib.pyplot as plt
import json

# 評価結果を読み取り
with open('evaluation_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# ビッグファイブスコアを抽出
dimensions = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
scores = {dim: [] for dim in dimensions}

for result in results:
    for dim, score in result['final_adjusted_scores'].items():
        if dim in scores:
            scores[dim].append(score)

# レーダーチャートを描画
angles = [n / float(len(dimensions)) * 2 * 3.14159 for n in range(len(dimensions))]
angles += angles[:1]

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, polar=True)

for dim in dimensions:
    values = scores[dim]
    avg_value = sum(values) / len(values)
    # 描画ロジック...

plt.title('性格特性分析', size=16, weight='bold')
plt.savefig('personality_radar.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 🔍 トラブルシューティング

### 一般的な問題と解決策

#### 1. Ollama接続失敗
```bash
# Ollamaサービス状態を確認
ollama list

# サービスが開始されていない場合
ollama serve

# ポートを確認
netstat -an | grep 11434
```

#### 2. モデルダウンロード失敗
```bash
# 手動でモデルをダウンロード
ollama pull qwen3:8b

# モデルリストを確認
ollama list

# 破損したモデルを削除して再ダウンロード
ollama rm qwen3:8b
ollama pull qwen3:8b
```

#### 3. APIキーエラー
```bash
# 環境変数を確認
echo $DASHSCOPE_API_KEY
echo $ANTHROPIC_API_KEY

# API接続をテスト
python -c "
import requests
response = requests.get('https://dashscope.aliyuncs.com/api/v1/models',
    headers={'Authorization': f'Bearer {os.environ.get(\"DASHSCOPE_API_KEY\")}'})
print('APIステータスコード:', response.status_code)
"
```

#### 4. メモリ不足
```bash
# メモリ使用量を監視
htop  # Linux/macOS
tasklist  # Windows

# 並列処理を削減
export OLLAMA_MAX_LOADED_MODELS=1

# より小さいモデルを使用
ollama pull qwen3:1.8b  # 1.8Bパラメータ版
```

#### 5. 相対インポートエラー
```bash
# 正しいディレクトリで実行していることを確認
cd production_pipelines/local_batch_production/single_report_pipeline
python -m transparent_pipeline

# またはPYTHONPATHを使用
export PYTHONPATH=$PYTHONPATH:$(pwd)
python your_script.py
```

## 📖 拡張学習

### 公式ドキュメント
- **プロジェクトURL**: https://github.com/ptreezh/AgentPsyAssessment
- **システム分離ガイド**: `README_SYSTEM_SEPARATION.md`
- **評価システムドキュメント**: `llm_assessment/README.md`
- **分析システムドキュメント**: `production_pipelines/local_batch_production/single_report_pipeline/README.md`

### 技術ドキュメント
- **適応的コンセンサスアルゴリズム**: `production_pipelines/cloud_fallback_enterprise/adaptive_consensus_algorithm.py`
- **API設定**: `CLAUDE.md`
- **バッチ処理**: `production_pipelines/local_batch_production/cli.py`

### コミュニティリソース
- **Issues**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **ディスカッション**: https://github.com/ptreezh/AgentPsyAssessment/discussions
- **Wiki**: https://github.com/ptreezh/AgentPsyAssessment/wiki

## 🎉 おめでとうございます！

AgentPsyAssessmentシステムのデプロイに成功しました！

🔥 **次のステップの推奨事項**:
1. サンプルスクリプトを試す
2. 異なる役割設定を探索する
3. より正確な評価のためにクラウドモデルを使用する
4. 生成された詳細レポートを確認する

質問がある場合は、トラブルシューティングセクションを確認するか、Issueを送信してください。