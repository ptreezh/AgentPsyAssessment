# 🚀 AgentPsyAssessment - Schnellstartanleitung v1.0

## 📋 Inhaltsverzeichnis
- [Systemübersicht](#systemübersicht)
- [Umgebungseinrichtung](#umgebungseinrichtung)
- [Schnellinstallation](#schnellinstallation)
- [5-Minuten-Erfahrung](#5-minuten-erfahrung)
- [Vereinheitlichtes Bewertungsfähigkeiten-System](#vereinheitlichtes-bewertungsfähigkeiten-system)
- [Grundlegende Nutzung](#grundlegende-nutzung)
- [API-Konfiguration](#api-konfiguration)
- [Unterstützte Bewertungstypen](#unterstützte-bewertungstypen)
- [Häufige Probleme](#häufige-probleme)
- [Fehlerbehebung](#fehlerbehebung)

## 🎯 Systemübersicht

AgentPsyAssessment ist ein tragbares, umfassendes Framework für psychologische Bewertungen, das multiple psychometrische Modelle (Big Five, MBTI, kognitive Funktionen) mit KI-gestützter Analyse kombiniert.

### ⚠️ Wichtig: Trennung von Bewertungs- und Auswertungssystem

- **📝 Bewertungssystem** (`llm_assessment/`): KI-generierte psychologische Fragebogenantworten
- **🎯 Auswertungssystem** (`production_pipelines/`): Wissenschaftliche Bewertung und Analyse von Antworten
- **🧠 Vereinheitlichtes Fähigkeiten-System** (`.claude/skills/unified-assessment-system/`): Konfigurationsgesteuertes Bewertungs-Framework

### 🆕 Neue Funktionen (v1.0)
- ✨ **Vereinheitlichtes Bewertungsfähigkeiten-System**: Konfigurationsgesteuerte Architektur, die 6 professionelle Bewertungstypen unterstützt
- 🤖 **Intelligente Typerkennung**: Automatische Identifizierung von Bewertungstypen ohne manuelle Konfiguration
- 📊 **Visualisierungsberichte**: Interaktive HTML-Berichte mit Chart.js-Datenvisualisierung
- 🌍 **Mehrsprachige Unterstützung**: Zweisprachige Oberfläche und Inhalte (Chinesisch/Englisch/Deutsch)
- 🎭 **16 MBTI-Persönlichkeiten**: Detaillierte Persönlichkeitstypen-Analyse und Zuordnung

## 🔧 Umgebungseinrichtung

### Systemanforderungen
- **Python**: 3.8+
- **Arbeitsspeicher**: 4GB+ (8GB+ empfohlen)
- **Speicher**: 2GB+ verfügbarer Speicherplatz
- **System**: Windows 10/11, macOS 10.15+, Linux

## ⚡ Schnellinstallation

### 1. Projekt klonen
```bash
# Projekt klonen
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2. Python-Umgebung einrichten
```bash
# Virtuelle Umgebung erstellen (empfohlen)
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt  # falls vorhanden
pip install ollama requests numpy pandas
```

### 3. Umgebungsvariablen konfigurieren
```bash
# Anbieter festlegen (lokal oder cloud)
export PROVIDER="local"  # oder "cloud"

# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-openai-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-key"

# macOS/Linux
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 4. Installation überprüfen
```bash
# Vereinheitlichtes Bewertungssystem-Tests ausführen
cd .claude/skills/unified-assessment-system
python test_runner.py

# Erwartete Ausgabe: 🎉 ALL TESTS PASSED!
```

## 🎯 5-Minuten-Erfahrung

### Methode 1: Schnelle Testerfahrung
```bash
# 1. Fragebogengenerierung erleben
python llm_assessment/run_assessment_unified.py \
    --model_name def \
    --test_file llm_assessment/test_files/single_test_question_10.json \
    --role_name def \
    --tmpr 0.7

# 2. Batch-Analyse erleben
python production_pipelines/local_batch_production/cli.py \
    assess --model gpt-4o --role def

# 3. Ergebnisse ansehen
ls results/
```

### Methode 2: Lokale Modellerfahrung
```bash
# Ollama starten (falls lokale Modelle verwendet werden)
ollama serve

# Modell herunterladen
ollama pull llama3.1

# Lokale Bewertung ausführen
python llm_assessment/run_assessment_unified.py \
    --model llama3.1 \
    --role a1 \
    --provider local
```

### Methode 3: Fähigkeiten-Demo-Erfahrung
```bash
# Fähigkeiten-Demo ausführen
python skills_demo_chinese_questionnaire.py

# Generierte HTML-Berichte ansehen
ls html/
```

## 🧠 Vereinheitlichtes Bewertungsfähigkeiten-System

### Systemarchitektur
```
.claude/skills/unified-assessment-system/
├── 📋 config_validator.py           # Konfigurations-Validator
├── 🔍 assessment_detector.py        # Bewertungstyp-Detektor
├── 🏗️ skill_base.py                 # Fähigkeiten-Basisarchitektur
├── 📝 unified_questionnaire_responder.py    # Vereinheitlichter Fragebogen-Responder
├── 📊 unified_psychological_analyzer.py    # Vereinheitlichter psychologischer Analysator
├── 📄 unified_report_generator.py          # Vereinheitlichter Berichtsgenerator
└── 📁 configs/                       # Konfigurationsdateien-Verzeichnis
    ├── big_five_personality.json     # Big Five Persönlichkeitsbewertung
    ├── citizenship_knowledge.json   # Staatsbürgerschaftswissensbewertung
    ├── financial_professional.json  # Finanzprofibewertung
    ├── legal_knowledge.json         # Rechtskenntnisbewertung
    ├── motivation_psychology.json   # Motivationspsychologiebewertung
    └── political_literacy.json      # Politische Bildungsbewertung
```

### Unterstützte Bewertungstypen
1. **Big Five Persönlichkeitsbewertung** - OCEAN fünf Dimensionen + MBTI-Zuordnung
2. **Staatsbürgerschaftswissensbewertung** - Bürgerrechte & -pflichten, politisches Systembewusstsein
3. **Finanzprofibewertung** - Finanzexpertise, Risikoidentifizierungsfähigkeiten
4. **Rechtskenntnisbewertung** - Rechtliche Grundlagen, praktische Betriebsfähigkeiten
5. **Motivationspsychologiebewertung** - Leistungsmotivation, Machtmotivation, Anschlussmotivation
6. **Politische Bildungsbewertung** - Politisches Systembewusstsein, kritisches Denken

### Verwendung des vereinheitlichten Fähigkeiten-Systems
```bash
# Vereinheitlichtes Bewertungssystem testen
cd .claude/skills/unified-assessment-system
python test_runner.py

# Erwartete Ausgabe:
# ✅ PASS Configuration System (6/6 configs loaded)
# ✅ PASS Assessment Detection (2/2 detections successful)
# ✅ PASS Questionnaire Response (Generated 2 responses)
# ✅ PASS Psychological Analysis (Big Five + MBTI analysis)
# ✅ PASS Report Generation (HTML report generated)
# 🎉 ALL TESTS PASSED!
```

## 🌐 Bereitstellung

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

**Alibaba Cloud Tongyi Qianwen (DashScope)**
```bash
# Registrieren: https://bailian.console.aliyun.com/
# API-Schlüssel erhalten
export DASHSCOPE_API_KEY=sk-your-api-key-here
```

**Anthropic Claude**
```bash
# Registrieren: https://console.anthropic.com/
# API-Schlüssel erhalten
export ANTHROPIC_API_KEY=sk-ant-api-key-here
```

**OpenAI GPT**
```bash
# Registrieren: https://platform.openai.com/
# API-Schlüssel erhalten
export OPENAI_API_KEY=sk-openai-key-here
```

#### 2. Umgebungsvariablen-Konfiguration
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-your-api-key"
$env:ANTHROPIC_API_KEY="sk-ant-api-key"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-your-api-key"
export ANTHROPIC_API_KEY="sk-ant-api-key"
export OPENAI_API_KEY="sk-openai-key"
```

## 🚀 Grundlegende Nutzung

### 1. Einzelbewertung
```bash
# Grundlegende Bewertung
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name enfj \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json

# Ausgabedatei-Speicherort
# results/assessment_<timestamp>_<model>_<role>.json
```

### 2. Batch-Bewertung
```bash
# Mehrere Rollen batch-verarbeiten
python production_pipelines/local_batch_production/run_batch_suite.py \
    --model llama3.1 \
    --roles a1,a2,b1

# Batch-Ergebnisse ansehen
python production_pipelines/local_batch_production/cli.py analyze \
    --input results/latest_batch.json
```

### 3. Erweiterte Konfiguration
```bash
# Temperatur und Parameter festlegen
python llm_assessment/run_assessment_unified.py \
    --model_name claude-3-5-sonnet \
    --role_name intj \
    --temperature 0.2 \
    --max_tokens 1000

# Spezifische Konfigurationsdatei verwenden
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --config_path configs/custom_assessment.json
```

## 🎨 Unterstützte Bewertungstypen

### 1. Big Five Persönlichkeit
```bash
# Dateimusterübereinstimmung: *big_five*, *personality*, *ocean*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-big-five-50-complete2.json
```

### 2. Staatsbürgerschaftswissen
```bash
# Dateimusterübereinstimmung: *citizenship*, *公民*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-citizenship-test.json
```

### 3. Finanzprofis
```bash
# Dateimusterübereinstimmung: *financial*, *金融*, *bank*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-fund-management-test.json
```

### 4. Rechtskenntnisse
```bash
# Dateimusterübereinstimmung: *legal*, *law*, *法律*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-legal-test.json
```

### 5. Motivationspsychologie
```bash
# Dateimusterübereinstimmung: *motivation*, *动机*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-motivation-test.json
```

### 6. Politische Bildung
```bash
# Dateimusterübereinstimmung: *political*, *政治*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-political-test.json
```

## 🔧 Schnellbefehlsreferenz

### Grundlegende Befehle
```bash
# Systemstatus überprüfen
python test_end_to_end_complete.py

# Schnelltest ausführen
python run_local_batch.py --quick

# Verfügbare Modelle anzeigen
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_available_models.py
```

### Berichterstellung
```bash
# HTML-Berichte generieren
python generate_all_html_reports.py

# Neueste Berichte anzeigen
ls html/ | tail -1
```

### Fehlerbehebung
```bash
# Abhängigkeiten überprüfen
pip check

# Konfiguration überprüfen
python -c "import llm_assessment; print('✅ Import erfolgreich')"

# API-Verbindung testen
python quick_cloud_test.py
```

## ❓ Häufige Fragen

### F1: Wie wähle ich das richtige Modell?
**A**:
- **Lokale Modelle**: `llama3.1`, `mistral` - Schnell, kostenlos, geeignet zum Testen
- **Cloud-Modelle**: `gpt-4o`, `claude-3-5-sonnet` - Hohe Qualität, erfordert API-Schlüssel
- **Empfehlung**: Lokale Modelle für Entwicklung, Cloud-Modelle für Produktion verwenden

### F2: Wo werden Bewertungsergebnisse gespeichert?
**A**:
- Rohergebnisse: `results/readonly-original/`
- Verarbeitete Ergebnisse: `results/ok/evaluated/`
- HTML-Berichte: `html/`
- Batch-Analysen: `results/final-*-batch-analysis/`

### F3: Wie füge ich neue Bewertungstypen hinzu?
**A**:
1. Neue JSON-Konfiguration in `.claude/skills/questionnaire-responder/configs/` hinzufügen
2. `python test_runner.py` ausführen, um Konfiguration zu überprüfen
3. Das System erkennt automatisch neue Bewertungstypen

### F4: Was tun bei unzureichendem Arbeitsspeicher?
**A**:
```bash
# Gleichzeitige Anfragen begrenzen
export MAX_CONCURRENT_REQUESTS=1

# Kleinere Modelle verwenden
python llm_assessment/run_assessment_unified.py --model mistral

# In Batches verarbeiten
python final_batch_processor.py --limit 5
```

### F5: Umgang mit API-Aufruffehlern?
**A**:
```bash
# API-Schlüssel überprüfen
echo $OPENAI_API_KEY

# Verbindung testen
python quick_cloud_test.py

# Lokales Backup verwenden
export PROVIDER=local
```

## 🎯 Nächste Schritte

### 📚 Weiterführendes Lernen
- 📖 [Vollständiges Benutzerhandbuch](../../USER_MANUAL.md)
- 🏗️ [Systemarchitektur-Dokumentation](ARCHITECTURE.md)
- 🔧 [API-Referenzdokumentation](API_REFERENCE.md)

### 🚀 Erweiterte Funktionen
- 🔌 [Plugin-Entwicklungsleitfaden](PLUGIN_DEVELOPMENT.md)
- 📊 [Batch-Verarbeitung-Tutorial](BATCH_PROCESSING.md)
- 🌐 [Cloud-Bereitstellungsleitfaden](CLOUD_DEPLOYMENT.md)

### 🤝 Community-Unterstützung
- 🐛 [Problem-Feedback](https://github.com/your-repo/issues)
- 💬 [Diskussionsbereich](https://github.com/your-repo/discussions)
- 📧 [E-Mail-Support](mailto:support@example.com)

## 🎉 Erfolgskontrollliste

Vervollständigen Sie die folgenden Schritte für erfolgreiche Einrichtung:

- [ ] ✅ Umgebungseinrichtung abgeschlossen (Python 3.8+)
- [ ] ✅ Projekt-Abhängigkeiten erfolgreich installiert
- [ ] ✅ Umgebungsvariablen korrekt konfiguriert
- [ ] ✅ Testlauf bestanden (`python test_runner.py`)
- [ ] ✅ Erstes Bewertungsergebnis generiert
- [ ] ✅ HTML-Bericht angezeigt
- [ ] ✅ Verschiedene Bewertungstypen ausprobiert

**🎊 Herzlichen Glückwunsch! Sie haben die grundlegende Nutzung von AgentPsyAssessment gemeistert!**

---

**Version**: v1.0.0
**Aktualisierungsdatum**: 2025-01-08
**Autor**: AgentPsyAssessment Team