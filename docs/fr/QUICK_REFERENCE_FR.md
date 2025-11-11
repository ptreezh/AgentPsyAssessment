# 🚀 Carte de Référence Rapide AgentPsyAssessment

## ⚡ Démarrage en Un Clic

### 🔽 Télécharger et Installer
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 🔧 Installer Ollama
```bash
# Windows
choco install ollama && ollama serve

# Linux
curl -fsSL https://ollama.ai/install.sh | sh && ollama serve

# macOS
brew install ollama && ollama serve

# Télécharger les modèles
ollama pull qwen3:8b deepseek-r1:8b
```

### 🔑 Configurer les Clés API (Modèles Cloud)
```bash
export DASHSCOPE_API_KEY=sk-votre-clé
export ANTHROPIC_API_KEY=sk-ant-clé
```

## 🎯 Commandes Principales

### 📝 Générer des Réponses (Système d'Évaluation)
```bash
# Basic
python llm_assessment/run_assessment_unified.py

# Spécifier un rôle
python llm_assessment/run_assessment_unified.py --role_name enfj

# Modèles cloud
export PROVIDER=cloud
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj
```

### 📊 Notation Scientifique (Système d'Analyse + Algorithme de Consensus Adaptatif)
```python
# Créer un script d'évaluation
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

pipeline = TransparentPipeline(use_cloud=True)  # Modèles cloud + consensus adaptatif
parser = InputParser()
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ Score : {result['final_adjusted_scores']}")
print(f"🎯 Fiabilité : {result['confidence_metrics']['overall_reliability']:.3f}")
```

### 🚀 Exécuter l'Évaluation
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../your_script.py
```

## 📋 Rôles Disponibles

| Rôle | Description | Idéal pour |
|------|-------------|------------|
| `enfj` | Protagoniste | Conseil, Éducation |
| `intj` | Architecte | Analyse, Stratégie |
| `estp` | Entrepreneur | Pratique, Opérations |
| `istj` | Logisticien | Gestion, Exécution |
| `infp` | Médiateur | Créativité, Art |
| `entj` | Commandant | Leadership, Décisions |
| `estj` | Superviseur | Exécution, Contrôle |
| `isfp` | Aventurier | Flexibilité, Adaptation |
| `intp` | Logicien | Recherche, Innovation |
| `esfp` | Artiste | Divertissement, Social |

## 🌐 Modèles Disponibles

### Modèles Locaux (Ollama)
- `qwen3:8b` - Qwen 8B
- `deepseek-r1:8b` - DeepSeek R1 8B
- `mistral-nemo:latest` - Mistral Nemo
- `llama3:latest` - Llama 3

### Modèles Cloud
- `deepseek-v3.1:671b-cloud` - DeepSeek V3.1 (671B)
- `gpt-oss:120b-cloud` - GPT (120B)
- `qwen3-vl:235b-cloud` - Qwen VL (235B)
- `gpt-4o` - GPT-4o
- `claude-3.5-sonnet` - Claude 3.5 Sonnet

## 🔍 Interprétation des Résultats

### Dimensions de la Personnalité Big Five
- **Ouverture** : Ouverture aux nouvelles expériences
- **Conscienciosité** : Organisation et autodiscipline
- **Extraversion** : Niveau d'activité sociale
- **Agréabilité** : Coopération et empathie
- **Névrosisme** : Stabilité émotionnelle

### Métriques de Fiabilité
- **0.8-1.0** 🟢 Haute fiabilité - Résultats fiables
- **0.6-0.8** 🟡 Fiabilité moyenne - Usage de référence
- **0.0-0.6** 🔴 Faible fiabilité - Recommander réévaluation

## ⚠️ Distinction Importante

- 📝 **Système d'Évaluation** : IA génère des réponses de questionnaire (`llm_assessment/`)
- 🎯 **Système d'Analyse** : Analyse de notation scientifique (`transparent_pipeline.py` + `adaptive_consensus_algorithm.py`)

**Workflow** : Générer des réponses → Analyse de notation

## 🛠️ Dépannage

### Problèmes Ollama
```bash
ollama list          # Vérifier les modèles
ollama serve         # Démarrer le service
netstat -an | grep 11434  # Vérifier le port
```

### Problèmes API
```bash
echo $DASHSCOPE_API_KEY     # Vérifier la clé
python -c "import requests; print('OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'FAIL')"
```

### Erreurs d'Importation
```bash
cd production_pipelines/local_batch_production/single_report_pipeline  # Bon répertoire
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Définir le chemin
```

## 📞 Support Technique

- 🌐 **URL du Projet** : https://github.com/ptreezh/AgentPsyAssessment
- 📖 **Séparation des Systèmes** : `README_SYSTEM_SEPARATION.md`
- 📚 **Guide Rapide** : `QUICK_START_GUIDE.md`
- 🔧 **Manuel d'Utilisation** : `USAGE_MANUAL.md`

---
🎉 Commencez votre voyage d'évaluation psychologique !