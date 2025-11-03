#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告管理器
处理评估报告的完成标记和文件移动
"""

import sys
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class ReportManager:
    """
    报告管理器
    """
    def __init__(self, base_dir: str = "results"):
        self.base_dir = Path(base_dir)
        self.original_dir = self.base_dir / "readonly-original"
        self.ok_dir = self.base_dir / "ok"
        self.ok_original_dir = self.ok_dir / "original"
        self.ok_evaluated_dir = self.ok_dir / "evaluated"
        
        # 创建必要的目录
        self.ok_original_dir.mkdir(parents=True, exist_ok=True)
        self.ok_evaluated_dir.mkdir(parents=True, exist_ok=True)

    def mark_report_complete(self, report_path: str, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        标记报告为已完成并移动文件
        :param report_path: 原始报告路径
        :param evaluation_result: 评估结果
        :return: 处理结果
        """
        try:
            original_path = Path(report_path)
            
            if not original_path.exists():
                return {
                    "success": False,
                    "error": f"原始文件不存在: {report_path}"
                }
            
            # 创建完成标记信息
            completion_info = {
                "completed_date": datetime.now().isoformat(),
                "evaluation_result_summary": {
                    "success": evaluation_result.get('success', False),
                    "consistency_score": evaluation_result.get('consistency_score', 0),
                    "reliability_score": evaluation_result.get('reliability_score', 0),
                    "reliability_passed": evaluation_result.get('reliability_passed', False),
                    "models_used": [model['name'] for model in evaluation_result.get('models_used', [])] if evaluation_result.get('models_used') else []
                }
            }
            
            # 移动原始文件到ok/original目录
            dest_original_path = self.ok_original_dir / original_path.name
            if dest_original_path.exists():
                # 添加时间戳避免覆盖
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_original_path = self.ok_original_dir / f"{original_path.stem}_{timestamp}{original_path.suffix}"
            
            shutil.move(str(original_path), str(dest_original_path))
            
            # 如果有评估结果文件，也移动到ok/evaluated目录
            evaluated_result_path = evaluation_result.get('output_path')
            dest_evaluated_path = None
            if evaluated_result_path:
                evaluated_path = Path(evaluated_result_path)
                if evaluated_path.exists():
                    dest_evaluated_path = self.ok_evaluated_dir / evaluated_path.name
                    if dest_evaluated_path.exists():
                        # 添加时间戳避免覆盖
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dest_evaluated_path = self.ok_evaluated_dir / f"{evaluated_path.stem}_{timestamp}{evaluated_path.suffix}"
                    
                    # 复制而不是移动，因为可能需要保留输出目录
                    shutil.copy2(str(evaluated_path), str(dest_evaluated_path))
            
            # 保存完成标记信息到评估结果文件中
            if dest_evaluated_path:
                try:
                    with open(dest_evaluated_path, 'r+', encoding='utf-8') as f:
                        data = json.load(f)
                        data['completion_info'] = completion_info
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"⚠️ 无法更新评估结果文件: {e}")
            
            return {
                "success": True,
                "original_moved_to": str(dest_original_path),
                "evaluated_moved_to": str(dest_evaluated_path) if dest_evaluated_path else None,
                "completion_info": completion_info,
                "message": f"报告已处理完成，原始文件移至: {dest_original_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"处理报告时发生错误: {str(e)}"
            }

    def check_completed_reports(self) -> Dict[str, Any]:
        """
        检查已完成的报告
        :return: 完成报告统计
        """
        original_files = list(self.ok_original_dir.glob("*.json"))
        evaluated_files = list(self.ok_evaluated_dir.glob("*.json"))
        
        return {
            "completed_original_count": len(original_files),
            "completed_evaluated_count": len(evaluated_files),
            "original_files": [str(f) for f in original_files],
            "evaluated_files": [str(f) for f in evaluated_files],
            "last_updated": datetime.now().isoformat()
        }

    def get_report_status(self, report_name: str) -> Dict[str, Any]:
        """
        获取特定报告的处理状态
        :param report_name: 报告文件名
        :return: 报告状态
        """
        original_path = self.ok_original_dir / report_name
        evaluated_path = self.ok_evaluated_dir / f"{Path(report_name).stem}_segmented_scoring_evaluation.json"
        
        status = {
            "report_name": report_name,
            "original_exists": original_path.exists(),
            "evaluated_exists": evaluated_path.exists(),
            "status": "unknown"
        }
        
        if original_path.exists() and evaluated_path.exists():
            status["status"] = "completed"
        elif original_path.exists():
            status["status"] = "moved_original_only"
        elif evaluated_path.exists():
            status["status"] = "evaluated_only"
        else:
            status["status"] = "not_found"
        
        # 如果评估文件存在，尝试读取其中的完成信息
        if evaluated_path.exists():
            try:
                with open(evaluated_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'completion_info' in data:
                        status["completion_info"] = data["completion_info"]
            except:
                pass
        
        return status


def main():
    """
    主函数 - 演示用法
    """
    # 创建报告管理器实例
    manager = ReportManager()
    
    # 检查已完成的报告
    stats = manager.check_completed_reports()
    print("已完成报告统计:")
    print(f"  原始文件数量: {stats['completed_original_count']}")
    print(f"  评估文件数量: {stats['completed_evaluated_count']}")
    print(f"  最后更新: {stats['last_updated']}")


if __name__ == "__main__":
    main()