import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List

def collect_test_results(results_dir: str) -> List[Dict]:
    """收集所有测试结果文件 - 修复空文档问题"""
    results = []
    
    if not os.path.exists(results_dir):
        print(f"结果目录不存在: {results_dir}")
        return results
    
    # 遍历结果目录
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    # 检查文件大小
                    file_size = os.path.getsize(file_path)
                    if file_size == 0:
                        print(f"跳过空文件: {file_path}")
                        continue
                    
                    # 尝试多种编码方式读取文件
                    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']
                    data = None
                    
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read().strip()
                                if not content:
                                    print(f"文件内容为空: {file_path}")
                                    continue
                                data = json.loads(content)
                            break
                        except UnicodeDecodeError:
                            continue
                        except json.JSONDecodeError as e:
                            print(f"JSON解析错误 {file_path}: {e}")
                            continue
                    
                    if data is None:
                        print(f"无法读取文件: {file_path}")
                        continue
                    
                    # 提取元数据 - 支持多种格式
                    metadata = {}
                    
                    # 优先从assessment_metadata提取
                    if 'assessment_metadata' in data:
                        metadata = data['assessment_metadata']
                    else:
                        # 从根级字段提取
                        metadata_fields = [
                            'tested_model', 'role_applied', 'test_name', 
                            'assessment_start_time', 'role_mbti_type',
                            'interference_level', 'assessment_end_time'
                        ]
                        for field in metadata_fields:
                            if field in data:
                                metadata[field] = data[field]
                    
                    # 如果还是缺少关键信息，从文件名提取
                    if not metadata.get('tested_model'):
                        filename_parts = file.replace('.json', '').split('_')
                        if len(filename_parts) >= 1:
                            metadata['tested_model'] = filename_parts[0]
                    
                    if not metadata.get('test_name'):
                        filename_parts = file.replace('.json', '').split('_')
                        if len(filename_parts) >= 2:
                            metadata['test_name'] = '_'.join(filename_parts[1:])
                    
                    # 清理角色名称
                    role_name = metadata.get('role_applied', 'Unknown')
                    if not isinstance(role_name, str):
                        role_name = str(role_name)
                    
                    # 处理编码问题
                    role_name = role_name.strip()
                    if '??' in role_name or '\ufffd' in role_name or len(role_name) > 100:
                        role_name = 'Unknown'
                    
                    results.append({
                        'file_path': file_path,
                        'model_id': metadata.get('tested_model', 'Unknown'),
                        'test_name': metadata.get('test_name', 'Unknown'),
                        'role_name': role_name,
                        'role_mbti_type': metadata.get('role_mbti_type', 'Unknown'),
                        'timestamp': metadata.get('assessment_start_time', 'Unknown'),
                        'stress_factors': {
                            'emotional_stress_level': metadata.get('interference_level', 0),
                            'cognitive_trap_type': 'none',
                            'context_load_tokens': 0,
                            'tmpr': None,
                            'context_length_mode': 'auto',
                            'context_length_static': 0,
                            'context_length_dynamic': '1/2'
                        },
                        'raw_data': data
                    })
                    
                except Exception as e:
                    print(f"处理文件错误 {file_path}: {e}")
                    continue
    
    print(f"收集完成: 找到 {len(results)} 个有效结果")
    return results

def standardize_test_conditions(result_entry: Dict) -> Dict:
    """标准化测试条件"""
    stress_factors = result_entry.get('stress_factors', {})
    
    return {
        'model_id': result_entry.get('model_id'),
        'test_name': result_entry.get('test_name'),
        'role_name': result_entry.get('role_name'),
        'role_mbti_type': result_entry.get('role_mbti_type'),
        'temperature': stress_factors.get('tmpr', 'default'),
        'emotional_stress_level': stress_factors.get('emotional_stress_level', 0),
        'cognitive_trap_type': stress_factors.get('cognitive_trap_type', 'none'),
        'context_length_mode': stress_factors.get('context_length_mode', 'auto'),
        'context_length_static': stress_factors.get('context_length_static', 0),
        'context_length_dynamic': stress_factors.get('context_length_dynamic', '1/2'),
        'timestamp': result_entry.get('timestamp')
    }

def extract_analyzed_mbti_type(scores_data: Dict) -> str:
    """从评分数据中提取分析得出的MBTI类型"""
    try:
        # 尝试从分析数据中提取MBTI类型
        if 'profile' in scores_data and 'mbti_type' in scores_data['profile']:
            return scores_data['profile']['mbti_type']
        elif 'mbti_type' in scores_data:
            return scores_data['mbti_type']
        else:
            return "Unknown"
    except Exception as e:
        print(f"Error extracting MBTI type: {e}")
        return "Unknown"

def evaluate_role_playing_ability(result_entry: Dict, scores_data: Dict) -> Dict:
    """评估角色扮演能力"""
    role_mbti = result_entry.get('role_mbti_type')
    if not role_mbti or role_mbti == 'Unknown':
        return {'ability': 'Unknown', 'reason': 'No role specified'}
    
    # 从scores_data中提取分析得出的MBTI类型
    analyzed_mbti = extract_analyzed_mbti_type(scores_data)
    
    if not analyzed_mbti or analyzed_mbti == "Unknown":
        return {'ability': 'Unknown', 'reason': 'Analysis failed'}
    
    # 比较设定角色与分析得出的角色
    matches = role_mbti == analyzed_mbti
    return {
        'ability': 'Successful' if matches else 'Failed',
        'set_role': role_mbti,
        'played_role': analyzed_mbti,
        'match': matches
    }

