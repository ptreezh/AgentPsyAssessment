# 🚀 AgentPsyAssessment - Руководство по Быстрому Началу v1.0

## 📋 Содержание
- [Обзор Системы](#обзор-системы)
- [Настройка Окружения](#настройка-окружения)
- [Быстрая Установка](#быстрая-установка)
- [5-минутный Опыт](#5-минутный-опыт)
- [Единая Система Навыков Оценки](#единая-система-навыков-оценки)
- [Базовое Использование](#базовое-использование)
- [Настройка API](#настройка-api)
- [Поддерживаемые Типы Оценки](#поддерживаемые-типы-оценки)
- [Распространенные Проблемы](#распространенные-проблемы)
- [Устранение Неполадок](#устранение-неполадок)

## 🎯 Обзор Системы

AgentPsyAssessment - это портативная, комплексная платформа для психологической оценки, которая объединяет несколько психометрических моделей (Большая Пятерка, MBTI, когнитивные функции) с возможностями анализа на основе ИИ.

### ⚠️ Важно: Разделение Систем Оценки и Анализа

- **📝 Система Оценки** (`llm_assessment/`): Генерация ответов на психологические вопросники с помощью ИИ
- **🎯 Система Анализа** (`production_pipelines/`): Научная оценка и анализ ответов
- **🧠 Единая Система Навыков** (`.claude/skills/unified-assessment-system/`): Фреймворк оценки, управляемый конфигурацией

### 🆕 Новые Функции (v1.0)
- ✨ **Единая Система Навыков Оценки**: Архитектура, управляемая конфигурацией, поддерживающая 6 профессиональных типов оценки
- 🤖 **Интеллектуальное Определение Типа**: Автоматическая идентификация типов оценки без ручной настройки
- 📊 **Отчеты Визуализации**: Интерактивные HTML-отчеты с визуализацией данных Chart.js
- 🌍 **Многоязычная Поддержка**: Двуязычный интерфейс и контент (Китайский/Английский/Русский)
- 🎭 **16 MBTI Личностей**: Детальный анализ типов личности и сопоставление

## 🔧 Настройка Окружения

### Системные Требования
- **Python**: 3.8+
- **Память**: 4GB+ (8GB+ рекомендуется)
- **Хранилище**: 2GB+ доступного пространства
- **Система**: Windows 10/11, macOS 10.15+, Linux

## ⚡ Быстрая Установка

### 1. Клонировать Проект
```bash
# Клонировать проект
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2. Настройка Окружения Python
```bash
# Создать виртуальное окружение (рекомендуется)
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Установить зависимости
pip install -r requirements.txt  # если доступно
pip install ollama requests numpy pandas
```

### 3. Настроить Переменные Окружения
```bash
# Установить провайдера (local или cloud)
export PROVIDER="local"  # или "cloud"

# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-openai-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-key"

# macOS/Linux
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 4. Проверить Установку
```bash
# Запустить тесты единой системы оценки
cd .claude/skills/unified-assessment-system
python test_runner.py

# Ожидаемый результат: 🎉 ALL TESTS PASSED!
```

## 🎯 5-минутный Опыт

### Метод 1: Быстрый Тестовый Опыт
```bash
# 1. Попробовать генерацию вопросника
python llm_assessment/run_assessment_unified.py \
    --model_name def \
    --test_file llm_assessment/test_files/single_test_question_10.json \
    --role_name def \
    --tmpr 0.7

# 2. Попробовать пакетный анализ
python production_pipelines/local_batch_production/cli.py \
    assess --model gpt-4o --role def

# 3. Посмотреть результаты
ls results/
```

### Метод 2: Опыт с Локальными Моделями
```bash
# Запустить Ollama (если используются локальные модели)
ollama serve

# Скачать модель
ollama pull llama3.1

# Запустить локальную оценку
python llm_assessment/run_assessment_unified.py \
    --model llama3.1 \
    --role a1 \
    --provider local
```

### Метод 3: Опыт Демонстрации Навыков
```bash
# Запустить демо навыков
python skills_demo_chinese_questionnaire.py

# Посмотреть сгенерированные HTML-отчеты
ls html/
```

## 🧠 Единая Система Навыков Оценки

### Архитектура Системы
```
.claude/skills/unified-assessment-system/
├── 📋 config_validator.py           # Валидатор конфигурации
├── 🔍 assessment_detector.py        # Детектор типов оценки
├── 🏗️ skill_base.py                 # Базовая архитектура навыков
├── 📝 unified_questionnaire_responder.py    # Единый ответчик на вопросники
├── 📊 unified_psychological_analyzer.py    # Единый психологический анализатор
├── 📄 unified_report_generator.py          # Единый генератор отчетов
└── 📁 configs/                       # Каталог файлов конфигурации
    ├── big_five_personality.json     # Оценка личности Большой Пятерки
    ├── citizenship_knowledge.json   # Оценка гражданских знаний
    ├── financial_professional.json  # Оценка финансовых профессионалов
    ├── legal_knowledge.json         # Оценка юридических знаний
    ├── motivation_psychology.json   # Оценка психологии мотивации
    └── political_literacy.json      # Оценка политической грамотности
```

### Поддерживаемые Типы Оценки
1. **Оценка Личности Большой Пятерки** - Пять измерений OCEAN + сопоставление MBTI
2. **Оценка Гражданских Знаний** - Гражданские права & обязанности, осведомленность о политической системе
3. **Оценка Финансовых Профессионалов** - Финансовая экспертиза, возможности идентификации рисков
4. **Оценка Юридических Знаний** - Юридические основы, практические операционные возможности
5. **Оценка Психологии Мотивации** - Мотивация достижений, мотивация власти, мотивация принадлежности
6. **Оценка Политической Грамотности** - Осведомленность о политической системе, критическое мышление

### Использование Единой Системы Навыков
```bash
# Тестировать единую систему оценки
cd .claude/skills/unified-assessment-system
python test_runner.py

# Ожидаемый результат:
# ✅ PASS Configuration System (6/6 configs loaded)
# ✅ PASS Assessment Detection (2/2 detections successful)
# ✅ PASS Questionnaire Response (Generated 2 responses)
# ✅ PASS Psychological Analysis (Big Five + MBTI analysis)
# ✅ PASS Report Generation (HTML report generated)
# 🎉 ALL TESTS PASSED!
```

## 🌐 Развертывание

### Вариант 1: Локальное Развертывание (Рекомендуется для Начинающих)

#### 1. Установить Ollama
```bash
# Windows (рекомендуется с Chocolatey)
choco install ollama

# Linux (с curl)
curl -fsSL https://ollama.ai/install.sh | sh

# macOS (с Homebrew)
brew install ollama
```

#### 2. Запустить Сервис Ollama
```bash
# Запустить сервис Ollama
ollama serve

# Открыть новый терминал, скачать рекомендованные модели
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

### Вариант 2: Облачное Развертывание (Рекомендуется для Профессионалов)

#### 1. Получить Ключи API

**Alibaba Cloud Tongyi Qianwen (DashScope)**
```bash
# Зарегистрироваться: https://bailian.console.aliyun.com/
# Получить ключ API
export DASHSCOPE_API_KEY=sk-your-api-key-here
```

**Anthropic Claude**
```bash
# Зарегистрироваться: https://console.anthropic.com/
# Получить ключ API
export ANTHROPIC_API_KEY=sk-ant-api-key-here
```

**OpenAI GPT**
```bash
# Зарегистрироваться: https://platform.openai.com/
# Получить ключ API
export OPENAI_API_KEY=sk-openai-key-here
```

#### 2. Настройка Переменных Окружения
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-your-api-key"
$env:ANTHROPIC_API_KEY="sk-ant-api-key"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-your-api-key"
export ANTHROPIC_API_KEY="sk-ant-api-key"
export OPENAI_API_KEY="sk-openai-key"
```

## 🚀 Базовое Использование

### 1. Индивидуальная Оценка
```bash
# Базовая оценка
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name enfj \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json

# Местоположение выходного файла
# results/assessment_<timestamp>_<model>_<role>.json
```

### 2. Пакетная Оценка
```bash
# Пакетная обработка нескольких ролей
python production_pipelines/local_batch_production/run_batch_suite.py \
    --model llama3.1 \
    --roles a1,a2,b1

# Посмотреть пакетные результаты
python production_pipelines/local_batch_production/cli.py analyze \
    --input results/latest_batch.json
```

### 3. Расширенная Конфигурация
```bash
# Установить температуру и параметры
python llm_assessment/run_assessment_unified.py \
    --model_name claude-3-5-sonnet \
    --role_name intj \
    --temperature 0.2 \
    --max_tokens 1000

# Использовать конкретный файл конфигурации
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --config_path configs/custom_assessment.json
```

## 🎨 Поддерживаемые Типы Оценки

### 1. Личность Большой Пятерки
```bash
# Соответствие шаблона файла: *big_five*, *personality*, *ocean*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-big-five-50-complete2.json
```

### 2. Гражданские Знания
```bash
# Соответствие шаблона файла: *citizenship*, *公民*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-citizenship-test.json
```

### 3. Финансовые Профессионалы
```bash
# Соответствие шаблона файла: *financial*, *金融*, *bank*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-fund-management-test.json
```

### 4. Юридические Знания
```bash
# Соответствие шаблона файла: *legal*, *law*, *法律*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-legal-test.json
```

### 5. Психология Мотивации
```bash
# Соответствие шаблона файла: *motivation*, *动机*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-motivation-test.json
```

### 6. Политическая Грамотность
```bash
# Соответствие шаблона файла: *political*, *政治*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-political-test.json
```

## 🔧 Быстрый Справочник Команд

### Базовые Команды
```bash
# Проверить статус системы
python test_end_to_end_complete.py

# Запустить быстрый тест
python run_local_batch.py --quick

# Посмотреть доступные модели
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_available_models.py
```

### Генерация Отчетов
```bash
# Сгенерировать HTML-отчеты
python generate_all_html_reports.py

# Посмотреть последние отчеты
ls html/ | tail -1
```

### Устранение Неполадок
```bash
# Проверить зависимости
pip check

# Проверить конфигурацию
python -c "import llm_assessment; print('✅ Импорт успешен')"

# Тестировать API-соединение
python quick_cloud_test.py
```

## ❓ Распространенные Вопросы

### В1: Как выбрать правильную модель?
**О**:
- **Локальные модели**: `llama3.1`, `mistral` - Быстрые, бесплатные, подходят для тестирования
- **Облачные модели**: `gpt-4o`, `claude-3-5-sonnet` - Высокое качество, требуют ключей API
- **Рекомендация**: Использовать локальные модели для разработки, облачные модели для производства

### В2: Где сохраняются результаты оценки?
**О**:
- Сырые результаты: `results/readonly-original/`
- Обработанные результаты: `results/ok/evaluated/`
- HTML-отчеты: `html/`
- Пакетные анализы: `results/final-*-batch-analysis/`

### В3: Как добавить новые типы оценки?
**О**:
1. Добавить новую JSON-конфигурацию в `.claude/skills/questionnaire-responder/configs/`
2. Запустить `python test_runner.py` для проверки конфигурации
3. Система автоматически обнаружит новые типы оценки

### В4: Что делать при недостаточной памяти?
**О**:
```bash
# Ограничить одновременные запросы
export MAX_CONCURRENT_REQUESTS=1

# Использовать меньшие модели
python llm_assessment/run_assessment_unified.py --model mistral

# Обрабатывать пакетами
python final_batch_processor.py --limit 5
```

### В5: Обработка сбоев вызов API?
**О**:
```bash
# Проверить ключи API
echo $OPENAI_API_KEY

# Тестировать соединение
python quick_cloud_test.py

# Использовать локальный резерв
export PROVIDER=local
```

## 🎯 Следующие Шаги

### 📚 Глубокое Изучение
- 📖 [Полное Руководство Пользователя](../../USER_MANUAL.md)
- 🏗️ [Документация Архитектуры Системы](ARCHITECTURE.md)
- 🔧 [Документация Справочника API](API_REFERENCE.md)

### 🚀 Расширенные Функции
- 🔌 [Руководство по Разработке Плагинов](PLUGIN_DEVELOPMENT.md)
- 📊 [Учебник по Пакетной Обработке](BATCH_PROCESSING.md)
- 🌐 [Руководство по Облачному Развертыванию](CLOUD_DEPLOYMENT.md)

### 🤝 Поддержка Сообщества
- 🐛 [Обратная связь по Проблемам](https://github.com/your-repo/issues)
- 💬 [Область Обсуждений](https://github.com/your-repo/discussions)
- 📧 [Поддержка по Email](mailto:support@example.com)

## 🎉 Контрольный Список Успеха

Выполните следующие шаги для указания успешной настройки:

- [ ] ✅ Настройка окружения завершена (Python 3.8+)
- [ ] ✅ Зависимости проекта успешно установлены
- [ ] ✅ Переменные окружения настроены правильно
- [ ] ✅ Тест пройден (`python test_runner.py`)
- [ ] ✅ Сгенерирован первый результат оценки
- [ ] ✅ Отображен HTML-отчет
- [ ] ✅ Попробованы разные типы оценки

**🎊 Поздравляем! Вы освоили базовое использование AgentPsyAssessment!**

---

**Версия**: v1.0.0
**Дата Обновления**: 2025-01-08
**Автор**: AgentPsyAssessment Team