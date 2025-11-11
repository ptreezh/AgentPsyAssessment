# 统一评估技能系统实施任务清单

## 项目信息

**项目名称**: 统一评估技能系统 (Unified Assessment Skills System)
**项目版本**: v1.0.0
**创建日期**: 2025-01-08
**文档类型**: 原子化任务清单
**TDD驱动**: 是
**系统集成**: 支持

## 任务说明

本任务清单采用TDD（测试驱动开发）方法，每个任务都是原子化的，可以独立开发、测试和集成。任务按照依赖关系组织，确保系统集成的稳定性。

## 阶段一：基础设施搭建 (第1-2天)

### 1.1 配置文件系统建设

#### 任务 1.1.1: 创建配置目录结构
**优先级**: 🔴 高
**预估时间**: 0.1天
**依赖**: 无
**TDD**: 是

**测试先行**:
```python
# test_config_structure.py
import unittest
import os

class TestConfigStructure(unittest.TestCase):
    def setUp(self):
        self.config_dir = Path('.claude/skills/questionnaire-responder/configs')

    def test_config_directory_exists(self):
        """测试配置目录是否正确创建"""
        self.assertTrue(self.config_dir.exists())
        self.assertTrue(self.config_dir.is_dir())

    def test_config_subdirectories(self):
        """测试配置子目录结构"""
        expected_dirs = ['big_five', 'knowledge', 'professional', 'motivation', 'thinking']
        for dir_name in expected_dirs:
            dir_path = self.config_dir / dir_name
            self.assertTrue(dir_path.exists(), f"Missing directory: {dir_name}")
```

**实现任务**:
- [ ] 创建 `.claude/skills/questionnaire-responder/configs/` 目录
- [ ] 创建子目录结构 (big_five, knowledge, professional, motivation, thinking)
- [ ] 创建配置文件模板和示例

#### 任务 1.1.2: 配置文件加载器
**优先级**: 🔴 高
**预估时间**: 0.2天
**依赖**: 任务 1.1.1
**TDD**: 是

**测试先行**:
```python
# test_config_loader.py
import unittest
from unittest.mock import patch
import json

class TestConfigLoader(unittest.TestCase):
    def test_load_valid_config(self):
        """测试加载有效配置文件"""
        config_data = {
            "assessment_type": "big_five_personality",
            "name": "大五人格测评",
            "scoring_method": "rating_scale"
        }

        with patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            config = ConfigLoader.load_config('test_config.json')

        self.assertEqual(config['assessment_type'], 'big_five_personality')
        self.assertEqual(config['name'], '大五人格测评')

    def test_validate_config_schema(self):
        """测试配置文件模式验证"""
        valid_config = {
            "assessment_type": "test_type",
            "name": "Test Assessment",
            "description": "Test Description",
            "scoring_method": "rating_scale",
            "dimensions": ["dim1", "dim2"]
        }

        self.assertTrue(ConfigLoader.validate_config(valid_config))

        invalid_config = {"assessment_type": "test_type"}  # 缺少必需字段
        self.assertFalse(ConfigLoader.validate_config(invalid_config))
```

**实现任务**:
- [ ] 实现 `ConfigLoader` 类
- [ ] 支持 JSON 配置文件加载
- [ ] 实现配置文件验证和模式检查
- [ ] 添加配置文件缓存机制

#### 任务 1.1.3: 配置验证工具
**优先级**: 🟡 中
**预估时间**: 0.2天
**依赖**: 任务 1.1.2
**TDD**: 是

**测试先行**:
```python
# test_config_validator.py
import unittest

class TestConfigValidator(unittest.TestCase):
    def test_validate_all_configs(self):
        """验证所有配置文件的完整性"""
        validator = ConfigValidator()
        results = validator.validate_all_configs()

        self.assertEqual(len(results['valid']), 6)  # 6个有效配置
        self.assertEqual(len(results['invalid']), 0)

    def test_config_completeness(self):
        """测试配置文件完整性"""
        validator = ConfigValidator()
        completeness = validator.check_completeness('big_five_personality.json')

        self.assertTrue(completeness['has_required_fields'])
        self.assertTrue(completeness['has_valid_dimensions'])
        self.assertTrue(completeness['has_valid_scoring_method'])
```

**实现任务**:
- [ ] 实现 `ConfigValidator` 类
- [ ] 验证所有必需配置文件存在
- [ ] 检查配置文件完整性和一致性
- [ ] 提供配置修复建议

### 1.2 测评类型检测器

#### 任务 1.2.1: 文件内容分析器
**优先级**: 🔴 高
**预估时间**: 0.3天
**依赖**: 任务 1.1.1
**TDD**: 是

**测试先行**:
```python
# test_content_analyzer.py
import unittest

class TestContentAnalyzer(unittest.TestCase):
    def test_analyze_big_five_content(self):
        """测试大五人格内容分析"""
        content = {
            "questionnaire_info": {"title": "Big Five Personality Assessment"},
            "test_bank": [
                {"question": "I am always prepared", "dimension": "C"},
                {"question": "I have a vivid imagination", "dimension": "O"}
            ]
        }

        analyzer = ContentAnalyzer()
        result = analyzer.analyze_content(content)

        self.assertEqual(result['detected_type'], 'big_five_personality')
        self.assertGreaterEqual(result['confidence'], 0.8)

    def test_analyze_knowledge_content(self):
        """测试知识类内容分析"""
        content = {
            "questionnaire_info": {"title": "Citizenship Knowledge Test"},
            "test_bank": [
                {"question": "中国的首都是哪里？", "answer": "北京"},
                {"question": "四大发明是什么？", "answer": "造纸术、指南针、火药、印刷术"}
            ]
        }

        analyzer = ContentAnalyzer()
        result = analyzer.analyze_content(content)

        self.assertEqual(result['detected_type'], 'citizenship_knowledge')
        self.assertGreaterEqual(result['confidence'], 0.7)
```

**实现任务**:
- [ ] 实现 `ContentAnalyzer` 类
- [ ] 基于关键词的模式识别
- [ ] 基于结构的类型推断
- [ ] 置信度计算算法

#### 任务 1.2.2: 类型检测器
**优先级**: 🔴 高
**预估时间**: 0.2天
**依赖**: 任务 1.2.1, 任务 1.1.2
**TDD**: 是

