# 📖 Руководство Пользователя AgentPsyAssessment

## 🎯 Быстрый Старт

### 1️⃣ Скачать Проект
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2️⃣ Установить Ollama (Локальные Модели)
```bash
# Windows
choco install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# Запустить сервис
ollama serve

# Скачать модели (новый терминал)
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
```

### 3️⃣ Настроить Ключи API (Облачные Модели)
```bash
# Alibaba Cloud Qwen
export DASHSCOPE_API_KEY=sk-ваш-api-ключ

# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-api-ключ

# OpenAI GPT
export OPENAI_API_KEY=sk-openai-ключ
```

## 🚀 Основной Рабочий Процесс Использования

### Шаг 1: Генерация Ответов Психологического Опросника (Система Оценки)
```bash
# Базовое использование (локальные модели)
python llm_assessment/run_assessment_unified.py

# Указать роль
python llm_assessment/run_assessment_unified.py --role_name enfj

# Использовать китайский опросник
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

### Шаг 2: Научный Анализ Оценки (Система Анализа)
```python
# Создать evaluate.py
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

# Инициализировать систему оценки
pipeline = TransparentPipeline(use_cloud=True)  # Облачные модели + адаптивный консенсус
parser = InputParser()

# Анализировать и оценивать
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ Оценка: {result['final_adjusted_scores']}")
print(f"🎯 Надёжность: {result['confidence_metrics']['overall_reliability']:.3f}")
```

Запустить оценку:
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../evaluate.py
```

## 📋 Справочник Частых Команд

### Оценка Локальных Моделей
```bash
# Генерировать ответы
python llm_assessment/run_assessment_unified.py --model_name qwen3:8b --role_name enfj

# Пакетная оценка ролей
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py --role_name $role
done
```

### Оценка Облачных Моделей
```bash
# Установить облачные модели
export PROVIDER=cloud

# Использовать облачные модели для генерации ответов
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj

# Запустить end-to-end тест
python test_end_to_end_complete.py
```

### Пакетная Обработка
```bash
# Пакетный анализ существующих результатов
python production_pipelines/local_batch_production/cli.py analyze --input results/

# Тест производительности
python adaptive_consensus_performance_test.py

# Интеграционный тест
python test_adaptive_consensus_integration.py
```

## 🔧 Файлы Конфигурации

### Конфигурация Моделей: `llm_assessment/config/ollama_config.json`
```json
{
  "models": {
    "qwen3:8b": {"provider": "ollama", "temperature": 0.7},
    "deepseek-r1:8b": {"provider": "ollama", "temperature": 0.7}
  }
}
```

### Конфигурация Ролей: `llm_assessment/roles/enfj.json`
```json
{
  "name": "ENFJ - Протагонист",
  "description": "Тёплый, идеалистичный, эмпатичный",
  "traits": {"extraversion": 0.7, "intuition": 0.8}
}
```

## 📊 Интерпретация Результатов

### Пример Вывода Оценки
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

### Руководство по Метрикам Надёжности
- **0.8-1.0**: Высокая надёжность, результаты надёжны
- **0.6-0.8**: Средняя надёжность, для справки
- **0.0-0.6**: Низкая надёжность, рекомендовать переоценку

## 🆘 Решение Проблем

### Проблемы с Ollama
```bash
# Проверить сервис
ollama list

# Перезапустить
ollama serve

# Проверить порт
netstat -an | grep 11434
```

### Проблемы с API
```bash
# Проверить ключи
echo $DASHSCOPE_API_KEY

# Проверить соединение
python -c "import requests; print('API OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'API Failed')"
```

### Ошибки Импорта
```bash
# Правильная рабочая директория
cd production_pipelines/local_batch_production/single_report_pipeline

# Или установить путь Python
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## 📚 Расширенные Функции

### 1. Пользовательские Роли
Создать `llm_assessment/roles/custom.json`:
```json
{
  "name": "Пользовательская Роль",
  "description": "Ваше описание роли",
  "traits": {"extraversion": 0.5, "openness": 0.6}
}
```

### 2. Скрипты Пакетной Обработки
```bash
# Создать пакетный скрипт
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

### 3. Визуализация Результатов
```python
import matplotlib.pyplot as plt
import json

# Прочитать результаты
with open('results/evaluation_result.json') as f:
    data = json.load(f)

# Нарисовать радар Большой Пятёрки
# ... код графика ...

plt.savefig('personality_profile.png')
```

## 🎯 Лучшие Практики

### 1. Выбрать Подходящие Модели
- **Новички**: Использовать локальные модели Ollama
- **Профессионалы**: Использовать облачные GPT-4/Claude-3.5
- **Исследования**: Использовать мульти-модель оценку с адаптивным консенсусом

### 2. Руководство по Выбору Ролей
- **ENFJ**: Подходит для консалтинга, образовательных сценариев
- **INTJ**: Подходит для анализа, стратегических сценариев
- **ESTP**: Подходит для практики, операционных сценариев
- **ISTJ**: Подходит для управления, сценариев исполнения

### 3. Оптимизация Надёжности
- Использовать облачные модели для повышения точности
- Включить адаптивный алгоритм консенсуса
- Установить подходящую температуру (0.3-0.7)
- Взять среднее от нескольких оценок

## 📞 Техническая Поддержка

- **URL Проекта**: https://github.com/ptreezh/AgentPsyAssessment
- **Обратная связь по проблемам**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **Руководство по разделению систем**: `README_SYSTEM_SEPARATION.md`

---
🎉 Теперь вы можете начать использовать AgentPsyAssessment для профессиональной психологической оценки!