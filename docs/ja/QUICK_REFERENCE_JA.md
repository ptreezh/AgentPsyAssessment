# 🚀 AgentPsyAssessment クイックリファレンスカード

## ⚡ ワンクリックスタート

### 🔽 ダウンロードとインストール
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 🔧 Ollamaをインストール
```bash
# Windows
choco install ollama && ollama serve

# Linux
curl -fsSL https://ollama.ai/install.sh | sh && ollama serve

# macOS
brew install ollama && ollama serve

# モデルをダウンロード
ollama pull qwen3:8b deepseek-r1:8b
```

### 🔑 APIキーを設定（クラウドモデル）
```bash
export DASHSCOPE_API_KEY=sk-あなたのキー
export ANTHROPIC_API_KEY=sk-ant-キー
```

## 🎯 主要コマンド

### 📝 回答を生成（評価システム）
```bash
# 基本
python llm_assessment/run_assessment_unified.py

# 役割を指定
python llm_assessment/run_assessment_unified.py --role_name enfj

# クラウドモデル
export PROVIDER=cloud
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj
```

### 📊 科学的スコアリング（分析システム + 適応的コンセンサスアルゴリズム）
```python
# 評価スクリプトを作成
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

pipeline = TransparentPipeline(use_cloud=True)  # クラウドモデル + 適応的コンセンサス
parser = InputParser()
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ スコア: {result['final_adjusted_scores']}")
print(f"🎯 信頼性: {result['confidence_metrics']['overall_reliability']:.3f}")
```

### 🚀 評価を実行
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../your_script.py
```

## 📋 利用可能な役割

| 役割 | 説明 | 最適な用途 |
|------|------|-----------|
| `enfj` | 主人公 | コンサルティング、教育 |
| `intj` | 建築家 | 分析、戦略 |
| `estp` | 起業家 | 実践、運用 |
| `istj` | 物流師 | 管理、実行 |
| `infp` | 調停者 | 創造性、芸術 |
| `entj` | 指揮官 | リーダーシップ、決定 |
| `estj` | 監督者 | 実行、制御 |
| `isfp` | 冒険家 | 柔軟性、適応 |
| `intp` | 論理学者 | 研究、革新 |
| `esfp` | エンターテイナー | 娯楽、社交 |

## 🌐 利用可能なモデル

### ローカルモデル（Ollama）
- `qwen3:8b` - Qwen 8B
- `deepseek-r1:8b` - DeepSeek R1 8B
- `mistral-nemo:latest` - Mistral Nemo
- `llama3:latest` - Llama 3

### クラウドモデル
- `deepseek-v3.1:671b-cloud` - DeepSeek V3.1 (671B)
- `gpt-oss:120b-cloud` - GPT (120B)
- `qwen3-vl:235b-cloud` - Qwen VL (235B)
- `gpt-4o` - GPT-4o
- `claude-3.5-sonnet` - Claude 3.5 Sonnet

## 🔍 結果の解釈

### ビッグファイブ性格次元
- **開放性**: 新しい経験への開放度
- **誠実性**: 組織性と自己規律
- **外向性**: 社会的活動レベル
- **協調性**: 協力と共感
- **神経症傾向**: 感情の安定性

### 信頼性指標
- **0.8-1.0** 🟢 高信頼性 - 結果は信頼できる
- **0.6-0.8** 🟡 中信頼性 - 参考用途
- **0.0-0.6** 🔴 低信頼性 - 再評価を推奨

## ⚠️ 重要な区別

- 📝 **評価システム**: AIが質問紙回答を生成 (`llm_assessment/`)
- 🎯 **分析システム**: 科学的スコアリング分析 (`transparent_pipeline.py` + `adaptive_consensus_algorithm.py`)

**ワークフロー**: 回答を生成 → スコアリング分析

## 🛠️ トラブルシューティング

### Ollamaの問題
```bash
ollama list          # モデルを確認
ollama serve         # サービスを開始
netstat -an | grep 11434  # ポートを確認
```

### APIの問題
```bash
echo $DASHSCOPE_API_KEY     # キーを確認
python -c "import requests; print('OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'FAIL')"
```

### インポートエラー
```bash
cd production_pipelines/local_batch_production/single_report_pipeline  # 正しいディレクトリ
export PYTHONPATH=$PYTHONPATH:$(pwd)  # パスを設定
```

## 📞 技術サポート

- 🌐 **プロジェクトURL**: https://github.com/ptreezh/AgentPsyAssessment
- 📖 **システム分離**: `README_SYSTEM_SEPARATION.md`
- 📚 **クイックガイド**: `QUICK_START_GUIDE.md`
- 🔧 **使用マニュアル**: `USAGE_MANUAL.md`

---
🎉 心理評価の旅を始めましょう！