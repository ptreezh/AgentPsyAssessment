# 🚀 AgentPsyAssessment Schnellreferenzkarte

## ⚡ Ein-Klick-Start

### 🔽 Herunterladen & Installieren
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 🔧 Ollama Installieren
```bash
# Windows
choco install ollama && ollama serve

# Linux
curl -fsSL https://ollama.ai/install.sh | sh && ollama serve

# macOS
brew install ollama && ollama serve

# Modelle herunterladen
ollama pull qwen3:8b deepseek-r1:8b
```

### 🔑 API-Schlüssel einrichten (Cloud-Modelle)
```bash
export DASHSCOPE_API_KEY=sk-ihren-schlüssel
export ANTHROPIC_API_KEY=sk-ant-schlüssel
```

## 🎯 Kernbefehle

### 📝 Antworten generieren (Bewertungssystem)
```bash
# Basic
python llm_assessment/run_assessment_unified.py

# Rolle angeben
python llm_assessment/run_assessment_unified.py --role_name enfj

# Cloud-Modelle
export PROVIDER=cloud
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj
```

### 📊 Wissenschaftliche Bewertung (Evaluierungssystem + Adaptiver Konsensalgorithmus)
```python
# Bewertungsskript erstellen
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

pipeline = TransparentPipeline(use_cloud=True)  # Cloud-Modelle + adaptiver Konsens
parser = InputParser()
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ Punktzahl: {result['final_adjusted_scores']}")
print(f"🎯 Zuverlässigkeit: {result['confidence_metrics']['overall_reliability']:.3f}")
```

### 🚀 Bewertung ausführen
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../your_script.py
```

## 📋 Verfügbare Rollen

| Rolle | Beschreibung | Am besten geeignet für |
|-------|-------------|------------------------|
| `enfj` | Protagonist | Beratung, Bildung |
| `intj` | Architekt | Analyse, Strategie |
| `estp` | Unternehmer | Praxis, Betrieb |
| `istj` | Logistiker | Management, Ausführung |
| `infp` | Vermittler | Kreativ, Kunst |
| `entj` | Kommandant | Führung, Entscheidungen |
| `estj` | Aufseher | Ausführung, Kontrolle |
| `isfp` | Abenteurer | Flexibilität, Anpassung |
| `intp` | Logiker | Forschung, Innovation |
| `esfp` | Unterhalter | Unterhaltung, Sozial |

## 🌐 Verfügbare Modelle

### Lokale Modelle (Ollama)
- `qwen3:8b` - Qwen 8B
- `deepseek-r1:8b` - DeepSeek R1 8B
- `mistral-nemo:latest` - Mistral Nemo
- `llama3:latest` - Llama 3

### Cloud-Modelle
- `deepseek-v3.1:671b-cloud` - DeepSeek V3.1 (671B)
- `gpt-oss:120b-cloud` - GPT (120B)
- `qwen3-vl:235b-cloud` - Qwen VL (235B)
- `gpt-4o` - GPT-4o
- `claude-3.5-sonnet` - Claude 3.5 Sonnet

## 🔍 Ergebnisinterpretation

### Big-Five-Persönlichkeitsdimensionen
- **Openness (Offenheit)**: Offenheit für neue Erfahrungen
- **Conscientiousness (Gewissenhaftigkeit)**: Organisation und Selbstdisziplin
- **Extraversion**: Soziale Aktivitätsniveau
- **Agreeableness (Verträglichkeit)**: Kooperation und Empathie
- **Neuroticism (Neurotizismus)**: Emotionale Stabilität

### Zuverlässigkeitsmetriken
- **0.8-1.0** 🟢 Hohe Zuverlässigkeit - Ergebnisse vertrauenswürdig
- **0.6-0.8** 🟡 Mittlere Zuverlässigkeit - Referenzverwendung
- **0.0-0.6** 🔴 Niedrige Zuverlässigkeit - Neubewertung empfohlen

## ⚠️ Wichtige Unterscheidung

- 📝 **Bewertungssystem**: KI generierte Fragebogenantworten (`llm_assessment/`)
- 🎯 **Evaluierungssystem**: Wissenschaftliche Bewertungsanalyse (`transparent_pipeline.py` + `adaptive_consensus_algorithm.py`)

**Workflow**: Antworten generieren → Bewertunganalyse

## 🛠️ Fehlerbehebung

### Ollama-Probleme
```bash
ollama list          # Modelle prüfen
ollama serve         # Dienst starten
netstat -an | grep 11434  # Port prüfen
```

### API-Probleme
```bash
echo $DASHSCOPE_API_KEY     # Schlüssel prüfen
python -c "import requests; print('OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'FAIL')"
```

### Importfehler
```bash
cd production_pipelines/local_batch_production/single_report_pipeline  # Korrektes Verzeichnis
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Pfad setzen
```

## 📞 Technischer Support

- 🌐 **Projekt-URL**: https://github.com/ptreezh/AgentPsyAssessment
- 📖 **Systemtrennung**: `README_SYSTEM_SEPARATION.md`
- 📚 **Schnellanleitung**: `QUICK_START_GUIDE.md`
- 🔧 **Benutzerhandbuch**: `USAGE_MANUAL.md`

---
🎉 **Beginnen Sie Ihre psychologische Bewertungsreise!**