**测试先行**:
```python
# test_type_detector.py
import unittest

class TestTypeDetector(unittest.TestCase):
    def test_auto_detect_assessment_type(self):
        """测试自动测评类型检测"""
        detector = TypeDetector()

        # 测试大五人格检测
        big_five_result = detector.detect_type('test_file.json')
        self.assertEqual(big_five_result['type'], 'big_five_personality')
        self.assertGreater(big_five_result['confidence'], 0.8)

        # 测试知识类检测
        knowledge_result = detector.detect_type('knowledge_test.json')
        self.assertEqual(knowledge_result['type'], 'citizenship_knowledge')
        self.assertGreater(knowledge_result['confidence'], 0.7)

    def test_type_detection_with_low_confidence(self):
        """测试低置信度类型检测"""
        detector = TypeDetector()
        result = detector.detect_type('ambiguous_file.json')

        self.assertEqual(result['type'], 'unknown')
        self.assertLess(result['confidence'], 0.5)
```

**实现任务**:
- [ ] 实现 `TypeDetector` 类
- [ ] 集成内容分析器和配置加载器
- [ ] 多种检测策略融合
- [ ] 置信度阈值管理

### 1.3 技能基础架构重构

#### 任务 1.3.1: 抽象基类设计
**优先级**: 🔴 高
**预估时间**: 0.3天
**依赖**: 任务 1.1.2
**TDD**: 是

**测试先行**:
```python
# test_base_responder.py
import unittest

class TestBaseResponder(unittest.TestCase):
    def test_base_responder_interface(self):
        """测试基类接口定义"""
        # 创建具体实现类
        class TestResponder(BaseResponder):
            def _generate_response(self, question, config):
                return "test response"

        responder = TestResponder()

        # 测试必须实现的方法
        self.assertTrue(hasattr(responder, 'generate_response'))
        self.assertTrue(callable(responder.generate_response))

    def test_base_responder_config_handling(self):
        """测试基类配置处理"""
        class TestResponder(BaseResponder):
            def _generate_response(self, question, config):
                return f"Response for {config.get('name', 'unknown')}"

        responder = TestResponder()
        config = {"name": "Test Config", "assessment_type": "test"}

        result = responder.generate_response("test question", config)
        self.assertEqual(result, "Response for Test Config")
```

**实现任务**:
- [ ] 设计 `BaseResponder` 抽象基类
- [ ] 定义统一的接口规范
- [ ] 实现配置处理机制
- [ ] 添加错误处理和日志记录

#### 任务 1.3.2: 响应器工厂
**优先级**: 🔴 高
**预估时间**: 0.2天
**依赖**: 任务 1.3.1, 任务 1.2.2
**TDD**: 是

**测试先行**:
```python
# test_responder_factory.py
import unittest

class TestResponderFactory(unittest.TestCase):
    def test_create_responder_by_type(self):
        """测试根据类型创建响应器"""
        factory = ResponderFactory()

        # 测试大五人格响应器
        big_five_responder = factory.create_responder('big_five_personality')
        self.assertIsInstance(big_five_responder, BigFiveResponder)

        # 测试知识响应器
        knowledge_responder = factory.create_responder('citizenship_knowledge')
        self.assertIsInstance(knowledge_responder, KnowledgeResponder)

    def test_factory_with_unknown_type(self):
        """测试未知类型的处理"""
        factory = ResponderFactory()

        with self.assertRaises(ValueError):
            factory.create_responder('unknown_type')

    def test_factory_caching(self):
        """测试响应器缓存机制"""
        factory = ResponderFactory()

        # 第一次创建
        responder1 = factory.create_responder('big_five_personality')
        # 第二次创建（应该使用缓存）
        responder2 = factory.create_responder('big_five_personality')

        self.assertIs(responder1, responder2)
```

**实现任务**:
- [ ] 实现 `ResponderFactory` 工厂类
- [ ] 支持类型到响应器的映射
- [ ] 实现响应器缓存机制
- [ ] 添加类型验证和错误处理

#### 任务 1.3.3: 现有功能兼容性
**优先级**: 🔴 高
**预估时间**: 0.2天
**依赖**: 任务 1.3.2
**TDD**: 是

**测试先行**:
```python
# test_compatibility.py
import unittest

class TestBackwardCompatibility(unittest.TestCase):
    def test_existing_api_compatibility(self):
        """测试现有API兼容性"""
        # 测试原有接口仍然可用
        responder = QuestionnaireResponder()

        # 测试原有方法
        self.assertTrue(hasattr(responder, 'generate_responses'))
        self.assertTrue(callable(responder.generate_responses))

        # 测试原有参数格式
        result = responder.generate_responses(
            questionnaire_file='test.json',
            persona='ENFJ',
            stress_level='moderate'
        )

        self.assertIsInstance(result, dict)
        self.assertIn('response_info', result)

    def test_extended_api_functionality(self):
        """测试扩展API功能"""
        responder = QuestionnaireResponder()

        # 测试新参数
        result = responder.generate_responses(
            questionnaire_file='test.json',
            persona='ENFJ',
            assessment_type='big_five_personality',
            temperature='moderate'
        )

        self.assertIsInstance(result, dict)
        self.assertIn('assessment_type', result)
```

**实现任务**:
- [ ] 保持现有API接口不变
- [ ] 添加新的可选参数支持
- [ ] 实现向后兼容性检查
- [ ] 更新文档和示例

## 阶段二：核心功能实现 (第3-4天)

### 2.1 Questionnaire Responder 扩展

#### 任务 2.1.1: Big Five 响应器扩展
**优先级**: 🔴 高
**预估时间**: 0.3天
**依赖**: 任务 1.3.3
**TDD**: 是

**测试先行**:
```python
# test_big_five_responder.py
import unittest

class TestBigFiveResponder(unittest.TestCase):
    def test_generate_big_five_response(self):
        """测试大五人格响应生成"""
        responder = BigFiveResponder()
        question = {
            "question": "I am always prepared for every situation",
            "dimension": "C"
        }
        config = {"assessment_type": "big_five_personality"}

        result = responder._generate_response(question, config)

        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 10)

    def test_dimension_specific_response(self):
        """测试维度特定的响应逻辑"""
        responder = BigFiveResponder()

        # 测试尽责性维度
        c_question = {"question": "I pay attention to details", "dimension": "C"}
        c_result = responder._generate_response(c_question, {})
        self.assertIn("仔细", c_result.lower()) or self.assertIn("认真", c_result.lower())

        # 测试开放性维度
        o_question = {"question": "I enjoy trying new things", "dimension": "O"}
        o_result = responder._generate_response(o_question, {})
        self.assertIn("新鲜", o_result.lower()) or self.assertIn("尝试", o_result.lower())
```