def compare_models_under_same_conditions(results: List[Dict]) -> pd.DataFrame:
    """在相同条件下对比不同模型"""
    # 标准化所有测试条件
    standardized_results = [standardize_test_conditions(r) for r in results]
    
    # 转换为DataFrame便于分析
    df = pd.DataFrame(standardized_results)
    
    # 按测试条件分组
    grouped = df.groupby([
        'test_name', 'role_name', 'temperature', 
        'emotional_stress_level', 'cognitive_trap_type',
        'context_length_mode'
    ])
    
    comparison_results = []
    for conditions, group in grouped:
        if len(group) > 1:  # 只有当有多个模型时才进行对比
            comparison_results.append({
                'conditions': conditions,
                'models': group['model_id'].tolist(),
                'count': len(group)
            })
    
    return pd.DataFrame(comparison_results)

def generate_summary_statistics(results: List[Dict]) -> str:
    """生成汇总统计"""
    if not results:
        return "无测试结果"
    
    # 模型统计
    model_counts = {}
    role_counts = {}
    test_counts = {}
    
    for result in results:
        # 统计模型
        model = result.get('model_id', 'Unknown')
        model_counts[model] = model_counts.get(model, 0) + 1
        
        # 统计角色
        role = result.get('role_name', 'Unknown')
        role_counts[role] = role_counts.get(role, 0) + 1
        
        # 统计测试
        test = result.get('test_name', 'Unknown')
        test_counts[test] = test_counts.get(test, 0) + 1
    
    # 生成统计文本
    stats_text = f"""
### 模型测试次数统计
{'\n'.join([f"- {model}: {count} 次" for model, count in model_counts.items()])}

### 角色使用频率统计
{'\n'.join([f"- {role}: {count} 次" for role, count in role_counts.items()])}

### 测试类型统计
{'\n'.join([f"- {test}: {count} 次" for test, count in test_counts.items()])}
    """
    
    return stats_text

def analyze_role_playing_abilities(results: List[Dict]) -> str:
    """分析角色扮演能力"""
    # 收集所有分析报告
    analysis_dir = "analysis_reports"
    role_playing_stats = []
    
    for result in results:
        # 查找对应的分析文件
        file_path = result.get('file_path', '')
        if not file_path:
            continue
            
        # 构造分析文件路径
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        # 检查多种可能的分析文件路径
        possible_paths = [
            os.path.join(analysis_dir, f"{base_name}_big5_mbti_analysis.json"),
            os.path.join(analysis_dir, base_name, "big5_mbti_analysis.json"),
            os.path.join(analysis_dir, base_name, f"{base_name}_big5_mbti_analysis.json")
        ]
        
        analysis_file = None
        for path in possible_paths:
            if os.path.exists(path):
                analysis_file = path
                break
        
        if analysis_file and os.path.exists(analysis_file):
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    scores_data = json.load(f)
                
                # 评估角色扮演能力
                ability = evaluate_role_playing_ability(result, scores_data)
                role_playing_stats.append({
                    'model': result.get('model_id', 'Unknown'),
                    'role': result.get('role_name', 'Unknown'),
                    'ability': ability
                })
            except Exception as e:
                print(f"Error analyzing {analysis_file}: {e}")
    
    # 统计角色扮演成功率
    successful_count = sum(1 for stat in role_playing_stats if stat['ability']['ability'] == 'Successful')
    total_count = len(role_playing_stats)
    
    if total_count > 0:
        success_rate = successful_count / total_count * 100
        stats_text = f"""
### 角色扮演能力统计
- 总评估次数: {total_count}
- 成功次数: {successful_count}
- 成功率: {success_rate:.2f}%

### 详细评估结果
{'\n'.join([f"- {stat['model']} ({stat['role']}): {stat['ability']['ability']}" for stat in role_playing_stats[:10]])}
        """
    else:
        stats_text = "无角色扮演能力评估数据"
    
    return stats_text

def generate_batch_analysis_report(results: List[Dict], output_dir: str):
    """生成批量分析报告"""
    # 创建报告目录
    report_dir = os.path.join(output_dir, f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(report_dir, exist_ok=True)
    
    # 生成汇总统计
    summary_stats = generate_summary_statistics(results)
    
    # 生成模型对比分析
    comparison_df = compare_models_under_same_conditions(results)
    
    # 生成角色扮演能力统计
    role_playing_stats = analyze_role_playing_abilities(results)
    
    # 生成报告内容
    report_content = f"""
# 批量测试分析报告

## 概述
- 总测试数量: {len(results)}
- 涉及模型数量: {len(set(r['model_id'] for r in results if r['model_id']))}
- 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 汇总统计
{summary_stats}

## 模型对比分析
{comparison_df.to_markdown() if not comparison_df.empty else "无足够数据进行对比"}

## 角色扮演能力分析
{role_playing_stats}
    """
    
    # 保存报告
    report_path = os.path.join(report_dir, "batch_analysis_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"批量分析报告已保存到: {report_path}")
    return report_path

import argparse

def main():
    parser = argparse.ArgumentParser(description='批量测试结果分析')
    parser.add_argument('--results-dir', type=str, default='results', 
                       help='测试结果目录')
    parser.add_argument('--output-dir', type=str, default='analysis_reports', 
                       help='分析报告输出目录')
    parser.add_argument('--compare-only', action='store_true',
                       help='仅执行模型对比分析')
    
    args = parser.parse_args()
    
    # 收集测试结果
    results = collect_test_results(args.results_dir)
    
    if not results:
        print("未找到测试结果文件")
        return
    
    # 生成分析报告
    report_path = generate_batch_analysis_report(results, args.output_dir)
    print(f"分析完成，报告已生成: {report_path}")

if __name__ == "__main__":
    main()