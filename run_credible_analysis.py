#!/usr/bin/env python3
"""
可信评估分析脚本
用于分析results/results目录下的所有测评报告文件
使用真实的评估器模型进行可信分析，并将完成的报告移动到finishedAnalyze目录
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

# 添加项目根目录到路径
import sys
sys.path.append(str(Path(__file__).parent))

from analyze_assessment_reports import BigFiveEvaluator


def setup_logging():
    """设置日志"""
    log_filename = f"credible_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def get_all_json_files(base_path: Path) -> List[Path]:
    """获取所有JSON文件（递归搜索）"""
    json_files = []
    
    # 先添加根目录的JSON文件
    json_files.extend(base_path.glob("*.json"))
    
    # 再添加所有子目录中的JSON文件（除了finishedAnalyze）
    for subdir in base_path.iterdir():
        if subdir.is_dir() and subdir.name != "finishedAnalyze":
            json_files.extend(subdir.glob("*.json"))
    
    return json_files


def extract_basic_parameters(assessment_data: Dict) -> Dict:
    """从测评报告中提取基础参数"""
    metadata = assessment_data.get('assessment_metadata', {})
    
    return {
        'model_id': metadata.get('model_id', 'Unknown'),
        'test_name': metadata.get('test_name', 'Unknown'),
        'role_name': metadata.get('role_name', 'Unknown'),
        'role_mbti_type': metadata.get('role_mbti_type', 'Unknown'),
        'timestamp': metadata.get('timestamp', 'Unknown'),
        'tested_model': metadata.get('tested_model', 'Unknown')
    }


def analyze_single_report(file_path: Path, evaluator: BigFiveEvaluator, output_dir: Path) -> bool:
    """分析单个测评报告"""
    logger = logging.getLogger(__name__)
    
    try:
        # 解析测评报告
        assessment_data = evaluator.parse_assessment_file(str(file_path))
        if not assessment_data:
            logger.error(f"无法解析文件: {file_path}")
            return False
        
        # 提取基础参数
        basic_params = extract_basic_parameters(assessment_data)
        
        # 计算大五人格分数
        responses = evaluator.extract_responses(assessment_data)
        if not responses:
            logger.error(f"文件中没有找到响应数据: {file_path}")
            return False
        
        dimension_scores = evaluator.calculate_dimension_scores(responses)
        final_scores = evaluator.calculate_final_scores(dimension_scores)
        mbti_type = evaluator.map_to_mbti(final_scores)
        
        # 输出基础信息
        logger.info(f"文件: {file_path.name}")
        logger.info(f"  模型: {basic_params['model_id']}")
        logger.info(f"  角色: {basic_params['role_name']}")
        logger.info(f"  角色MBTI: {basic_params['role_mbti_type']}")
        logger.info(f"  大五人格分数: E={final_scores.get('E', 0):.2f}, A={final_scores.get('A', 0):.2f}, C={final_scores.get('C', 0):.2f}, N={final_scores.get('N', 0):.2f}, O={final_scores.get('O', 0):.2f}")
        logger.info(f"  评估MBTI: {mbti_type}")
        logger.info("-" * 50)
        
        # 生成评估报告
        report_path = evaluator.generate_evaluation_report(str(file_path), str(output_dir))
        if report_path:
            logger.info(f"  评估报告已生成: {Path(report_path).name}")
        else:
            logger.error(f"  生成评估报告失败: {file_path.name}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"分析文件时出错 {file_path}: {e}")
        return False


def main():
    logger = setup_logging()
    logger.info("开始可信评估分析")
    
    # 设置路径
    base_path = Path("D:/AIDevelop/portable_psyagent/results/results")
    finished_dir = base_path / "finishedAnalyze"
    output_dir = base_path / "out1"  # 使用已存在的目录存放评估报告
    
    # 创建finishedAnalyze目录
    finished_dir.mkdir(exist_ok=True)
    
    # 获取所有JSON文件
    json_files = get_all_json_files(base_path)
    logger.info(f"找到 {len(json_files)} 个JSON测评报告文件")
    
    # 初始化评估器
    evaluator = BigFiveEvaluator()
    
    # 统计
    total_files = len(json_files)
    success_count = 0
    error_count = 0
    
    # 处理每个文件
    for i, json_file in enumerate(json_files, 1):
        logger.info(f"[{i}/{total_files}] 正在分析: {json_file.name}")
        
        # 分析报告
        success = analyze_single_report(json_file, evaluator, output_dir)
        
        if success:
            success_count += 1
            # 移动文件到finishedAnalyze目录
            dest_path = finished_dir / json_file.name
            try:
                shutil.move(str(json_file), str(dest_path))
                logger.info(f"  文件已移动到: {dest_path}")
            except Exception as e:
                logger.error(f"  移动文件失败: {e}")
        else:
            error_count += 1
    
    # 输出总结
    logger.info("=" * 50)
    logger.info("分析完成!")
    logger.info(f"总计: {total_files}")
    logger.info(f"成功: {success_count}")
    logger.info(f"失败: {error_count}")
    logger.info(f"输出目录: {output_dir}")
    logger.info(f"已完成分析的文件目录: {finished_dir}")


if __name__ == "__main__":
    main()