**实现任务**:
- [ ] 扩展现有16种MBTI人格支持
- [ ] 实现职业化场景应答逻辑
- [ ] 添加压力测试和参数影响模拟
- [ ] 优化应答质量和一致性

#### 任务 2.1.2: 知识应答器
**优先级**: 🔴 高
**预估时间**: 0.3天
**依赖**: 任务 1.3.3
**TDD**: 是

**测试先行**:
```python
# test_knowledge_responder.py
import unittest

class TestKnowledgeResponder(unittest.TestCase):
    def test_generate_knowledge_response(self):
        """测试知识类响应生成"""
        responder = KnowledgeResponder()
        question = {
            "question": "中国的首都是哪里？",
            "dimension": "geography"
        }
        config = {"assessment_type": "citizenship_knowledge"}

        result = responder._generate_response(question, config)

        self.assertIn("北京", result)
        self.assertGreater(len(result), 5)

    def test_keyword_matching_accuracy(self):
        """测试关键词匹配准确性"""
        responder = KnowledgeResponder()

        # 测试地理知识
        geo_question = {"question": "中国的四大发明有哪些？"}
        geo_result = responder._generate_response(geo_question, {})

        keywords = ["造纸术", "指南针", "火药", "印刷术"]
        matched_count = sum(1 for kw in keywords if kw in geo_result)
        self.assertGreaterEqual(matched_count, 3)

    def test_domain_specific_knowledge(self):
        """测试领域特定知识"""
        responder = KnowledgeResponder()

        # 测试金融知识
        finance_question = {"question": "什么是股票？"}
        finance_result = responder._generate_response(finance_question, {"domain": "finance"})
        self.assertIn("股票", finance_result)
        self.assertIn("投资", finance_result) or self.assertIn("证券", finance_result)
```

**实现任务**:
- [ ] 实现公民知识应答逻辑
- [ ] 实现金融知识应答逻辑
- [ ] 实现法律知识应答逻辑
- [ ] 优化关键词匹配和准确性

#### 任务 2.1.3: 专业应答器
**优先级**: 🟡 中
**预估时间**: 0.3天
**依赖**: 任务 1.3.3
**TDD**: 是

**测试先行**:
```python
# test_professional_responder.py
import unittest

class TestProfessionalResponder(unittest.TestCase):
    def test_generate_professional_response(self):
        """测试专业类响应生成"""
        responder = ProfessionalResponder()
        question = {
            "question": "如何评估投资风险？",
            "domain": "investment"
        }
        config = {"assessment_type": "financial_professional"}

        result = responder._generate_response(question, config)

        self.assertIn("风险评估", result.lower())
        self.assertIn("风险管理", result.lower())
        self.assertGreater(len(result), 20)

    def test_compliance_awareness(self):
        """测试合规意识体现"""
        responder = ProfessionalResponder()

        # 测试合规相关问题
        compliance_question = {"question": "如何确保交易合规？"}
        compliance_result = responder._generate_response(compliance_question, {})

        compliance_terms = ["合规", "监管", "法律", "规定"]
        compliance_count = sum(1 for term in compliance_terms if term in compliance_result)
        self.assertGreaterEqual(compliance_count, 2)

    def test_risk_management_focus(self):
        """测试风险管理重点"""
        responder = ProfessionalResponder()

        risk_question = {"question": "投资失败后应该怎么办？"}
        risk_result = responder._generate_response(risk_question, {})

        risk_terms = ["止损", "反思", "学习", "调整"]
        risk_count = sum(1 for term in risk_terms if term in risk_result)
        self.assertGreaterEqual(risk_count, 2)
```

**实现任务**:
- [ ] 实现专业标准应答框架
- [ ] 添加风险管理和合规意识体现
- [ ] 实现实务经验模拟
- [ ] 支持多种专业领域

#### 任务 2.1.4: 动机应答器
**优先级**: 🟡 中
**预估时间**: 0.3天
**依赖**: 任务 1.3.3
**TDD**: 是

**测试先行**:
```python
# test_motivation_responder.py
import unittest

class TestMotivationResponder(unittest.TestCase):
    def test_generate_motivation_response(self):
        """测试动机类响应生成"""
        responder = MotivationResponder()
        question = {
            "question": "什么能激励你努力工作？",
            "motivation_type": "achievement"
        }
        config = {"assessment_type": "motivation_psychology"}

        result = responder._generate_response(question, config)

        self.assertIn("成就", result.lower())
        self.assertIn("激励", result.lower())
        self.assertGreater(len(result), 15)

    def test_eight_motivation_types(self):
        """测试8种动机类型支持"""
        responder = MotivationResponder()

        motivation_types = [
            "achievement", "affiliation", "power", "autonomy",
            "security", "social", "competence", "growth"
        ]

        for mot_type in motivation_types:
            question = {"question": f"What drives your {mot_type}?", "motivation_type": mot_type}
            result = responder._generate_response(question, {})
            self.assertGreater(len(result), 10)

    def test_intrinsic_motivation_emphasis(self):
        """测试内在动机强调"""
        responder = MotivationResponder()

        intrinsic_question = {"question": "你为什么选择这个工作？"}
        intrinsic_result = responder._generate_response(intrinsic_question, {})

        intrinsic_terms = ["兴趣", "热情", "意义", "价值", "内在"]
        intrinsic_count = sum(1 for term in intrinsic_terms if term in intrinsic_result)
        self.assertGreaterEqual(intrinsic_count, 2)
```

**实现任务**:
- [ ] 实现8种动机类型应答逻辑
- [ ] 实现情景化动机测试设计
- [ ] 优化内在动机表达
- [ ] 添加动机强度评估

#### 任务 2.1.5: 思维应答器
**优先级**: 🟡 中
**预估时间**: 0.3天
**依赖**: 任务 1.3.3
**TDD**: 是

