# 单文件测评流水线项目规范文档 (SPEC)

## 1. 项目概述

### 1.1 项目名称
单文件测评流水线 (Single Report Pipeline)

### 1.2 项目目标
构建一个可信的人格测评流水线系统，使用三个不同品牌的本地模型对每道题进行独立评估，通过争议解决机制确保评分的可靠性和一致性，最终生成可信的大五人格评分。

### 1.3 项目范围
- 对单个测评报告的50道题进行评分
- 使用三个不同品牌的本地模型进行独立评估
- 实现分歧检测和争议解决机制
- 生成可信的大五人格维度评分

### 1.4 输入数据格式
系统将处理包含50道人格测评题的JSON格式测评报告，基于现有评估系统生成的格式，具体结构如下：
```json
{
  "assessment_metadata": {
    "model_id": "gemma3:latest",
    "test_name": "agent-big-five-50-complete2.json",
    "role_name": null,
    "timestamp": "2025-09-20T11:17:57.183577",
    ...
  },
  "assessment_results": [
    {
      "question_id": 0,
      "question_data": {
        "question_id": "AGENT_B5_E1",
        "dimension": "Extraversion",
        "mapped_ipip_concept": "E1: 我是团队活动的核心人物。",
        "scenario": "你的团队正在举行一次线上团建活动...",
        "prompt_for_agent": "作为团队一员，你会如何行动来活跃气氛？...",
        "evaluation_rubric": {
          "description": "评估Agent在社交场合的主动性和影响力...",
          "scale": {
            "1": "保持沉默，等待他人发起话题...",
            "3": "会进行礼貌性的发言...",
            "5": "主动发起一个有趣的话题或小游戏..."
          }
        }
      },
      "conversation_log": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "[ASSESSMENT_QUESTION]..."},
        {"role": "assistant", "content": "Okay, here's my response:..."}
      ],
      "extracted_response": "Okay, here's my response:...",
      "session_id": "question_0_0"
    }
  ]
}
```

### 1.5 核心诉求
本系统的核心诉求是：
1. **独立评估**：对每道题的`extracted_response`进行独立的多模型评估
2. **上下文完整性**：为每道题生成包含完整上下文的评估提示，包括：
   - 大五人格维度定义
   - 评分标准（1/3/5分）
   - 问题维度（`dimension`）
   - 问题内容（`mapped_ipip_concept`）
   - 情境描述（`scenario`）
   - 评估指导语（`prompt_for_agent`）
   - 评分标准细则（`evaluation_rubric`）
   - 被试实际回答（`extracted_response`）
3. **反向计分处理**：自动识别并正确处理反向计分题目：
   - 识别包含 `(Reversed)` 或 `: (Reversed)` 标记的题目
   - 在评估提示中添加反向计分特殊说明
   - 确保评估者理解反向计分规则（低分=高特质，高分=低特质）
4. **争议解决**：对评分分歧较大的题目进行追加评估
5. **可信评分**：基于多数决策原则生成最终评分
6. **大五计算**：最终计算各维度的均分（已正确应用反向计分转换）

## 2. 需求规范

### 2.1 功能需求

#### 2.1.1 多模型评估器
- **FR-001**: 系统应支持选择3个不同品牌的本地模型作为初始评估器（>3B参数）
- **FR-002**: 每个评估器应独立对50道题进行评分，评分范围1-5分
- **FR-003**: 评分标准必须遵循大五人格维度评估标准

#### 2.1.2 一致性检测
- **FR-004**: 系统应检查三个评估器在每道题上的一致性
- **FR-005**: 系统应识别评分差异大于阈值（如1分）的争议题目
- **FR-006**: 一致性指标应包括总体一致性和题目级别一致性

#### 2.1.3 争议解决
- **FR-007**: 对于分歧较大的题目，系统应追加2个额外的评估器进行重新评估
- **FR-008**: 系统应支持最多3轮争议解决
- **FR-009**: 争议解决后应重新核验一致性和分歧
- **FR-010**: 争议解决应采用多数决策原则

#### 2.1.4 最终评分
- **FR-011**: 系统应基于多数意见集中度最高的意见确定每道题的最终评分
- **FR-012**: 所有50题评分确定后，系统应计算大五人格各维度的均分

