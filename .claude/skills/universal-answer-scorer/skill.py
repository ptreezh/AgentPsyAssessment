#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用答卷评分技能 - 完全独立版本
自动识别答卷类型，选择权威专家，严格按照评分标准评分
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class UniversalAnswerScorer:
    """通用答卷评分技能 - 完全自包含"""

    def __init__(self):
        self.name = "universal-answer-scorer"
        self.description = "通用答卷评分技能，自动识别答卷类型，选择权威专家，严格按照评分标准评分"

        # 内嵌专家角色库
        self.expert_roles = self._create_expert_roles()

        # 答卷类型识别规则
        self.questionnaire_patterns = self._create_questionnaire_patterns()

        # 评分方法配置
        self.scoring_config = {
            "temperature": 0.1,  # 严格标准
            "strict_mode": True,
            "require_keywords": True,
            "penalty_for_missing": 0.5,  # 关键词缺失扣分比例
        }

    def _create_expert_roles(self) -> Dict[str, Dict]:
        """创建内嵌专家角色库"""
        return {
            "national_knowledge_expert": {
                "name": "国情知识专家",
                "field": "中国历史地理政治文化",
                "expertise": [
                    "中国历史发展脉络", "地理环境特征", "政治制度体系",
                    "文化传统传承", "经济社会发展", "科技成就贡献"
                ],
                "prompt": """你是一位资深的国情知识专家，拥有30年的中国研究和教学经验。你对中国历史、地理、政治、文化、经济、科技等领域有深入的了解。

你的评分原则：
1. 严格按照题目要求的评分标准进行评分
2. 重点考察答案的准确性、完整性和专业性
3. 对于历史问题，要求时间、人物、事件等关键要素准确
4. 对于地理问题，要求地理位置、特征、意义等要素完整
5. 对于政治问题，要求制度、政策、影响等要素清晰
6. 对于文化问题，要求传统、内涵、价值等要素深入

请严格按照评分标准，给出0-10分的精确评分，每道题都要有明确的评分依据。""",
                "keywords_weight": 0.7,  # 关键词权重
                "completeness_weight": 0.2,  # 完整性权重
                "accuracy_weight": 0.1  # 准确性权重
            },

            "psychology_expert": {
                "name": "心理学专家",
                "field": "人格心理学与心理测量",
                "expertise": [
                    "大五人格理论", "MBTI人格类型", "心理测量学",
                    "人格评估方法", "心理特质分析", "行为模式识别"
                ],
                "prompt": """你是一位权威的心理学专家，专攻人格心理学和心理测量领域，拥有20年的临床和研究经验。你精通各种人格理论和心理评估方法。

你的评分原则：
1. 严格按照心理测量的专业标准进行评分
2. 重点考察答案的一致性、合理性和心理真实性
3. 对于人格特质问题，要求回答体现出对特质的准确理解
4. 对于行为模式问题，要求回答符合心理学理论
5. 对于自我认知问题，要求回答展现出内省和洞察力
6. 对于态度偏好问题，要求回答明确且符合逻辑

请严格按照评分标准，给出0-10分的精确评分，每道题都要有专业的心理学评分依据。""",
                "keywords_weight": 0.4,  # 关键词权重
                "consistency_weight": 0.3,  # 一致性权重
                "psychological_validity_weight": 0.3  # 心理有效性权重
            },

            "customer_service_expert": {
                "name": "客服管理专家",
                "field": "客户服务管理与沟通",
                "expertise": [
                    "客户沟通技巧", "服务质量管理", "投诉处理流程",
                    "客户关系维护", "服务标准制定", "客服团队管理"
                ],
                "prompt": """你是一位资深的企业客服管理专家，拥有15年的客服行业经验，曾为多家世界500强企业设计客服体系和培训方案。

你的评分原则：
1. 严格按照客服行业的专业标准进行评分
2. 重点考察答案的专业性、实用性和客户导向
3. 对于沟通技巧问题，要求回答体现出同理心和有效性
4. 对于问题处理问题，要求回答符合标准流程和最佳实践
5. 对于服务态度问题，要求回答展现专业素养和客户关怀
6. 对于特殊情况处理，要求回答体现应变能力和解决方案

请严格按照评分标准，给出0-10分的精确评分，每道题都要有明确的客服专业评分依据。""",
                "keywords_weight": 0.5,  # 关键词权重
                "professionalism_weight": 0.3,  # 专业性权重
                "practicality_weight": 0.2  # 实用性权重
            },

            "cognitive_expert": {
                "name": "认知科学专家",
                "field": "认知心理学与逻辑思维",
                "expertise": [
                    "认知偏差分析", "逻辑推理能力", "思维模式评估",
                    "决策制定过程", "问题解决策略", "批判性思维"
                ],
                "prompt": """你是一位认知科学专家，专攻认知心理学和逻辑思维研究，拥有博士学位和10年的认知评估经验。你对人类的思维过程、认知偏差和逻辑推理有深入的理解。

你的评分原则：
1. 严格按照认知科学的专业标准进行评分
2. 重点考察答案的逻辑性、严谨性和认知深度
3. 对于逻辑推理问题，要求论证过程清晰、结论合理
4. 对于认知偏差问题，要求识别准确、分析深入
5. 对于问题解决问题，要求思路清晰、方法有效
6. 对于批判性思维问题，要求体现出质疑精神和分析能力

请严格按照评分标准，给出0-10分的精确评分，每道题都要有严谨的认知科学评分依据。""",
                "keywords_weight": 0.4,  # 关键词权重
                "logic_weight": 0.4,  # 逻辑性权重
                "depth_weight": 0.2  # 深度权重
            },

            "general_education_expert": {
                "name": "通用教育专家",
                "field": "综合知识与教育评估",
                "expertise": [
                    "基础知识评估", "综合能力测试", "教育测量方法",
                    "学科交叉分析", "通识教育设计", "学习成果评估"
                ],
                "prompt": """你是一位经验丰富的通用教育专家，拥有25年的教育评估和课程设计经验。你擅长跨学科知识评估和综合能力测评。

你的评分原则：
1. 严格按照教育测量的专业标准进行评分
2. 重点考察答案的知识性、理解性和应用性
3. 对于基础知识问题，要求概念准确、理解深入
4. 对于应用性问题，要求方法正确、结果合理
5. 对于分析性问题，要求思路清晰、论证有力
6. 对于综合性问题，要求知识整合、观点新颖

请严格按照评分标准，给出0-10分的精确评分，每道题都要有明确的教育专业评分依据。""",
                "keywords_weight": 0.6,  # 关键词权重
                "understanding_weight": 0.2,  # 理解性权重
                "application_weight": 0.2  # 应用性权重
            }
        }

    def _create_questionnaire_patterns(self) -> Dict[str, Dict]:
        """创建答卷类型识别规则"""
        return {
            "national_knowledge": {
                "keywords": ["四大发明", "改革开放", "秦始皇", "新疆", "国家主席", "春节", "GDP", "高铁", "中国", "历史", "地理", "政治", "文化"],
                "question_patterns": [
                    r"中国的.*是什么", r".*是哪一年", r".*排名第几", r".*是谁", r".*什么时候"
                ],
                "dimensions": ["historical_knowledge", "geographical_knowledge", "political_knowledge", "cultural_knowledge", "economic_knowledge", "technological_knowledge"],
                "expert": "national_knowledge_expert"
            },

            "big_five": {
                "keywords": ["外向", "宜人", "尽责", "神经质", "开放", "extraversion", "agreeableness", "conscientiousness", "neuroticism", "openness", "人格", "性格", "通常"],
                "question_patterns": [
                    r"在.*场合，我.*", r"我.*是.*的人", r"我.*喜欢", r"面对.*时，我.*", r"我通常.*"
                ],
                "dimensions": ["extraversion", "agreeableness", "conscientiousness", "neuroticism", "openness"],
                "expert": "psychology_expert"
            },

            "customer_service": {
                "keywords": ["客户", "顾客", "投诉", "服务", "沟通", "处理", "解决", "满意", "需求", "客服"],
                "question_patterns": [
                    r"如何处理.*投诉", r"面对.*客户，你.*", r"如果.*不满意的", r"客服.*应该", r"服务.*的关键是"
                ],
                "dimensions": ["communication", "problem_solving", "service_attitude", "professional_knowledge", "efficiency"],
                "expert": "customer_service_expert"
            },

            "cognitive_bias": {
                "keywords": ["认知", "偏差", "思维", "逻辑", "推理", "判断", "决策", "陷阱", "谬误", "批判性"],
                "question_patterns": [
                    r".*认知偏差", r".*逻辑错误", r".*思维陷阱", r"如何避免.*", r"批判性.*"
                ],
                "dimensions": ["logical_reasoning", "cognitive_bias_identification", "critical_thinking", "decision_making", "problem_analysis"],
                "expert": "cognitive_expert"
            },

            "general_assessment": {
                "keywords": ["评估", "测试", "能力", "知识", "技能", "理解", "分析", "应用"],
                "question_patterns": [
                    r".*是什么", r".*为什么", r".*如何", r".*请解释", r".*请分析"
                ],
                "dimensions": ["knowledge", "understanding", "application", "analysis", "synthesis"],
                "expert": "general_education_expert"
            }
        }

    def identify_questionnaire_type(self, answer_data: Dict) -> Tuple[str, Dict]:
        """识别答卷类型"""

        # 提取答卷内容
        questions = []
        if "answers" in answer_data:
            questions = answer_data["answers"]
        elif "questions" in answer_data:
            questions = answer_data["questions"]

        if not questions:
            return "general_assessment", self.questionnaire_patterns["general_assessment"]

        # 统计关键词和模式匹配
        scores = {}
        all_text = ""

        for question in questions:
            question_text = ""

            # 提取问题文本
            if "question_data" in question and "question" in question["question_data"]:
                question_text = question["question_data"]["question"]
            elif "question" in question:
                question_text = question["question"]
            elif "prompt" in question:
                question_text = question["prompt"]

            all_text += " " + question_text.lower()

        # 计算每种类型的匹配分数
        for q_type, pattern in self.questionnaire_patterns.items():
            score = 0

            # 关键词匹配
            for keyword in pattern["keywords"]:
                if keyword.lower() in all_text:
                    score += 1

            # 模式匹配
            for pattern_regex in pattern["question_patterns"]:
                if re.search(pattern_regex, all_text, re.IGNORECASE):
                    score += 2

            scores[q_type] = score

        # 选择得分最高的类型
        best_type = max(scores.items(), key=lambda x: x[1])[0]

        # 如果所有得分都很低，使用通用评估
        if scores[best_type] == 0:
            best_type = "general_assessment"

        return best_type, self.questionnaire_patterns[best_type]

    def extract_answer_for_question(self, question_data: Dict) -> Optional[str]:
        """提取问题对应的答案"""

        # 检查是否已有答案
        if "answer" in question_data:
            return question_data["answer"]

        # 检查conversation中最后一条是否是assistant的回答
        if "conversation" in question_data:
            conversation = question_data["conversation"]
            for msg in reversed(conversation):
                if msg.get("role") == "assistant":
                    return msg.get("content", "")

        # 检查response字段
        if "response" in question_data:
            return question_data["response"]

        return None

    def calculate_question_score(self, question_data: Dict, expert_config: Dict) -> Dict:
        """计算单个问题的分数"""

        question_text = ""
        expected_keywords = []
        dimension = ""

        # 提取问题信息
        if "question_data" in question_data:
            qd = question_data["question_data"]
            question_text = qd.get("question", "")
            expected_keywords = qd.get("evaluation_rubric", {}).get("expected_keywords", [])
            dimension = qd.get("dimension", "")
        else:
            question_text = question_data.get("question", "")
            expected_keywords = question_data.get("expected_keywords", [])
            dimension = question_data.get("dimension", "")

        # 提取答案
        answer_text = self.extract_answer_for_question(question_data)

        if not answer_text:
            return {
                "question_id": question_data.get("question_id", "unknown"),
                "score": 0,
                "max_score": 10,
                "reasoning": "未找到答案内容",
                "keywords_found": [],
                "keywords_missing": expected_keywords,
                "dimension": dimension
            }

        # 转换为小写进行匹配
        answer_text_lower = answer_text.lower()

        # 检查关键词匹配
        keywords_found = []
        keywords_missing = []

        for keyword in expected_keywords:
            if keyword.lower() in answer_text_lower:
                keywords_found.append(keyword)
            else:
                keywords_missing.append(keyword)

        # 计算基础分数
        if expected_keywords:
            keyword_score = (len(keywords_found) / len(expected_keywords)) * 10
        else:
            # 如果没有关键词，根据答案质量和长度给分
            if len(answer_text.strip()) > 50:
                keyword_score = 7.0  # 有实质性内容
            elif len(answer_text.strip()) > 10:
                keyword_score = 5.0  # 有基本内容
            else:
                keyword_score = 3.0  # 内容过短

        # 应用专家权重调整
        keyword_weight = expert_config.get("keywords_weight", 0.6)
        base_score = keyword_score * keyword_weight

        # 补充分数（基于完整性、专业性等）
        additional_score = 0

        # 完整性加分
        if len(answer_text.strip()) > 100:
            additional_score += 1.0 * (1 - keyword_weight)
        elif len(answer_text.strip()) > 50:
            additional_score += 0.5 * (1 - keyword_weight)

        # 专业性加分（检查是否包含专业术语或深入分析）
        professional_indicators = ["因为", "所以", "首先", "其次", "最后", "总之", "可以看出", "显然", "重要的是"]
        professional_count = sum(1 for indicator in professional_indicators if indicator in answer_text)
        if professional_count >= 2:
            additional_score += 0.5 * (1 - keyword_weight)

        # 计算最终分数
        final_score = min(10.0, base_score + additional_score)

        # 构建评分理由
        reasoning_parts = []

        if expected_keywords:
            reasoning_parts.append(f"关键词匹配：{len(keywords_found)}/{len(expected_keywords)} ({', '.join(keywords_found)})")

        if keywords_missing:
            reasoning_parts.append(f"缺失关键词：{', '.join(keywords_missing)}")

        reasoning_parts.append(f"答案长度：{len(answer_text.strip())}字符")

        if professional_count >= 2:
            reasoning_parts.append("展现专业分析能力")

        reasoning = "; ".join(reasoning_parts)

        return {
            "question_id": question_data.get("question_id", "unknown"),
            "score": round(final_score, 1),
            "max_score": 10,
            "reasoning": reasoning,
            "keywords_found": keywords_found,
            "keywords_missing": keywords_missing,
            "dimension": dimension,
            "answer_length": len(answer_text.strip()),
            "professional_indicators": professional_count
        }

    def score_answer_sheet(self, answer_data: Dict, temperature: float = 0.1) -> Dict:
        """对整份答卷进行评分"""

        # 识别答卷类型
        q_type, pattern = self.identify_questionnaire_type(answer_data)
        expert_config = self.expert_roles[pattern["expert"]]

        # 提取问题列表
        questions = []
        if "answers" in answer_data:
            questions = answer_data["answers"]
        elif "questions" in answer_data:
            questions = answer_data["questions"]

        if not questions:
            return {
                "error": "未找到有效的问题数据",
                "questionnaire_type": q_type,
                "expert": expert_config["name"],
                "scores": []
            }

        # 为每个问题评分
        scores = []
        total_score = 0
        total_questions = len(questions)

        for question in questions:
            score_result = self.calculate_question_score(question, expert_config)
            scores.append(score_result)
            total_score += score_result["score"]

        # 计算统计信息
        average_score = total_score / total_questions if total_questions > 0 else 0

        return {
            "questionnaire_type": q_type,
            "expert": expert_config["name"],
            "expertise_field": expert_config["field"],
            "scoring_time": datetime.now().isoformat(),
            "temperature": temperature,
            "total_questions": total_questions,
            "total_score": round(total_score, 1),
            "average_score": round(average_score, 1),
            "max_possible_score": total_questions * 10,
            "scores": scores
        }

    def generate_expert_evaluation_prompt(self, answer_data: Dict, question_scores: List[Dict]) -> str:
        """生成专家评估提示词"""

        # 识别答卷类型和专家
        q_type, pattern = self.identify_questionnaire_type(answer_data)
        expert_config = self.expert_roles[pattern["expert"]]

        prompt = f"{expert_config['prompt']}\n\n"
        prompt += f"答卷类型：{q_type}\n"
        prompt += f"题目总数：{len(question_scores)}\n\n"

        prompt += "请按照以下格式对每道题进行评分：\n\n"

        for i, score_data in enumerate(question_scores, 1):
            prompt += f"题目{i}（ID: {score_data['question_id']}）：\n"
            prompt += f"得分：{score_data['score']}/10\n"
            prompt += f"评分理由：{score_data['reasoning']}\n\n"

        prompt += "请确认以上评分是否合理，如有需要调整的地方，请说明理由。"

        return prompt

    def save_scoring_results(self, results: Dict, output_dir: str = "results") -> str:
        """保存评分结果"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scores_{results['questionnaire_type']}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return filepath

    def print_scores_summary(self, results: Dict):
        """打印评分结果摘要"""
        print(f"\n📊 评分结果摘要")
        print("=" * 50)
        print(f"📋 答卷类型：{results['questionnaire_type']}")
        print(f"👨‍🏫 评分专家：{results['expert']}")
        print(f"🎯 专业领域：{results['expertise_field']}")
        print(f"📝 题目总数：{results['total_questions']}")
        print(f"💯 总分：{results['total_score']}/{results['max_possible_score']}")
        print(f"📈 平均分：{results['average_score']}/10")

        print(f"\n📋 各题得分详情：")
        for i, score in enumerate(results['scores'], 1):
            print(f"   题目{i} ({score['question_id']}): {score['score']}/10 - {score['reasoning']}")

def main():
    """主函数 - 技能入口点"""
    scorer = UniversalAnswerScorer()

    print("🧠 通用答卷评分技能")
    print("=" * 50)
    print("👨‍🏫 支持的专家领域：")
    for expert_key, expert_config in scorer.expert_roles.items():
        print(f"   • {expert_config['name']} - {expert_config['field']}")

    # 示例：测试独立问卷技能生成的答案文件
    test_file = "D:\\AIDevelop\\portable_psyagent\\.claude\\skills\\standalone-questionnaire\\results\\answers_national_knowledge_default_20251109_211005.json"

    if os.path.exists(test_file):
        print(f"\n🔬 测试评分功能，使用文件：{test_file}")

        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                answer_data = json.load(f)

            # 进行评分
            results = scorer.score_answer_sheet(answer_data, temperature=0.1)

            # 打印结果摘要
            scorer.print_scores_summary(results)

            # 保存结果
            output_file = scorer.save_scoring_results(results)
            print(f"\n💾 评分结果已保存至：{output_file}")

        except Exception as e:
            print(f"❌ 评分失败：{e}")
    else:
        print(f"\n📝 测试文件不存在：{test_file}")
        print("技能已准备就绪，可以对接任何答卷数据文件进行评分")

    return scorer

if __name__ == "__main__":
    main()