**测试先行**:
```python
# test_thinking_responder.py
import unittest

class TestThinkingResponder(unittest.TestCase):
    def test_generate_thinking_response(self):
        """测试思维类响应生成"""
        responder = ThinkingResponder()
        question = {
            "question": "如何看待这个社会问题？",
            "thinking_type": "critical"
        }
        config = {"assessment_type": "political_literacy"}

        result = responder._generate_response(question, config)

        self.assertIn("多角度", result.lower()) or self.assertIn("分析", result.lower())
        self.assertGreater(len(result), 20)

    def test_multiple_perspectives(self):
        """测试多角度思考"""
        responder = ThinkingResponder()

        perspective_question = {"question": "如何评价这项政策？"}
        perspective_result = responder._generate_response(perspective_question, {})

        perspective_indicators = ["一方面", "另一方面", "从...角度看", "综合考虑"]
        perspective_count = sum(1 for indicator in perspective_indicators if indicator in perspective_result)
        self.assertGreaterEqual(perspective_count, 1)

    def test_critical_thinking_elements(self):
        """测试批判性思维要素"""
        responder = ThinkingResponder()

        critical_question = {"question": "这个推理有什么问题？"}
        critical_result = responder._generate_response(critical_question, {})

        critical_terms = ["逻辑", "假设", "证据", "推理", "分析"]
        critical_count = sum(1 for term in critical_terms if term in critical_result)
        self.assertGreaterEqual(critical_count, 2)
```

**实现任务**:
- [ ] 实现多角度思考应答框架
- [ ] 添加批判性思维体现
- [ ] 实现政治素养和公民意识
- [ ] 支持平衡理性分析

### 2.2 配置文件创建

#### 任务 2.2.1: Big Five 配置文件
**优先级**: 🟡 中
**预估时间**: 0.1天
**依赖**: 任务 1.1.1
**TDD**: 是

**测试先行**:
```python
# test_big_five_config.py
import unittest

class TestBigFiveConfig(unittest.TestCase):
    def test_config_file_exists(self):
        """测试配置文件存在"""
        config_path = Path('.claude/skills/questionnaire-responder/configs/big_five/big_five_personality.json')
        self.assertTrue(config_path.exists())

    def test_config_content_validation(self):
        """测试配置内容验证"""
        config = ConfigLoader.load_config('big_five_personality.json')

        required_fields = ['assessment_type', 'name', 'description', 'scoring_method', 'dimensions']
        for field in required_fields:
            self.assertIn(field, config, f"Missing required field: {field}")

        self.assertEqual(config['assessment_type'], 'big_five_personality')
        self.assertEqual(config['scoring_method'], 'rating_scale')
```

**实现任务**:
- [ ] 创建 `big_five_personality.json` 配置文件
- [ ] 定义OCEAN维度和评分标准
- [ ] 配置MBTI映射规则
- [ ] 验证配置文件正确性

#### 任务 2.2.2: 知识类配置文件
**优先级**: 🟡 中
**预估时间**: 0.1天
**依赖**: 任务 2.2.1
**TDD**: 是

**实现任务**:
- [ ] 创建 `citizenship_knowledge.json` 配置文件
- [ ] 创建 `financial_professional.json` 配置文件
- [ ] 创建 `legal_knowledge.json` 配置文件
- [ ] 定义知识域和评分标准

#### 任务 2.2.3: 心理类配置文件
**优先级**: 🟡 中
**预估时间**: 0.1天
**依赖**: 任务 2.2.2
**TDD**: 是

**实现任务**:
- [ ] 创建 `motivation_psychology.json` 配置文件
- [ ] 创建 `political_literacy.json` 配置文件
- [ ] 定义心理维度和评估标准
- [ ] 验证配置文件正确性

### 2.3 Psychological Analyzer 扩展

#### 任务 2.3.1: 分析器架构重构
**优先级**: 🔴 高
**预估时间**: 0.3天
**依赖**: 任务 2.1.5
**TDD**: 是

**测试先行**:
```python
# test_analyzer_architecture.py
import unittest

class TestAnalyzerArchitecture(unittest.TestCase):
    def test_base_analyzer_interface(self):
        """测试分析器基类接口"""
        # 创建具体实现类
        class TestAnalyzer(BaseAnalyzer):
            def _analyze_question(self, question, config):
                return {"scores": {"test": 3}}

        analyzer = TestAnalyzer()

        # 测试必须实现的方法
        self.assertTrue(hasattr(analyzer, 'analyze_question'))
        self.assertTrue(callable(analyzer.analyze_question))

    def test_analyzer_factory(self):
        """测试分析器工厂"""
        factory = AnalyzerFactory()

        # 测试创建大五人格分析器
        big_five_analyzer = factory.create_analyzer('big_five_personality')
        self.assertIsInstance(big_five_analyzer, BigFiveAnalyzer)

        # 测试创建知识分析器
        knowledge_analyzer = factory.create_analyzer('citizenship_knowledge')
        self.assertIsInstance(knowledge_analyzer, KnowledgeAnalyzer)
```

**实现任务**:
- [ ] 设计 `BaseAnalyzer` 抽象基类
- [ ] 创建分析器工厂类
- [ ] 实现分析器接口规范
- [ ] 添加分析器缓存机制

#### 任务 2.3.2: Big Five 分析器
**优先级**: 🔴 高
**预估时间**: 0.3天
**依赖**: 任务 2.3.1
**TDD**: 是

**测试先行**:
```python
# test_big_five_analyzer.py
import unittest

class TestBigFiveAnalyzer(unittest.TestCase):
    def test_analyze_ocean_scores(self):
        """测试OCEAN维度评分分析"""
        analyzer = BigFiveAnalyzer()
        question = {
            "question": "I am always prepared",
            "response": "I always make sure to prepare in advance",
            "dimension": "C"
        }

        result = analyzer._analyze_question(question, {})

        self.assertIn('scores', result)
        self.assertIn('C', result['scores'])
        self.assertIsInstance(result['scores']['C'], (int, float))
        self.assertTrue(1 <= result['scores']['C'] <= 5)

    def test_mbti_mapping_accuracy(self):
        """测试MBTI映射准确性"""
        analyzer = BigFiveAnalyzer()

        # 高外向性应该映射到E型
        high_e_scores = {"E": 4.5, "I": 2.0, "S": 2.0, "N": 3.0, "C": 3.0}
        mbti_result = analyzer._infer_mbti_type(high_e_scores)
        self.assertEqual(mbti_result['mbti_type'][0], 'E')

        # 高开放性应该映射到N型
        high_o_scores = {"O": 4.5, "C": 3.0, "E": 3.0, "A": 3.0, "N": 3.0}
        mbti_result = analyzer._infer_mbti_type(high_o_scores)
        self.assertEqual(mbti_result['mbti_type'][1], 'N')
```