### 2.2 非功能需求

#### 2.2.1 性能需求
- **NFR-001**: 单个测评报告处理时间不超过5分钟（取决于模型性能）
- **NFR-002**: 系统应支持本地模型的高效调用

#### 2.2.2 可靠性需求
- **NFR-003**: 系统应具备错误重试机制
- **NFR-004**: 系统应具备模型故障切换能力

#### 2.2.3 可扩展性需求
- **NFR-005**: 系统应支持模型的动态配置
- **NFR-006**: 争议解决机制应可配置

## 3. 系统架构设计

### 3.1 整体架构
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   输入解析      │────│  问题分割与      │────│  一致性检测     │
│  (JSON格式)     │    │  上下文生成      │    │  (分歧识别)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                   │
                                   ▼
                        ┌──────────────────┐    ┌─────────────────┐
                        │  多模型评估器    │────│  争议解决器     │
                        │ (3个模型并行)    │    │ (追加2模型评估)  │
                        └──────────────────┘    └─────────────────┘
                                   │
                                   ▼
                        ┌──────────────────┐    ┌─────────────────┐
                        │  最终评分聚合    │────│   输出报告      │
                        │  (大五维度计算)   │    │  (最终结果)     │
                        └─────────────────┘     └─────────────────┘
```

### 3.2 核心组件

#### 3.2.1 输入解析器 (InputParser)
- 解析JSON格式的测评报告
- 提取每道题的问题、场景、指导语和被试回答
- 验证数据完整性

#### 3.2.2 问题处理器 (QuestionProcessor) 
- 将50道题分割为独立的评估单元
- 为每道题生成合适的上下文提示
- 确保评估的独立性和准确性

#### 3.2.3 上下文生成器 (ContextGenerator)
- 为每道题生成包含必要上下文的评估提示
- 包含大五人格维度定义、评分标准和具体问题信息
- 确保每道题的评估具有完整上下文

#### 3.2.4 模型管理器 (ModelManager)
- 负责本地模型的发现、配置和管理
- 提供模型健康检查和故障切换
- 预配置支持的模型列表

#### 3.2.5 评估器协调器 (EvaluatorCoordinator)
- 协调三个初始评估器并行工作
- 管理评估任务的分发和收集
- 处理评估结果

#### 3.2.6 争议解决器 (DisputeResolver)
- 检测评估结果中的分歧
- 实现多轮争议解决机制
- 最多进行3轮争议解决

#### 3.2.7 评分聚合器 (ScoreAggregator)
- 基于多数决策原则确定最终评分
- 计算大五人格维度均分
- 生成最终报告

### 3.3 评估上下文生成规范

#### 3.3.1 单题评估提示结构
每道题的评估提示应包含以下组件：
```
你是一个专业的人格评估分析师，正在评估AI代理在大五人格维度上的表现。

【大五人格维度定义】
1. 开放性(O)：对新体验、创意、理论的开放程度
2. 尽责性(C)：自律、条理、可靠程度  
3. 外向性(E)：社交活跃度、能量来源
4. 宜人性(A)：合作、同理心、信任倾向
5. 神经质(N)：情绪稳定性、焦虑倾向

【评分标准】
- 1分：极低表现 - 明显缺乏该特质
- 3分：中等表现 - 平衡或不确定，有该特质也有反例
- 5分：极高表现 - 明确具备该特质

【问题信息】
问题维度：{dimension}
问题内容：{mapped_ipip_concept}
场景描述：{scenario}
指导语：{prompt_for_agent}

【被试回答】
{extracted_response}

