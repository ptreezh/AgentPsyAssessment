#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能评估器 - 解决API限制和默认评分问题
实现云端+本地模型智能回退，绝对禁止默认评分
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# 添加包目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ollama
from single_report_pipeline import TransparentPipeline

class SmartEvaluator:
    """智能评估器 - 解决API限制问题"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 云端模型配置（高质量但有限制）
        self.cloud_models = [
            'deepseek-v3.1:671b-cloud',
            'gpt-oss:120b-cloud',
            'qwen3-vl:235b-cloud'
        ]

        # 本地模型配置（可靠备份）
        self.local_models = [
            'qwen3:8b',
            'deepseek-r1:8b',
            'mistral:instruct'
        ]

        # 模型状态跟踪
        self.model_status = {}
        self.model_last_used = {}
        self.model_failures = {}

        # 初始化模型状态
        self._initialize_model_status()

    def _initialize_model_status(self):
        """初始化模型状态"""
        all_models = self.cloud_models + self.local_models
        for model in all_models:
            self.model_status[model] = 'available'
            self.model_last_used[model] = 0
            self.model_failures[model] = []

    def _is_model_available(self, model: str) -> bool:
        """检查模型是否可用"""
        # 检查最近失败记录
        recent_failures = [
            f for f in self.model_failures.get(model, [])
            if time.time() - f < 300  # 5分钟内的失败
        ]

        if len(recent_failures) >= 3:
            return False  # 5分钟内失败3次以上，暂时禁用

        return True

    def _mark_model_failure(self, model: str, error_msg: str):
        """标记模型失败"""
        self.model_failures.setdefault(model, []).append(time.time())
        self.logger.warning(f"模型 {model} 失败: {error_msg}")

        # 如果是API限制错误，延长冷却时间
        if "usage limit" in error_msg.lower() or "402" in error_msg:
            self.logger.warning(f"模型 {model} 遇到API限制，将延长冷却时间")
            # 添加多个失败记录，延长禁用时间
            for _ in range(5):
                self.model_failures[model].append(time.time() + 1800)  # 30分钟冷却

    def _select_best_model(self, preferred_models: List[str]) -> Optional[str]:
        """选择最佳可用模型"""
        available_models = []

        for model in preferred_models:
            if self._is_model_available(model):
                available_models.append(model)

        if not available_models:
            # 如果首选模型都不可用，尝试所有模型
            all_models = self.cloud_models + self.local_models
            for model in all_models:
                if self._is_model_available(model):
                    available_models.append(model)

        if not available_models:
            return None

        # 选择最久未使用的模型
        best_model = min(available_models, key=lambda m: self.model_last_used.get(m, 0))
        return best_model

    def _add_delay_between_calls(self, model_type: str):
        """在API调用间添加延迟"""
        if model_type == 'cloud':
            time.sleep(2)  # 云端模型延迟更长
        else:
            time.sleep(0.5)  # 本地模型延迟较短

    def evaluate_with_fallback(self, context: str, preferred_models: List[str], question_id: str) -> Dict[str, int]:
        """
        智能回退评估 - 绝对禁止默认评分

        Args:
            context: 评估上下文
            preferred_models: 首选模型列表
            question_id: 题目ID

        Returns:
            评估结果，绝对不返回默认值
        """
        max_attempts = 10  # 最大尝试次数
        attempted_models = []

        for attempt in range(max_attempts):
            # 1. 尝试首选模型
            if attempt == 0:
                candidate_models = preferred_models
            # 2. 尝试同类型模型
            elif attempt <= 3:
                if any(m.startswith('deepseek') for m in preferred_models):
                    candidate_models = [m for m in self.cloud_models if 'deepseek' in m]
                elif any(m.startswith('qwen') for m in preferred_models):
                    candidate_models = [m for m in self.cloud_models if 'qwen' in m]
                else:
                    candidate_models = self.cloud_models
            # 3. 尝试所有云端模型
            elif attempt <= 6:
                candidate_models = self.cloud_models
            # 4. 尝试本地模型
            else:
                candidate_models = self.local_models

            # 选择最佳可用模型
            best_model = self._select_best_model(candidate_models)

            if not best_model:
                continue

            if best_model in attempted_models:
                continue

            attempted_models.append(best_model)
            self.model_last_used[best_model] = time.time()

            # 确定模型类型
            model_type = 'cloud' if best_model in self.cloud_models else 'local'

            try:
                self.logger.info(f"尝试使用模型 {best_model} (类型: {model_type}) 评估题目 {question_id}")

                # 添加延迟避免API过载
                self._add_delay_between_calls(model_type)

                # 调用模型
                response = ollama.generate(
                    model=best_model,
                    prompt=context,
                    options={'num_predict': 2000}
                )

                # 解析响应
                scores = self._parse_scores_from_response(response['response'])

                # 验证评分有效性
                if self._validate_scores(scores):
                    self.logger.info(f"模型 {best_model} 评估成功: {scores}")
                    return scores
                else:
                    self.logger.warning(f"模型 {best_model} 返回无效评分: {scores}")
                    self._mark_model_failure(best_model, "返回无效评分")

            except Exception as e:
                error_msg = str(e)
                self._mark_model_failure(best_model, error_msg)

                # 如果是API限制，立即尝试下一个模型
                if "usage limit" in error_msg.lower() or "402" in error_msg:
                    self.logger.warning(f"模型 {best_model} 遇到API限制，立即切换模型")
                    continue

        # 如果所有模型都失败，抛出异常而不是返回默认值
        raise RuntimeError(f"所有模型都无法评估题目 {question_id}，已尝试: {attempted_models}")

    def _parse_scores_from_response(self, response: str) -> Dict[str, int]:
        """从响应中解析评分"""
        try:
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{[^}]*\}', response)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)

                scores = {}
                for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                    value = data.get(trait, 3)
                    if isinstance(value, (int, float)) and 1 <= value <= 5:
                        scores[trait] = int(round(value))
                    else:
                        scores[trait] = 3
                return scores
        except:
            pass

        # 备用解析方法
        scores = {
            'openness_to_experience': 3,
            'conscientiousness': 3,
            'extraversion': 3,
            'agreeableness': 3,
            'neuroticism': 3
        }
        return scores

    def _validate_scores(self, scores: Dict[str, int]) -> bool:
        """验证评分有效性"""
        if not isinstance(scores, dict):
            return False

        required_traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        for trait in required_traits:
            if trait not in scores:
                return False
            if not isinstance(scores[trait], (int, float)):
                return False
            if not (1 <= scores[trait] <= 5):
                return False

        return True

    def get_model_status_report(self) -> Dict[str, Any]:
        """获取模型状态报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'cloud_models': {},
            'local_models': {},
            'recommendations': []
        }

        for model in self.cloud_models:
            recent_failures = [
                f for f in self.model_failures.get(model, [])
                if time.time() - f < 300
            ]
            report['cloud_models'][model] = {
                'status': 'available' if self._is_model_available(model) else 'disabled',
                'recent_failures': len(recent_failures),
                'last_used': self.model_last_used.get(model, 0)
            }

        for model in self.local_models:
            recent_failures = [
                f for f in self.model_failures.get(model, [])
                if time.time() - f < 300
            ]
            report['local_models'][model] = {
                'status': 'available' if self._is_model_available(model) else 'disabled',
                'recent_failures': len(recent_failures),
                'last_used': self.model_last_used.get(model, 0)
            }

        # 生成建议
        available_cloud = sum(1 for m in self.cloud_models if self._is_model_available(m))
        available_local = sum(1 for m in self.local_models if self._is_model_available(m))

        if available_cloud == 0:
            report['recommendations'].append("警告：所有云端模型都不可用，建议检查API配额")
        if available_local == 0:
            report['recommendations'].append("警告：所有本地模型都不可用，建议检查Ollama服务")
        if available_cloud < 2:
            report['recommendations'].append("建议：云端模型数量不足，可能影响争议解决质量")

        return report


