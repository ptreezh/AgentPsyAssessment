# 🚀 Быстрое Руководство по Началу Работы с AgentPsyAssessment

## 📋 Содержание
- [Обзор Системы](#обзор-системы)
- [Настройка Окружения](#настройка-окружения)
- [Установка и Развертывание](#установка-и-развертывание)
- [Быстрое Использование](#быстрое-использование)
- [Конфигурация API](#конфигурация-api)
- [Полные Примеры](#полные-примеры)
- [Решение Проблем](#решение-проблем)

## 🎯 Обзор Системы

AgentPsyAssessment - это портативный фреймворк психологической оценки, который использует большие языковые модели ИИ для анализа личности.

### ⚠️ Важно: Разделение Систем Оценки vs Анализа

- **📝 Система Оценки** (`llm_assessment/`): ИИ генерирует ответы психологических опросников
- **🎯 Система Анализа** (`production_pipelines/.../transparent_pipeline.py`): Научная оценка ответов

## 🔧 Настройка Окружения

### Системные Требования
- **Python**: 3.8+
- **Память**: 8GB+ (рекомендуется 16GB+)
- **Система**: Windows/Linux/macOS

### 1. Клонировать Проект
```bash
# Использовать Git для клонирования проекта
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment

# Или скачать ZIP-пакет напрямую
# Посетить: https://github.com/ptreezh/AgentPsyAssessment
# Нажать "Code" → "Download ZIP"
```

### 2. Управление Окружением Python
```bash
# Рекомендуется использовать виртуальное окружение
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Установить зависимости
pip install -r requirements.txt  # если существует
pip install ollama requests numpy pandas
```

## 🌐 Установка и Развертывание

### Вариант 1: Локальное Развертывание (Рекомендуется для Начинающих)

#### 1. Установить Ollama
```bash
# Windows (рекомендуется использовать Chocolatey)
choco install ollama

# Linux (используя curl)
curl -fsSL https://ollama.ai/install.sh | sh

# macOS (используя Homebrew)
brew install ollama
```

#### 2. Запустить Сервис Ollama
```bash
# Запустить сервис Ollama
ollama serve

# Открыть новый терминал, скачать рекомендуемые модели
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

### Вариант 2: Облачное Развертывание (Рекомендуется для Профессиональных Пользователей)

#### 1. Получить Ключи API

**Alibaba Cloud Qwen (DashScope)**
```bash
# Зарегистрироваться: https://bailian.console.aliyun.com/
# Получить Ключ API
export DASHSCOPE_API_KEY=sk-ваш-api-ключ-здесь
```

**Anthropic Claude**
```bash
# Зарегистрироваться: https://console.anthropic.com/
# Получить Ключ API
export ANTHROPIC_API_KEY=sk-ant-api-ключ-здесь
```

**OpenAI GPT**
```bash
# Зарегистрироваться: https://platform.openai.com/
# Получить Ключ API
export OPENAI_API_KEY=sk-openai-ключ-здесь
```

#### 2. Конфигурация Переменных Окружения
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-ваш-api-ключ"
$env:ANTHROPIC_API_KEY="sk-ant-api-ключ"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-ваш-api-ключ"
export ANTHROPIC_API_KEY="sk-ant-api-ключ"
export OPENAI_API_KEY="sk-openai-ключ"
```

## 🚀 Быстрое Использование

### Шаг 1: Генерация Ответов Психологического Опросника (Система Оценки)

```bash
# Базовое использование - использовать модель по умолчанию
python llm_assessment/run_assessment_unified.py

# Указать модель и роль
python llm_assessment/run_assessment_unified.py \
    --model_name deepseek-r1:8b \
    --role_name enfj \
    --tmpr 0.7

# Использовать китайский опросник
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name def \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

**Пример Вывода**:
```
🎯 Оценка ИИ Завершена!
Модель: deepseek-r1:8b
Роль: enfj
Файл вывода: results/assessment_result_20250108_123456.json
```

### Шаг 2: Научный Анализ Оценки (Система Анализа)

```python
# Создать скрипт оценки evaluate_result.py
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser
import json

# Инициализировать конвейер оценки (облачные модели + адаптивный алгоритм консенсуса)
pipeline = TransparentPipeline(use_cloud=True)

# Анализировать ответы
parser = InputParser()
questions = parser.parse_assessment_json('results/assessment_result_20250108_123456.json')

# Оценить первый вопрос
question = questions[0]
result = pipeline.process_single_question(question, 0)

# Показать результаты
print(f"✅ Оценка Завершена!")
print(f"Финальная Оценка: {result['final_adjusted_scores']}")
print(f"Общая Надёжность: {result['confidence_metrics']['overall_reliability']:.3f}")
print(f"Использовано Моделей: {len(result['models_used'])}")
print(f"Метод Консенсуса: {result['confidence_metrics']['consensus_method']}")
```

Запустить оценку:
```bash
python evaluate_result.py
```

## 🔑 Детали Конфигурации API

### Файл Конфигурации Моделей
Отредактировать `llm_assessment/config/ollama_config.json`:

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

### Конфигурация Облачных Моделей
Отредактировать `production_pipelines/local_batch_production/single_report_pipeline/config.yaml`:

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

## 📚 Полные Примеры

### Пример 1: Полный Рабочий Процесс Оценки

```bash
# 1. Генерировать ответы
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name enfj \
    --tmpr 0.7

# 2. Создать скрипт оценки
cat > complete_evaluation.py << 'EOF'
from transparent_pipeline import TransparentPipeline
from input_parser import InputParser

# Инициализировать облачную систему оценки
pipeline = TransparentPipeline(use_cloud=True)
parser = InputParser()

# Анализировать ответы
questions = parser.parse_assessment_json('results/latest_assessment.json')

# Пакетная оценка
all_results = []
for i, question in enumerate(questions):
    print(f"Оцениваю вопрос {i+1}/{len(questions)}: {question.get('question_id', 'Unknown')}")
    result = pipeline.process_single_question(question, i)
    all_results.append(result)

# Генерировать итоговый отчёт
print("\n🎉 Оценка Завершена!")
print(f"Всего вопросов: {len(all_results)}")
print(f"Средняя надёжность: {sum(r['confidence_metrics']['overall_reliability'] for r in all_results) / len(all_results):.3f}")

# Сохранить результаты
import json
with open('evaluation_results.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
EOF

# 3. Запустить оценку
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../../../complete_evaluation.py
```

### Пример 2: Пакетная Обработка Множественных Ролей

```bash
# Генерировать ответы для множественных ролей
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py \
        --model_name qwen3:8b \
        --role_name $role \
        --tmpr 0.7
    echo "✅ Завершена оценка роли $role"
done

# Пакетная оценка
python batch_evaluation.py
```

## 🛠️ Расширенные Функции

### 1. Конфигурация Пользовательских Ролей
Отредактировать `llm_assessment/roles/enfj.json`:
```json
{
  "name": "ENFJ - Протагонист",
  "description": "Тёплый, идеалистичный, эмпатичный тип личности",
  "traits": {
    "extraversion": 0.7,
    "intuition": 0.8,
    "feeling": 0.9,
    "judging": 0.8
  },
  "communication_style": "Тёплый, ободряющий, проницательный"
}
```

### 2. Скрипты Пакетной Обработки
```bash
# Создать пакетный скрипт
cat > batch_assess.sh << 'EOF'
#!/bin/bash
ROLES=("enfj" "intj" "estp" "istj" "infp" "entj")
MODEL="qwen3:8b"

for role in "${ROLES[@]}"; do
    echo "🎯 Обработка роли: $role"
    python llm_assessment/run_assessment_unified.py \
        --model_name $MODEL \
        --role_name $role \
        --tmpr 0.7
    sleep 2  # Избежать лимитов API
done

echo "✅ Пакетная оценка завершена!"
EOF

chmod +x batch_assess.sh
./batch_assess.sh
```

### 3. Визуализация Результатов
```python
# Создать скрипт визуализации
import matplotlib.pyplot as plt
import json

# Прочитать результаты оценки
with open('evaluation_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Извлечь оценки Большой Пятёрки
dimensions = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
scores = {dim: [] for dim in dimensions}

for result in results:
    for dim, score in result['final_adjusted_scores'].items():
        if dim in scores:
            scores[dim].append(score)

# Нарисовать радарную диаграмму
angles = [n / float(len(dimensions)) * 2 * 3.14159 for n in range(len(dimensions))]
angles += angles[:1]

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, polar=True)

for dim in dimensions:
    values = scores[dim]
    avg_value = sum(values) / len(values)
    # Логика рисования...

plt.title('Анализ Черт Личности', size=16, weight='bold')
plt.savefig('personality_radar.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 🔍 Решение Проблем

### Распространённые Проблемы и Решения

#### 1. Сбой Подключения Ollama
```bash
# Проверить статус сервиса Ollama
ollama list

# Если сервис не запущен
ollama serve

# Проверить порт
netstat -an | grep 11434
```

#### 2. Сбой Загрузки Модели
```bash
# Вручную скачать модель
ollama pull qwen3:8b

# Проверить список моделей
ollama list

# Удалить повреждённую модель и перезакачать
ollama rm qwen3:8b
ollama pull qwen3:8b
```

#### 3. Ошибка Ключа API
```bash
# Проверить переменные окружения
echo $DASHSCOPE_API_KEY
echo $ANTHROPIC_API_KEY

# Проверить соединение API
python -c "
import requests
response = requests.get('https://dashscope.aliyuncs.com/api/v1/models',
    headers={'Authorization': f'Bearer {os.environ.get(\"DASHSCOPE_API_KEY\")}'})
print('Статус код API:', response.status_code)
"
```

#### 4. Недостаточно Памяти
```bash
# Мониторить использование памяти
htop  # Linux/macOS
tasklist  # Windows

# Снизить параллелизм
export OLLAMA_MAX_LOADED_MODELS=1

# Использовать меньшие модели
ollama pull qwen3:1.8b  # Версия 1.8B параметров
```

#### 5. Ошибка Относительного Импорта
```bash
# Убедиться, что выполняете в правильной директории
cd production_pipelines/local_batch_production/single_report_pipeline
python -m transparent_pipeline

# Или использовать PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
python your_script.py
```

## 📖 Расширенное Обучение

### Официальная Документация
- **URL Проекта**: https://github.com/ptreezh/AgentPsyAssessment
- **Руководство по Разделению Систем**: `README_SYSTEM_SEPARATION.md`
- **Документация Системы Оценки**: `llm_assessment/README.md`
- **Документация Системы Анализа**: `production_pipelines/local_batch_production/single_report_pipeline/README.md`

### Техническая Документация
- **Адаптивный Алгоритм Консенсуса**: `production_pipelines/cloud_fallback_enterprise/adaptive_consensus_algorithm.py`
- **Конфигурация API**: `CLAUDE.md`
- **Пакетная Обработка**: `production_pipelines/local_batch_production/cli.py`

### Ресурсы Сообщества
- **Issues**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **Обсуждения**: https://github.com/ptreezh/AgentPsyAssessment/discussions
- **Wiki**: https://github.com/ptreezh/AgentPsyAssessment/wiki

## 🎉 Поздравляем!

Вы успешно развернули систему AgentPsyAssessment!

🔥 **Рекомендации Следующих Шагов**:
1. Попробовать запустить пример скриптов
2. Исследовать различные конфигурации ролей
3. Использовать облачные модели для более точной оценки
4. Проверить сгенерированные подробные отчёты

Если у вас есть вопросы, пожалуйста, проверьте раздел решения проблем или отправьте Issue.