# 🚀 Tarjeta de Referencia Rápida de AgentPsyAssessment

## ⚡ Inicio con un Clic

### 🔽 Descargar e Instalar
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 🔧 Instalar Ollama
```bash
# Windows
choco install ollama && ollama serve

# Linux
curl -fsSL https://ollama.ai/install.sh | sh && ollama serve

# macOS
brew install ollama && ollama serve

# Descargar modelos
ollama pull qwen3:8b deepseek-r1:8b
```

### 🔑 Configurar Claves API (Modelos Cloud)
```bash
export DASHSCOPE_API_KEY=sk-tu-clave
export ANTHROPIC_API_KEY=sk-ant-clave
```

## 🎯 Comandos Principales

### 📝 Generar Respuestas (Sistema de Evaluación)
```bash
# Básico
python llm_assessment/run_assessment_unified.py

# Especificar rol
python llm_assessment/run_assessment_unified.py --role_name enfj

# Modelos cloud
export PROVIDER=cloud
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj
```

### 📊 Puntuación Científica (Sistema de Análisis + Algoritmo de Consenso Adaptativo)
```python
# Crear script de evaluación
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

pipeline = TransparentPipeline(use_cloud=True)  # Modelos cloud + consenso adaptativo
parser = InputParser()
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ Puntuación: {result['final_adjusted_scores']}")
print(f"🎯 Fiabilidad: {result['confidence_metrics']['overall_reliability']:.3f}")
```

### 🚀 Ejecutar Evaluación
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../your_script.py
```

## 📋 Roles Disponibles

| Rol | Descripción | Ideal para |
|-----|-------------|------------|
| `enfj` | Protagonista | Consultoría, Educación |
| `intj` | Arquitecto | Análisis, Estrategia |
| `estp` | Emprendedor | Práctica, Operaciones |
| `istj` | Logístico | Gestión, Ejecución |
| `infp` | Mediador | Creatividad, Arte |
| `entj` | Comandante | Liderazgo, Decisiones |
| `estj` | Supervisor | Ejecución, Control |
| `isfp` | Aventurero | Flexibilidad, Adaptación |
| `intp` | Lógico | Investigación, Innovación |
| `esfp` | Artista | Entretenimiento, Social |

## 🌐 Modelos Disponibles

### Modelos Locales (Ollama)
- `qwen3:8b` - Qwen 8B
- `deepseek-r1:8b` - DeepSeek R1 8B
- `mistral-nemo:latest` - Mistral Nemo
- `llama3:latest` - Llama 3

### Modelos Cloud
- `deepseek-v3.1:671b-cloud` - DeepSeek V3.1 (671B)
- `gpt-oss:120b-cloud` - GPT (120B)
- `qwen3-vl:235b-cloud` - Qwen VL (235B)
- `gpt-4o` - GPT-4o
- `claude-3.5-sonnet` - Claude 3.5 Sonnet

## 🔍 Interpretación de Resultados

### Dimensiones de Personalidad Big Five
- **Openness (Apertura)**: Apertura a nuevas experiencias
- **Conscientiousness (Responsabilidad)**: Organización y autodisciplina
- **Extraversion**: Nivel de actividad social
- **Agreeableness (Amabilidad)**: Cooperación y empatía
- **Neuroticism (Neuroticismo)**: Estabilidad emocional

### Métricas de Fiabilidad
- **0.8-1.0** 🟢 Alta fiabilidad - Resultados confiables
- **0.6-0.8** 🟡 Fiabilidad media - Uso de referencia
- **0.0-0.6** 🔴 Baja fiabilidad - Recomendar reevaluación

## ⚠️ Distinción Importante

- 📝 **Sistema de Evaluación**: IA genera respuestas de cuestionario (`llm_assessment/`)
- 🎯 **Sistema de Análisis**: Análisis de puntuación científica (`transparent_pipeline.py` + `adaptive_consensus_algorithm.py`)

**Flujo de trabajo**: Generar respuestas → Análisis de puntuación

## 🛠️ Solución de Problemas

### Problemas con Ollama
```bash
ollama list          # Verificar modelos
ollama serve         # Iniciar servicio
netstat -an | grep 11434  # Verificar puerto
```

### Problemas con API
```bash
echo $DASHSCOPE_API_KEY     # Verificar clave
python -c "import requests; print('OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'FAIL')"
```

### Errores de Importación
```bash
cd production_pipelines/local_batch_production/single_report_pipeline  # Directorio correcto
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Establecer ruta
```

## 📞 Soporte Técnico

- 🌐 **URL del Proyecto**: https://github.com/ptreezh/AgentPsyAssessment
- 📖 **Separación de Sistemas**: `README_SYSTEM_SEPARATION.md`
- 📚 **Guía Rápida**: `QUICK_START_GUIDE.md`
- 🔧 **Manual de Uso**: `USAGE_MANUAL.md`

---
🎉 ¡Comienza tu viaje de evaluación psicológica!