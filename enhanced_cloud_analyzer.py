#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版云评估器分段式心理评估分析器
支持多个云服务提供商：Qwen、DeepSeek、GLM、Moonshot等
"""

import json
import sys
import time
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
import openai
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class EnhancedCloudAnalyzer:
    """增强版云评估器，支持多个云服务提供商"""

    def __init__(self, model: str = "qwen-long", api_key: str = None, base_url: str = None, max_questions_per_segment: int = 2):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.max_questions_per_segment = max_questions_per_segment

        # 根据模型确定API配置
        self._configure_api()

        # 初始化Big5评分累积器
        self.big_five_traits = {
            'openness_to_experience': {'scores': [], 'evidence': [], 'weight': 0},
            'conscientiousness': {'scores': [], 'evidence': [], 'weight': 0},
            'extraversion': {'scores': [], 'evidence': [], 'weight': 0},
            'agreeableness': {'scores': [], 'evidence': [], 'weight': 0},
            'neuroticism': {'scores': [], 'evidence': [], 'weight': 0}
        }

        self.analysis_log = []
        self.per_question_scores = []
        self.segment_results = []

        # 初始化云评估器客户端
        if self.api_key and self.base_url:
            if self.api_type == 'anthropic':
                # Anthropic API通过OpenAI兼容接口访问
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            else:
                # OpenAI兼容接口
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
        else:
            self.client = None

        # 检查API连接
        self.api_available = self._check_api_connection()

    def _configure_api(self):
        """根据模型配置API参数"""
        model_configs = {
            # DashScope API中实际可用的模型
            'qwen-long': {
                'api_key_env': 'DASHSCOPE_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            },
            'qwen-max': {
                'api_key_env': 'DASHSCOPE_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            },

            # DeepSeek Models (通过DashScope API，实际可用)
            'deepseek-v3.2-exp': {
                'api_key_env': 'DASHSCOPE_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            },
            'deepseek-chat': {
                'api_key_env': 'DASHSCOPE_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            },

            # Moonshot Models (通过DashScope API，实际可用)
            'Moonshot-Kimi-K2-Instruct': {
                'api_key_env': 'DASHSCOPE_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            },

            # Anthropic Models (via BigModel)
            'claude-3.5-sonnet': {
                'api_key_env': 'ANTHROPIC_AUTH_TOKEN',
                'base_url_env': 'ANTHROPIC_BASE_URL',
                'api_type': 'anthropic'
            },
            'claude-3-opus': {
                'api_key_env': 'ANTHROPIC_AUTH_TOKEN',
                'base_url_env': 'ANTHROPIC_BASE_URL',
                'api_type': 'anthropic'
            },

            # GLM Models (在DashScope API中不可用，保留配置)
            'GLM-4.5': {
                'api_key_env': 'DASHSCOPE_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'note': '在DashScope API中不可用'
            },
            'GLM-4.5-AIR': {
                'api_key_env': 'DASHSCOPE_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'note': '在DashScope API中不可用'
            },
            'glm4.5': {
                'api_key_env': 'DASHSCOPE_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'note': '在DashScope API中不可用'
            },
            'glm-4.5': {
                'api_key_env': 'DASHSCOPE_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'note': '在DashScope API中不可用'
            },
            'glm4': {
                'api_key_env': 'DASHSCOPE_API_KEY',
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'note': '在DashScope API中不可用'
            }
        }

        config = model_configs.get(self.model, {})

        if not self.api_key:
            import os
            self.api_key = os.getenv(config.get('api_key_env', ''))

        if not self.base_url:
            if 'base_url_env' in config:
                self.base_url = os.getenv(config['base_url_env'], '')
            else:
                self.base_url = config.get('base_url', '')

        # 设置API类型
        self.api_type = config.get('api_type', 'openai')

        # 设置默认值（用于测试）
        if not self.api_key and self.api_type == 'openai':
            self.api_key = "sk-ffd03518254b495b8d27e723cd413fc1"

    def _check_api_connection(self) -> bool:
        """检查API连接是否可用"""
        if not self.client:
            print(f"❌ 未配置客户端: {self.model}")
            return False

        try:
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            print(f"✅ API连接成功: {self.model}")
            return True
        except Exception as e:
            print(f"❌ API连接失败: {self.model} - {e}")
            return False

    def extract_questions(self, assessment_data: Dict) -> List[Dict]:
        """从评估数据中提取问题列表"""
        if 'assessment_results' in assessment_data:
            assessment_results = assessment_data['assessment_results']

            if isinstance(assessment_results, list):
                if len(assessment_results) > 0 and isinstance(assessment_results[0], dict):
                    if 'question_data' in assessment_results[0]:
                        questions = []
                        for result in assessment_results:
                            if 'question_data' in result:
                                question_data = result['question_data'].copy()
                                if 'conversation_log' in result:
                                    for msg in result['conversation_log']:
                                        if msg.get('role') == 'assistant':
                                            question_data['agent_response'] = msg['content']
                                            break
                                questions.append(question_data)
                        return questions

        if 'questions' in assessment_data:
            return assessment_data['questions']

        print(f"警告: 无法从数据中提取问题，可用键: {list(assessment_data.keys())}")
        return []

    def create_segments(self, questions: List[Dict]) -> List[List[Dict]]:
        """创建分段，每段包含指定数量的问题"""
        segments = []
        for i in range(0, len(questions), self.max_questions_per_segment):
            segment = questions[i:i + self.max_questions_per_segment]
            if segment:
                segments.append(segment)

        print(f"创建 {len(segments)} 个分段，每段最多 {self.max_questions_per_segment} 个问题")
        return segments

    def validate_and_fix_score(self, score: Any) -> int:
        """验证并修复评分，确保只能是1、3、5"""
        try:
            score = int(score)
            if score in [1, 3, 5]:
                return score
            elif score <= 2:
                return 1
            elif score <= 4:
                return 3
            else:
                return 5
        except (ValueError, TypeError):
            return 3  # 默认值

    def analyze_segment(self, segment: List[Dict], segment_number: int) -> Dict:
        """分析单个分段，使用严格的1-3-5评分标准"""
        try:
            # 构建分段分析提示
            segment_prompt = self._build_segment_prompt(segment, segment_number)

            # 调用云API进行分析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的心理评估分析师，专门分析Big5人格特质。请严格按照1-3-5评分标准进行评估。"},
                    {"role": "user", "content": segment_prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )

            analysis_content = response.choices[0].message.content

            # 解析分析结果
            segment_result = self._parse_segment_response(analysis_content, segment_number)

            if segment_result['success']:
                # 累积评分到对应维度
                self._accumulate_scores(segment_result['scores'], segment_result['evidence'])
                print(f"✅ 段 {segment_number} 分析成功")
                return segment_result
            else:
                print(f"❌ 段 {segment_number} 分析失败: {segment_result.get('error', 'Unknown error')}")
                return {'success': False, 'segment_number': segment_number, 'error': segment_result.get('error', 'Unknown error')}

        except Exception as e:
            print(f"💥 段 {segment_number} 分析异常: {e}")
            return {'success': False, 'segment_number': segment_number, 'error': str(e)}

    def _build_segment_prompt(self, segment: List[Dict], segment_number: int) -> str:
        """构建分段分析提示"""
        prompt = f"""请分析以下第{segment_number}段问卷回答，评估Big5人格特质。