**实现任务**:
- [ ] 实现OCEAN维度评分算法
- [ ] 优化MBTI类型映射算法
- [ ] 实现贝尔宾角色映射
- [ ] 添加评分一致性检查

#### 任务 2.3.3: 知识分析器
**优先级**: 🔴 高
**预估时间**: 0.3天
**依赖**: 任务 2.3.1
**TDD**: 是

**测试先行**:
```python
# test_knowledge_analyzer.py
import unittest

class TestKnowledgeAnalyzer(unittest.TestCase):
    def test_keyword_matching_scoring(self):
        """测试关键词匹配评分"""
        analyzer = KnowledgeAnalyzer()
        question = {
            "question": "中国的四大发明是什么？",
            "response": "中国的四大发明是造纸术、指南针、火药和印刷术",
            "expected_keywords": ["造纸术", "指南针", "火药", "印刷术"]
        }

        result = analyzer._analyze_question(question, {})

        self.assertIn('scores', result)
        self.assertIn('accuracy', result)
        self.assertGreaterEqual(result['accuracy'], 0.75)  # 至少匹配75%的关键词

    def test_domain_knowledge_structure(self):
        """测试领域知识结构分析"""
        analyzer = KnowledgeAnalyzer()

        # 测试地理知识结构
        geography_questions = [
            {"question": "首都是哪里？", "response": "北京", "domain": "geography"},
            {"question": "最长的河流是什么？", "response": "长江", "domain": "geography"}
        ]

        structure_result = analyzer._analyze_knowledge_structure(geography_questions)
        self.assertIn('geography', structure_result)
        self.assertGreaterEqual(structure_result['geography']['correct_count'], 1)
```

**实现任务**:
- [ ] 实现关键词匹配算法
- [ ] 实现准确性评分计算
- [ ] 实现知识结构分析
- [ ] 添加完整性评估

#### 任务 2.3.4: 专业分析器
**优先级**: 🟡 中
**预估时间**: 0.3天
**依赖**: 任务 2.3.1
**TDD**: 是

**测试先行**:
```python
# test_professional_analyzer.py
import unittest

class TestProfessionalAnalyzer(unittest.TestCase):
    def test_professional_competency_scoring(self):
        """测试专业能力评分"""
        analyzer = ProfessionalAnalyzer()
        question = {
            "question": "如何评估投资项目的风险？",
            "response": "需要考虑市场风险、信用风险、流动性风险等多个维度，并制定相应的风险控制措施",
            "domain": "investment"
        }

        result = analyzer._analyze_question(question, {})

        self.assertIn('scores', result)
        self.assertIn('competency_level', result)
        self.assertGreaterEqual(result['competency_level'], 3.0)

    def test_risk_assessment_analysis(self):
        """测试风险评估分析"""
        analyzer = ProfessionalAnalyzer()

        risk_response = "投资有风险，需要进行充分的风险评估，包括市场风险、信用风险、流动性风险等"
        risk_score = analyzer._assess_risk_awareness(risk_response)

        self.assertGreaterEqual(risk_score, 0.7)  # 显示良好的风险意识

        low_risk_response = "投资没什么风险，直接投就行了"
        low_risk_score = analyzer._assess_risk_awareness(low_risk_response)
        self.assertLessEqual(low_risk_score, 0.5)  # 风险意识不足
```

**实现任务**:
- [ ] 实现专业能力评分框架
- [ ] 实现风险评估算法
- [ ] 实现合规意识评估
- [ ] 添加专业标准参照

#### 任务 2.3.5: 动机分析器
**优先级**: 🟡 中
**预估时间**: 0.3天
**依赖**: 任务 2.3.1
**TDD**: 是

**测试先行**:
```python
# test_motivation_analyzer.py
import unittest

class TestMotivationAnalyzer(unittest.TestCase):
    def test_motivation_type_identification(self):
        """测试动机类型识别"""
        analyzer = MotivationAnalyzer()
        question = {
            "question": "我努力工作是为了获得成就感",
            "response": "通过克服挑战来实现自我价值"
        }

        result = analyzer._analyze_question(question, {})

        self.assertIn('primary_motivation', result)
        self.assertEqual(result['primary_motivation'], 'achievement')
        self.assertGreater(result['motivation_strength'], 0.7)

    def test_motivation_structure_analysis(self):
        """测试动机结构分析"""
        analyzer = MotivationAnalyzer()

        multiple_responses = [
            {"response": "我既想获得成就，也希望有良好的人际关系"},
            {"response": "工作应该有意义，同时也要有合理的报酬"}
        ]

        structure = analyzer._analyze_motivation_structure(multiple_responses)

        self.assertIn('dominant_motivation', structure)
        self.assertIn('secondary_motivations', structure)
        self.assertGreaterEqual(len(structure['secondary_motivations']), 1)
```

**实现任务**:
- [ ] 实现8种动机类型识别算法
- [ ] 实现动机强度评估
- [ ] 实现动机结构分析
- [ ] 添加职业倾向预测

### 2.4 集成测试和验证

#### 任务 2.4.1: 端到端集成测试
**优先级**: 🔴 高
**预估时间**: 0.5天
**依赖**: 任务 2.3.5
**TDD**: 是

**测试先行**:
```python
# test_end_to_end_integration.py
import unittest

class TestEndToEndIntegration(unittest.TestCase):
    def test_big_five_assessment_flow(self):
        """测试大五人格评估完整流程"""
        # 1. 问卷应答
        responder = QuestionnaireResponder()
        response_result = responder.generate_responses(
            'test_big_five.json', 'ENFJ', 'big_five_personality'
        )

        self.assertIn('response_info', response_result)
        self.assertEqual(response_result['response_info']['persona'], 'ENFJ')

        # 2. 评估分析
        analyzer = PsychologicalAnalyzer()
        analyzer.start_evaluation_session(5, 'test_session')

        for response in response_result['responses']:
            analysis_result = analyzer.evaluate_single_question(response)
            self.assertIn('scores', analysis_result)

        final_result = analyzer.complete_evaluation()
        self.assertIn('big_five_results', final_result)
        self.assertIn('mbti_analysis', final_result)

        # 3. 报告生成
        generator = EvaluationReportGenerator()
        report_file = generator.generate_comprehensive_report(final_result)

        self.assertTrue(Path(report_file).exists())
        self.assertTrue(report_file.endswith('.html'))

    def test_knowledge_assessment_flow(self):
        """测试知识类评估完整流程"""
        # 测试公民知识评估流程
        # (类似大五人格流程的测试，但针对知识类)
        pass
```

