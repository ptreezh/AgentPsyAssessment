# 🚀 Карточка Быстрой Справки AgentPsyAssessment

## ⚡ Запуск в Один Клик

### 🔽 Скачать и Установить
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 🔧 Установить Ollama
```bash
# Windows
choco install ollama && ollama serve

# Linux
curl -fsSL https://ollama.ai/install.sh | sh && ollama serve

# macOS
brew install ollama && ollama serve

# Скачать модели
ollama pull qwen3:8b deepseek-r1:8b
```

### 🔑 Настроить Ключи API (Облачные Модели)
```bash
export DASHSCOPE_API_KEY=sk-ваш-ключ
export ANTHROPIC_API_KEY=sk-ant-ключ
```

## 🎯 Основные Команды

### 📝 Генерировать Ответы (Система Оценки)
```bash
# Базовый
python llm_assessment/run_assessment_unified.py

# Указать роль
python llm_assessment/run_assessment_unified.py --role_name enfj

# Облачные модели
export PROVIDER=cloud
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj
```

### 📊 Научная Оценка (Система Анализа + Адаптивный Алгоритм Консенсуса)
```python
# Создать скрипт оценки
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

pipeline = TransparentPipeline(use_cloud=True)  # Облачные модели + адаптивный консенсус
parser = InputParser()
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ Оценка: {result['final_adjusted_scores']}")
print(f"🎯 Надёжность: {result['confidence_metrics']['overall_reliability']:.3f}")
```

### 🚀 Запустить Оценку
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../your_script.py
```

## 📋 Доступные Роли

| Роль | Описание | Идеально для |
|------|-----------|--------------|
| `enfj` | Протагонист | Консалтинг, Образование |
| `intj` | Архитектор | Анализ, Стратегия |
| `estp` | Предприниматель | Практика, Операции |
| `istj` | Логистик | Управление, Исполнение |
| `infp` | Посредник | Творчество, Искусство |
| `entj` | Командир | Лидерство, Решения |
| `estj` | Supervizor | Исполнение, Контроль |
| `isfp` | Искатель | Гибкость, Адаптация |
| `intp` | Логик | Исследования, Инновации |
| `esfp` | Артист | Развлечения, Социальное |

## 🌐 Доступные Модели

### Локальные Модели (Ollama)
- `qwen3:8b` - Qwen 8B
- `deepseek-r1:8b` - DeepSeek R1 8B
- `mistral-nemo:latest` - Mistral Nemo
- `llama3:latest` - Llama 3

### Облачные Модели
- `deepseek-v3.1:671b-cloud` - DeepSeek V3.1 (671B)
- `gpt-oss:120b-cloud` - GPT (120B)
- `qwen3-vl:235b-cloud` - Qwen VL (235B)
- `gpt-4o` - GPT-4o
- `claude-3.5-sonnet` - Claude 3.5 Sonnet

## 🔍 Интерпретация Результатов

### Измерения Личности Большой Пятёрки
- **Openness (Открытость)**: Открытость к новому опыту
- **Conscientiousness (Сознательность)**: Организация и самодисциплина
- **Extraversion**: Уровень социальной активности
- **Agreeableness (Доброжелательность)**: Сотрудничество и эмпатия
- **Neuroticism (Нейротизм)**: Эмоциональная стабильность

### Метрики Надёжности
- **0.8-1.0** 🟢 Высокая надёжность - Результаты надёжны
- **0.6-0.8** 🟡 Средняя надёжность - Для справки
- **0.0-0.6** 🔴 Низкая надёжность - Рекомендовать переоценку

## ⚠️ Важное Различие

- 📝 **Система Оценки**: ИИ генерирует ответы опросника (`llm_assessment/`)
- 🎯 **Система Анализа**: Научный анализ оценки (`transparent_pipeline.py` + `adaptive_consensus_algorithm.py`)

**Рабочий процесс**: Генерировать ответы → Анализ оценки

## 🛠️ Решение Проблем

### Проблемы с Ollama
```bash
ollama list          # Проверить модели
ollama serve         # Запустить сервис
netstat -an | grep 11434  # Проверить порт
```

### Проблемы с API
```bash
echo $DASHSCOPE_API_KEY     # Проверить ключ
python -c "import requests; print('OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'FAIL')"
```

### Ошибки Импорта
```bash
cd production_pipelines/local_batch_production/single_report_pipeline  # Правильная директория
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Установить путь
```

## 📞 Техническая Поддержка

- 🌐 **URL Проекта**: https://github.com/ptreezh/AgentPsyAssessment
- 📖 **Разделение Систем**: `README_SYSTEM_SEPARATION.md`
- 📚 **Быстрое Руководство**: `QUICK_START_GUIDE.md`
- 🔧 **Руководство Пользователя**: `USAGE_MANUAL.md`

---
🎉 Начните своё путешествие психологической оценки!