**评分标准（重要）：**
- 1分 = 低表现
- 3分 = 中等表现
- 5分 = 高表现
- 只能使用1、3、5三个分数值

**问卷内容：**
"""

        for i, question in enumerate(segment, 1):
            prompt += f"\n问题{i}: {question.get('question_text', 'N/A')}\n"
            prompt += f"回答: {question.get('user_response', question.get('response', 'N/A'))}\n"

            if 'agent_response' in question:
                prompt += f"智能体回复: {question['agent_response'][:200]}...\n"
            prompt += "---\n"

        prompt += """
**分析要求：**
1. 逐题分析回答内容
2. 基于回答评估每个Big5维度：开放性(O)、尽责性(C)、外向性(E)、宜人性(A)、神经质(N)
3. 严格按照1-3-5评分，不使用其他数值
4. 为每个评分提供具体的评估依据

**输出格式（JSON）：**
```json
{
  "success": true,
  "segment_number": 分段编号,
  "scores": {
    "openness_to_experience": 评分(1/3/5),
    "conscientiousness": 评分(1/3/5),
    "extraversion": 评分(1/3/5),
    "agreeableness": 评分(1/3/5),
    "neuroticism": 评分(1/3/5)
  },
  "evidence": {
    "openness_to_experience": "评估依据",
    "conscientiousness": "评估依据",
    "extraversion": "评估依据",
    "agreeableness": "评估依据",
    "neuroticism": "评估依据"
  },
  "analysis": "详细分析过程"
}
```
"""
        return prompt

    def _clean_json_string(self, json_str: str) -> str:
        """清理JSON字符串中的控制字符和无效字符"""
        import re

        # 移除控制字符（除了换行符、制表符、回车符）
        json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_str)

        # 修复常见的JSON格式问题
        # 移除多余的逗号（在}或]之前）
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

        # 确保字符串值被正确引号包围
        json_str = re.sub(r':\s*([^",\[\]\{\}\s][^",\[\]\{\}]*[^",\[\]\{\}\s])(\s*[,}\]])', r': "\1"\2', json_str)

        # 修复转义字符问题
        json_str = json_str.replace('\\"', '"')
        json_str = json_str.replace('\\/', '/')

        return json_str

    def _extract_and_fix_json(self, response_content: str) -> str:
        """更激进的JSON提取和修复"""
        import re

        # 尝试多种JSON提取模式
        patterns = [
            # 标准JSON对象
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            # 带有换行的JSON
            r'\{[\s\S]*?\}',
            # 简化的JSON结构
            r'\{[^}]*"scores"[^}]*\}',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response_content)
            for match in matches:
                try:
                    # 清理和修复
                    cleaned = self._clean_json_string(match)
                    # 验证是否为有效JSON
                    json.loads(cleaned)
                    return cleaned
                except:
                    continue

        # 如果以上都失败，尝试手动构建JSON
        return self._build_fallback_json(response_content)

    def _build_fallback_json(self, response_content: str) -> str:
        """构建备用的JSON结构"""
        import re

        # 尝试提取分数信息
        scores = {}
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        for trait in traits:
            # 查找形如 "openness_to_experience": 3 的模式
            pattern = rf'"{trait}"\s*:\s*([1-5])'
            match = re.search(pattern, response_content)
            if match:
                scores[trait] = int(match.group(1))
            else:
                scores[trait] = 3  # 默认值

        # 构建标准JSON
        return json.dumps({
            'scores': scores,
            'analysis': 'Auto-fixed from malformed response',
            'confidence': 'medium'
        })

    def _parse_segment_response(self, response_content: str, segment_number: int) -> Dict:
        """解析分段分析响应"""
        try:
            # 尝试提取JSON部分
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_content[json_start:json_end]

                # 清理JSON字符串中的控制字符和无效字符
                json_str = self._clean_json_string(json_str)

                result = json.loads(json_str)

                # 验证并修复评分
                if 'scores' in result:
                    for trait in result['scores']:
                        result['scores'][trait] = self.validate_and_fix_score(result['scores'][trait])

                result['segment_number'] = segment_number
                result['raw_response'] = response_content
                return result
            else:
                return {
                    'success': False,
                    'segment_number': segment_number,
                    'error': '无法提取JSON结果',
                    'raw_response': response_content
                }

        except json.JSONDecodeError as e:
            # 尝试更激进的JSON修复
            try:
                # 尝试提取并修复JSON
                fixed_json = self._extract_and_fix_json(response_content)
                if fixed_json:
                    result = json.loads(fixed_json)

                    # 验证并修复评分
                    if 'scores' in result:
                        for trait in result['scores']:
                            result['scores'][trait] = self.validate_and_fix_score(result['scores'][trait])

                    result['segment_number'] = segment_number
                    result['raw_response'] = response_content
                    result['json_fixed'] = True
                    return result
            except:
                pass  # 如果修复失败，继续到原始错误处理

            return {
                'success': False,
                'segment_number': segment_number,
                'error': f'JSON解析错误: {e}',
                'raw_response': response_content
            }
        except Exception as e:
            # 处理其他异常，特别是'success'键错误
            try:
                # 尝试提取并修复JSON
                fixed_json = self._extract_and_fix_json(response_content)
                if fixed_json:
                    result = json.loads(fixed_json)

                    # 验证并修复评分
                    if 'scores' in result:
                        for trait in result['scores']:
                            result['scores'][trait] = self.validate_and_fix_score(result['scores'][trait])

                    result['segment_number'] = segment_number
                    result['raw_response'] = response_content
                    result['json_fixed'] = True
                    return result
            except:
                pass  # 如果修复失败，继续到原始错误处理

            return {
                'success': False,
                'segment_number': segment_number,
                'error': f'解析错误: {e}',
                'raw_response': response_content
            }

    def _accumulate_scores(self, scores: Dict, evidence: Dict):
        """累积分段评分到总评分"""
        for trait, score in scores.items():
            if trait in self.big_five_traits:
                self.big_five_traits[trait]['scores'].append(score)
                self.big_five_traits[trait]['weight'] += 1

        for trait, ev in evidence.items():
            if trait in self.big_five_traits:
                self.big_five_traits[trait]['evidence'].append(ev)

    def analyze_full_assessment(self, input_file: str, output_dir: str) -> Dict:
        """分析完整的测评评估"""
        print(f"🔍 开始分析: {input_file}")

        try:
            # 读取评估数据
            with open(input_file, 'r', encoding='utf-8') as f:
                assessment_data = json.load(f)

            # 提取问题
            questions = self.extract_questions(assessment_data)
            if not questions:
                return {
                    'success': False,
                    'error': '无法提取问题数据',
                    'file': input_file
                }

            print(f"📊 提取到 {len(questions)} 个问题")

            # 创建分段
            segments = self.create_segments(questions)

            # 分析每个分段
            successful_segments = 0
            for i, segment in enumerate(segments, 1):
                print(f"📝 分析分段 {i}/{len(segments)}...")
                print(f"  使用 {self.model} 分析段 {i} ({len(segment)} 题)")

                segment_result = self.analyze_segment(segment, i)
                self.segment_results.append(segment_result)

                if segment_result['success']:
                    successful_segments += 1
                    print(f"  成功累积分段 {i} 的评分")
                else:
                    print(f"  段 {i} 分析失败: {segment_result.get('error', 'Unknown error')}")

            # 计算最终评分
            final_scores = self.calculate_final_scores()
            mbti_result = self.generate_mbti_type(final_scores)

            # 保存结果
            self.save_analysis_results(input_file, output_dir, final_scores, mbti_result)

            success_rate = successful_segments / len(segments) * 100 if segments else 0
            print(f"✅ 分析完成: {Path(input_file).name}")
            print(f"📊 成功率: {success_rate:.1f}% ({successful_segments}/{len(segments)})")

            return {
                'success': True,
                'file': input_file,
                'success_rate': success_rate,
                'final_scores': final_scores,
                'mbti_result': mbti_result
            }

        except Exception as e:
            print(f"💥 分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'file': input_file
            }

    def calculate_final_scores(self) -> Dict:
        """计算最终Big5评分"""
        final_scores = {}

        for trait, data in self.big_five_traits.items():
            scores = data['scores']

            if scores:
                # 计算平均分
                avg_score = sum(scores) / len(scores)

                # 四舍五入到最接近的1、3、5
                if avg_score <= 2:
                    final_score = 1
                elif avg_score <= 4:
                    final_score = 3
                else:
                    final_score = 5

                # 计算置信度
                score_distribution = {1: 0, 3: 0, 5: 0}
                for score in scores:
                    score_distribution[score] += 1

                # 置信度计算：基于评分一致性
                max_count = max(score_distribution.values())
                consistency = max_count / len(scores)
                confidence = round(consistency * 100, 1)

                final_scores[trait] = {
                    'final_score': final_score,
                    'average_score': round(avg_score, 2),
                    'raw_scores': scores.copy(),
                    'score_distribution': score_distribution,
                    'confidence_percent': confidence,
                    'evidence_count': len(data['evidence']),
                    'weight': len(scores),
                    'evidence_samples': data['evidence'][:3]
                }
            else:
                final_scores[trait] = {
                    'final_score': 3,  # 默认中等分数
                    'average_score': 3.0,
                    'raw_scores': [],
                    'score_distribution': {1: 0, 3: 0, 5: 0},
                    'confidence_percent': 0.0,
                    'evidence_count': 0,
                    'weight': 0,
                    'evidence_samples': [],
                    'warning': 'No successful segment analysis'
                }

        return final_scores

    def generate_mbti_type(self, final_scores: Dict) -> Dict:
        """基于Big5评分生成MBTI类型"""
        O = final_scores.get('openness_to_experience', {}).get('final_score', 3)
        C = final_scores.get('conscientiousness', {}).get('final_score', 3)
        E = final_scores.get('extraversion', {}).get('final_score', 3)
        A = final_scores.get('agreeableness', {}).get('final_score', 3)
        N = final_scores.get('neuroticism', {}).get('final_score', 3)

        # MBTI计算逻辑
        e_score = E + (5 - N)
        i_score = (5 - E) + N
        E_preference = 'E' if e_score > i_score else 'I'
        E_confidence = abs(e_score - i_score) / 8

        S_confidence = abs(O - 3) / 2
        S_preference = 'N' if O > 3 else 'S'

        T_confidence = abs(A - 3) / 2
        T_preference = 'T' if A < 3 else 'F'

        J_confidence = abs(C - 3) / 2
        J_preference = 'J' if C > 3 else 'P'

        overall_confidence = (E_confidence + S_confidence + T_confidence + J_confidence) / 4

        mbti_type = f"{E_preference}{S_preference}{T_preference}{J_preference}"

        return {
            'type': mbti_type,
            'preferences': {
                'E/I': {'score': e_score, 'preference': E_preference, 'confidence': round(E_confidence * 100, 1)},
                'S/N': {'score': O, 'preference': S_preference, 'confidence': round(S_confidence * 100, 1)},
                'T/F': {'score': A, 'preference': T_preference, 'confidence': round(T_confidence * 100, 1)},
                'J/P': {'score': C, 'preference': J_preference, 'confidence': round(J_confidence * 100, 1)}
            },
            'overall_confidence': round(overall_confidence * 100, 1)
        }

    def save_analysis_results(self, input_file: str, output_dir: str, final_scores: Dict, mbti_result: Dict):
        """保存分析结果到分离的文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filename_base = Path(input_file).stem

        # 保存摘要文件（只包含评分和MBTI）
        summary_data = {
            'analysis_info': {
                'file_analyzed': input_file,
                'filename': Path(input_file).name,
                'analysis_timestamp': datetime.now().isoformat(),
                'model_used': self.model,
                'analyzer_type': 'enhanced_cloud_segmented_v1.0'
            },
            'big5_final_scores': {
                trait: {
                    'final_score': data['final_score'],
                    'confidence_percent': data['confidence_percent'],
                    'evidence_count': data['evidence_count']
                } for trait, data in final_scores.items()
            },
            'mbti_type': mbti_result['type'],
            'mbti_confidence': mbti_result['overall_confidence'],
            'analysis_quality': {
                'successful_segments': sum(1 for r in self.segment_results if r['success']),
                'total_segments': len(self.segment_results),
                'success_rate': sum(1 for r in self.segment_results if r['success']) / len(self.segment_results) * 100 if self.segment_results else 0
            }
        }

        summary_file = output_path / f"{filename_base}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        # 保存详细证据文件（包含所有评分依据）
        evidence_data = {
            'analysis_info': summary_data['analysis_info'],
            'detailed_scores': final_scores,
            'mbti_detailed': mbti_result,
            'segment_results': self.segment_results,
            'raw_traits_data': self.big_five_traits
        }

        evidence_file = output_path / f"{filename_base}_detailed_evidence.json"
        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(evidence_data, f, ensure_ascii=False, indent=2)

        print(f"📄 摘要文件: {summary_file.name}")
        print(f"📋 详细证据文件: {evidence_file.name}")

        # 打印最终结果摘要
        print(f"🎯 Big5最终评分:")
        for trait, data in final_scores.items():
            confidence = data['confidence_percent']
            print(f"  {trait}: {data['final_score']}/5 (置信度: {confidence}%, 基于{data['weight']}个证据)")
        print(f"🧠 MBTI类型: {mbti_result['type']} (置信度: {mbti_result['overall_confidence']}%)")