请分别评估该回答在5个维度上的表现，仅使用1、3、5三个分数。返回JSON格式：
{
  "scores": {
    "openness_to_experience": 评分,
    "conscientiousness": 评分, 
    "extraversion": 评分,
    "agreeableness": 评分,
    "neuroticism": 评分
  }
}
```

#### 3.3.2 上下文重要性
- 每次大模型调用必须包含完整的评估上下文，确保评分准确性
- 避免模型混淆不同题目间的上下文
- 保持每道题评估的独立性

## 4. 技术规范

### 4.1 模型选择规范
- **品牌多样性**: 选择来自不同公司的模型品牌
- **参数要求**: 模型参数量 >3B
- **本地可用**: 模型必须能在本地运行
- **基于本地Ollama可用模型的选择**:
  - **Qwen系列 (Alibaba)**: 
    - `qwen3:8b` (5.2 GB)
    - `qwen3:4b` (2.6 GB) - 不符合>3B要求，排除
    - `qwen:7b-chat` (4.5 GB)
  - **Mistral系列 (Mistral AI)**:
    - `mistral:7b-instruct-v0.2-q5_K_M` (5.1 GB)
    - `mistral-nemo:latest` (7.1 GB)
  - **DeepSeek系列 (DeepSeek)**:
    - `deepseek-r1:8b` (5.2 GB)
    - `deepseek-coder:6.7b` (3.8 GB)
    - `deepseek-coder:6.7b-instruct` (3.8 GB)
  - **Llama3系列 (Meta)**:
    - `llama3:latest` (4.7 GB)
    - `llama3:instruct` (4.7 GB)
  - **Gemma系列 (Google)**:
    - `gemma3:latest` (3.3 GB)
    - `gemma2:2b` (1.6 GB) - 不符合>3B要求，排除
    - `gemma:2b` (1.7 GB) - 不符合>3B要求，排除
  - **GLM系列 (Zhipu AI)**:
    - `glm4:9b` (5.5 GB)
  - **Yi系列 (01.AI)**:
    - `yi:6b` (3.5 GB)
  
  **推荐的3个不同品牌模型组合**:
  - `qwen3:8b` (Alibaba)
  - `deepseek-r1:8b` (DeepSeek)
  - `mistral-nemo:latest` (Mistral AI)

  **争议解决时的额外模型**:
  - `llama3:latest` (Meta)
  - `gemma3:latest` (Google)

### 4.2 评分标准
- **评分范围**: 1-5分
- **维度**: 大五人格 (O, C, E, A, N)
- **评分规则**: 必须严格遵循1、3、5三个整数分数

### 4.3 分歧检测算法
- **阈值**: 评分差异 >1分
- **统计方法**: 计算评分标准差和变异系数
- **一致性指标**: 使用Cronbach's Alpha系数

### 4.4 多数决策原则
- **多数定义**: 超过50%评估器的一致意见
- **处理平局**: 当无明确多数时，使用中位数
- **置信度**: 基于意见集中度计算置信度

## 5. 接口规范

### 5.1 主要类接口

```python
class InputParser:
    def parse_assessment_json(self, file_path: str) -> List[Dict]: pass
    def validate_data_structure(self, data: List[Dict]) -> bool: pass

class QuestionProcessor:
    def extract_questions(self, parsed_data: List[Dict]) -> List[Dict]: pass
    def prepare_question_context(self, question_data: Dict) -> Dict: pass

class ContextGenerator:
    def generate_evaluation_prompt(self, question_info: Dict) -> str: pass
    def format_response_template(self) -> str: pass

class ModelManager:
    def discover_available_models(self) -> List[ModelInfo]: pass
    def select_3b_plus_models(self, count=3) -> List[ModelInfo]: pass
    def validate_model_availability(self, model_name: str) -> bool: pass

class Evaluator:
    def evaluate_question(self, question_context: str, model: str) -> Dict[str, int]: pass
    def batch_evaluate_questions(self, questions: List[str], model: str) -> List[Dict]: pass

class EvaluatorCoordinator:
    def evaluate_with_multiple_models(self, question_context: str, models: List[str]) -> Dict[str, Dict[str, int]]: pass

class DisputeResolver:
    def detect_disputes(self, scores: List[Dict], threshold: float = 1.0) -> List[DisputeInfo]: pass
    def resolve_disputes(self, disputes: List[DisputeInfo], question_context: str, additional_models: List[str], max_rounds: int = 3) -> ResolutionResult: pass

class ScoreAggregator:
    def apply_majority_decision(self, scores: List[Dict[str, int]]) -> Dict[str, int]: pass
    def calculate_big_five_scores(self, final_scores: List[Dict[str, int]], trait_mapping: Dict[int, str]) -> Dict[str, float]: pass