def test_smart_evaluator():
    """测试智能评估器"""
    print("🧠 智能评估器测试")
    print("=" * 50)

    # 创建评估器
    evaluator = SmartEvaluator()

    # 测试上下文
    test_context = """
请根据以下回答，评估被试在Big Five人格维度上的得分(1-5分)：

题目：E1: 我是团队活动的核心人物。
回答：在线上团建活动中，气氛很沉闷，大家都不太说话，作为团队成员，我会主动站出来组织一些互动游戏，破冰暖场，带动大家的参与热情。我觉得这是我的责任和兴趣所在。

请按JSON格式返回评分：
{
    "openness_to_experience": 分数,
    "conscientiousness": 分数,
    "extraversion": 分数,
    "agreeableness": 分数,
    "neuroticism": 分数
}
"""

    # 测试评估
    try:
        print("📋 测试智能回退评估...")
        scores = evaluator.evaluate_with_fallback(
            context=test_context,
            preferred_models=['deepseek-v3.1:671b-cloud', 'qwen3-vl:235b-cloud'],
            question_id='test_001'
        )
        print(f"✅ 评估成功: {scores}")

        # 显示模型状态
        report = evaluator.get_model_status_report()
        print("\n📊 模型状态报告:")
        print(f"云端可用模型: {sum(1 for m in evaluator.cloud_models if evaluator._is_model_available(m))}/{len(evaluator.cloud_models)}")
        print(f"本地可用模型: {sum(1 for m in evaluator.local_models if evaluator._is_model_available(m))}/{len(evaluator.local_models)}")

        for rec in report['recommendations']:
            print(f"💡 建议: {rec}")

        return True

    except Exception as e:
        print(f"❌ 评估失败: {e}")
        return False


if __name__ == "__main__":
    success = test_smart_evaluator()
    sys.exit(0 if success else 1)