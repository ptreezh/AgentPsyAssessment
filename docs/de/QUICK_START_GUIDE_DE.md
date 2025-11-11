# 🚀 AgentPsyAssessment Schnellstartleitfaden

## 📋 Inhaltsverzeichnis
- [Systemübersicht](#systemübersicht)
- [Umgebungseinrichtung](#umgebungseinrichtung)
- [Installation & Bereitstellung](#installation--bereitstellung)
- [Schnelle Verwendung](#schnelle-verwendung)
- [API-Konfiguration](#api-konfiguration)
- [Vollständige Beispiele](#vollständige-beispiele)
- [Fehlerbehebung](#fehlerbehebung)

## 🎯 Systemübersicht

AgentPsyAssessment ist ein tragbares psychologisches Bewertungsframework, das KI-Sprachmodelle für Persönlichkeitsbewertungsanalysen verwendet.

### ⚠️ Wichtig: Bewertungs- vs. Evaluierungssystemtrennung

- **📝 Bewertungssystem** (`llm_assessment/`): KI generiert psychologische Fragebogenantworten
- **🎯 Evaluierungssystem** (`production_pipelines/.../transparent_pipeline.py`): Wissenschaftliche Bewertung von Antworten

## 🔧 Umgebungseinrichtung

### Systemanforderungen
- **Python**: 3.8+
- **Speicher**: 8GB+ (16GB+ empfohlen)
- **System**: Windows/Linux/macOS

### 1. Projekt klonen
```bash
# Git verwenden, um Projekt zu klonen
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment

# Oder ZIP-Paket direkt herunterladen
# Besuchen: https://github.com/ptreezh/AgentPsyAssessment
# Klicken Sie auf "Code" → "Download ZIP"
```

### 2. Python-Umgebungsverwaltung
```bash
# Virtuelle Umgebung empfehlen
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt  # falls vorhanden
pip install ollama requests numpy pandas
```

## 🌐 Installation & Bereitstellung

### Option 1: Lokale Bereitstellung (Empfohlen für Anfänger)

#### 1. Ollama installieren
```bash
# Windows (empfohlen mit Chocolatey)
choco install ollama

# Linux (mit curl)
curl -fsSL https://ollama.ai/install.sh | sh

# macOS (mit Homebrew)
brew install ollama
```

#### 2. Ollama-Dienst starten
```bash
# Ollama-Dienst starten
ollama serve

# Neues Terminal öffnen, empfohlene Modelle herunterladen
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

### Option 2: Cloud-Bereitstellung (Empfohlen für professionelle Benutzer)

#### 1. API-Schlüssel erhalten

**Alibaba Cloud Qwen (DashScope)**
```bash
# Registrieren: https://bailian.console.aliyun.com/
# API-Schlüssel erhalten
export DASHSCOPE_API_KEY=sk-ihren-api-schlüssel-hier
```

**Anthropic Claude**
```bash
# Registrieren: https://console.anthropic.com/
# API-Schlüssel erhalten
export ANTHROPIC_API_KEY=sk-ant-api-schlüssel-hier
```

**OpenAI GPT**
```bash
# Registrieren: https://platform.openai.com/
# API-Schlüssel erhalten
export OPENAI_API_KEY=sk-openai-schlüssel-hier
```

#### 2. Umgebungsvariablen-Konfiguration
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-ihren-api-schlüssel"
$env:ANTHROPIC_API_KEY="sk-ant-api-schlüssel"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-ihren-api-schlüssel"
export ANTHROPIC_API_KEY="sk-ant-api-schlüssel"
export OPENAI_API_KEY="sk-openai-schlüssel"
```

## 🚀 Schnelle Verwendung

### Schritt 1: Psychologische Fragebogenantworten generieren (Bewertungssystem)

```bash
# Grundlegende Verwendung - Standardmodell verwenden
python llm_assessment/run_assessment_unified.py

# Modell und Rolle angeben
python llm_assessment/run_assessment_unified.py \
    --model_name deepseek-r1:8b \
    --role_name enfj \
    --tmpr 0.7

# Chinesischen Fragebogen verwenden
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name def \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

**Ausgabebeispiel**:
```
🎯 KI-Bewertung abgeschlossen!
Modell: deepseek-r1:8b
Rolle: enfj
Ausgabedatei: results/assessment_result_20250108_123456.json
```

### Schritt 2: Wissenschaftliche Bewertungsanalyse (Evaluierungssystem)

```python
# Bewertungsskript evaluate_result.py erstellen
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser
import json

# Bewertungspipeline initialisieren (Cloud-Modelle + adaptiver Konsensalgorithmus)
pipeline = TransparentPipeline(use_cloud=True)

# Antworten analysieren
parser = InputParser()
questions = parser.parse_assessment_json('results/assessment_result_20250108_123456.json')

# Erste Frage bewerten
question = questions[0]
result = pipeline.process_single_question(question, 0)

# Ergebnisse ausgeben
print(f"✅ Bewertung abgeschlossen!")
print(f"Finale Punktzahl: {result['final_adjusted_scores']}")
print(f"Gesamtzuverlässigkeit: {result['confidence_metrics']['overall_reliability']:.3f}")
print(f"Verwendete Modelle: {len(result['models_used'])}")
print(f"Konsensmethode: {result['confidence_metrics']['consensus_method']}")
```

Bewertung ausführen:
```bash
python evaluate_result.py
```

## 🔑 API-Konfigurationsdetails

### Modellkonfigurationsdatei
Bearbeite `llm_assessment/config/ollama_config.json`:

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

### Cloud-Modellkonfiguration
Bearbeite `production_pipelines/local_batch_production/single_report_pipeline/config.yaml`:

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

## 📚 Vollständige Beispiele

### Beispiel 1: Vollständiger Bewertungsworkflow

```bash
# 1. Antworten generieren
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name enfj \
    --tmpr 0.7

# 2. Bewertungsskript erstellen
cat > complete_evaluation.py << 'EOF'
from transparent_pipeline import TransparentPipeline
from input_parser import InputParser

# Cloud-Bewertungssystem initialisieren
pipeline = TransparentPipeline(use_cloud=True)
parser = InputParser()

# Antworten analysieren
questions = parser.parse_assessment_json('results/latest_assessment.json')

# Batch-Bewertung
all_results = []
for i, question in enumerate(questions):
    print(f"Bewerte Frage {i+1}/{len(questions)}: {question.get('question_id', 'Unknown')}")
    result = pipeline.process_single_question(question, i)
    all_results.append(result)

# Zusammenfassungsbericht generieren
print("\n🎉 Bewertung abgeschlossen!")
print(f"Gesamtfragen: {len(all_results)}")
print(f"Durchschnittliche Zuverlässigkeit: {sum(r['confidence_metrics']['overall_reliability'] for r in all_results) / len(all_results):.3f}")

# Ergebnisse speichern
import json
with open('evaluation_results.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
EOF

# 3. Bewertung ausführen
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../../../complete_evaluation.py
```

### Beispiel 2: Batch-Verarbeitung mehrerer Rollen

```bash
# Antworten für mehrere Rollen generieren
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py \
        --model_name qwen3:8b \
        --role_name $role \
        --tmpr 0.7
    echo "✅ $role Rollenbewertung abgeschlossen"
done

# Batch-Bewertung
python batch_evaluation.py
```

## 🛠️ Erweiterte Funktionen

### 1. Benutzerdefinierte Rollenkonfiguration
Bearbeite `llm_assessment/roles/enfj.json`:
```json
{
  "name": "ENFJ - Protagonist",
  "description": "Warm, idealistisch, empathischer Persönlichkeitstyp",
  "traits": {
    "extraversion": 0.7,
    "intuition": 0.8,
    "feeling": 0.9,
    "judging": 0.8
  },
  "communication_style": "Warm, ermutigend, einfühlsam"
}
```

### 2. Batch-Verarbeitungsskripte
```bash
# Batch-Skript erstellen
cat > batch_assess.sh << 'EOF'
#!/bin/bash
ROLES=("enfj" "intj" "estp" "istj" "infp" "entj")
MODEL="qwen3:8b"

for role in "${ROLES[@]}"; do
    echo "🎯 Verarbeite Rolle: $role"
    python llm_assessment/run_assessment_unified.py \
        --model_name $MODEL \
        --role_name $role \
        --tmpr 0.7
    sleep 2  # API-Limits vermeiden
done

echo "✅ Batch-Bewertung abgeschlossen!"
EOF

chmod +x batch_assess.sh
./batch_assess.sh
```

### 3. Ergebnisvisualisierung
```python
# Visualisierungsskript erstellen
import matplotlib.pyplot as plt
import json

# Bewertungsergebnisse lesen
with open('evaluation_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Big-Five-Punktzahlen extrahieren
dimensions = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
scores = {dim: [] for dim in dimensions}

for result in results:
    for dim, score in result['final_adjusted_scores'].items():
        if dim in scores:
            scores[dim].append(score)

# Radardiagramm zeichnen
angles = [n / float(len(dimensions)) * 2 * 3.14159 for n in range(len(dimensions))]
angles += angles[:1]

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, polar=True)

for dim in dimensions:
    values = scores[dim]
    avg_value = sum(values) / len(values)
    # Zeichenlogik...

plt.title('Persönlichkeitsmerkmalanalyse', size=16, weight='bold')
plt.savefig('personality_radar.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 🔍 Fehlerbehebung

### Häufige Probleme und Lösungen

#### 1. Ollama-Verbindung fehlgeschlagen
```bash
# Ollama-Dienststatus prüfen
ollama list

# Wenn Dienst nicht gestartet
ollama serve

# Port prüfen
netstat -an | grep 11434
```

#### 2. Modell-Download fehlgeschlagen
```bash
# Modell manuell herunterladen
ollama pull qwen3:8b

# Modelliste prüfen
ollama list

# Beschädigtes Modell löschen und neu herunterladen
ollama rm qwen3:8b
ollama pull qwen3:8b
```

#### 3. API-Schlüssel-Fehler
```bash
# Umgebungsvariablen prüfen
echo $DASHSCOPE_API_KEY
echo $ANTHROPIC_API_KEY

# API-Verbindung testen
python -c "
import requests
response = requests.get('https://dashscope.aliyuncs.com/api/v1/models',
    headers={'Authorization': f'Bearer {os.environ.get(\"DASHSCOPE_API_KEY\")}'})
print('API-Statuscode:', response.status_code)
"
```

#### 4. Ungenügender Speicher
```bash
# Speichernutzung überwachen
htop  # Linux/macOS
tasklist  # Windows

# Parallelität reduzieren
export OLLAMA_MAX_LOADED_MODELS=1

# Kleinere Modelle verwenden
ollama pull qwen3:1.8b  # 1.8B Parameter-Version
```

#### 5. relativer Importfehler
```bash
# Sicherstellen, dass im korrekten Verzeichnis ausgeführt wird
cd production_pipelines/local_batch_production/single_report_pipeline
python -m transparent_pipeline

# Oder PYTHONPATH verwenden
export PYTHONPATH=$PYTHONPATH:$(pwd)
python your_script.py
```

## 📖 Erweitertes Lernen

### Offizielle Dokumentation
- **Projekt-URL**: https://github.com/ptreezh/AgentPsyAssessment
- **Systemtrennungsleitfaden**: `README_SYSTEM_SEPARATION.md`
- **Bewertungssystem-Dokumentation**: `llm_assessment/README.md`
- **Evaluierungssystem-Dokumentation**: `production_pipelines/local_batch_production/single_report_pipeline/README.md`

### Technische Dokumentation
- **Adaptiver Konsensalgorithmus**: `production_pipelines/cloud_fallback_enterprise/adaptive_consensus_algorithm.py`
- **API-Konfiguration**: `CLAUDE.md`
- **Batch-Verarbeitung**: `production_pipelines/local_batch_production/cli.py`

### Community-Ressourcen
- **Issues**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **Diskussionen**: https://github.com/ptreezh/AgentPsyAssessment/discussions
- **Wiki**: https://github.com/ptreezh/AgentPsyAssessment/wiki

## 🎉 Herzlichen Glückwunsch!

Sie haben das AgentPsyAssessment-System erfolgreich bereitgestellt!

🔥 **Nächste Schritte Empfehlungen**:
1. Beispielskripte ausprobieren
2. Verschiedene Rollenkonfigurationen erkunden
3. Cloud-Modelle für genauere Bewertung verwenden
4. Detaillierte Berichte überprüfen

Bei Fragen überprüfen Sie bitte den Fehlerbehebungsabschnitt oder reichen Sie ein Issue ein!