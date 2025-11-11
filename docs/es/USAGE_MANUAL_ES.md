# 📖 Manual de Usuario de AgentPsyAssessment

## 🎯 Inicio Rápido

### 1️⃣ Descargar Proyecto
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2️⃣ Instalar Ollama (Modelos Locales)
```bash
# Windows
choco install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# Iniciar servicio
ollama serve

# Descargar modelos (nueva terminal)
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
```

### 3️⃣ Configurar Claves API (Modelos Cloud)
```bash
# Alibaba Cloud Qwen
export DASHSCOPE_API_KEY=sk-tu-clave-api

# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-clave-api

# OpenAI GPT
export OPENAI_API_KEY=sk-clave-openai
```

## 🚀 Flujo de Trabajo Principal de Uso

### Paso 1: Generar Respuestas de Cuestionario Psicológico (Sistema de Evaluación)
```bash
# Uso básico (modelos locales)
python llm_assessment/run_assessment_unified.py

# Especificar rol
python llm_assessment/run_assessment_unified.py --role_name enfj

# Usar cuestionario chino
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

### Paso 2: Análisis de Puntuación Científica (Sistema de Análisis)
```python
# Crear evaluate.py
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

# Inicializar sistema de evaluación
pipeline = TransparentPipeline(use_cloud=True)  # Modelos cloud + consenso adaptativo
parser = InputParser()

# Analizar y evaluar
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ Puntuación: {result['final_adjusted_scores']}")
print(f"🎯 Fiabilidad: {result['confidence_metrics']['overall_reliability']:.3f}")
```

Ejecutar evaluación:
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../evaluate.py
```

## 📋 Referencia Rápida de Comandos Comunes

### Evaluación de Modelos Locales
```bash
# Generar respuestas
python llm_assessment/run_assessment_unified.py --model_name qwen3:8b --role_name enfj

# Evaluación de lotes de roles
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py --role_name $role
done
```

### Evaluación de Modelos Cloud
```bash
# Establecer modelos cloud
export PROVIDER=cloud

# Usar modelos cloud para generar respuestas
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj

# Ejecutar prueba end-to-end
python test_end_to_end_complete.py
```

### Procesamiento por Lotes
```bash
# Analizar resultados existentes por lotes
python production_pipelines/local_batch_production/cli.py analyze --input results/

# Prueba de rendimiento
python adaptive_consensus_performance_test.py

# Prueba de integración
python test_adaptive_consensus_integration.py
```

## 🔧 Archivos de Configuración

### Configuración de Modelos: `llm_assessment/config/ollama_config.json`
```json
{
  "models": {
    "qwen3:8b": {"provider": "ollama", "temperature": 0.7},
    "deepseek-r1:8b": {"provider": "ollama", "temperature": 0.7}
  }
}
```

### Configuración de Roles: `llm_assessment/roles/enfj.json`
```json
{
  "name": "ENFJ - Protagonista",
  "description": "Cálido, idealista, empático",
  "traits": {"extraversion": 0.7, "intuition": 0.8}
}
```

## 📊 Interpretación de Resultados

### Ejemplo de Salida de Evaluación
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

### Guía de Métricas de Fiabilidad
- **0.8-1.0**: Alta fiabilidad, resultados confiables
- **0.6-0.8**: Fiabilidad media, uso de referencia
- **0.0-0.6**: Baja fiabilidad, recomendar reevaluación

## 🆘 Solución de Problemas

### Problemas con Ollama
```bash
# Verificar servicio
ollama list

# Reiniciar
ollama serve

# Verificar puerto
netstat -an | grep 11434
```

### Problemas con API
```bash
# Verificar claves
echo $DASHSCOPE_API_KEY

# Probar conexión
python -c "import requests; print('API OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'API Failed')"
```

### Errores de Importación
```bash
# Directorio de trabajo correcto
cd production_pipelines/local_batch_production/single_report_pipeline

# O establecer ruta de Python
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## 📚 Funciones Extendidas

### 1. Roles Personalizados
Crear `llm_assessment/roles/custom.json`:
```json
{
  "name": "Rol Personalizado",
  "description": "Tu descripción de rol",
  "traits": {"extraversion": 0.5, "openness": 0.6}
}
```

### 2. Scripts de Procesamiento por Lotes
```bash
# Crear script por lotes
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

### 3. Visualización de Resultados
```python
import matplotlib.pyplot as plt
import json

# Leer resultados
with open('results/evaluation_result.json') as f:
    data = json.load(f)

# Dibujar gráfico de radar Big Five
# ... código de gráfico ...

plt.savefig('personality_profile.png')
```

## 🎯 Mejores Prácticas

### 1. Elegir Modelos Apropiados
- **Principiantes**: Usar modelos locales Ollama
- **Profesionales**: Usar GPT-4/Claude-3.5 cloud
- **Investigación**: Usar evaluación multi-modelo con consenso adaptativo

### 2. Guía de Selección de Roles
- **ENFJ**: Adecuado para consultoría, escenarios educativos
- **INTJ**: Adecuado para análisis, escenarios estratégicos
- **ESTP**: Adecuado para práctica, escenarios operativos
- **ISTJ**: Adecuado para gestión, escenarios de ejecución

### 3. Optimización de Fiabilidad
- Usar modelos cloud para mejorar precisión
- Habilitar algoritmo de consenso adaptativo
- Establecer temperatura apropiada (0.3-0.7)
- Tomar promedio de múltiples evaluaciones

## 📞 Soporte Técnico

- **URL del Proyecto**: https://github.com/ptreezh/AgentPsyAssessment
- **Feedback de Problemas**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **Guía de Separación de Sistemas**: `README_SYSTEM_SEPARATION.md`

---
🎉 ¡Ahora puedes comenzar a usar AgentPsyAssessment para evaluación psicológica profesional!