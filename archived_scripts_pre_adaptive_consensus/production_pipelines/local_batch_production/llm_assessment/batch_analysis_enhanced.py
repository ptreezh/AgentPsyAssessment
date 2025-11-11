import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
import argparse

def get_role_mbti_type(role_name):
    """获取角色对应的MBTI类型"""
    # 角色到MBTI类型的映射字典
    role_mbti_mapping = {
        # A系列角色
        'a1': 'ISTJ', 'a2': 'INFP', 'a3': 'INTJ', 'a4': 'ENTJ', 'a5': 'ESFP',
        'a6': 'ENFP', 'a7': 'ESTP', 'a8': 'ISFP', 'a9': 'INFJ', 'a10': 'ENFJ',
        # B系列角色
        'b1': 'INFJ', 'b2': 'INTP', 'b3': 'ENTJ', 'b4': 'ENTP', 'b5': 'ISTJ',
        'b6': 'ISFJ', 'b7': 'ESTJ', 'b8': 'ESFJ', 'b9': 'ESTP', 'b10': 'ISTP'
    }
    
    # 处理英文版本角色文件
    if role_name and '_en' in role_name:
        base_role = role_name.replace('_en', '')
        return role_mbti_mapping.get(base_role, 'Unknown')
    
    return role_mbti_mapping.get(role_name, 'Unknown')

def collect_analysis_results(analysis_reports_dir: str) -> List[Dict]:
    """收集所有分析结果文件"""
    results = []
    
    # 遍历分析报告目录
    for root, dirs, files in os.walk(analysis_reports_dir):
        for file in files:
            if file == 'scores.json':
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 提取关键信息
                    agent_info = data.get('agent_info', {})
                    # 从目录名中提取测试条件信息
                    dir_name = os.path.basename(root)
                    
                    # 解析目录名获取模型、角色等信息
                    parts = dir_name.split('_')
                    model_id = parts[0] if len(parts) > 0 else 'Unknown'
                    role_name = parts[1] if len(parts) > 1 else 'default'
                    
                    # 尝试从文件路径中提取更多测试条件信息
                    # 例如：results/Interactive_Suite_20250826_175341/gemma3_latest_agent-big-five-50-complete2_b10_3i
                    path_parts = root.split(os.sep)
                    stress_level = 0
                    temperature = 0.7  # 默认温度
                    
                    # 检查路径中是否包含压力信息
                    for part in path_parts:
                        if part.endswith('i') and part[:-1].isdigit():
                            try:
                                stress_level = int(part[:-1])
                            except:
                                pass
                    
                    # 检查目录名中是否包含温度信息
                    for part in parts:
                        if 'tmp' in part and part.replace('tmp', '').replace('.', '').isdigit():
                            try:
                                temperature = float(part.replace('tmp', ''))
                            except:
                                pass
                    
                    results.append({
                        'file_path': file_path,
                        'model_id': agent_info.get('model', model_id),
                        'test_name': agent_info.get('test_name', 'Unknown'),
                        'role_name': agent_info.get('role', role_name),
                        'role_mbti_type': get_role_mbti_type(agent_info.get('role', role_name)),
                        'scores_data': data,
                        'directory_name': dir_name,
                        'stress_level': stress_level,
                        'temperature': temperature
                    })
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
    
    return results

def extract_big_five_scores(scores_data: Dict) -> Dict[str, float]:
    """从评分数据中提取Big Five分数"""
    try:
        # 使用第一个评估器的平均分数
        evaluator_names = list(scores_data["evaluator_scores"].keys())
        if not evaluator_names:
            return None
            
        evaluator_name = evaluator_names[0]
        full_scores = scores_data["evaluator_scores"][evaluator_name]["average_scores"]
        
        # 转换为单字母键
        converted_scores = {
            "E": full_scores.get("Extraversion", 0),
            "A": full_scores.get("Agreeableness", 0),
            "C": full_scores.get("Conscientiousness", 0),
            "N": full_scores.get("Neuroticism", 0),
            "O": full_scores.get("Openness to Experience", 0)
        }
        
        return converted_scores
    except Exception as e:
        print(f"Error extracting Big Five scores: {e}")
        return None

