# 📖 AgentPsyAssessment 使用マニュアル

## 🎯 クイックスタート

### 1️⃣ プロジェクトをダウンロード
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2️⃣ Ollamaをインストール（ローカルモデル）
```bash
# Windows
choco install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# サービスを開始
ollama serve

# モデルをダウンロード（新しいターミナル）
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
```

### 3️⃣ APIキーを設定（クラウドモデル）
```bash
# Alibaba Cloud Qwen
export DASHSCOPE_API_KEY=sk-あなたのAPIキー

# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-APIキー

# OpenAI GPT
export OPENAI_API_KEY=sk-openaiキー
```

## 🚀 主要使用ワークフロー

### ステップ1：心理質問紙回答を生成（評価システム）
```bash
# 基本使用（ローカルモデル）
python llm_assessment/run_assessment_unified.py

# 役割を指定
python llm_assessment/run_assessment_unified.py --role_name enfj

# 中国語質問紙を使用
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

### ステップ2：科学的スコアリング分析（分析システム）
```python
# evaluate.pyを作成
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

# 評価システムを初期化
pipeline = TransparentPipeline(use_cloud=True)  # クラウドモデル + 適応的コンセンサス
parser = InputParser()

# 解析して評価
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ スコア: {result['final_adjusted_scores']}")
print(f"🎯 信頼性: {result['confidence_metrics']['overall_reliability']:.3f}")
```

評価を実行：
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../evaluate.py
```

## 📋 よく使うコマンドクイックリファレンス

### ローカルモデル評価
```bash
# 回答を生成
python llm_assessment/run_assessment_unified.py --model_name qwen3:8b --role_name enfj

# 役割のバッチ評価
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py --role_name $role
done
```

### クラウドモデル評価
```bash
# クラウドモデルを設定
export PROVIDER=cloud

# クラウドモデルで回答を生成
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj

# エンドツーエンドテストを実行
python test_end_to_end_complete.py
```

### バッチ処理
```bash
# 既存結果のバッチ分析
python production_pipelines/local_batch_production/cli.py analyze --input results/

# パフォーマンステスト
python adaptive_consensus_performance_test.py

# 統合テスト
python test_adaptive_consensus_integration.py
```

## 🔧 設定ファイル

### モデル設定：`llm_assessment/config/ollama_config.json`
```json
{
  "models": {
    "qwen3:8b": {"provider": "ollama", "temperature": 0.7},
    "deepseek-r1:8b": {"provider": "ollama", "temperature": 0.7}
  }
}
```

### 役割設定：`llm_assessment/roles/enfj.json`
```json
{
  "name": "ENFJ - 主人公",
  "description": "温かく、理想的で、共感的",
  "traits": {"extraversion": 0.7, "intuition": 0.8}
}
```

## 📊 結果の解釈

### 評価出力例
```json
{
  "final_adjusted_scores": {
    "openness": 4.2,
    "conscientiousness": 3.8,
    "extraversion": 2.9,
    "agreeableness": 4.1,
    "neuroticism": 2.3
  },
  "confidence_metrics": {
    "overall_reliability": 0.856,
    "consensus_method": "minor_consensus",
    "quality_metrics": {
      "consensus_strength": 0.823,
      "agreement_level": "high"
    }
  }
}
```

### 信頼性指標ガイド
- **0.8-1.0**: 高信頼性、結果は信頼できる
- **0.6-0.8**: 中信頼性、参考用途
- **0.0-0.6**: 低信頼性、再評価を推奨

## 🆘 トラブルシューティング

### Ollamaの問題
```bash
# サービスを確認
ollama list

# 再起動
ollama serve

# ポートを確認
netstat -an | grep 11434
```

### APIの問題
```bash
# キーを確認
echo $DASHSCOPE_API_KEY

# 接続をテスト
python -c "import requests; print('API OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'API Failed')"
```

### インポートエラー
```bash
# 正しい作業ディレクトリ
cd production_pipelines/local_batch_production/single_report_pipeline

# またはPythonパスを設定
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## 📚 拡張機能

### 1. カスタム役割
`llm_assessment/roles/custom.json`を作成：
```json
{
  "name": "カスタム役割",
  "description": "あなたの役割説明",
  "traits": {"extraversion": 0.5, "openness": 0.6}
}
```

### 2. バッチ処理スクリプト
```bash
# バッチスクリプトを作成
cat > batch_run.sh << 'EOF'
#!/bin/bash
ROLES=("enfj" "intj" "estp" "istj")
for role in "${ROLES[@]}"; do
    python llm_assessment/run_assessment_unified.py --role_name $role
done
EOF

chmod +x batch_run.sh
./batch_run.sh
```

### 3. 結果の可視化
```python
import matplotlib.pyplot as plt
import json

# 結果を読み取り
with open('results/evaluation_result.json') as f:
    data = json.load(f)

# ビッグファイブ性格レーダーチャートを描画
# ... プロットコード ...

plt.savefig('personality_profile.png')
```

## 🎯 ベストプラクティス

### 1. 適切なモデルを選択
- **初心者**: ローカルOllamaモデルを使用
- **プロフェッショナル**: クラウドGPT-4/Claude-3.5を使用
- **研究**: 適応的コンセンサスによるマルチモデル評価を使用

### 2. 役割選択ガイドライン
- **ENFJ**: コンサルティング、教育シナリオに適している
- **INTJ**: 分析、戦略シナリオに適している
- **ESTP**: 実践、運用シナリオに適している
- **ISTJ**: 管理、実行シナリオに適している

### 3. 信頼性の最適化
- 精度向上のためクラウドモデルを使用
- 適応的コンセンサスアルゴリズムを有効化
- 適切な温度を設定（0.3-0.7）
- 複数評価の平均を取る

## 📞 技術サポート

- **プロジェクトURL**: https://github.com/ptreezh/AgentPsyAssessment
- **問題フィードバック**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **システム分離ガイド**: `README_SYSTEM_SEPARATION.md`

---
🎉 これでAgentPsyAssessmentを使った専門的な心理評価を開始できます！