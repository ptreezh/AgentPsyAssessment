# 📖 AgentPsyAssessment Benutzerhandbuch

## 🎯 Schnellstart

### 1️⃣ Projekt herunterladen
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2️⃣ Ollama installieren (Lokale Modelle)
```bash
# Windows
choco install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# Dienst starten
ollama serve

# Modelle herunterladen (neues Terminal)
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
```

### 3️⃣ API-Schlüssel konfigurieren (Cloud-Modelle)
```bash
# Alibaba Cloud Qwen
export DASHSCOPE_API_KEY=sk-ihren-api-schlüssel

# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-api-schlüssel

# OpenAI GPT
export OPENAI_API_KEY=sk-openai-schlüssel
```

## 🚀 Kern-Verwendungsworkflow

### Schritt 1: Psychologische Fragebogenantworten generieren (Bewertungssystem)
```bash
# Grundlegende Verwendung (lokale Modelle)
python llm_assessment/run_assessment_unified.py

# Rolle angeben
python llm_assessment/run_assessment_unified.py --role_name enfj

# Chinesischen Fragebogen verwenden
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

### Schritt 2: Wissenschaftliche Bewertungsanalyse (Evaluierungssystem)
```python
# evaluate.py erstellen
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

# Evaluierungssystem initialisieren
pipeline = TransparentPipeline(use_cloud=True)  # Cloud-Modelle + adaptiver Konsens
parser = InputParser()

# Analysieren und bewerten
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ Punktzahl: {result['final_adjusted_scores']}")
print(f"🎯 Zuverlässigkeit: {result['confidence_metrics']['overall_reliability']:.3f}")
```

Bewertung ausführen:
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../evaluate.py
```

## 📋 Häufige Befehle - Schnellreferenz

### Lokale Modellbewertung
```bash
# Antworten generieren
python llm_assessment/run_assessment_unified.py --model_name qwen3:8b --role_name enfj

# Batch-Rollenbewertung
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py --role_name $role
done
```

### Cloud-Modellbewertung
```bash
# Cloud-Modelle einstellen
export PROVIDER=cloud

# Cloud-Modelle für Antwortgenerierung verwenden
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj

# End-to-End-Test ausführen
python test_end_to_end_complete.py
```

### Batch-Verarbeitung
```bash
# Batch-Analyse vorhandener Ergebnisse
python production_pipelines/local_batch_production/cli.py analyze --input results/

# Leistungstest
python adaptive_consensus_performance_test.py

# Integrationstest
python test_adaptive_consensus_integration.py
```

## 🔧 Konfigurationsdateien

### Modellkonfiguration: `llm_assessment/config/ollama_config.json`
```json
{
  "models": {
    "qwen3:8b": {"provider": "ollama", "temperature": 0.7},
    "deepseek-r1:8b": {"provider": "ollama", "temperature": 0.7}
  }
}
```

### Rollenkonfiguration: `llm_assessment/roles/enfj.json`
```json
{
  "name": "ENFJ - Protagonist",
  "description": "Warm, idealistisch, empathisch",
  "traits": {"extraversion": 0.7, "intuition": 0.8}
}
```

## 📊 Ergebnisinterpretation

### Bewertungsausgabebeispiel
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

### Zuverlässigkeitsmetriken-Leitfaden
- **0.8-1.0**: Hohe Zuverlässigkeit, Ergebnisse vertrauenswürdig
- **0.6-0.8**: Mittlere Zuverlässigkeit, Referenzverwendung
- **0.0-0.6**: Niedrige Zuverlässigkeit, Neubewertung empfohlen

## 🆘 Fehlerbehebung

### Ollama-Probleme
```bash
# Dienst prüfen
ollama list

# Neustarten
ollama serve

# Port prüfen
netstat -an | grep 11434
```

### API-Probleme
```bash
# Schlüssel prüfen
echo $DASHSCOPE_API_KEY

# Verbindung testen
python -c "import requests; print('API OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'API Failed')"
```

### Importfehler
```bash
# Korrektes Arbeitsverzeichnis
cd production_pipelines/local_batch_production/single_report_pipeline

# Oder Python-Pfad setzen
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## 📚 Erweiterte Funktionen

### 1. Benutzerdefinierte Rollen
Erstelle `llm_assessment/roles/custom.json`:
```json
{
  "name": "Benutzerdefinierte Rolle",
  "description": "Ihre Rollenbeschreibung",
  "traits": {"extraversion": 0.5, "openness": 0.6}
}
```

### 2. Batch-Verarbeitungsskripte
```bash
# Batch-Skript erstellen
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

### 3. Ergebnisvisualisierung
```python
import matplotlib.pyplot as plt
import json

# Ergebnisse lesen
with open('results/evaluation_result.json') as f:
    data = json.load(f)

# Big-Five-Persönlichkeits-Radardiagramm zeichnen
# ... Plot-Code ...

plt.savefig('personality_profile.png')
```

## 🎯 Bewährte Praktiken

### 1. Geeignete Modelle auswählen
- **Anfänger**: Lokale Ollama-Modelle verwenden
- **Professionell**: Cloud GPT-4/Claude-3.5 verwenden
- **Forschung**: Multi-Modell-Evaluierung mit adaptivem Konsens verwenden

### 2. Rollenauswahlrichtlinien
- **ENFJ**: Geeignet für Beratung, Bildungsszenarien
- **INTJ**: Geeignet für Analyse, Strategie-Szenarien
- **ESTP**: Geeignet für Praxis, Betriebsszenarien
- **ISTJ**: Geeignet für Management, Ausführungsszenarien

### 3. Zuverlässigkeitsoptimierung
- Cloud-Modelle für verbesserte Genauigkeit verwenden
- Adaptiven Konsensalgorithmus aktivieren
- Angemessene Temperatur einstellen (0.3-0.7)
- Mittelwert mehrerer Bewertungen nehmen

## 📞 Technischer Support

- **Projekt-URL**: https://github.com/ptreezh/AgentPsyAssessment
- **Problem-Feedback**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **Systemtrennungsleitfaden**: `README_SYSTEM_SEPARATION.md`

---
🎉 Sie können jetzt AgentPsyAssessment für professionelle psychologische Bewertung verwenden!