def map_to_mbti(big_five_scores: Dict[str, float]) -> str:
    """将Big Five分数映射到MBTI类型"""
    if not big_five_scores:
        return "Unknown"
    
    # 简单的映射规则（需要根据实际情况调整）
    e = big_five_scores.get("E", 0)
    n = big_five_scores.get("N", 0)
    a = big_five_scores.get("A", 0)
    c = big_five_scores.get("C", 0)
    o = big_five_scores.get("O", 0)
    
    # 确定维度
    ei = "E" if e >= 3 else "I"
    sn = "N" if n >= 3 else "S"
    tf = "F" if a >= 3 else "T"  # 简化处理，用宜人性代替思维/情感维度
    jp = "P" if o >= 3 else "J"  # 简化处理，用开放性代替知觉/判断维度
    
    return f"{ei}{sn}{tf}{jp}"

def analyze_role_playing_ability(result_entry: Dict) -> Dict:
    """评估角色扮演能力"""
    role_mbti = result_entry.get('role_mbti_type')
    if not role_mbti or role_mbti == 'Unknown':
        return {'ability': 'Unknown', 'reason': 'No role specified'}
    
    # 从评分数据中提取分析得出的MBTI类型
    scores_data = result_entry.get('scores_data', {})
    big_five_scores = extract_big_five_scores(scores_data)
    if not big_five_scores:
        return {'ability': 'Unknown', 'reason': 'Analysis failed'}
    
    analyzed_mbti = map_to_mbti(big_five_scores)
    
    # 比较设定角色与分析得出的角色
    matches = role_mbti == analyzed_mbti
    return {
        'ability': 'Successful' if matches else 'Failed',
        'set_role': role_mbti,
        'played_role': analyzed_mbti,
        'match': matches,
        'big_five_scores': big_five_scores
    }

def compare_models_under_same_conditions(results: List[Dict]) -> pd.DataFrame:
    """在相同条件下对比不同模型"""
    # 提取标准化数据
    standardized_results = []
    for result in results:
        scores_data = result.get('scores_data', {})
        big_five_scores = extract_big_five_scores(scores_data)
        if big_five_scores:
            standardized_results.append({
                'model_id': result.get('model_id'),
                'test_name': result.get('test_name'),
                'role_name': result.get('role_name'),
                'role_mbti_type': result.get('role_mbti_type'),
                'big_five_scores': big_five_scores,
                'stress_level': result.get('stress_level', 0),
                'temperature': result.get('temperature', 0.7)
            })
    
    if not standardized_results:
        return pd.DataFrame()
    
    # 转换为DataFrame便于分析
    df = pd.DataFrame(standardized_results)
    
    # 按测试和角色分组，比较不同模型的表现
    grouped = df.groupby(['test_name', 'role_name'])
    
    comparison_results = []
    for (test, role), group in grouped:
        if len(group) > 1:  # 只有当有多个模型时才进行对比
            # 计算每个模型的平均分数
            model_scores = {}
            for _, row in group.iterrows():
                model_id = row['model_id']
                scores = row['big_five_scores']
                if model_id not in model_scores:
                    model_scores[model_id] = []
                model_scores[model_id].append(scores)
            
            # 计算平均值
            avg_scores = {}
            for model_id, scores_list in model_scores.items():
                avg_scores[model_id] = {
                    dim: sum(s[dim] for s in scores_list) / len(scores_list)
                    for dim in ['E', 'A', 'C', 'N', 'O']
                }
            
            comparison_results.append({
                'test_name': test,
                'role_name': role,
                'models': list(avg_scores.keys()),
                'scores': avg_scores
            })
    
    return pd.DataFrame(comparison_results)

