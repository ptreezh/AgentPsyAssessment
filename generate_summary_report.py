#!/usr/bin/env python3
"""
生成测评报告汇总分析
统计所有评估报告的结果，生成综合分析报告
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import statistics as stats

class AssessmentSummaryAnalyzer:
    """评估报告汇总分析器"""
    
    def __init__(self):
        self.mbti_types = []
        self.big_five_scores = defaultdict(list)
        self.model_performance = defaultdict(list)
        self.role_performance = defaultdict(list)
        
    def parse_evaluation_report(self, filepath: str) -> Dict:
        """解析单个评估报告"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取基础信息
            model_match = re.search(r'\*\*模型ID\*\*: (.+)', content)
            role_match = re.search(r'\*\*角色名称\*\*: (.+)', content)
            role_mbti_match = re.search(r'\*\*角色MBTI\*\*: (.+)', content)
            
            # 提取大五人格分数
            big_five_pattern = r'\| (\w+) \((\w+)\) \| (\d+\.?\d*) \| (\w+) \|'
            big_five_matches = re.findall(big_five_pattern, content)
            
            # 提取MBTI类型
            mbti_match = re.search(r'\*\*评估MBTI类型\*\*: (\w+)', content)
            
            result = {
                'filename': Path(filepath).name,
                'model_id': model_match.group(1) if model_match else 'Unknown',
                'role_name': role_match.group(1) if role_match else 'Unknown',
                'role_mbti': role_mbti_match.group(1) if role_mbti_match else 'Unknown',
                'big_five_scores': {},
                'mbti_type': mbti_match.group(1) if mbti_match else 'Unknown'
            }
            
            # 解析大五人格分数
            for match in big_five_matches:
                dimension_name, dimension_code, score, interpretation = match
                result['big_five_scores'][dimension_code] = {
                    'name': dimension_name,
                    'score': float(score),
                    'interpretation': interpretation
                }
            
            return result
            
        except Exception as e:
            print(f"解析报告失败 {filepath}: {e}")
            return None
    
    def analyze_all_reports(self, reports_dir: str) -> Dict:
        """分析所有报告"""
        reports_path = Path(reports_dir)
        report_files = list(reports_path.glob("*_evaluation_report.md"))
        
        print(f"找到 {len(report_files)} 个评估报告")
        
        all_results = []
        for report_file in report_files:
            result = self.parse_evaluation_report(str(report_file))
            if result:
                all_results.append(result)
        
        # 生成统计分析
        analysis = {
            'total_reports': len(all_results),
            'mbti_distribution': self.analyze_mbti_distribution(all_results),
            'big_five_statistics': self.analyze_big_five_statistics(all_results),
            'model_performance': self.analyze_model_performance(all_results),
            'role_performance': self.analyze_role_performance(all_results),
            'correlation_analysis': self.analyze_correlations(all_results)
        }
        
        return analysis
    
    def analyze_mbti_distribution(self, results: List[Dict]) -> Dict:
        """分析MBTI类型分布"""
        mbti_types = [result['mbti_type'] for result in results]
        mbti_counter = Counter(mbti_types)
        
        # 分析各维度分布
        dimensions = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
        
        for mbti in mbti_types:
            if len(mbti) == 4:
                for i, dim in enumerate(['E/I', 'S/N', 'T/F', 'J/P']):
                    if mbti[i] in dimensions:
                        dimensions[mbti[i]] += 1
        
        return {
            'total_types': len(mbti_counter),
            'type_counts': dict(mbti_counter),
            'dimension_distribution': dimensions,
            'most_common': mbti_counter.most_common(5),
            'least_common': mbti_counter.most_common()[-5:]
        }
    
    def analyze_big_five_statistics(self, results: List[Dict]) -> Dict:
        """分析大五人格统计"""
        dimension_scores = defaultdict(list)
        
        for result in results:
            for dim_code, dim_data in result['big_five_scores'].items():
                dimension_scores[dim_code].append(dim_data['score'])
        
        statistics_result = {}
        for dim_code, scores in dimension_scores.items():
            if scores:
                statistics_result[dim_code] = {
                    'mean': stats.mean(scores),
                    'median': stats.median(scores),
                    'std': stats.stdev(scores) if len(scores) > 1 else 0,
                    'min': min(scores),
                    'max': max(scores),
                    'count': len(scores)
                }
        
        return statistics_result
    
    def analyze_model_performance(self, results: List[Dict]) -> Dict:
        """分析模型表现"""
        model_stats = defaultdict(lambda: {'count': 0, 'mbti_types': [], 'avg_scores': defaultdict(list)})
        
        for result in results:
            model = result['model_id']
            model_stats[model]['count'] += 1
            model_stats[model]['mbti_types'].append(result['mbti_type'])
            
            for dim_code, dim_data in result['big_five_scores'].items():
                model_stats[model]['avg_scores'][dim_code].append(dim_data['score'])
        
        # 计算平均值
        for model, model_data in model_stats.items():
            for dim_code in model_data['avg_scores']:
                scores = model_data['avg_scores'][dim_code]
                model_data['avg_scores'][dim_code] = stats.mean(scores)
        
        return dict(model_stats)
    
    def analyze_role_performance(self, results: List[Dict]) -> Dict:
        """分析角色表现"""
        role_stats = defaultdict(lambda: {'count': 0, 'mbti_types': [], 'avg_scores': defaultdict(list)})
        
        for result in results:
            role = result['role_name']
            role_stats[role]['count'] += 1
            role_stats[role]['mbti_types'].append(result['mbti_type'])
            
            for dim_code, dim_data in result['big_five_scores'].items():
                role_stats[role]['avg_scores'][dim_code].append(dim_data['score'])
        
        # 计算平均值
        for role, role_data in role_stats.items():
            for dim_code in role_data['avg_scores']:
                scores = role_data['avg_scores'][dim_code]
                role_data['avg_scores'][dim_code] = stats.mean(scores)
        
        return dict(role_stats)
    
    def analyze_correlations(self, results: List[Dict]) -> Dict:
        """分析相关性"""
        # 角色MBTI与评估MBTI的一致性
        consistency_count = 0
        total_count = 0
        
        for result in results:
            role_mbti = result['role_mbti']
            eval_mbti = result['mbti_type']
            if role_mbti != '未知MBTI' and eval_mbti != 'Unknown':
                total_count += 1
                # 计算相似度（相同字母的数量）
                similarity = sum(1 for i in range(4) if i < len(role_mbti) and i < len(eval_mbti) and role_mbti[i] == eval_mbti[i])
                if similarity >= 3:  # 至少3个维度一致
                    consistency_count += 1
        
        consistency_rate = consistency_count / total_count if total_count > 0 else 0
        
        return {
            'mbti_consistency_rate': consistency_rate,
            'consistent_count': consistency_count,
            'total_comparable': total_count
        }
    
    def generate_summary_report(self, analysis: Dict, output_path: str):
        """生成汇总报告"""
        report_content = f"""# 大五人格评估汇总报告

## 总体统计

- **总报告数量**: {analysis['total_reports']}
- **MBTI类型总数**: {analysis['mbti_distribution']['total_types']}
- **评估模型数量**: {len(analysis['model_performance'])}
- **评估角色数量**: {len(analysis['role_performance'])}

## MBTI类型分布

### 最常见MBTI类型
"""
        
        for mbti_type, count in analysis['mbti_distribution']['most_common']:
            percentage = (count / analysis['total_reports']) * 100
            report_content += f"- **{mbti_type}**: {count} 次 ({percentage:.1f}%)\n"
        
        report_content += f"""
### MBTI维度分布
- **外向(E)**: {analysis['mbti_distribution']['dimension_distribution']['E']} 次
- **内向(I)**: {analysis['mbti_distribution']['dimension_distribution']['I']} 次
- **感觉(S)**: {analysis['mbti_distribution']['dimension_distribution']['S']} 次
- **直觉(N)**: {analysis['mbti_distribution']['dimension_distribution']['N']} 次
- **思考(T)**: {analysis['mbti_distribution']['dimension_distribution']['T']} 次
- **情感(F)**: {analysis['mbti_distribution']['dimension_distribution']['F']} 次
- **判断(J)**: {analysis['mbti_distribution']['dimension_distribution']['J']} 次
- **知觉(P)**: {analysis['mbti_distribution']['dimension_distribution']['P']} 次

## 大五人格统计

| 维度 | 平均分 | 中位数 | 标准差 | 最小值 | 最大值 |
|------|--------|--------|--------|--------|--------|n"""
        
        for dim_code, stats_data in analysis['big_five_statistics'].items():
            dim_names = {'E': '外向性', 'A': '宜人性', 'C': '尽责性', 'N': '神经质', 'O': '开放性'}
            dim_name = dim_names.get(dim_code, dim_code)
            report_content += f"| {dim_name}({dim_code}) | {stats_data['mean']:.2f} | {stats_data['median']:.2f} | {stats_data['std']:.2f} | {stats_data['min']:.2f} | {stats_data['max']:.2f} |\n"
        
        report_content += f"""
## 模型表现分析

### 各模型平均人格分数
"""
        
        for model, stats in sorted(analysis['model_performance'].items(), key=lambda x: x[0]):
            report_content += f"\n**{model}** (样本数: {stats['count']})\n"
            for dim_code, score in stats['avg_scores'].items():
                dim_names = {'E': '外向性', 'A': '宜人性', 'C': '尽责性', 'N': '神经质', 'O': '开放性'}
                dim_name = dim_names.get(dim_code, dim_code)
                report_content += f"- {dim_name}: {score:.2f}\n"
        
        report_content += f"""
## 角色表现分析

### 各角色平均人格分数
"""
        
        for role, stats in sorted(analysis['role_performance'].items(), key=lambda x: x[0]):
            report_content += f"\n**{role}** (样本数: {stats['count']})\n"
            for dim_code, score in stats['avg_scores'].items():
                dim_names = {'E': '外向性', 'A': '宜人性', 'C': '尽责性', 'N': '神经质', 'O': '开放性'}
                dim_name = dim_names.get(dim_code, dim_code)
                report_content += f"- {dim_name}: {score:.2f}\n"
        
        report_content += f"""
## 一致性分析

### 角色MBTI与评估MBTI一致性
- **一致性率**: {analysis['correlation_analysis']['mbti_consistency_rate']:.2%}
- **一致数量**: {analysis['correlation_analysis']['consistent_count']}
- **可比总数**: {analysis['correlation_analysis']['total_comparable']}

## 关键发现

1. **MBTI类型分布**: 评估结果显示了多样化的人格类型分布，反映了不同模型和角色的行为特征差异。

2. **大五人格特征**: 各维度分数分布相对均衡，表明评估体系能够捕捉不同的人格特征。

3. **模型差异**: 不同AI模型在人格评估中表现出一定的差异性，这可能反映了模型训练数据和架构的影响。

4. **角色一致性**: 角色设定的MBTI类型与评估结果的一致性率为{analysis['correlation_analysis']['mbti_consistency_rate']:.2%}，表明角色设定在一定程度上影响了模型行为。

## 结论

本次汇总分析基于{analysis['total_reports']}份评估报告，涵盖了多个AI模型和角色设定。分析结果为了解AI模型的行为特征和人格倾向提供了有价值的参考数据。

**注意事项**:
- 本分析基于文本评估，结果仅供参考
- 评估结果可能受到多种因素影响
- 建议结合具体应用场景进行解读

---
*报告生成时间: {self.get_current_timestamp()}*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"汇总报告已生成: {output_path}")
    
    def get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    analyzer = AssessmentSummaryAnalyzer()
    
    # 输入目录
    reports_dir = r"D:\AIDevelop\portable_psyagent\results\results\out1"
    output_path = r"D:\AIDevelop\portable_psyagent\results\results\out1\summary_report.md"
    
    print("开始分析评估报告...")
    analysis = analyzer.analyze_all_reports(reports_dir)
    
    print("生成汇总报告...")
    analyzer.generate_summary_report(analysis, output_path)
    
    print(f"分析完成!")
    print(f"总报告数量: {analysis['total_reports']}")
    print(f"MBTI类型总数: {analysis['mbti_distribution']['total_types']}")
    print(f"输出文件: {output_path}")

if __name__ == "__main__":
    main()