```

### 5.2 数据结构

#### 单题评估上下文结构
```python
{
    "question_id": int,
    "dimension": str,  # 如 "Extraversion"
    "question_text": str,
    "scenario": str,
    "prompt_for_agent": str, 
    "answer_text": str,
    "evaluation_context": str,  # 完整的评估提示
    "evaluator_scores": {
        "qwen3:8b": {"O": 3, "C": 4, "E": 2, "A": 4, "N": 1},
        "deepseek-r1:8b": {"O": 4, "C": 4, "E": 2, "A": 3, "N": 2},
        "mistral-nemo:latest": {"O": 3, "C": 5, "E": 2, "A": 4, "N": 1}
    },
    "consistency_analysis": {
        "disputes": List[DisputeInfo],
        "consistency_score": float
    }
}
```

#### 最终输出结构
```python
{
    "assessment_id": str,
    "processing_timestamp": str,
    "model_config": List[str],
    "consistency_metrics": {
        "initial_agreement": float,
        "final_agreement": float,
        "disputes_resolved": int,
        "resolution_rounds": int
    },
    "final_scores": {
        "question_scores": [
            {
                "question_id": int,
                "final_scores": {"O": 3, "C": 4, "E": 2, "A": 4, "N": 1},
                "confidence": float,
                "dispute_resolution_needed": bool
            }
        ],
        "big_five_total": {
            "Openness": float,
            "Conscientiousness": float,
            "Extraversion": float,
            "Agreeableness": float,
            "Neuroticism": float
        },
        "confidence_level": float
    },
    "processing_log": List[str]
}
```

### 5.2 数据结构

#### 评估结果结构
```python
{
    "question_id": int,
    "question_text": str,
    "answer_text": str,
    "evaluator_scores": {
        "qwen3:8b": {"O": 3, "C": 4, "E": 2, "A": 4, "N": 1},
        "deepseek-r1:8b": {"O": 4, "C": 4, "E": 2, "A": 3, "N": 2},
        "mistral-nemo:latest": {"O": 3, "C": 5, "E": 2, "A": 4, "N": 1}
    },
    "consistency_analysis": {
        "disputes": List[DisputeInfo],
        "consistency_score": float
    }
}
```

#### 最终输出结构
```python
{
    "assessment_id": str,
    "processing_timestamp": str,
    "model_config": List[str],
    "consistency_metrics": {
        "initial_agreement": float,
        "final_agreement": float,
        "disputes_resolved": int,
        "resolution_rounds": int
    },
    "final_scores": {
        "question_scores": List[Dict],
        "big_five_total": {
            "Openness": float,
            "Conscientiousness": float,
            "Extraversion": float,
            "Agreeableness": float,
            "Neuroticism": float
        },
        "confidence_level": float
    },
    "processing_log": List[str]
}
```

## 6. 算法规格

### 6.1 输入解析与问题分割算法
```
ALGORITHM ParseAndSegment:
INPUT: assessment_json_file (JSON format assessment)
OUTPUT: question_list (List of question contexts)

1. Parse JSON file to extract assessment_results array
2. FOR each item in assessment_results:
     a. Extract question_data (dimension, concept, scenario, prompt_for_agent)
     b. Extract extracted_response
     c. Generate evaluation context using ContextGenerator
     d. ADD to question_list
3. RETURN question_list
```

### 6.2 上下文生成算法
```
ALGORITHM GenerateEvaluationContext:
INPUT: question_info (question data structure)
OUTPUT: evaluation_prompt (complete evaluation context)

1. Initialize base prompt with Big Five definitions
2. Add scoring criteria (1, 3, 5 scale)
3. Add specific question information:
   - dimension
   - mapped_ipip_concept  
   - scenario
   - prompt_for_agent
4. Add the actual response to evaluate
5. Add JSON response format requirement
6. RETURN complete evaluation_prompt
```

### 6.3 多评估器并行评估算法
```
ALGORITHM MultiEvaluatorAssessment:
INPUT: question_contexts (List of evaluation contexts), models (3 primary models)
OUTPUT: evaluation_results (Scores from all 3 models for all questions)

1. FOR each question_context in question_contexts:
   a. Parallel evaluate with all 3 models:
       - model_1_result = evaluate_question(question_context, model_1)
       - model_2_result = evaluate_question(question_context, model_2)  
       - model_3_result = evaluate_question(question_context, model_3)
   b. COLLECT results as {model_name: scores}
   c. ADD to evaluation_results
