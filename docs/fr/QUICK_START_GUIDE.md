# 🚀 AgentPsyAssessment - Guide de Démarrage Rapide v1.0

## 📋 Table des Matières
- [Aperçu du Système](#aperçu-du-système)
- [Configuration de l'Environnement](#configuration-de-lenvironnement)
- [Installation Rapide](#installation-rapide)
- [Expérience de 5 Minutes](#expérience-de-5-minutes)
- [Système Unifié de Compétences d'Évaluation](#système-unifié-de-compétences-dévaluation)
- [Utilisation de Base](#utilisation-de-base)
- [Configuration API](#configuration-api)
- [Types d'Évaluation Supportés](#types-dévaluation-supportés)
- [Problèmes Courants](#problèmes-courants)
- [Dépannage](#dépannage)

## 🎯 Aperçu du Système

AgentPsyAssessment est un cadre d'évaluation psychologique portable et complet qui combine plusieurs modèles psychométriques (Big Five, MBTI, fonctions cognitives) avec des capacités d'analyse basées sur l'IA.

### ⚠️ Important : Séparation des Systèmes d'Évaluation et d'Analyse

- **📝 Système d'Évaluation** (`llm_assessment/`) : Réponses de questionnaire psychologique générées par l'IA
- **🎯 Système d'Analyse** (`production_pipelines/`) : Notation scientifique et analyse des réponses
- **🧠 Système Unifié de Compétences** (`.claude/skills/unified-assessment-system/`) : Cadre d'évaluation piloté par configuration

### 🆕 Nouvelles Fonctionnalités (v1.0)
- ✨ **Système Unifié de Compétences d'Évaluation** : Architecture pilotée par configuration supportant 6 types d'évaluation professionnels
- 🤖 **Détection Intelligente de Type** : Identification automatique des types d'évaluation sans configuration manuelle
- 📊 **Rapports de Visualisation** : Rapports HTML interactifs avec visualisation de données Chart.js
- 🌍 **Support Multilingue** : Interface et contenu bilingues (Chinois/Anglais/Français)
- 🎭 **16 Personnalités MBTI** : Analyse détaillée des types de personnalité et mappage

## 🔧 Configuration de l'Environnement

### Exigences Système
- **Python** : 3.8+
- **Mémoire** : 4GB+ (8GB+ recommandés)
- **Stockage** : 2GB+ d'espace disponible
- **Système** : Windows 10/11, macOS 10.15+, Linux

## ⚡ Installation Rapide

### 1. Cloner le Projet
```bash
# Cloner le projet
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2. Configuration de l'Environnement Python
```bash
# Créer un environnement virtuel (recommandé)
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Installer les dépendances
pip install -r requirements.txt  # si disponible
pip install ollama requests numpy pandas
```

### 3. Configurer les Variables d'Environnement
```bash
# Définir le fournisseur (local ou cloud)
export PROVIDER="local"  # ou "cloud"

# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-openai-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-key"

# macOS/Linux
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 4. Vérifier l'Installation
```bash
# Exécuter les tests du système unifié d'évaluation
cd .claude/skills/unified-assessment-system
python test_runner.py

# Résultat attendu : 🎉 ALL TESTS PASSED!
```

## 🎯 Expérience de 5 Minutes

### Méthode 1 : Expérience de Test Rapide
```bash
# 1. Expérimenter la génération de questionnaire
python llm_assessment/run_assessment_unified.py \
    --model_name def \
    --test_file llm_assessment/test_files/single_test_question_10.json \
    --role_name def \
    --tmpr 0.7

# 2. Expérimenter l'analyse par lots
python production_pipelines/local_batch_production/cli.py \
    assess --model gpt-4o --role def

# 3. Voir les résultats
ls results/
```

### Méthode 2 : Expérience de Modèle Local
```bash
# Démarrer Ollama (si utilisant des modèles locaux)
ollama serve

# Télécharger le modèle
ollama pull llama3.1

# Exécuter l'évaluation locale
python llm_assessment/run_assessment_unified.py \
    --model llama3.1 \
    --role a1 \
    --provider local
```

### Méthode 3 : Expérience de Démo de Compétences
```bash
# Exécuter la démo de compétences
python skills_demo_chinese_questionnaire.py

# Voir les rapports HTML générés
ls html/
```

## 🧠 Système Unifié de Compétences d'Évaluation

### Architecture du Système
```
.claude/skills/unified-assessment-system/
├── 📋 config_validator.py           # Validateur de configuration
├── 🔍 assessment_detector.py        # Détecteur de type d'évaluation
├── 🏗️ skill_base.py                 # Architecture de base des compétences
├── 📝 unified_questionnaire_responder.py    # Compétence unifiée de réponse au questionnaire
├── 📊 unified_psychological_analyzer.py    # Compétence unifiée d'analyse psychologique
├── 📄 unified_report_generator.py          # Compétence unifiée de génération de rapport
└── 📁 configs/                       # Répertoire des fichiers de configuration
    ├── big_five_personality.json     # Évaluation de personnalité Big Five
    ├── citizenship_knowledge.json   # Évaluation des connaissances citoyennes
    ├── financial_professional.json  # Évaluation professionnelle financière
    ├── legal_knowledge.json         # Évaluation des connaissances juridiques
    ├── motivation_psychology.json   # Évaluation de psychologie de la motivation
    └── political_literacy.json      # Évaluation de l'alphabétisation politique
```

### Types d'Évaluation Supportés
1. **Évaluation de Personnalité Big Five** - Cinq dimensions OCEAN + mappage MBTI
2. **Évaluation des Connaissances Citoyennes** - Droits & obligations civiques, conscience du système politique
3. **Évaluation Professionnelle Financière** - Expertise financière, capacités d'identification des risques
4. **Évaluation des Connaissances Juridiques** - Fondements juridiques, capacités opérationnelles pratiques
5. **Évaluation de Psychologie de la Motivation** - Motivation de réalisation, motivation de pouvoir, motivation d'affiliation
6. **Évaluation de l'Alphabétisation Politique** - Conscience du système politique, pensée critique

### Utilisation du Système Unifié de Compétences
```bash
# Tester le système unifié d'évaluation
cd .claude/skills/unified-assessment-system
python test_runner.py

# Résultat attendu :
# ✅ PASS Configuration System (6/6 configs loaded)
# ✅ PASS Assessment Detection (2/2 detections successful)
# ✅ PASS Questionnaire Response (Generated 2 responses)
# ✅ PASS Psychological Analysis (Big Five + MBTI analysis)
# ✅ PASS Report Generation (HTML report generated)
# 🎉 ALL TESTS PASSED!
```

## 🌐 Déploiement

### Option 1 : Déploiement Local (Recommandé pour les Débutants)

#### 1. Installer Ollama
```bash
# Windows (recommandé avec Chocolatey)
choco install ollama

# Linux (avec curl)
curl -fsSL https://ollama.ai/install.sh | sh

# macOS (avec Homebrew)
brew install ollama
```

#### 2. Démarrer le Service Ollama
```bash
# Démarrer le service Ollama
ollama serve

# Ouvrir un nouveau terminal, télécharger les modèles recommandés
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

### Option 2 : Déploiement Cloud (Recommandé pour les Utilisateurs Professionnels)

#### 1. Obtenir les Clés API

**Alibaba Cloud Tongyi Qianwen (DashScope)**
```bash
# S'inscrire : https://bailian.console.aliyun.com/
# Obtenir la clé API
export DASHSCOPE_API_KEY=sk-your-api-key-here
```

**Anthropic Claude**
```bash
# S'inscrire : https://console.anthropic.com/
# Obtenir la clé API
export ANTHROPIC_API_KEY=sk-ant-api-key-here
```

**OpenAI GPT**
```bash
# S'inscrire : https://platform.openai.com/
# Obtenir la clé API
export OPENAI_API_KEY=sk-openai-key-here
```

#### 2. Configuration des Variables d'Environnement
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-your-api-key"
$env:ANTHROPIC_API_KEY="sk-ant-api-key"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-your-api-key"
export ANTHROPIC_API_KEY="sk-ant-api-key"
export OPENAI_API_KEY="sk-openai-key"
```

## 🚀 Utilisation de Base

### 1. Évaluation Individuelle
```bash
# Évaluation de base
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name enfj \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json

# Emplacement du fichier de sortie
# results/assessment_<timestamp>_<model>_<role>.json
```

### 2. Évaluation par Lots
```bash
# Traiter plusieurs rôles par lots
python production_pipelines/local_batch_production/run_batch_suite.py \
    --model llama3.1 \
    --roles a1,a2,b1

# Voir les résultats par lots
python production_pipelines/local_batch_production/cli.py analyze \
    --input results/latest_batch.json
```

### 3. Configuration Avancée
```bash
# Définir la température et les paramètres
python llm_assessment/run_assessment_unified.py \
    --model_name claude-3-5-sonnet \
    --role_name intj \
    --temperature 0.2 \
    --max_tokens 1000

# Utiliser un fichier de configuration spécifique
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --config_path configs/custom_assessment.json
```

## 🎨 Types d'Évaluation Supportés

### 1. Personnalité Big Five
```bash
# Correspondance de modèle de fichier : *big_five*, *personality*, *ocean*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-big-five-50-complete2.json
```

### 2. Connaissances Citoyennes
```bash
# Correspondance de modèle de fichier : *citizenship*, *公民*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-citizenship-test.json
```

### 3. Professionnels Financiers
```bash
# Correspondance de modèle de fichier : *financial*, *金融*, *bank*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-fund-management-test.json
```

### 4. Connaissances Juridiques
```bash
# Correspondance de modèle de fichier : *legal*, *law*, *法律*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-legal-test.json
```

### 5. Psychologie de la Motivation
```bash
# Correspondance de modèle de fichier : *motivation*, *动机*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-motivation-test.json
```

### 6. Alphabétisation Politique
```bash
# Correspondance de modèle de fichier : *political*, *政治*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-political-test.json
```

## 🔧 Référence Rapide des Commandes

### Commandes de Base
```bash
# Vérifier le statut du système
python test_end_to_end_complete.py

# Exécuter un test rapide
python run_local_batch.py --quick

# Voir les modèles disponibles
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_available_models.py
```

### Génération de Rapports
```bash
# Générer les rapports HTML
python generate_all_html_reports.py

# Voir les derniers rapports
ls html/ | tail -1
```

### Dépannage
```bash
# Vérifier les dépendances
pip check

# Vérifier la configuration
python -c "import llm_assessment; print('✅ Import réussi')"

# Tester la connexion API
python quick_cloud_test.py
```

## ❓ Questions Courantes

### Q1 : Comment choisir le bon modèle ?
**A** :
- **Modèles locaux** : `llama3.1`, `mistral` - Rapides, gratuits, adaptés aux tests
- **Modèles cloud** : `gpt-4o`, `claude-3-5-sonnet` - Haute qualité, nécessitent des clés API
- **Recommandation** : Utiliser les modèles locaux pour le développement, les modèles cloud pour la production

### Q2 : Où sont sauvegardés les résultats d'évaluation ?
**A** :
- Résultats bruts : `results/readonly-original/`
- Résultats traités : `results/ok/evaluated/`
- Rapports HTML : `html/`
- Analyses par lots : `results/final-*-batch-analysis/`

### Q3 : Comment ajouter de nouveaux types d'évaluation ?
**A** :
1. Ajouter une nouvelle configuration JSON dans `.claude/skills/questionnaire-responder/configs/`
2. Exécuter `python test_runner.py` pour vérifier la configuration
3. Le système détectera automatiquement les nouveaux types d'évaluation

### Q4 : Que faire en cas de mémoire insuffisante ?
**A** :
```bash
# Limiter les requêtes simultanées
export MAX_CONCURRENT_REQUESTS=1

# Utiliser des modèles plus petits
python llm_assessment/run_assessment_unified.py --model mistral

# Traiter par lots
python final_batch_processor.py --limit 5
```

### Q5 : Gestion des échecs d'appels API ?
**A** :
```bash
# Vérifier les clés API
echo $OPENAI_API_KEY

# Tester la connexion
python quick_cloud_test.py

# Utiliser le backup local
export PROVIDER=local
```

## 🎯 Prochaines Étapes

### 📚 Apprentissage Approfondi
- 📖 [Manuel Utilisateur Complet](../../USER_MANUAL.md)
- 🏗️ [Documentation d'Architecture Système](ARCHITECTURE.md)
- 🔧 [Documentation de Référence API](API_REFERENCE.md)

### 🚀 Fonctionnalités Avancées
- 🔌 [Guide de Développement de Plugins](PLUGIN_DEVELOPMENT.md)
- 📊 [Tutoriel de Traitement par Lots](BATCH_PROCESSING.md)
- 🌐 [Guide de Déploiement Cloud](CLOUD_DEPLOYMENT.md)

### 🤝 Support Communautaire
- 🐛 [Feedback sur les Problèmes](https://github.com/your-repo/issues)
- 💬 [Zone de Discussion](https://github.com/your-repo/discussions)
- 📧 [Support Email](mailto:support@example.com)

## 🎉 Liste de Vérification de Succès

Complétez les étapes suivantes pour indiquer une configuration réussie :

- [ ] ✅ Configuration de l'environnement terminée (Python 3.8+)
- [ ] ✅ Dépendances du projet installées avec succès
- [ ] ✅ Variables d'environnement configurées correctement
- [ ] ✅ Test réussi (`python test_runner.py`)
- [ ] ✅ Premier résultat d'évaluation généré
- [ ] ✅ Rapport HTML affiché
- [ ] ✅ Différents types d'évaluation essayés

**🎊 Félicitations ! Vous avez maîtrisé l'utilisation de base d'AgentPsyAssessment !**

---

**Version** : v1.0.0
**Date de Mise à Jour** : 2025-01-08
**Auteur** : AgentPsyAssessment Team