**实现任务**:
- [ ] 编写6种测评类型的端到端测试
- [ ] 验证自动类型识别准确性
- [ ] 测试数据流转的正确性
- [ ] 验证输出结果的质量

#### 任务 2.4.2: 性能基准测试
**优先级**: 🟡 中
**预估时间**: 0.5天
**依赖**: 任务 2.4.1
**TDD**: 是

**测试先行**:
```python
# test_performance_benchmarks.py
import unittest
import time

class TestPerformanceBenchmarks(unittest.TestCase):
    def test_response_generation_performance(self):
        """测试响应生成性能基准"""
        responder = QuestionnaireResponder()

        start_time = time.time()
        result = responder.generate_responses(
            'test_file.json', 'ENFJ', 'big_five_personality'
        )
        end_time = time.time()

        generation_time = end_time - start_time
        self.assertLess(generation_time, 5.0)  # 目标：小于5秒

    def test_analysis_performance(self):
        """测试分析性能基准"""
        analyzer = PsychologicalAnalyzer()
        analyzer.start_evaluation_session(10, 'test_session')

        start_time = time.time()
        for i in range(10):
            question = {"question": f"Test question {i+1}", "response": "Test response"}
            analyzer.evaluate_single_question(question)
        end_time = time.time()

        analysis_time = end_time - start_time
        self.assertLess(analysis_time, 2.0)  # 目标：平均每个问题小于0.2秒

    def test_report_generation_performance(self):
        """测试报告生成性能基准"""
        generator = EvaluationReportGenerator()

        test_data = self._create_test_evaluation_data()

        start_time = time.time()
        report_file = generator.generate_comprehensive_report(test_data)
        end_time = time.time()

        generation_time = end_time - start_time
        self.assertLess(generation_time, 10.0)  # 目标：小于10秒
```

**实现任务**:
- [ ] 建立性能基准测试套件
- [ ] 测试响应生成时间目标（< 5秒）
- [ ] 测试分析处理时间目标（< 2秒）
- [ ] 测试报告生成时间目标（< 10秒）

## 阶段三：报告系统实现 (第5天)

### 3.1 Evaluation Report Generator 扩展

#### 任务 3.1.1: 报告模板系统
**优先级**: 🔴 高
**预估时间**: 0.3天
**依赖**: 任务 2.4.2
**TDD**: 是

**测试先行**:
```python
# test_report_template_system.py
import unittest

class TestReportTemplateSystem(unittest.TestCase):
    def test_template_selection_by_type(self):
        """测试根据类型选择模板"""
        template_system = ReportTemplateSystem()

        # 测试大五人格模板选择
        big_five_template = template_system.get_template('big_five_personality')
        self.assertEqual(big_five_template['name'], 'Big Five Assessment Report')

        # 测试知识模板选择
        knowledge_template = template_system.get_template('citizenship_knowledge')
        self.assertEqual(knowledge_template['name'], 'Knowledge Assessment Report')

    def test_template_data_binding(self):
        """测试模板数据绑定"""
        template_system = ReportTemplateSystem()
        template = template_system.get_template('big_five_personality')

        test_data = {
            "big_five_results": {"final_scores": {"O": 4.2, "C": 3.8}},
            "mbti_analysis": {"mbti_type": "ENFJ"}
        }

        rendered_html = template_system.render_template(template, test_data)

        self.assertIn("4.2", rendered_html)  # 分数显示
        self.assertIn("ENFJ", rendered_html)  # 类型显示
        self.assertIn("Big Five Assessment Report", rendered_html)  # 标题显示
```

**实现任务**:
- [ ] 设计模板引擎接口
- [ ] 实现数据绑定和渲染系统
- [ ] 创建模板选择逻辑
- [ ] 添加模板缓存机制

#### 任务 3.1.2: 人格报告模板
**优先级**: 🔴 高
**预估时间**: 0.2天
**依赖**: 任务 3.1.1
**TDD**: 是

**测试先行**:
```python
# test_personality_report_template.py
import unittest

class TestPersonalityReportTemplate(unittest.TestCase):
    def test_mbti_section_rendering(self):
        """测试MBTI部分渲染"""
        template = PersonalityReportTemplate()

        mbti_data = {
            "mbti_type": "ENFJ",
            "dimension_confidence": {"E/I": 0.85, "S/N": 0.75},
            "type_description": "主人公 - 同理心强，富有魅力的领导者"
        }

        mbti_section = template.render_mbti_section(mbti_data)

        self.assertIn("ENFJ", mbti_section)
        self.assertIn("主人公", mbti_section)
        self.assertIn("同理心", mbti_section)

    def test_team_roles_section_rendering(self):
        """测试团队角色部分渲染"""
        template = PersonalityReportTemplate()

        belbin_data = {
            "primary_role": "CO",
            "primary_role_name": "协调者",
            "top_three_roles": [
                {"role": "CO", "name": "协调者", "score": 4.2},
                {"role": "TW", "name": "团队协作者", "score": 3.8}
            ]
        }

        team_section = template.render_team_roles_section(belbin_data)

        self.assertIn("协调者", team_section)
        self.assertIn("团队协作者", team_section)
        self.assertIn("4.2", team_section)
```

**实现任务**:
- [ ] 实现MBTI详细报告模板
- [ ] 实现团队角色分析报告
- [ ] 实现职业发展建议模板
- [ ] 优化可视化组件

#### 任务 3.1.3: 知识报告模板
**优先级**: 🟡 中
**预估时间**: 0.2天
**依赖**: 任务 3.1.1
**TDD**: 是

**实现任务**:
- [ ] 实现知识掌握度报告模板
- [ ] 实现学习建议报告模板
- [ ] 实现知识结构分析模板
- [ ] 优化知识可视化组件

