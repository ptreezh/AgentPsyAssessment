#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强健的统一评估系统 - 具备智能容错能力
支持多种测试文件格式，提供优雅的错误处理和向后兼容
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RobustAssessmentSystem:
    """强健的统一评估系统"""

    def __init__(self):
        self.supported_formats = [
            "traditional_test_bank",    # 传统 test_bank 格式
            "unified_questions",       # 统一 assessment_questions 格式
            "simplified",              # 简化格式
            "custom"                  # 自定义格式
        ]

        self.format_detectors = {
            "traditional_test_bank": self._detect_traditional_format,
            "unified_questions": self._detect_unified_format,
            "simplified": self._detect_simplified_format,
            "custom": self._detect_custom_format
        }

        self.format_processors = {
            "traditional_test_bank": self._process_traditional_format,
            "unified_questions": self._process_unified_format,
            "simplified": self._process_simplified_format,
            "custom": self._process_custom_format
        }

    def detect_format(self, file_path: Union[str, Path]) -> str:
        """智能检测文件格式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)

            logger.info(f"检测文件格式: {file_path}")

            # 按优先级检测格式
            for format_name, detector in self.format_detectors.items():
                if detector(content):
                    logger.info(f"✅ 检测到格式: {format_name}")
                    return format_name

            logger.warning("⚠️ 未检测到已知格式，使用默认处理器")
            return "simplified"

        except Exception as e:
            logger.error(f"❌ 文件读取失败: {e}")
            return "simplified"

    def _detect_traditional_format(self, content: Dict) -> bool:
        """检测传统 test_bank 格式"""
        return "test_bank" in content and isinstance(content.get("test_bank"), list)

    def _detect_unified_format(self, content: Dict) -> bool:
        """检测统一 assessment_questions 格式"""
        return ("assessment_questions" in content and
                isinstance(content.get("assessment_questions"), list)) or \
               ("assessment_metadata" in content and
                "test_info" in content)

    def _detect_simplified_format(self, content: Dict) -> bool:
        """检测简化格式"""
        # 简化格式：只有基本元数据和问题列表
        return ("questions" in content and isinstance(content.get("questions"), list)) or \
               ("items" in content and isinstance(content.get("items"), list))

    def _detect_custom_format(self, content: Dict) -> bool:
        """检测自定义格式"""
        # 任何包含问题内容的格式都算自定义
        keys_to_check = ["questions", "items", "test_items", "problems", "scenarios",
                         "assessment_items", "test_questions", "questionnaire", "survey"]
        return any(key in content for key in keys_to_check)

    def process_file(self, file_path: Union[str, Path],
                       personality_params: Optional[Dict] = None) -> Dict[str, Any]:
        """处理评估文件，具有完整容错能力"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 检测格式
            format_type = self.detect_format(file_path)

            # 使用对应的处理器
            processor = self.format_processors[format_type]
            processed_data = processor(file_path, personality_params)

            # 添加元数据
            processed_data["system_info"] = {
                "format_type": format_type,
                "file_path": str(file_path),
                "processing_time": datetime.now().isoformat(),
                "system_version": "1.0.0",
                "robust_mode": True
            }

            logger.info(f"✅ 成功处理文件: {file_path} (格式: {format_type})")
            return processed_data

        except Exception as e:
            logger.error(f"❌ 文件处理失败: {e}")
            # 返回错误结果而不是崩溃
            return self._create_error_result(file_path, str(e), personality_params)

    def _process_traditional_format(self, file_path: Path,
                                   personality_params: Optional[Dict] = None) -> Dict:
        """处理传统 test_bank 格式"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        # 转换为统一格式
        unified_questions = []

        for item in content.get("test_bank", []):
            unified_question = {
                "question_id": item.get("question_id", f"Q_{len(unified_questions) + 1}"),
                "question": item.get("prompt_for_agent", ""),
                "scenario": item.get("scenario", ""),
                "dimension": item.get("dimension", "general"),
                "evaluation_rubric": item.get("evaluation_rubric", {}),
                "original_format": "traditional"
            }
            unified_questions.append(unified_question)

        return {
            "assessment_metadata": content.get("test_info", {}),
            "assessment_questions": unified_questions,
            "original_content": content
        }

    def _process_unified_format(self, file_path: Path,
                               personality_params: Optional[Dict] = None) -> Dict:
        """处理统一 assessment_questions 格式"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        # 已经是统一格式，直接返回
        return content

    def _process_simplified_format(self, file_path: Path,
                                  personality_params: Optional[Dict] = None) -> Dict:
        """处理简化格式"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        # 尝试提取问题列表
        questions_field = None
        for field in ["questions", "items", "test_items", "problems", "scenarios"]:
            if field in content:
                questions_field = field
                break

        if not questions_field:
            logger.warning("⚠️ 未找到问题字段，创建默认问题")
            return self._create_default_assessment(file_path, personality_params)

        questions = content[questions_field]
        unified_questions = []

        for i, item in enumerate(questions):
            if isinstance(item, str):
                # 简单字符串格式
                unified_question = {
                    "question_id": f"Q_{i+1}",
                    "question": item,
                    "dimension": "general",
                    "evaluation_rubric": {
                        "description": "基于回答内容进行综合评估"
                    }
                }
            elif isinstance(item, dict):
                # 对象格式
                unified_question = {
                    "question_id": item.get("id", item.get("question_id", f"Q_{i+1}")),
                    "question": item.get("question", item.get("text", item.get("content", ""))),
                    "dimension": item.get("dimension", "general"),
                    "evaluation_rubric": item.get("rubric", item.get("evaluation", {})),
                    "scenario": item.get("scenario", ""),
                    "original_format": "simplified"
                }
            else:
                continue

            unified_questions.append(unified_question)

        return {
            "assessment_metadata": {
                "test_name": f"简化格式评估 - {file_path.name}",
                "format": "simplified",
                "total_questions": len(unified_questions)
            },
            "assessment_questions": unified_questions,
            "original_content": content
        }

    def _process_custom_format(self, file_path: Path,
                             personality_params: Optional[Dict] = None) -> Dict:
        """处理自定义格式"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        logger.info(f"🔍 处理自定义格式文件: {file_path.name}")

        # 智能提取问题内容
        unified_questions = []

        # 查找可能的问题字段
        potential_question_fields = []
        for key, value in content.items():
            if key in ["questions", "items", "test_items", "problems", "scenarios"]:
                if isinstance(value, list):
                    potential_question_fields.append((key, value))
                elif isinstance(value, dict):
                    potential_question_fields.append((key, list(value.values())))

        if potential_question_fields:
            # 使用第一个找到的问题字段
            field_name, questions_data = potential_question_fields[0]
            logger.info(f"📝 使用问题字段: {field_name}")

            for i, item in enumerate(questions_data):
                question_text = item.get("question", item.get("text", item.get("content", "")))
                unified_question = {
                    "question_id": item.get("id", item.get("question_id", f"Q_{i+1}")),
                    "question": str(question_text)[0:500],  # 限制长度
                    "dimension": item.get("dimension", "general"),
                    "evaluation_rubric": item.get("rubric", item.get("evaluation", {})),
                    "original_field": field_name
                }
                unified_questions.append(unified_question)
        else:
            logger.warning("⚠️ 未找到可用问题字段，创建默认评估")
            return self._create_default_assessment(file_path, personality_params)

        return {
            "assessment_metadata": {
                "test_name": f"自定义格式评估 - {file_path.name}",
                "format": "custom",
                "field_used": field_name if potential_question_fields else "none",
                "total_questions": len(unified_questions)
            },
            "assessment_questions": unified_questions,
            "original_content": content
        }

    def _create_default_assessment(self, file_path: Path,
                                personality_params: Optional[Dict] = None) -> Dict:
        """创建默认评估内容"""
        logger.info("🔄 创建默认评估内容")

        default_questions = [
            {
                "question_id": "Q1",
                "question": "请描述您的个人特点和动机。",
                "dimension": "general",
                "evaluation_rubric": {
                    "description": "基于回答内容进行综合评估"
                }
            },
            {
                "question_id": "Q2",
                "question": "面对挑战时，您通常会如何应对？",
                "dimension": "challenge",
                "evaluation_rubric": {
                    "description": "评估应对挑战的方式和能力"
                }
            },
            {
                "question_id": "Q3",
                "question": "您认为什么样的事情最有意义？",
                "dimension": "values",
                "evaluation_rubric": {
                    "description": "评估价值观和人生意义观"
                }
            }
        ]

        return {
            "assessment_metadata": {
                "test_name": f"默认评估 - {file_path.name}",
                "format": "default",
                "total_questions": len(default_questions),
                "auto_generated": True
            },
            "assessment_questions": default_questions,
            "warning": "使用默认评估内容，建议提供具体的测试文件"
        }

    def _create_error_result(self, file_path: Union[str, Path], error_message: str,
                           personality_params: Optional[Dict] = None) -> Dict:
        """创建错误结果"""
        logger.error(f"🚨 创建错误结果: {error_message}")

        return {
            "assessment_metadata": {
                "test_name": f"错误处理 - {Path(file_path).name}",
                "format": "error",
                "error": True,
                "error_message": error_message
            },
            "assessment_questions": [],
            "system_info": {
                "error_occurred": True,
                "error_time": datetime.now().isoformat(),
                "robust_mode": True
            },
            "original_file_path": str(file_path)
        }

    def validate_processed_data(self, data: Dict) -> bool:
        """验证处理后的数据"""
        if not isinstance(data, dict):
            logger.error("❌ 处理后的数据不是字典格式")
            return False

        if "assessment_questions" not in data:
            logger.error("❌ 缺少 assessment_questions 字段")
            return False

        questions = data.get("assessment_questions", [])
        if not isinstance(questions, list):
            logger.error("❌ assessment_questions 不是列表格式")
            return False

        if len(questions) == 0:
            logger.warning("⚠️ 没有找到任何问题")
            return False

        # 验证每个问题字段
        for i, question in enumerate(questions):
            if not isinstance(question, dict):
                logger.error(f"❌ 问题 {i+1} 不是字典格式")
                return False

            if "question_id" not in question:
                logger.warning(f"⚠️ 问题 {i+1} 缺少 question_id")

            if "question" not in question or not question["question"].strip():
                logger.warning(f"⚠️ 问题 {i+1} 缺少或内容为空")

        return True

    def run_assessment(self, file_path: Union[str, Path],
                        personality_params: Optional[Dict] = None) -> Dict[str, Any]:
        """运行完整的评估流程"""
        try:
            logger.info(f"🚀 开始强健评估: {file_path}")

            # 处理文件
            processed_data = self.process_file(file_path, personality_params)

            # 验证数据
            if not self.validate_processed_data(processed_data):
                logger.error("❌ 数据验证失败")
                return processed_data

            # 执行评估（这里可以集成实际的评估逻辑）
            logger.info("📊 执行评估分析...")

            # 生成评估结果
            assessment_result = {
                "success": True,
                "total_questions": len(processed_data.get("assessment_questions", [])),
                "processed_format": processed_data.get("system_info", {}).get("format_type", "unknown"),
                "file_path": str(file_path),
                "processing_time": processed_data.get("system_info", {}).get("processing_time"),
                "validation_passed": True
            }

            # 添加到处理结果中
            processed_data["assessment_result"] = assessment_result

            logger.info("✅ 评估完成")
            return processed_data

        except Exception as e:
            logger.error(f"❌ 评估流程失败: {e}")
            return self._create_error_result(file_path, str(e), personality_params)

def main():
    """演示强健评估系统"""
    system = RobustAssessmentSystem()

    print("🛡️ 强健统一评估系统演示")
    print("=" * 50)

    # 测试不同格式的文件
    test_files = [
        "llm_assessment/test_files/中文版/agent-motivation-test.json",  # 新格式
        # 可以添加更多测试文件
    ]

    for file_path in test_files:
        print(f"\n📋 测试文件: {file_path}")
        print("-" * 30)

        result = system.run_assessment(file_path)

        if result.get("assessment_result", {}).get("success", False):
            print("✅ 处理成功")
            print(f"📊 格式类型: {result.get('system_info', {}).get('format_type', 'unknown')}")
            print(f"📝 问题数量: {result.get('assessment_result', {}).get('total_questions', 0)}")
        else:
            print("❌ 处理失败")
            print(f"⚠️ 错误信息: {result.get('assessment_metadata', {}).get('error_message', '未知错误')}")

if __name__ == "__main__":
    main()