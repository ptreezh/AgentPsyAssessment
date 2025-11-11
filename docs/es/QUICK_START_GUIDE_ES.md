# 🚀 Guía de Inicio Rápido de AgentPsyAssessment

## 📋 Tabla de Contenidos
- [Resumen del Sistema](#resumen-del-sistema)
- [Configuración del Entorno](#configuración-del-entorno)
- [Instalación y Despliegue](#instalación-y-despliegue)
- [Uso Rápido](#uso-rápido)
- [Configuración de API](#configuración-de-api)
- [Ejemplos Completos](#ejemplos-completos)
- [Solución de Problemas](#solución-de-problemas)

## 🎯 Resumen del Sistema

AgentPsyAssessment es un marco de evaluación psicológica portátil que utiliza modelos de lenguaje de IA para el análisis de personalidad.

### ⚠️ Importante: Separación de Sistemas de Evaluación vs Análisis

- **📝 Sistema de Evaluación** (`llm_assessment/`): IA genera respuestas de cuestionarios psicológicos
- **🎯 Sistema de Análisis** (`production_pipelines/.../transparent_pipeline.py`): Puntuación científica de respuestas

## 🔧 Configuración del Entorno

### Requisitos del Sistema
- **Python**: 3.8+
- **Memoria**: 8GB+ (16GB+ recomendado)
- **Sistema**: Windows/Linux/macOS

### 1. Clonar Proyecto
```bash
# Usar Git para clonar proyecto
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment

# O descargar paquete ZIP directamente
# Visitar: https://github.com/ptreezh/AgentPsyAssessment
# Hacer clic en "Code" → "Download ZIP"
```

### 2. Gestión del Entorno Python
```bash
# Recomendado usar entorno virtual
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Instalar dependencias
pip install -r requirements.txt  # si existe
pip install ollama requests numpy pandas
```

## 🌐 Instalación y Despliegue

### Opción 1: Despliegue Local (Recomendado para Principiantes)

#### 1. Instalar Ollama
```bash
# Windows (recomendado usar Chocolatey)
choco install ollama

# Linux (usando curl)
curl -fsSL https://ollama.ai/install.sh | sh

# macOS (usando Homebrew)
brew install ollama
```

#### 2. Iniciar Servicio Ollama
```bash
# Iniciar servicio Ollama
ollama serve

# Abrir nueva terminal, descargar modelos recomendados
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

### Opción 2: Despliegue Cloud (Recomendado para Usuarios Profesionales)

#### 1. Obtener Claves API

**Alibaba Cloud Qwen (DashScope)**
```bash
# Registrarse: https://bailian.console.aliyun.com/
# Obtener Clave API
export DASHSCOPE_API_KEY=sk-tu-clave-api-aquí
```

**Anthropic Claude**
```bash
# Registrarse: https://console.anthropic.com/
# Obtener Clave API
export ANTHROPIC_API_KEY=sk-ant-clave-api-aquí
```

**OpenAI GPT**
```bash
# Registrarse: https://platform.openai.com/
# Obtener Clave API
export OPENAI_API_KEY=sk-openai-clave-aquí
```

#### 2. Configuración de Variables de Entorno
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-tu-clave-api"
$env:ANTHROPIC_API_KEY="sk-ant-clave-api"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-tu-clave-api"
export ANTHROPIC_API_KEY="sk-ant-clave-api"
export OPENAI_API_KEY="sk-openai-clave"
```

## 🚀 Uso Rápido

### Paso 1: Generar Respuestas de Cuestionario Psicológico (Sistema de Evaluación)

```bash
# Uso básico - usar modelo predeterminado
python llm_assessment/run_assessment_unified.py

# Especificar modelo y rol
python llm_assessment/run_assessment_unified.py \
    --model_name deepseek-r1:8b \
    --role_name enfj \
    --tmpr 0.7

# Usar cuestionario chino
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name def \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

**Ejemplo de Salida**:
```
🎯 ¡Evaluación IA Completa!
Modelo: deepseek-r1:8b
Rol: enfj
Archivo de salida: results/assessment_result_20250108_123456.json
```

### Paso 2: Análisis de Puntuación Científica (Sistema de Análisis)

```python
# Crear script de evaluación evaluate_result.py
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser
import json

# Inicializar pipeline de evaluación (modelos cloud + algoritmo de consenso adaptativo)
pipeline = TransparentPipeline(use_cloud=True)

# Analizar respuestas
parser = InputParser()
questions = parser.parse_assessment_json('results/assessment_result_20250108_123456.json')

# Evaluar primera pregunta
question = questions[0]
result = pipeline.process_single_question(question, 0)

# Mostrar resultados
print(f"✅ ¡Evaluación Completa!")
print(f"Puntuación Final: {result['final_adjusted_scores']}")
print(f"Fiabilidad General: {result['confidence_metrics']['overall_reliability']:.3f}")
print(f"Modelos Usados: {len(result['models_used'])}")
print(f"Método de Consenso: {result['confidence_metrics']['consensus_method']}")
```

Ejecutar evaluación:
```bash
python evaluate_result.py
```

## 🔑 Detalles de Configuración de API

### Archivo de Configuración de Modelos
Editar `llm_assessment/config/ollama_config.json`:

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

### Configuración de Modelos Cloud
Editar `production_pipelines/local_batch_production/single_report_pipeline/config.yaml`:

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

## 📚 Ejemplos Completos

### Ejemplo 1: Flujo de Trabajo de Evaluación Completo

```bash
# 1. Generar respuestas
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name enfj \
    --tmpr 0.7

# 2. Crear script de evaluación
cat > complete_evaluation.py << 'EOF'
from transparent_pipeline import TransparentPipeline
from input_parser import InputParser

# Inicializar sistema de evaluación cloud
pipeline = TransparentPipeline(use_cloud=True)
parser = InputParser()

# Analizar respuestas
questions = parser.parse_assessment_json('results/latest_assessment.json')

# Evaluación por lotes
all_results = []
for i, question in enumerate(questions):
    print(f"Evaluando pregunta {i+1}/{len(questions)}: {question.get('question_id', 'Unknown')}")
    result = pipeline.process_single_question(question, i)
    all_results.append(result)

# Generar informe resumido
print("\n🎉 ¡Evaluación Completa!")
print(f"Total de preguntas: {len(all_results)}")
print(f"Fiabilidad promedio: {sum(r['confidence_metrics']['overall_reliability'] for r in all_results) / len(all_results):.3f}")

# Guardar resultados
import json
with open('evaluation_results.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
EOF

# 3. Ejecutar evaluación
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../../../complete_evaluation.py
```

### Ejemplo 2: Procesamiento por Lotes de Múltiples Roles

```bash
# Generar respuestas para múltiples roles
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py \
        --model_name qwen3:8b \
        --role_name $role \
        --tmpr 0.7
    echo "✅ Completada evaluación de rol $role"
done

# Evaluación por lotes
python batch_evaluation.py
```

## 🛠️ Funciones Avanzadas

### 1. Configuración de Roles Personalizados
Editar `llm_assessment/roles/enfj.json`:
```json
{
  "name": "ENFJ - Protagonista",
  "description": "Tipo de personalidad cálida, idealista, empática",
  "traits": {
    "extraversion": 0.7,
    "intuition": 0.8,
    "feeling": 0.9,
    "judging": 0.8
  },
  "communication_style": "Cálido, alentador, perspicaz"
}
```

### 2. Scripts de Procesamiento por Lotes
```bash
# Crear script por lotes
cat > batch_assess.sh << 'EOF'
#!/bin/bash
ROLES=("enfj" "intj" "estp" "istj" "infp" "entj")
MODEL="qwen3:8b"

for role in "${ROLES[@]}"; do
    echo "🎯 Procesando rol: $role"
    python llm_assessment/run_assessment_unified.py \
        --model_name $MODEL \
        --role_name $role \
        --tmpr 0.7
    sleep 2  # Evitar límites de API
done

echo "✅ ¡Evaluación por lotes completa!"
EOF

chmod +x batch_assess.sh
./batch_assess.sh
```

### 3. Visualización de Resultados
```python
# Crear script de visualización
import matplotlib.pyplot as plt
import json

# Leer resultados de evaluación
with open('evaluation_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Extraer puntuaciones Big Five
dimensions = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
scores = {dim: [] for dim in dimensions}

for result in results:
    for dim, score in result['final_adjusted_scores'].items():
        if dim in scores:
            scores[dim].append(score)

# Dibujar gráfico de radar
angles = [n / float(len(dimensions)) * 2 * 3.14159 for n in range(len(dimensions))]
angles += angles[:1]

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, polar=True)

for dim in dimensions:
    values = scores[dim]
    avg_value = sum(values) / len(values)
    # Lógica de dibujo...

plt.title('Análisis de Rasgos de Personalidad', size=16, weight='bold')
plt.savefig('personality_radar.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 🔍 Solución de Problemas

### Problemas Comunes y Soluciones

#### 1. Fallo de Conexión Ollama
```bash
# Verificar estado del servicio Ollama
ollama list

# Si el servicio no está iniciado
ollama serve

# Verificar puerto
netstat -an | grep 11434
```

#### 2. Fallo de Descarga de Modelo
```bash
# Descargar modelo manualmente
ollama pull qwen3:8b

# Verificar lista de modelos
ollama list

# Eliminar modelo dañado y volver a descargar
ollama rm qwen3:8b
ollama pull qwen3:8b
```

#### 3. Error de Clave API
```bash
# Verificar variables de entorno
echo $DASHSCOPE_API_KEY
echo $ANTHROPIC_API_KEY

# Probar conexión API
python -c "
import requests
response = requests.get('https://dashscope.aliyuncs.com/api/v1/models',
    headers={'Authorization': f'Bearer {os.environ.get(\"DASHSCOPE_API_KEY\")}'})
print('Código de estado API:', response.status_code)
"
```

#### 4. Memoria Insuficiente
```bash
# Monitorear uso de memoria
htop  # Linux/macOS
tasklist  # Windows

# Reducir concurrencia
export OLLAMA_MAX_LOADED_MODELS=1

# Usar modelos más pequeños
ollama pull qwen3:1.8b  # Versión 1.8B parámetros
```

#### 5. Error de Importación Relativa
```bash
# Asegurarse de ejecutar en directorio correcto
cd production_pipelines/local_batch_production/single_report_pipeline
python -m transparent_pipeline

# O usar PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
python your_script.py
```

## 📖 Aprendizaje Extendido

### Documentación Oficial
- **URL del Proyecto**: https://github.com/ptreezh/AgentPsyAssessment
- **Guía de Separación de Sistemas**: `README_SYSTEM_SEPARATION.md`
- **Documentación del Sistema de Evaluación**: `llm_assessment/README.md`
- **Documentación del Sistema de Análisis**: `production_pipelines/local_batch_production/single_report_pipeline/README.md`

### Documentación Técnica
- **Algoritmo de Consenso Adaptativo**: `production_pipelines/cloud_fallback_enterprise/adaptive_consensus_algorithm.py`
- **Configuración de API**: `CLAUDE.md`
- **Procesamiento por Lotes**: `production_pipelines/local_batch_production/cli.py`

### Recursos de la Comunidad
- **Issues**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **Discusiones**: https://github.com/ptreezh/AgentPsyAssessment/discussions
- **Wiki**: https://github.com/ptreezh/AgentPsyAssessment/wiki

## 🎉 ¡Felicidades!

¡Has desplegado exitosamente el sistema AgentPsyAssessment!

🔥 **Recomendaciones de Siguientes Pasos**:
1. Probar scripts de ejemplo
2. Explorar diferentes configuraciones de roles
3. Usar modelos cloud para evaluación más precisa
4. Revisar informes detallados generados

Si tienes preguntas, por favor revisa la sección de solución de problemas o envía un Issue.