#### 任务 3.1.4: 专业报告模板
**优先级**: 🟡 中
**预估时间**: 0.2天
**依赖**: 任务 3.1.1
**TDD**: 是

**实现任务**:
- [ ] 实现专业能力评估报告模板
- [ ] 实现风险评估报告模板
- [ ] 实现发展路径建议模板
- [ ] 优化专业指标可视化

#### 任务 3.1.5: 动机和思维报告模板
**优先级**: 🟡 中
**预估时间**: 0.1天
**依赖**: 任务 3.1.4
**TDD**: 是

**实现任务**:
- [ ] 实现动机结构分析报告模板
- [ ] 实现思维模式分析报告模板
- [ ] 实现个性化发展建议模板
- [ ] 优化心理维度可视化

### 3.2 可视化组件优化

#### 任务 3.2.1: 雷达图组件优化
**优先级**: 🟡 中
**预估时间**: 0.2天
**依赖**: 任务 3.1.5
**TDD**: 是

**测试先行**:
```python
# test_radar_chart_component.py
import unittest

class TestRadarChartComponent(unittest.TestCase):
    def test_radar_chart_rendering(self):
        """测试雷达图渲染"""
        component = RadarChartComponent()

        chart_data = {
            "labels": ["开放性", "尽责性", "外向性", "宜人性", "神经质"],
            "values": [4.2, 3.8, 3.5, 4.1, 2.9]
        }

        chart_html = component.render_chart(chart_data)

        self.assertIn("radarChart", chart_html)
        self.assertIn("canvas", chart_html)
        self.assertIn("开放性", chart_html)
        self.assertIn("4.2", chart_html)

    def test_chart_interactivity(self):
        """测试图表交互性"""
        component = RadarChartComponent()

        # 测试悬停效果
        hover_script = component.get_interactivity_script()
        self.assertIn("addEventListener", hover_script)
        self.assertIn("mouseover", hover_script)

        # 测试数据更新
        update_script = component.get_update_script()
        self.assertIn("updateChart", update_script)
```

**实现任务**:
- [ ] 优化雷达图渲染算法
- [ ] 添加交互式悬停效果
- [ ] 实现动态数据更新
- [ ] 优化移动端显示

#### 任务 3.2.2: 进度条和卡片组件
**优先级**: 🟢 低
**预估时间**: 0.1天
**依赖**: 任务 3.2.1
**TDD**: 是

**实现任务**:
- [ ] 优化进度条动画效果
- [ ] 实现卡片悬停交互
- [ ] 添加响应式布局
- [ ] 优化颜色主题

#### 任务 3.2.3: 响应式布局优化
**优先级**: 🟢 低
**预估时间**: 0.1天
**依赖**: 任务 3.2.2
**TDD**: 是

**实现任务**:
- [ ] 优化移动端显示效果
- [ ] 实现自适应布局
- [ ] 优化触摸交互
- [ ] 添加打印样式

## 阶段四：集成测试与优化 (第6-7天)

### 4.1 全面集成测试

#### 任务 4.1.1: 多类型集成测试
**优先级**: 🔴 高
**预估时间**: 0.5天
**依赖**: 任务 3.2.3
**TDD**: 是

**测试先行**:
```python
# test_multi_type_integration.py
import unittest

class TestMultiTypeIntegration(unittest.TestCase):
    def test_all_assessment_types_coverage(self):
        """测试所有测评类型覆盖"""
        assessment_types = [
            'big_five_personality',
            'citizenship_knowledge',
            'financial_professional',
            'legal_knowledge',
            'motivation_psychology',
            'political_literacy'
        ]

        for assessment_type in assessment_types:
            with self.subTest(f"Test {assessment_type}"):
                # 测试每种类型的完整流程
                self._test_single_assessment_type(assessment_type)

    def _test_single_assessment_type(self, assessment_type):
        """测试单个测评类型完整流程"""
        # 1. 测试文件准备
        test_file = self._prepare_test_file(assessment_type)

        # 2. 测试自动类型识别
        detector = TypeDetector()
        detected_type = detector.detect_type(test_file)
        self.assertEqual(detected_type['type'], assessment_type)

        # 3. 测试问卷应答
        responder = QuestionnaireResponder()
        response_result = responder.generate_responses(
            test_file, 'ENFJ', assessment_type
        )

        # 4. 测试评估分析
        analyzer = PsychologicalAnalyzer()
        analyzer.start_evaluation_session(5, f'test_{assessment_type}')

        for response in response_result['responses'][:3]:  # 测试前3个问题
            analyzer.evaluate_single_question(response)

        # 5. 测试报告生成
        generator = EvaluationReportGenerator()
        report_data = analyzer.complete_evaluation()
        report_file = generator.generate_comprehensive_report(report_data)

        # 6. 验证结果
        self.assertTrue(Path(report_file).exists())
        self._validate_report_content(report_file, assessment_type)
```

**实现任务**:
- [ ] 编写6种测评类型的完整集成测试
- [ ] 验证系统稳定性
- [ ] 测试错误处理和恢复
- [ ] 验证输出结果一致性

#### 任务 4.1.2: 并发处理测试
**优先级**: 🟡 中
**预估时间**: 0.3天
**依赖**: 任务 4.1.1
**TDD**: 是

**测试先行**:
```python
# test_concurrent_processing.py
import unittest
import threading
import time

class TestConcurrentProcessing(unittest.TestCase):
    def test_concurrent_assessment_sessions(self):
        """测试并发评估会话"""
        analyzer = PsychologicalAnalyzer()

        def assessment_worker(session_id, questions):
            analyzer.start_evaluation_session(len(questions), session_id)
            for question in questions:
                analyzer.evaluate_single_question(question)
            return analyzer.complete_evaluation()

        # 创建3个并发会话
        questions1 = [{"question": f"Test {i}"} for i in range(3)]
        questions2 = [{"question": f"Test {i}"} for i in range(3)]
        questions3 = [{"question": f"Test {i}"} for i in range(3)]

        threads = [
            threading.Thread(target=assessment_worker, args=("session1", questions1)),
            threading.Thread(target=assessment_worker, args=("session2", questions2)),
            threading.Thread(target=assessment_worker, args=("session3", questions3))
        ]

        start_time = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        end_time = time.time()

        # 验证并发处理没有冲突
        self.assertLess(end_time - start_time, 10.0)

        # 验证每个会话的独立性
        self.assertEqual(analyzer.get_current_session_info()['session_id'], 'session3')
```

