#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复所有模块中的相对导入问题
确保所有模块都能正确导入
"""

import os
import re
from pathlib import Path


def fix_relative_imports():
    """修复所有模块中的相对导入问题"""
    pipeline_dir = Path("D:/AIDevelop/portable_psyagent/single_report_pipeline")
    
    # 需要修复的导入语句
    import_fixes = [
        ("from .context_generator import", "from .context_generator import"),
        ("from .reverse_scoring_processor import", "from .reverse_scoring_processor import"),
        ("from .input_parser import", "from .input_parser import"),
        ("from .transparent_pipeline import", "from .transparent_pipeline import"),
        ("from .pipeline import", "from .pipeline import"),
        ("from .batch_processor import", "from .batch_processor import"),
        ("from .demo_pipeline import", "from .demo_pipeline import"),
        ("from .process_single_report import", "from .process_single_report import"),
        ("from .process_real_report import", "from .process_real_report import"),
        ("from .validate_models import", "from .validate_models import"),
        ("from .validate_pipeline_real_data import", "from .validate_pipeline_real_data import"),
        ("from .verify_bigfive import", "from .verify_bigfive import"),
        ("from .verify_bigfive_logic import", "from .verify_bigfive_logic import")
    ]
    
    # 遍历所有Python文件
    python_files = list(pipeline_dir.glob("*.py"))
    print(f"找到 {len(python_files)} 个Python文件")
    
    fixed_count = 0
    
    for py_file in python_files:
        try:
            # 读取文件内容
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否需要修复
            original_content = content
            for old_import, new_import in import_fixes:
                content = content.replace(old_import, new_import)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ 修复文件: {py_file.name}")
                fixed_count += 1
                
        except Exception as e:
            print(f"  ❌ 修复文件 {py_file.name} 时出错: {e}")
            continue
    
    print(f"\n总共修复了 {fixed_count} 个文件")
    return fixed_count


def main():
    """主函数"""
    print("修复所有模块中的相对导入问题")
    print("="*60)
    
    try:
        fixed_count = fix_relative_imports()
        print(f"\n{'='*60}")
        print(f"修复完成! 共修复 {fixed_count} 个文件")
        print(f"现在可以正常导入所有模块了!")
    except Exception as e:
        print(f"\n❌ 修复过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()