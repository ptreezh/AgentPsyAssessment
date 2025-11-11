# 🚀 AgentPsyAssessment - Guía de Inicio Rápido v1.0

## 📋 Tabla de Contenidos
- [Descripción del Sistema](#descripción-del-sistema)
- [Configuración del Entorno](#configuración-del-entorno)
- [Instalación Rápida](#instalación-rápida)
- [Experiencia de 5 Minutos](#experiencia-de-5-minutos)
- [Sistema Unificado de Habilidades de Evaluación](#sistema-unificado-de-habilidades-de-evaluación)
- [Uso Básico](#uso-básico)
- [Configuración API](#configuración-api)
- [Tipos de Evaluación Soportados](#tipos-de-evaluación-soportados)
- [Problemas Comunes](#problemas-comunes)
- [Solución de Problemas](#solución-de-problemas)

## 🎯 Descripción del Sistema

AgentPsyAssessment es un marco de evaluación psicológico portátil y completo que combina múltiples modelos psicométricos (Big Five, MBTI, funciones cognitivas) con capacidades de análisis impulsadas por IA.

### ⚠️ Importante: Separación de Sistemas de Evaluación y Análisis

- **📝 Sistema de Evaluación** (`llm_assessment/`): Respuestas de cuestionarios psicológicos generadas por IA
- **🎯 Sistema de Análisis** (`production_pipelines/`): Puntuación científica y análisis de respuestas
- **🧠 Sistema Unificado de Habilidades** (`.claude/skills/unified-assessment-system/`): Marco de evaluación impulsado por configuración

### 🆕 Nuevas Funciones (v1.0)
- ✨ **Sistema Unificado de Habilidades de Evaluación**: Arquitectura impulsada por configuración soportando 6 tipos de evaluación profesionales
- 🤖 **Detección Inteligente de Tipo**: Identificación automática de tipos de evaluación sin configuración manual
- 📊 **Informes de Visualización**: Informes HTML interactivos con visualización de datos Chart.js
- 🌍 **Soporte Multiidioma**: Interfaz y contenido bilingüe (Chino/Inglés/Español)
- 🎭 **16 Personalidades MBTI**: Análisis detallado de tipos de personalidad y mapeo

## 🔧 Configuración del Entorno

### Requisitos del Sistema
- **Python**: 3.8+
- **Memoria**: 4GB+ (8GB+ recomendados)
- **Almacenamiento**: 2GB+ de espacio disponible
- **Sistema**: Windows 10/11, macOS 10.15+, Linux

## ⚡ Instalación Rápida

### 1. Clonar el Proyecto
```bash
# Clonar el proyecto
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2. Configuración del Entorno Python
```bash
# Crear entorno virtual (recomendado)
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Instalar dependencias
pip install -r requirements.txt  # si está disponible
pip install ollama requests numpy pandas
```

### 3. Configurar Variables de Entorno
```bash
# Establecer proveedor (local o cloud)
export PROVIDER="local"  # o "cloud"

# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-openai-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-key"

# macOS/Linux
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 4. Verificar Instalación
```bash
# Ejecutar pruebas del sistema unificado de evaluación
cd .claude/skills/unified-assessment-system
python test_runner.py

# Salida esperada: 🎉 ALL TESTS PASSED!
```

## 🎯 Experiencia de 5 Minutos

### Método 1: Experiencia de Prueba Rápida
```bash
# 1. Experimentar generación de cuestionario
python llm_assessment/run_assessment_unified.py \
    --model_name def \
    --test_file llm_assessment/test_files/single_test_question_10.json \
    --role_name def \
    --tmpr 0.7

# 2. Experimentar análisis por lotes
python production_pipelines/local_batch_production/cli.py \
    assess --model gpt-4o --role def

# 3. Ver resultados
ls results/
```

### Método 2: Experiencia con Modelo Local
```bash
# Iniciar Ollama (si se usan modelos locales)
ollama serve

# Descargar modelo
ollama pull llama3.1

# Ejecutar evaluación local
python llm_assessment/run_assessment_unified.py \
    --model llama3.1 \
    --role a1 \
    --provider local
```

### Método 3: Experiencia de Demostración de Habilidades
```bash
# Ejecutar demostración de habilidades
python skills_demo_chinese_questionnaire.py

# Ver informes HTML generados
ls html/
```

## 🧠 Sistema Unificado de Habilidades de Evaluación

### Arquitectura del Sistema
```
.claude/skills/unified-assessment-system/
├── 📋 config_validator.py           # Validador de configuración
├── 🔍 assessment_detector.py        # Detector de tipos de evaluación
├── 🏗️ skill_base.py                 # Arquitectura base de habilidades
├── 📝 unified_questionnaire_responder.py    # Respondedor unificado de cuestionarios
├── 📊 unified_psychological_analyzer.py    # Analizador psicológico unificado
├── 📄 unified_report_generator.py          # Generador de informes unificado
└── 📁 configs/                       # Directorio de archivos de configuración
    ├── big_five_personality.json     # Evaluación de personalidad Big Five
    ├── citizenship_knowledge.json   # Evaluación de conocimiento ciudadano
    ├── financial_professional.json  # Evaluación profesional financiera
    ├── legal_knowledge.json         # Evaluación de conocimiento legal
    ├── motivation_psychology.json   # Evaluación de psicología motivacional
    └── political_literacy.json      # Evaluación de alfabetización política
```

### Tipos de Evaluación Soportados
1. **Evaluación de Personalidad Big Five** - Cinco dimensiones OCEAN + mapeo MBTI
2. **Evaluación de Conocimiento Ciudadano** - Derechos & obligaciones cívicas, conciencia del sistema político
3. **Evaluación Profesional Financiera** - Experiencia financiera, capacidades de identificación de riesgos
4. **Evaluación de Conocimiento Legal** - Fundamentos legales, capacidades operativas prácticas
5. **Evaluación de Psicología Motivacional** - Motivación de logro, motivación de poder, motivación de afiliación
6. **Evaluación de Alfabetización Política** - Conciencia del sistema político, pensamiento crítico

### Uso del Sistema Unificado de Habilidades
```bash
# Probar sistema unificado de evaluación
cd .claude/skills/unified-assessment-system
python test_runner.py

# Salida esperada:
# ✅ PASS Configuration System (6/6 configs loaded)
# ✅ PASS Assessment Detection (2/2 detections successful)
# ✅ PASS Questionnaire Response (Generated 2 responses)
# ✅ PASS Psychological Analysis (Big Five + MBTI analysis)
# ✅ PASS Report Generation (HTML report generated)
# 🎉 ALL TESTS PASSED!
```

## 🌐 Despliegue

### Opción 1: Despliegue Local (Recomendado para Principiantes)

#### 1. Instalar Ollama
```bash
# Windows (recomendado con Chocolatey)
choco install ollama

# Linux (con curl)
curl -fsSL https://ollama.ai/install.sh | sh

# macOS (con Homebrew)
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

### Opción 2: Despliegue en la Nube (Recomendado para Profesionales)

#### 1. Obtener Claves API

**Alibaba Cloud Tongyi Qianwen (DashScope)**
```bash
# Registrarse: https://bailian.console.aliyun.com/
# Obtener clave API
export DASHSCOPE_API_KEY=sk-your-api-key-here
```

**Anthropic Claude**
```bash
# Registrarse: https://console.anthropic.com/
# Obtener clave API
export ANTHROPIC_API_KEY=sk-ant-api-key-here
```

**OpenAI GPT**
```bash
# Registrarse: https://platform.openai.com/
# Obtener clave API
export OPENAI_API_KEY=sk-openai-key-here
```

#### 2. Configuración de Variables de Entorno
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-your-api-key"
$env:ANTHROPIC_API_KEY="sk-ant-api-key"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-your-api-key"
export ANTHROPIC_API_KEY="sk-ant-api-key"
export OPENAI_API_KEY="sk-openai-key"
```

## 🚀 Uso Básico

### 1. Evaluación Individual
```bash
# Evaluación básica
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name enfj \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json

# Ubicación del archivo de salida
# results/assessment_<timestamp>_<model>_<role>.json
```

### 2. Evaluación por Lotes
```bash
# Procesar múltiples roles por lotes
python production_pipelines/local_batch_production/run_batch_suite.py \
    --model llama3.1 \
    --roles a1,a2,b1

# Ver resultados por lotes
python production_pipelines/local_batch_production/cli.py analyze \
    --input results/latest_batch.json
```

### 3. Configuración Avanzada
```bash
# Establecer temperatura y parámetros
python llm_assessment/run_assessment_unified.py \
    --model_name claude-3-5-sonnet \
    --role_name intj \
    --temperature 0.2 \
    --max_tokens 1000

# Usar archivo de configuración específico
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --config_path configs/custom_assessment.json
```

## 🎨 Tipos de Evaluación Soportados

### 1. Personalidad Big Five
```bash
# Coincidencia de patrón de archivo: *big_five*, *personality*, *ocean*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-big-five-50-complete2.json
```

### 2. Conocimiento Ciudadano
```bash
# Coincidencia de patrón de archivo: *citizenship*, *公民*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-citizenship-test.json
```

### 3. Profesionales Financieros
```bash
# Coincidencia de patrón de archivo: *financial*, *金融*, *bank*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-fund-management-test.json
```

### 4. Conocimiento Legal
```bash
# Coincidencia de patrón de archivo: *legal*, *law*, *法律*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-legal-test.json
```

### 5. Psicología Motivacional
```bash
# Coincidencia de patrón de archivo: *motivation*, *动机*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-motivation-test.json
```

### 6. Alfabetización Política
```bash
# Coincidencia de patrón de archivo: *political*, *政治*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-political-test.json
```

## 🔧 Referencia Rápida de Comandos

### Comandos Básicos
```bash
# Verificar estado del sistema
python test_end_to_end_complete.py

# Ejecutar prueba rápida
python run_local_batch.py --quick

# Ver modelos disponibles
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_available_models.py
```

### Generación de Informes
```bash
# Generar informes HTML
python generate_all_html_reports.py

# Ver informes más recientes
ls html/ | tail -1
```

### Solución de Problemas
```bash
# Verificar dependencias
pip check

# Verificar configuración
python -c "import llm_assessment; print('✅ Importación exitosa')"

# Probar conexión API
python quick_cloud_test.py
```

## ❓ Preguntas Frecuentes

### P1: ¿Cómo elegir el modelo adecuado?
**A**:
- **Modelos locales**: `llama3.1`, `mistral` - Rápidos, gratuitos, adecuados para pruebas
- **Modelos en la nube**: `gpt-4o`, `claude-3-5-sonnet` - Alta calidad, requieren claves API
- **Recomendación**: Usar modelos locales para desarrollo, modelos en la nube para producción

### P2: ¿Dónde se guardan los resultados de evaluación?
**A**:
- Resultados brutos: `results/readonly-original/`
- Resultados procesados: `results/ok/evaluated/`
- Informes HTML: `html/`
- Análisis por lotes: `results/final-*-batch-analysis/`

### P3: ¿Cómo agregar nuevos tipos de evaluación?
**A**:
1. Agregar nueva configuración JSON en `.claude/skills/questionnaire-responder/configs/`
2. Ejecutar `python test_runner.py` para verificar configuración
3. El sistema detectará automáticamente nuevos tipos de evaluación

### P4: ¿Qué hacer con memoria insuficiente?
**A**:
```bash
# Limitar solicitudes simultáneas
export MAX_CONCURRENT_REQUESTS=1

# Usar modelos más pequeños
python llm_assessment/run_assessment_unified.py --model mistral

# Procesar por lotes
python final_batch_processor.py --limit 5
```

### P5: Manejo de fallos de llamadas API?
**A**:
```bash
# Verificar claves API
echo $OPENAI_API_KEY

# Probar conexión
python quick_cloud_test.py

# Usar respaldo local
export PROVIDER=local
```

## 🎯 Próximos Pasos

### 📚 Aprendizaje Profundo
- 📖 [Manual Completo del Usuario](../../USER_MANUAL.md)
- 🏗️ [Documentación de Arquitectura del Sistema](ARCHITECTURE.md)
- 🔧 [Documentación de Referencia API](API_REFERENCE.md)

### 🚀 Funciones Avanzadas
- 🔌 [Guía de Desarrollo de Plugins](PLUGIN_DEVELOPMENT.md)
- 📊 [Tutorial de Procesamiento por Lotes](BATCH_PROCESSING.md)
- 🌐 [Guía de Despliegue en la Nube](CLOUD_DEPLOYMENT.md)

### 🤝 Soporte Comunitario
- 🐛 [Retroalimentación de Problemas](https://github.com/your-repo/issues)
- 💬 [Área de Discusión](https://github.com/your-repo/discussions)
- 📧 [Soporte por Correo](mailto:support@example.com)

## 🎉 Lista de Verificación de Éxito

Complete los siguientes pasos para indicar configuración exitosa:

- [ ] ✅ Configuración de entorno completada (Python 3.8+)
- [ ] ✅ Dependencias del proyecto instaladas exitosamente
- [ ] ✅ Variables de entorno configuradas correctamente
- [ ] ✅ Prueba aprobada (`python test_runner.py`)
- [ ] ✅ Primer resultado de evaluación generado
- [ ] ✅ Informe HTML mostrado
- [ ] ✅ Diferentes tipos de evaluación probados

**🎊 ¡Felicidades! Ha dominado el uso básico de AgentPsyAssessment!**

---

**Versión**: v1.0.0
**Fecha de Actualización**: 2025-01-08
**Autor**: AgentPsyAssessment Team