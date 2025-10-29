# AgentPsy 技术亮点和架构说明

## 1. 系统架构

AgentPsy 采用模块化架构设计，主要分为以下几个核心模块：

### 1.1 核心服务层
- **LLMClient**：统一的LLM客户端，支持本地和云模型
- **ModelManager**：模型管理器，负责加载和管理不同模型
- **ModelService**：模型服务接口，为不同云服务提供统一接口

### 1.2 测评执行层
- **PromptBuilder**：提示构建器，负责构建包含压力因子的对话提示
- **StressInjector**：压力注入器，提供各种压力材料
- **ResponseExtractor**：响应提取器，从多轮对话中提取最终响应
- **SessionManager**：会话管理器，管理独立的测评会话

### 1.3 数据管理层
- **AssessmentLogger**：测评日志记录器，记录完整的测评过程
- **结果存储**：将测评结果保存为JSON文件，便于后续分析

### 1.4 分析层
- **分析模块**：提供多种测评结果分析工具
- **报告生成器**：生成Markdown和JSON格式的分析报告

## 2. 技术亮点

### 2.1 统一模型接口
AgentPsy 通过`ModelService`抽象类和`ModelManager`实现了统一的模型接口，支持多种本地和云模型：

```python
# ModelService抽象类
class ModelService(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def generate_response(self, model_id: str, messages: List[Dict[str, str]], options: Optional[Dict[str, Any]] = None) -> Optional[str]:
        pass

# 不同云服务的具体实现
class OpenRouterService(ModelService):
    # 实现OpenRouter特定的API调用

class GLMService(ModelService):
    # 实现GLM特定的API调用
```

这种设计使得系统可以轻松扩展支持新的模型服务，而无需修改核心代码。

### 2.2 压力测试框架
AgentPsy 实现了一个灵活的压力测试框架，支持多种压力因子的动态注入：

```python
class StressInjector:
    def __init__(self, trap_dir: str, context_dir: str):
        # 加载认知陷阱和上下文材料
        
    def get_trap(self, trap_type_abbr: str) -> str:
        # 获取指定类型的认知陷阱
        
    def get_context_filler(self, tokens: int) -> str:
        # 获取指定长度的上下文填充内容
        
    def get_emotional_prompt(self, level: int) -> str:
        # 获取指定等级的情感压力提示
```

通过`PromptBuilder`将这些压力因子动态注入到测评对话中，实现对模型的全面压力测试。

### 2.3 会话隔离机制
AgentPsy 使用`SessionManager`和`Session`类实现会话隔离，确保每个测评问题的独立性：

```python
class Session:
    def __init__(self, question_id: str, metadata: Dict[str, Any] = None):
        self.session_id = str(uuid.uuid4())  # 唯一会话ID
        self.question_id = question_id       # 问题ID
        self.conversation_history = []       # 独立的对话历史
        
class SessionManager:
    def create_session(self, question_id: str, metadata: Dict[str, Any] = None) -> Session:
        # 为每个问题创建独立会话
        
    def get_session(self, session_id: str) -> Optional[Session]:
        # 获取指定会话
```

这种机制确保了不同问题的测评过程不会相互干扰。

### 2.4 智能响应提取
`ResponseExtractor`类能够从复杂的多轮对话中智能提取最终的测评响应：

```python
class ResponseExtractor:
    ASSESSMENT_MARKER = "[ASSESSMENT_QUESTION]"
    
    def extract_final_response(self, conversation: List[Dict[str, Any]]) -> Optional[str]:
        # 通过标记和对话结构智能提取最终响应
        
    def add_assessment_marker(self, question: str) -> str:
        # 为问题添加标记，便于后续提取
```

### 2.5 完整的日志记录
`AssessmentLogger`提供了完整的测评过程日志记录功能：

```python
class AssessmentLogger:
    def log_complete_session(self, session_id: str, conversation: list, extracted_response: str, metadata: Dict[str, Any] = None):
        # 记录完整的会话信息
        
    def log_llm_interaction(self, session_id: str, prompt: str, response: str, metadata: Dict[str, Any] = None):
        # 记录LLM交互详情
```

### 2.6 批量处理能力
AgentPsy 支持通过配置文件进行批量测评：

```json
{
  "models_to_test": ["ollama/llama3:8b", "ollama/qwen2.5:7b"],
  "roles_to_test": ["default", "a1"],
  "interference_levels_to_test": [0, 1],
  "evaluation_suite": [
    {
      "test_name": "BigFive_Evaluation",
      "baseline_file": "agent-big-five-50-complete.json",
      "baseline_evaluators": ["gpt"]
    }
  ]
}
```

## 3. 扩展性设计

### 3.1 插件化测评模块
AgentPsy 的测评模块设计为插件化结构，可以轻松添加新的测评量表：

1. 创建新的测试文件（JSON格式）
2. 实现对应的分析脚本
3. 在批量配置中添加新的测评套件

### 3.2 可配置的压力因子
所有压力因子都通过配置文件或命令行参数进行控制，无需修改代码即可调整压力测试策略。

### 3.3 多语言支持
系统通过`i18n.py`模块提供国际化支持，可以轻松扩展支持更多语言。