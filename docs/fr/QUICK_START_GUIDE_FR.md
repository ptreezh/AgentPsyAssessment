# 🚀 Guide de Démarrage Rapide AgentPsyAssessment

## 📋 Table des Matières
- [Aperçu du Système](#aperçu-du-système)
- [Configuration de l'Environnement](#configuration-de-lenvironnement)
- [Installation et Déploiement](#installation-et-déploiement)
- [Utilisation Rapide](#utilisation-rapide)
- [Configuration API](#configuration-api)
- [Exemples Complets](#exemples-complets)
- [Dépannage](#dépannage)

## 🎯 Aperçu du Système

AgentPsyAssessment est un framework d'évaluation psychologique portable qui utilise des modèles de langage IA pour l'analyse de la personnalité.

### ⚠️ Important : Séparation des Systèmes d'Évaluation vs d'Analyse

- **📝 Système d'Évaluation** (`llm_assessment/`) : L'IA génère des réponses de questionnaires psychologiques
- **🎯 Système d'Analyse** (`production_pipelines/.../transparent_pipeline.py`) : Notation scientifique des réponses

## 🔧 Configuration de l'Environnement

### Exigences Système
- **Python** : 3.8+
- **Mémoire** : 8GB+ (16GB+ recommandé)
- **Système** : Windows/Linux/macOS

### 1. Cloner le Projet
```bash
# Utiliser Git pour cloner le projet
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment

# Ou télécharger le package ZIP directement
# Visiter : https://github.com/ptreezh/AgentPsyAssessment
# Cliquer sur "Code" → "Download ZIP"
```

### 2. Gestion de l'Environnement Python
```bash
# Recommandé d'utiliser un environnement virtuel
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Installer les dépendances
pip install -r requirements.txt  # si existe
pip install ollama requests numpy pandas
```

## 🌐 Installation et Déploiement

### Option 1 : Déploiement Local (Recommandé pour les Débutants)

#### 1. Installer Ollama
```bash
# Windows (recommandé d'utiliser Chocolatey)
choco install ollama

# Linux (utilisant curl)
curl -fsSL https://ollama.ai/install.sh | sh

# macOS (utilisant Homebrew)
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

**Alibaba Cloud Qwen (DashScope)**
```bash
# S'inscrire : https://bailian.console.aliyun.com/
# Obtenir la Clé API
export DASHSCOPE_API_KEY=sk-votre-clé-api-ici
```

**Anthropic Claude**
```bash
# S'inscrire : https://console.anthropic.com/
# Obtenir la Clé API
export ANTHROPIC_API_KEY=sk-ant-clé-api-ici
```

**OpenAI GPT**
```bash
# S'inscrire : https://platform.openai.com/
# Obtenir la Clé API
export OPENAI_API_KEY=sk-clé-openai-ici
```

#### 2. Configuration des Variables d'Environnement
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-votre-clé-api"
$env:ANTHROPIC_API_KEY="sk-ant-clé-api"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-votre-clé-api"
export ANTHROPIC_API_KEY="sk-ant-clé-api"
export OPENAI_API_KEY="sk-clé-openai"
```

## 🚀 Utilisation Rapide

### Étape 1 : Générer des Réponses de Questionnaire Psychologique (Système d'Évaluation)

```bash
# Usage de base - utiliser le modèle par défaut
python llm_assessment/run_assessment_unified.py

# Spécifier le modèle et le rôle
python llm_assessment/run_assessment_unified.py \
    --model_name deepseek-r1:8b \
    --role_name enfj \
    --tmpr 0.7

# Utiliser un questionnaire chinois
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name def \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

**Exemple de Sortie** :
```
🎯 Évaluation IA Terminée !
Modèle : deepseek-r1:8b
Rôle : enfj
Fichier de sortie : results/assessment_result_20250108_123456.json
```

### Étape 2 : Analyse de Notation Scientifique (Système d'Analyse)

```python
# Créer le script d'évaluation evaluate_result.py
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser
import json

# Initialiser le pipeline d'évaluation (modèles cloud + algorithme de consensus adaptatif)
pipeline = TransparentPipeline(use_cloud=True)

# Analyser les réponses
parser = InputParser()
questions = parser.parse_assessment_json('results/assessment_result_20250108_123456.json')

# Évaluer la première question
question = questions[0]
result = pipeline.process_single_question(question, 0)

# Afficher les résultats
print(f"✅ Évaluation Terminée !")
print(f"Score Final : {result['final_adjusted_scores']}")
print(f"Fiabilité Globale : {result['confidence_metrics']['overall_reliability']:.3f}")
print(f"Modèles Utilisés : {len(result['models_used'])}")
print(f"Méthode de Consensus : {result['confidence_metrics']['consensus_method']}")
```

Exécuter l'évaluation :
```bash
python evaluate_result.py
```

## 🔑 Détails de Configuration API

### Fichier de Configuration des Modèles
Éditer `llm_assessment/config/ollama_config.json` :

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

### Configuration des Modèles Cloud
Éditer `production_pipelines/local_batch_production/single_report_pipeline/config.yaml` :

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

## 📚 Exemples Complets

### Exemple 1 : Workflow d'Évaluation Complet

```bash
# 1. Générer les réponses
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name enfj \
    --tmpr 0.7

# 2. Créer le script d'évaluation
cat > complete_evaluation.py << 'EOF'
from transparent_pipeline import TransparentPipeline
from input_parser import InputParser

# Initialiser le système d'évaluation cloud
pipeline = TransparentPipeline(use_cloud=True)
parser = InputParser()

# Analyser les réponses
questions = parser.parse_assessment_json('results/latest_assessment.json')

# Évaluation par lot
all_results = []
for i, question in enumerate(questions):
    print(f"Évaluation de la question {i+1}/{len(questions)} : {question.get('question_id', 'Unknown')}")
    result = pipeline.process_single_question(question, i)
    all_results.append(result)

# Générer le rapport résumé
print("\n🎉 Évaluation Terminée !")
print(f"Total des questions : {len(all_results)}")
print(f"Fiabilité moyenne : {sum(r['confidence_metrics']['overall_reliability'] for r in all_results) / len(all_results):.3f}")

# Sauvegarder les résultats
import json
with open('evaluation_results.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
EOF

# 3. Exécuter l'évaluation
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../../../complete_evaluation.py
```

### Exemple 2 : Traitement par Lot de Multiples Rôles

```bash
# Générer des réponses pour plusieurs rôles
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py \
        --model_name qwen3:8b \
        --role_name $role \
        --tmpr 0.7
    echo "✅ Évaluation de rôle $role terminée"
done

# Évaluation par lot
python batch_evaluation.py
```

## 🛠️ Fonctions Avancées

### 1. Configuration de Rôles Personnalisés
Éditer `llm_assessment/roles/enfj.json` :
```json
{
  "name": "ENFJ - Protagoniste",
  "description": "Type de personnalité chaleureux, idéaliste, empathique",
  "traits": {
    "extraversion": 0.7,
    "intuition": 0.8,
    "feeling": 0.9,
    "judging": 0.8
  },
  "communication_style": "Chaleureux, encourageant, perspicace"
}
```

### 2. Scripts de Traitement par Lot
```bash
# Créer un script par lot
cat > batch_assess.sh << 'EOF'
#!/bin/bash
ROLES=("enfj" "intj" "estp" "istj" "infp" "entj")
MODEL="qwen3:8b"

for role in "${ROLES[@]}"; do
    echo "🎯 Traitement du rôle : $role"
    python llm_assessment/run_assessment_unified.py \
        --model_name $MODEL \
        --role_name $role \
        --tmpr 0.7
    sleep 2  # Éviter les limites API
done

echo "✅ Évaluation par lot terminée !"
EOF

chmod +x batch_assess.sh
./batch_assess.sh
```

### 3. Visualisation des Résultats
```python
# Créer un script de visualisation
import matplotlib.pyplot as plt
import json

# Lire les résultats d'évaluation
with open('evaluation_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Extraire les scores Big Five
dimensions = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
scores = {dim: [] for dim in dimensions}

for result in results:
    for dim, score in result['final_adjusted_scores'].items():
        if dim in scores:
            scores[dim].append(score)

# Dessiner un graphique radar
angles = [n / float(len(dimensions)) * 2 * 3.14159 for n in range(len(dimensions))]
angles += angles[:1]

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, polar=True)

for dim in dimensions:
    values = scores[dim]
    avg_value = sum(values) / len(values)
    # Logique de dessin...

plt.title('Analyse des Traits de Personnalité', size=16, weight='bold')
plt.savefig('personality_radar.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 🔍 Dépannage

### Problèmes Courants et Solutions

#### 1. Échec de Connexion Ollama
```bash
# Vérifier l'état du service Ollama
ollama list

# Si le service n'est pas démarré
ollama serve

# Vérifier le port
netstat -an | grep 11434
```

#### 2. Échec de Téléchargement de Modèle
```bash
# Télécharger manuellement le modèle
ollama pull qwen3:8b

# Vérifier la liste des modèles
ollama list

# Supprimer le modèle corrompu et retélécharger
ollama rm qwen3:8b
ollama pull qwen3:8b
```

#### 3. Erreur de Clé API
```bash
# Vérifier les variables d'environnement
echo $DASHSCOPE_API_KEY
echo $ANTHROPIC_API_KEY

# Tester la connexion API
python -c "
import requests
response = requests.get('https://dashscope.aliyuncs.com/api/v1/models',
    headers={'Authorization': f'Bearer {os.environ.get(\"DASHSCOPE_API_KEY\")}'})
print('Code de statut API :', response.status_code)
"
```

#### 4. Mémoire Insuffisante
```bash
# Surveiller l'utilisation de la mémoire
htop  # Linux/macOS
tasklist  # Windows

# Réduire la concurrence
export OLLAMA_MAX_LOADED_MODELS=1

# Utiliser des modèles plus petits
ollama pull qwen3:1.8b  # Version 1.8B paramètres
```

#### 5. Erreur d'Importation Relatif
```bash
# S'assurer d'exécuter dans le bon répertoire
cd production_pipelines/local_batch_production/single_report_pipeline
python -m transparent_pipeline

# Ou utiliser PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
python your_script.py
```

## 📖 Apprentissage Étendu

### Documentation Officielle
- **URL du Projet** : https://github.com/ptreezh/AgentPsyAssessment
- **Guide de Séparation des Systèmes** : `README_SYSTEM_SEPARATION.md`
- **Documentation du Système d'Évaluation** : `llm_assessment/README.md`
- **Documentation du Système d'Analyse** : `production_pipelines/local_batch_production/single_report_pipeline/README.md`

### Documentation Technique
- **Algorithme de Consensus Adaptatif** : `production_pipelines/cloud_fallback_enterprise/adaptive_consensus_algorithm.py`
- **Configuration API** : `CLAUDE.md`
- **Traitement par Lot** : `production_pipelines/local_batch_production/cli.py`

### Ressources Communautaires
- **Issues** : https://github.com/ptreezh/AgentPsyAssessment/issues
- **Discussions** : https://github.com/ptreezh/AgentPsyAssessment/discussions
- **Wiki** : https://github.com/ptreezh/AgentPsyAssessment/wiki

## 🎉 Félicitations !

Vous avez réussi à déployer le système AgentPsyAssessment !

🔥 **Recommandations pour les Prochaines Étapes** :
1. Essayer les scripts d'exemple
2. Explorer différentes configurations de rôles
3. Utiliser les modèles cloud pour une évaluation plus précise
4. Vérifier les rapports détaillés générés

Si vous avez des questions, veuillez consulter la section de dépannage ou soumettre un Issue.