**实现任务**:
- [ ] 实现并发会话管理测试
- [ ] 测试线程安全性
- [ ] 验证内存使用效率
- [ ] 测试资源竞争处理

#### 任务 4.1.3: 配置文件集成测试
**优先级**: 🟡 中
**预估时间**: 0.2天
**依赖**: 任务 4.1.2
**TDD**: 是

**实现任务**:
- [ ] 测试所有配置文件加载
- [ ] 验证配置文件完整性
- [ ] 测试配置文件更新
- [ ] 验证配置错误处理

### 4.2 性能优化

#### 任务 4.2.1: 响应时间优化
**优先级**: 🟡 中
**预估时间**: 0.3天
**依赖**: 任务 4.1.3
**TDD**: 是

**测试先行**:
```python
# test_response_time_optimization.py
import unittest
import time

class TestResponseTimeOptimization(unittest.TestCase):
    def test_response_generation_caching(self):
        """测试响应生成缓存优化"""
        responder = QuestionnaireResponder()

        # 第一次调用（无缓存）
        start_time = time.time()
        result1 = responder.generate_responses(
            'test_file.json', 'ENFJ', 'big_five_personality'
        )
        first_time = time.time() - start_time

        # 第二次调用（有缓存）
        start_time = time.time()
        result2 = responder.generate_responses(
            'test_file.json', 'ENFJ', 'big_five_personality'
        )
        second_time = time.time() - start_time

        # 缓存应该显著提升性能
        self.assertLess(second_time, first_time * 0.5)

        # 结果应该相同
        self.assertEqual(result1['response_info']['persona'], result2['response_info']['persona'])

    def test_config_loading_optimization(self):
        """测试配置加载优化"""
        loader = ConfigLoader()

        # 第一次加载
        start_time = time.time()
        config1 = loader.load_config('big_five_personality.json')
        first_time = time.time() - start_time

        # 第二次加载（应该使用缓存）
        start_time = time.time()
        config2 = loader.load_config('big_five_personality.json')
        second_time = time.time() - start_time

        # 缓存应该显著提升性能
        self.assertLess(second_time, first_time * 0.3)
        self.assertEqual(config1, config2)
```

**实现任务**:
- [ ] 实现响应生成缓存机制
- [ ] 优化配置文件加载速度
- [ ] 实现智能预加载策略
- [ ] 添加性能监控和报告

#### 任务 4.2.2: 内存使用优化
**优先级**: 🟢 低
**预估时间**: 0.2天
**依赖**: 任务 4.2.1
**TDD**: 是

**实现任务**:
- [ ] 实现内存使用监控
- [ ] 优化大数据集处理
- [ ] 实现垃圾回收策略
- [ ] 添加内存泄漏检测

### 4.3 文档完善

#### 任务 4.3.1: 用户文档编写
**优先级**: 🟢 中
**预估时间**: 0.3天
**依赖**: 任务 4.2.2
**TDD**: 是

**实现任务**:
- [ ] 编写用户使用指南
- [ ] 创建配置文件说明文档
- [ ] 编写API接口文档
- [ ] 创建故障排除指南

#### 任务 4.3.2: 示例和最佳实践
**优先级**: 🟢 低
**预估时间**: 0.2天
**依赖**: 任务 4.3.1
**TDD**: 是

**实现任务**:
- [ ] 创建6种测评类型示例数据
- [ ] 生成示例报告文件
- [ ] 编写使用案例和最佳实践
- [ ] 创建集成示例代码

## 5. 质量保证检查点

### 5.1 代码质量检查点

#### 检查点 1: 单元测试覆盖率
- [ ] 所有模块测试覆盖率 ≥ 90%
- [ ] 所有公共接口有单元测试
- [ ] 关键算法有详细测试

#### 检查点 2: 集成测试覆盖
- [ ] 端到端流程测试覆盖率 = 100%
- [ ] 所有测评类型集成测试通过
- [ ] 错误处理测试通过

#### 检查点 3: 性能基准达标
- [ ] 响应生成时间 < 5秒
- [ ] 分析处理时间 < 2秒
- [ ] 报告生成时间 < 10秒

### 5.2 功能验收标准

#### 验收标准 1: 功能完整性
- [ ] 支持6种测评类型的完整流程
- [ ] 自动类型识别准确率 ≥ 95%
- [ ] 所有配置文件正常工作
- [ ] 生成的报告质量符合专业标准

#### 验收标准 2: 系统稳定性
- [ ] 连续运行24小时无崩溃
- [ ] 并发处理测试通过
- [ ] 内存使用稳定
- [ ] 错误恢复机制正常

#### 验收标准 3: 用户体验
- [ ] 自动类型识别准确高效
- [ ] 错误信息清晰有用
- [ ] 响应时间满足要求
- [ ] 报告质量专业美观

## 6. 任务执行指南

### 6.1 任务执行顺序
1. **严格按照依赖关系执行任务**
2. **每个任务必须先写测试再实现**
3. **完成任务后立即运行测试验证**
4. **确保测试通过后再进入下一个任务**

### 6.2 TDD开发流程
1. **编写测试用例**：明确功能需求和预期结果
2. **运行测试（预期失败）**：验证测试能检测到功能缺失
3. **实现最小功能**：编写最少代码使测试通过
4. **运行测试（预期成功）**：验证基本功能正常
5. **完善功能实现**：优化代码质量和功能完整性
6. **重构优化**：改进代码结构和性能

### 6.3 集成验证流程
1. **单元测试验证**：确保每个模块独立正常工作
2. **模块集成测试**：验证模块间接口正确性
3. **系统集成测试**：验证端到端流程完整性
4. **性能测试**：验证系统性能指标达标
5. **用户验收测试**：验证最终产品质量

### 6.4 错误处理流程
1. **测试失败分析**：理解失败原因和根本问题
2. **代码修复**：针对问题进行代码修改
3. **测试重跑**：验证修复效果
4. **问题记录**：记录问题和解决方案
5. **回归测试**：确保修复不影响其他功能

---

**文档版本**: v1.0.0
**最后更新**: 2025-01-08
**任务总数**: 60个
**预估工期**: 5-7天
**TDD驱动**: 是
**系统集成**: 支持