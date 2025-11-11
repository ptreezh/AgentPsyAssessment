# 📖 Manuel d'Utilisation AgentPsyAssessment

## 🎯 Démarrage Rapide

### 1️⃣ Télécharger le Projet
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2️⃣ Installer Ollama (Modèles Locaux)
```bash
# Windows
choco install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# Démarrer le service
ollama serve

# Télécharger les modèles (nouveau terminal)
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
```

### 3️⃣ Configurer les Clés API (Modèles Cloud)
```bash
# Alibaba Cloud Qwen
export DASHSCOPE_API_KEY=sk-votre-clé-api

# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-clé-api

# OpenAI GPT
export OPENAI_API_KEY=sk-clé-openai
```

## 🚀 Workflow Principal d'Utilisation

### Étape 1 : Générer des Réponses de Questionnaire Psychologique (Système d'Évaluation)
```bash
# Usage de base (modèles locaux)
python llm_assessment/run_assessment_unified.py

# Spécifier un rôle
python llm_assessment/run_assessment_unified.py --role_name enfj

# Utiliser un questionnaire chinois
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

### Étape 2 : Analyse de Notation Scientifique (Système d'Analyse)
```python
# Créer evaluate.py
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

# Initialiser le système d'évaluation
pipeline = TransparentPipeline(use_cloud=True)  # Modèles cloud + consensus adaptatif
parser = InputParser()

# Analyser et évaluer
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ Score : {result['final_adjusted_scores']}")
print(f"🎯 Fiabilité : {result['confidence_metrics']['overall_reliability']:.3f}")
```

Exécuter l'évaluation :
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../evaluate.py
```

## 📋 Référence Rapide des Commandes Courantes

### Évaluation de Modèles Locaux
```bash
# Générer des réponses
python llm_assessment/run_assessment_unified.py --model_name qwen3:8b --role_name enfj

# Évaluation de lot de rôles
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py --role_name $role
done
```

### Évaluation de Modèles Cloud
```bash
# Définir les modèles cloud
export PROVIDER=cloud

# Utiliser les modèles cloud pour générer des réponses
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj

# Exécuter le test end-to-end
python test_end_to_end_complete.py
```

### Traitement par Lot
```bash
# Analyse par lot des résultats existants
python production_pipelines/local_batch_production/cli.py analyze --input results/

# Test de performance
python adaptive_consensus_performance_test.py

# Test d'intégration
python test_adaptive_consensus_integration.py
```

## 🔧 Fichiers de Configuration

### Configuration des Modèles : `llm_assessment/config/ollama_config.json`
```json
{
  "models": {
    "qwen3:8b": {"provider": "ollama", "temperature": 0.7},
    "deepseek-r1:8b": {"provider": "ollama", "temperature": 0.7}
  }
}
```

### Configuration des Rôles : `llm_assessment/roles/enfj.json`
```json
{
  "name": "ENFJ - Protagoniste",
  "description": "Chaleureux, idéaliste, empathique",
  "traits": {"extraversion": 0.7, "intuition": 0.8}
}
```

## 📊 Interprétation des Résultats

### Exemple de Sortie d'Évaluation
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

### Guide des Métriques de Fiabilité
- **0.8-1.0** : Haute fiabilité, résultats fiables
- **0.6-0.8** : Fiabilité moyenne, usage de référence
- **0.0-0.6** : Faible fiabilité, recommander réévaluation

## 🆘 Dépannage

### Problèmes Ollama
```bash
# Vérifier le service
ollama list

# Redémarrer
ollama serve

# Vérifier le port
netstat -an | grep 11434
```

### Problèmes API
```bash
# Vérifier les clés
echo $DASHSCOPE_API_KEY

# Tester la connexion
python -c "import requests; print('API OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'API Failed')"
```

### Erreurs d'Importation
```bash
# Bon répertoire de travail
cd production_pipelines/local_batch_production/single_report_pipeline

# Ou définir le chemin Python
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## 📚 Fonctions Étendues

### 1. Rôles Personnalisés
Créer `llm_assessment/roles/custom.json` :
```json
{
  "name": "Rôle Personnalisé",
  "description": "Votre description de rôle",
  "traits": {"extraversion": 0.5, "openness": 0.6}
}
```

### 2. Scripts de Traitement par Lot
```bash
# Créer un script par lot
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

### 3. Visualisation des Résultats
```python
import matplotlib.pyplot as plt
import json

# Lire les résultats
with open('results/evaluation_result.json') as f:
    data = json.load(f)

# Dessiner un graphique radar Big Five
# ... code de graphique ...

plt.savefig('personality_profile.png')
```

## 🎯 Meilleures Pratiques

### 1. Choisir les Modèles Appropriés
- **Débutants** : Utiliser les modèles locaux Ollama
- **Professionnels** : Utiliser GPT-4/Claude-3.5 cloud
- **Recherche** : Utiliser l'évaluation multi-modèles avec consensus adaptatif

### 2. Directives de Sélection de Rôles
- **ENFJ** : Adapté pour le conseil, scénarios éducatifs
- **INTJ** : Adapté pour l'analyse, scénarios stratégiques
- **ESTP** : Adapté pour la pratique, scénarios opérationnels
- **ISTJ** : Adapté pour la gestion, scénarios d'exécution

### 3. Optimisation de la Fiabilité
- Utiliser les modèles cloud pour améliorer la précision
- Activer l'algorithme de consensus adaptatif
- Définir une température appropriée (0.3-0.7)
- Prendre la moyenne de plusieurs évaluations

## 📞 Support Technique

- **URL du Projet** : https://github.com/ptreezh/AgentPsyAssessment
- **Feedback des Problèmes** : https://github.com/ptreezh/AgentPsyAssessment/issues
- **Guide de Séparation des Systèmes** : `README_SYSTEM_SEPARATION.md`

---
🎉 Vous pouvez maintenant commencer à utiliser AgentPsyAssessment pour l'évaluation psychologique professionnelle !