def compare_temperature_effects(results: List[Dict]) -> pd.DataFrame:
    """分析不同温度设置对模型表现的影响"""
    # 提取标准化数据
    standardized_results = []
    for result in results:
        scores_data = result.get('scores_data', {})
        big_five_scores = extract_big_five_scores(scores_data)
        if big_five_scores:
            standardized_results.append({
                'model_id': result.get('model_id'),
                'test_name': result.get('test_name'),
                'role_name': result.get('role_name'),
                'big_five_scores': big_five_scores,
                'temperature': result.get('temperature', 0.7)
            })
    
    if not standardized_results:
        return pd.DataFrame()
    
    # 转换为DataFrame便于分析
    df = pd.DataFrame(standardized_results)
    
    # 按模型、测试和角色分组，比较不同温度下的表现
    grouped = df.groupby(['model_id', 'test_name', 'role_name'])
    
    temp_comparison_results = []
    for (model, test, role), group in grouped:
        # 按温度排序
        group_sorted = group.sort_values('temperature')
        if len(group_sorted) > 1:  # 只有当有多个温度设置时才进行对比
            # 计算每个温度下的平均分数
            temp_scores = {}
            for _, row in group_sorted.iterrows():
                temp = row['temperature']
                scores = row['big_five_scores']
                if temp not in temp_scores:
                    temp_scores[temp] = []
                temp_scores[temp].append(scores)
            
            # 计算平均值
            avg_temp_scores = {}
            for temp, scores_list in temp_scores.items():
                avg_temp_scores[temp] = {
                    dim: sum(s[dim] for s in scores_list) / len(scores_list)
                    for dim in ['E', 'A', 'C', 'N', 'O']
                }
            
            temp_comparison_results.append({
                'model_id': model,
                'test_name': test,
                'role_name': role,
                'temperatures': list(avg_temp_scores.keys()),
                'scores': avg_temp_scores
            })
    
    return pd.DataFrame(temp_comparison_results)

def compare_stress_effects(results: List[Dict]) -> pd.DataFrame:
    """分析不同压力参数对模型表现的影响"""
    # 提取标准化数据
    standardized_results = []
    for result in results:
        scores_data = result.get('scores_data', {})
        big_five_scores = extract_big_five_scores(scores_data)
        if big_five_scores:
            standardized_results.append({
                'model_id': result.get('model_id'),
                'test_name': result.get('test_name'),
                'role_name': result.get('role_name'),
                'big_five_scores': big_five_scores,
                'stress_level': result.get('stress_level', 0)
            })
    
    if not standardized_results:
        return pd.DataFrame()
    
    # 转换为DataFrame便于分析
    df = pd.DataFrame(standardized_results)
    
    # 按模型、测试和角色分组，比较不同压力参数下的表现
    grouped = df.groupby(['model_id', 'test_name', 'role_name'])
    
    stress_comparison_results = []
    for (model, test, role), group in grouped:
        # 检查是否有不同的压力设置
        if len(group['stress_level'].unique()) > 1:
            # 计算每个压力水平下的平均分数
            stress_scores = {}
            for _, row in group.iterrows():
                stress_level = row['stress_level']
                scores = row['big_five_scores']
                if stress_level not in stress_scores:
                    stress_scores[stress_level] = []
                stress_scores[stress_level].append(scores)
            
            # 计算平均值
            avg_stress_scores = {}
            for stress_level, scores_list in stress_scores.items():
                avg_stress_scores[stress_level] = {
                    dim: sum(s[dim] for s in scores_list) / len(scores_list)
                    for dim in ['E', 'A', 'C', 'N', 'O']
                }
            
            stress_comparison_results.append({
                'model_id': model,
                'test_name': test,
                'role_name': role,
                'stress_levels': list(avg_stress_scores.keys()),
                'scores': avg_stress_scores
            })
    
    return pd.DataFrame(stress_comparison_results)

def generate_summary_statistics(results: List[Dict]) -> str:
    """生成汇总统计"""
    if not results:
        return "No results available."
    
    # 模型统计
    models = [r['model_id'] for r in results if r['model_id']]
    model_counts = pd.Series(models).value_counts()
    
    # 角色统计
    roles = [r['role_name'] for r in results if r['role_name']]
    role_counts = pd.Series(roles).value_counts()
    
    # 角色MBTI类型统计
    mbti_types = [r['role_mbti_type'] for r in results if r['role_mbti_type']]
    mbti_counts = pd.Series(mbti_types).value_counts()
    
    # 温度设置统计
    temperatures = [r['temperature'] for r in results if 'temperature' in r]
    temp_counts = pd.Series(temperatures).value_counts()
    
    # 压力水平统计
    stress_levels = [r['stress_level'] for r in results if 'stress_level' in r]
    stress_counts = pd.Series(stress_levels).value_counts()
    
    stats = f"""
### 模型使用统计
{model_counts.to_string()}

### 角色使用统计
{role_counts.to_string()}

### 角色MBTI类型统计
{mbti_counts.to_string()}

### 温度设置统计
{temp_counts.to_string()}

### 压力水平统计
{stress_counts.to_string()}
"""
    
    return stats