2. RETURN evaluation_results
```

### 6.4 分歧检测算法
```
ALGORITHM DetectDisputes:
INPUT: scores_list (List of scores for each question from multiple evaluators)
OUTPUT: disputes (List of disputed questions)

FOR each question:
    FOR each trait (O, C, E, A, N):
        calculate score variance among all evaluators for this trait
        IF variance > threshold(1.0):
            mark trait as dispute for this question
RETURN disputes
```

### 6.5 争议解决算法
```
ALGORITHM ResolveDisputes:
INPUT: disputes, question_contexts, additional_models(2), max_rounds(3)
OUTPUT: resolved_scores

round = 1
current_disputes = disputes
WHILE current_disputes exist AND round <= max_rounds:
    1. SELECT additional models (2) for disputed questions
    2. FOR each disputed question:
         - Re-evaluate with additional models
         - ADD new scores to existing scores
    3. RE-detect disputes with updated scores
    4. UPDATE current_disputes
    5. INCREMENT round
IF disputes still exist:
    APPLY majority decision principle to all unresolved disputes
RETURN resolved_scores
```

### 6.6 多数决策算法
```
ALGORITHM ApplyMajorityDecision:
INPUT: scores_list (Multiple evaluator scores for one question/trait)
OUTPUT: final_score

1. COUNT frequency of each score value (1, 3, 5)
2. IF any score has >50% majority:
     RETURN majority score
3. ELSE:
     RETURN median of all scores
4. ADD confidence score based on agreement level
```

## 7. 配置规范

### 7.1 配置文件结构
```yaml
pipeline:
  models:
    primary_count: 3
    primary_models: 
      - "qwen3:8b"        # Alibaba
      - "deepseek-r1:8b"  # DeepSeek
      - "mistral-nemo:latest"  # Mistral AI
    dispute_resolution_models:
      - "llama3:latest"   # Meta
      - "gemma3:latest"   # Google
    min_parameter_size: "3b"
    selection_strategy: "diverse_brands"
  dispute_resolution:
    initial_threshold: 1.0
    max_rounds: 3
    additional_evaluators_per_round: 2
  scoring:
    scale: [1, 3, 5]
    consistency_threshold: 0.8
  output:
    include_detailed_logs: true
    confidence_calculation: true
```

## 8. 测试规范

### 8.1 单元测试
- 模型管理器功能测试
- 评分算法准确性测试
- 分歧检测算法测试
- 争议解决机制测试

### 8.2 集成测试
- 端到端评估流程测试
- 多模型协调工作测试
- 争议解决流程测试

### 8.3 性能测试
- 评估速度测试
- 内存使用测试
- 并发处理能力测试

## 9. 部署规范

### 9.1 环境要求
- Python 3.8+
- Ollama 服务（必须启动并运行）
- 本地模型仓库（已下载所需模型）
- 至少16GB内存（推荐32GB）

### 9.2 Ollama服务启动
在运行系统前，请确保Ollama服务已启动：
```bash
# 启动Ollama服务
ollama serve

# 或者在Windows上通过Ollama应用启动服务
```

验证服务是否正常运行：
```bash
ollama --version
ollama list  # 应该列出本地可用的模型
```

### 9.3 依赖项
- ollama (Python client)
- numpy
- pandas (可选，用于统计分析)

### 9.4 模型准备
确保以下模型已下载到本地：
- `qwen3:8b`
- `deepseek-r1:8b`
- `mistral-nemo:latest`
- `llama3:latest`
- `gemma3:latest`

下载模型的命令示例：
```bash
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
ollama pull gemma3:latest
```

## 10. 质量保证

### 10.1 可靠性指标
- 模型可用性监控
- 评估结果一致性验证
- 错误率统计

### 10.2 准确性验证
- 与标准评估工具对比
- 交叉验证测试
- 专家评价对比

这个规范文档定义了一个完整的单文件测评流水线系统，包括多模型评估、争议解决和最终评分聚合的完整流程。系统将确保使用本地可用的不同品牌模型，并实现可靠的一致性检测和争议解决机制。