def analyze_role_playing_abilities(results: List[Dict]) -> str:
    """分析角色扮演能力"""
    role_stats = {}
    
    for result in results:
        role_name = result.get('role_name')
        if not role_name:
            continue
            
        # 评估角色扮演能力
        ability_result = analyze_role_playing_ability(result)
        ability = ability_result['ability']
        
        if role_name not in role_stats:
            role_stats[role_name] = {'Successful': 0, 'Failed': 0, 'Unknown': 0}
        role_stats[role_name][ability] += 1
    
    # 生成统计报告
    report = "### 角色扮演能力统计\n"
    for role, stats in role_stats.items():
        total = sum(stats.values())
        success_rate = (stats['Successful'] / total * 100) if total > 0 else 0
        report += f"- {role}: 成功率 {success_rate:.1f}% ({stats['Successful']}/{total})\n"
    
    return report

def generate_detailed_comparison_report(results: List[Dict], output_dir: str):
    """生成详细的对比分析报告"""
    # 创建报告目录
    report_dir = os.path.join(output_dir, f"detailed_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(report_dir, exist_ok=True)
    
    # 生成模型对比分析
    comparison_df = compare_models_under_same_conditions(results)
    
    # 生成温度效果对比分析
    temp_comparison_df = compare_temperature_effects(results)
    
    # 生成压力效果对比分析
    stress_comparison_df = compare_stress_effects(results)
    
    # 生成详细的报告内容
    report_content = f"""
# 详细批量测试分析报告

## 概述
- 总测试数量: {len(results)}
- 涉及模型数量: {len(set(r['model_id'] for r in results if r['model_id']))}
- 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 模型对比分析
{comparison_df.to_markdown() if not comparison_df.empty else "无足够数据进行对比"}

## 温度效果对比分析
{temp_comparison_df.to_markdown() if not temp_comparison_df.empty else "无足够数据进行温度对比"}

## 压力效果对比分析
{stress_comparison_df.to_markdown() if not stress_comparison_df.empty else "无足够数据进行压力对比"}
    """
    
    # 保存报告
    report_path = os.path.join(report_dir, "detailed_analysis_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"详细分析报告已保存到: {report_path}")
    return report_path

def generate_batch_analysis_report(results: List[Dict], output_dir: str):
    """生成批量分析报告"""
    # 创建报告目录
    report_dir = os.path.join(output_dir, f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(report_dir, exist_ok=True)
    
    # 生成汇总统计
    summary_stats = generate_summary_statistics(results)
    
    # 生成模型对比分析
    comparison_df = compare_models_under_same_conditions(results)
    
    # 生成温度效果对比分析
    temp_comparison_df = compare_temperature_effects(results)
    
    # 生成压力效果对比分析
    stress_comparison_df = compare_stress_effects(results)
    
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

## 温度效果对比分析
{temp_comparison_df.to_markdown() if not temp_comparison_df.empty else "无足够数据进行温度对比"}

## 压力效果对比分析
{stress_comparison_df.to_markdown() if not stress_comparison_df.empty else "无足够数据进行压力对比"}

## 角色扮演能力分析
{role_playing_stats}
    """
    
    # 保存报告
    report_path = os.path.join(report_dir, "batch_analysis_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"批量分析报告已保存到: {report_path}")
    
    # 生成详细对比报告
    detailed_report_path = generate_detailed_comparison_report(results, output_dir)
    
    return report_path

def main():
    parser = argparse.ArgumentParser(description='批量测试结果分析')
    parser.add_argument('--analysis-reports-dir', type=str, default='analysis_reports', 
                       help='分析报告目录')
    parser.add_argument('--output-dir', type=str, default='analysis_reports', 
                       help='分析报告输出目录')
    
    args = parser.parse_args()
    
    # 收集分析结果
    results = collect_analysis_results(args.analysis_reports_dir)
    
    if not results:
        print("未找到分析结果文件")
        return
    
    # 生成分析报告
    report_path = generate_batch_analysis_report(results, args.output_dir)
    print(f"分析完成，报告已生成: {report_path}")

if __name__ == "__main__":
    main()