import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_data(csv_path):
    """加载评分数据"""
    df = pd.read_csv(csv_path)
    return df

def analysis_1_same_model_same_role_different_stress(df):
    """同模型同角色不同压力等级的对比分析"""
    print("=== 分析1: 同模型同角色不同压力等级的对比分析 ===")
    
    # 按模型和角色分组，查看不同压力等级下的表现
    grouped = df.groupby(['Model', 'Role'])
    
    analysis_results = []
    
    for (model, role), group in grouped:
        if len(group) > 1:  # 只分析有多个压力等级的数据
            # 计算每个压力等级下的平均分
            stress_avg = group.groupby('Interference_Level')[[
                'Extraversion', 'Agreeableness', 'Conscientiousness', 
                'Neuroticism', 'Openness_to_Experience'
            ]].mean()
            
            # 计算标准差
            stress_std = group.groupby('Interference_Level')[[
                'Extraversion', 'Agreeableness', 'Conscientiousness', 
                'Neuroticism', 'Openness_to_Experience'
            ]].std()
            
            analysis_results.append({
                'model': model,
                'role': role,
                'stress_levels': stress_avg.index.tolist(),
                'extraversion_avg': stress_avg['Extraversion'].tolist(),
                'agreeableness_avg': stress_avg['Agreeableness'].tolist(),
                'conscientiousness_avg': stress_avg['Conscientiousness'].tolist(),
                'neuroticism_avg': stress_avg['Neuroticism'].tolist(),
                'openness_avg': stress_avg['Openness_to_Experience'].tolist(),
                'extraversion_std': stress_std['Extraversion'].tolist(),
                'agreeableness_std': stress_std['Agreeableness'].tolist(),
                'conscientiousness_std': stress_std['Conscientiousness'].tolist(),
                'neuroticism_std': stress_std['Neuroticism'].tolist(),
                'openness_std': stress_std['Openness_to_Experience'].tolist()
            })
    
    # 生成分析报告
    report = "# 分析1: 同模型同角色不同压力等级的对比分析\n\n"
    report += "## 主要发现\n\n"
    
    for result in analysis_results:
        report += f"### 模型: {result['model']}, 角色: {result['role']}\n\n"
        report += "| 压力等级 | 外向性 | 宜人性 | 尽责性 | 神经质 | 开放性 |\n"
        report += "|---------|--------|--------|--------|--------|--------|\n"
        
        for i, level in enumerate(result['stress_levels']):
            extraversion_std_val = result['extraversion_std'][i] if not np.isnan(result['extraversion_std'][i]) else 0
            agreeableness_std_val = result['agreeableness_std'][i] if not np.isnan(result['agreeableness_std'][i]) else 0
            conscientiousness_std_val = result['conscientiousness_std'][i] if not np.isnan(result['conscientiousness_std'][i]) else 0
            neuroticism_std_val = result['neuroticism_std'][i] if not np.isnan(result['neuroticism_std'][i]) else 0
            openness_std_val = result['openness_std'][i] if not np.isnan(result['openness_std'][i]) else 0
            
            report += f"| {level} | {result['extraversion_avg'][i]:.2f}±{extraversion_std_val:.2f} | "
            report += f"{result['agreeableness_avg'][i]:.2f}±{agreeableness_std_val:.2f} | "
            report += f"{result['conscientiousness_avg'][i]:.2f}±{conscientiousness_std_val:.2f} | "
            report += f"{result['neuroticism_avg'][i]:.2f}±{neuroticism_std_val:.2f} | "
            report += f"{result['openness_avg'][i]:.2f}±{openness_std_val:.2f} |\n"
        report += "\n"
    
    # 分析趋势
    report += "## 趋势分析\n\n"
    for result in analysis_results:
        report += f"### {result['model']} ({result['role']}角色)\n"
        
        # 分析每个维度随压力变化的趋势
        dimensions = ['extraversion', 'agreeableness', 'conscientiousness', 'neuroticism', 'openness']
        dimension_names = ['外向性', '宜人性', '尽责性', '神经质', '开放性']
        
        for i, dim in enumerate(dimensions):
            avg_values = result[f'{dim}_avg']
            if len(avg_values) >= 2:
                # 计算趋势
                trend = np.polyfit(result['stress_levels'], avg_values, 1)[0]
                if trend > 0.1:
                    trend_desc = "随着压力增加而显著上升"
                elif trend > 0:
                    trend_desc = "随着压力增加略有上升"
                elif trend < -0.1:
                    trend_desc = "随着压力增加而显著下降"
                elif trend < 0:
                    trend_desc = "随着压力增加略有下降"
                else:
                    trend_desc = "随压力变化不明显"
                
                report += f"- {dimension_names[i]}: {trend_desc}\n"
        report += "\n"
    
    return analysis_results, report

def analysis_2_same_model_different_roles_same_stress(df):
    """同模型不同角色同压力等级的对比分析"""
    print("=== 分析2: 同模型不同角色同压力等级的对比分析 ===")
    
    # 按模型和压力等级分组，查看不同角色下的表现
    grouped = df.groupby(['Model', 'Interference_Level'])
    
    analysis_results = []
    
    for (model, stress_level), group in grouped:
        if len(group['Role'].unique()) > 1:  # 只分析有多个角色的数据
            # 计算每个角色下的平均分
            role_avg = group.groupby('Role')[[
                'Extraversion', 'Agreeableness', 'Conscientiousness', 
                'Neuroticism', 'Openness_to_Experience'
            ]].mean()
            
            # 计算标准差
            role_std = group.groupby('Role')[[
                'Extraversion', 'Agreeableness', 'Conscientiousness', 
                'Neuroticism', 'Openness_to_Experience'
            ]].std()
            
            analysis_results.append({
                'model': model,
                'stress_level': stress_level,
                'roles': role_avg.index.tolist(),
                'extraversion_avg': role_avg['Extraversion'].tolist(),
                'agreeableness_avg': role_avg['Agreeableness'].tolist(),
                'conscientiousness_avg': role_avg['Conscientiousness'].tolist(),
                'neuroticism_avg': role_avg['Neuroticism'].tolist(),
                'openness_avg': role_avg['Openness_to_Experience'].tolist(),
                'extraversion_std': role_std['Extraversion'].tolist(),
                'agreeableness_std': role_std['Agreeableness'].tolist(),
                'conscientiousness_std': role_std['Conscientiousness'].tolist(),
                'neuroticism_std': role_std['Neuroticism'].tolist(),
                'openness_std': role_std['Openness_to_Experience'].tolist()
            })
    
    # 生成分析报告
    report = "# 分析2: 同模型不同角色同压力等级的对比分析\n\n"
    report += "## 主要发现\n\n"
    
    for result in analysis_results:
        report += f"### 模型: {result['model']}, 压力等级: {result['stress_level']}\n\n"
        report += "| 角色 | 外向性 | 宜人性 | 尽责性 | 神经质 | 开放性 |\n"
        report += "|------|--------|--------|--------|--------|--------|\n"
        
        for i, role in enumerate(result['roles']):
            extraversion_std_val = result['extraversion_std'][i] if not np.isnan(result['extraversion_std'][i]) else 0
            agreeableness_std_val = result['agreeableness_std'][i] if not np.isnan(result['agreeableness_std'][i]) else 0
            conscientiousness_std_val = result['conscientiousness_std'][i] if not np.isnan(result['conscientiousness_std'][i]) else 0
            neuroticism_std_val = result['neuroticism_std'][i] if not np.isnan(result['neuroticism_std'][i]) else 0
            openness_std_val = result['openness_std'][i] if not np.isnan(result['openness_std'][i]) else 0
            
            report += f"| {role} | {result['extraversion_avg'][i]:.2f}±{extraversion_std_val:.2f} | "
            report += f"{result['agreeableness_avg'][i]:.2f}±{agreeableness_std_val:.2f} | "
            report += f"{result['conscientiousness_avg'][i]:.2f}±{conscientiousness_std_val:.2f} | "
            report += f"{result['neuroticism_avg'][i]:.2f}±{neuroticism_std_val:.2f} | "
            report += f"{result['openness_avg'][i]:.2f}±{openness_std_val:.2f} |\n"
        report += "\n"
    
    # 分析差异最大的维度
    report += "## 角色影响分析\n\n"
    for result in analysis_results:
        report += f"### {result['model']} (压力等级{result['stress_level']})\n"
        
        # 找出不同角色间差异最大的维度
        max_diff_dims = []
        for dim in ['extraversion', 'agreeableness', 'conscientiousness', 'neuroticism', 'openness']:
            avg_values = result[f'{dim}_avg']
            if len(avg_values) >= 2:
                diff = max(avg_values) - min(avg_values)
                max_diff_dims.append((dim, diff))
        
        max_diff_dims.sort(key=lambda x: x[1], reverse=True)
        if max_diff_dims:
            report += f"- 差异最大的维度: {max_diff_dims[0][0]} (差异度: {max_diff_dims[0][1]:.2f})\n"
        report += "\n"
    
    return analysis_results, report

def analysis_3_different_models_same_role_same_stress(df):
    """不同模型同角色同压力等级的对比分析"""
    print("=== 分析3: 不同模型同角色同压力等级的对比分析 ===")
    
    # 按角色和压力等级分组，查看不同模型下的表现
    grouped = df.groupby(['Role', 'Interference_Level'])
    
    analysis_results = []
    
    for (role, stress_level), group in grouped:
        if len(group['Model'].unique()) > 1:  # 只分析有多个模型的数据
            # 计算每个模型下的平均分
            model_avg = group.groupby('Model')[[
                'Extraversion', 'Agreeableness', 'Conscientiousness', 
                'Neuroticism', 'Openness_to_Experience'
            ]].mean()
            
            # 计算标准差
            model_std = group.groupby('Model')[[
                'Extraversion', 'Agreeableness', 'Conscientiousness', 
                'Neuroticism', 'Openness_to_Experience'
            ]].std()
            
            analysis_results.append({
                'role': role,
                'stress_level': stress_level,
                'models': model_avg.index.tolist(),
                'extraversion_avg': model_avg['Extraversion'].tolist(),
                'agreeableness_avg': model_avg['Agreeableness'].tolist(),
                'conscientiousness_avg': model_avg['Conscientiousness'].tolist(),
                'neuroticism_avg': model_avg['Neuroticism'].tolist(),
                'openness_avg': model_avg['Openness_to_Experience'].tolist(),
                'extraversion_std': model_std['Extraversion'].tolist(),
                'agreeableness_std': model_std['Agreeableness'].tolist(),
                'conscientiousness_std': model_std['Conscientiousness'].tolist(),
                'neuroticism_std': model_std['Neuroticism'].tolist(),
                'openness_std': model_std['Openness_to_Experience'].tolist()
            })
    
    # 生成分析报告
    report = "# 分析3: 不同模型同角色同压力等级的对比分析\n\n"
    report += "## 主要发现\n\n"
    
    for result in analysis_results:
        report += f"### 角色: {result['role']}, 压力等级: {result['stress_level']}\n\n"
        report += "| 模型 | 外向性 | 宜人性 | 尽责性 | 神经质 | 开放性 |\n"
        report += "|------|--------|--------|--------|--------|--------|\n"
        
        for i, model in enumerate(result['models']):
            extraversion_std_val = result['extraversion_std'][i] if not np.isnan(result['extraversion_std'][i]) else 0
            agreeableness_std_val = result['agreeableness_std'][i] if not np.isnan(result['agreeableness_std'][i]) else 0
            conscientiousness_std_val = result['conscientiousness_std'][i] if not np.isnan(result['conscientiousness_std'][i]) else 0
            neuroticism_std_val = result['neuroticism_std'][i] if not np.isnan(result['neuroticism_std'][i]) else 0
            openness_std_val = result['openness_std'][i] if not np.isnan(result['openness_std'][i]) else 0
            
            report += f"| {model} | {result['extraversion_avg'][i]:.2f}±{extraversion_std_val:.2f} | "
            report += f"{result['agreeableness_avg'][i]:.2f}±{agreeableness_std_val:.2f} | "
            report += f"{result['conscientiousness_avg'][i]:.2f}±{conscientiousness_std_val:.2f} | "
            report += f"{result['neuroticism_avg'][i]:.2f}±{neuroticism_std_val:.2f} | "
            report += f"{result['openness_avg'][i]:.2f}±{openness_std_val:.2f} |\n"
        report += "\n"
    
    # 分析表现最好的模型
    report += "## 模型性能对比\n\n"
    for result in analysis_results:
        report += f"### {result['role']}角色 (压力等级{result['stress_level']})\n"
        
        # 找出在各维度表现最好的模型
        dimensions = ['extraversion', 'agreeableness', 'conscientiousness', 'neuroticism', 'openness']
        dimension_names = ['外向性', '宜人性', '尽责性', '神经质', '开放性']
        
        for i, dim in enumerate(dimensions):
            avg_values = result[f'{dim}_avg']
            if avg_values and len(avg_values) > 0:
                best_model_idx = np.argmax(avg_values)
                best_model = result['models'][best_model_idx]
                best_score = avg_values[best_model_idx]
                report += f"- {dimension_names[i]}表现最好: {best_model} ({best_score:.2f})\n"
        report += "\n"
    
    return analysis_results, report

def generate_visualizations(df):
    """生成可视化图表"""
    print("=== 生成可视化图表 ===")
    
    # 创建输出目录
    viz_dir = "/home/user1/xbots/psy/analysis_visualizations"
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
    
    # 1. 同模型不同压力等级的对比图
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('同模型不同压力等级的人格特质变化', fontsize=16)
    
    models = df['Model'].unique()[:4]  # 选择前4个模型进行展示
    for idx, model in enumerate(models):
        ax = axes[idx//2, idx%2]
        model_data = df[df['Model'] == model]
        
        # 计算每个压力等级的平均值
        stress_avg = model_data.groupby('Interference_Level')[[
            'Extraversion', 'Agreeableness', 'Conscientiousness', 
            'Neuroticism', 'Openness_to_Experience'
        ]].mean()
        
        # 绘制折线图
        stress_avg.plot(ax=ax, marker='o')
        ax.set_title(f'{model}')
        ax.set_xlabel('压力等级')
        ax.set_ylabel('平均分')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{viz_dir}/same_model_different_stress.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. 不同模型的雷达图
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
    fig.suptitle('不同模型人格特质对比雷达图', fontsize=16)
    
    # 选择一个特定的角色和压力等级进行对比
    sample_data = df[(df['Role'] == 'custom') & (df['Interference_Level'] == 2)]
    
    if len(sample_data) > 0:
        models_data = sample_data.groupby('Model')[[
            'Extraversion', 'Agreeableness', 'Conscientiousness', 
            'Neuroticism', 'Openness_to_Experience'
        ]].mean()
        
        # 绘制雷达图
        categories = ['外向性', '宜人性', '尽责性', '神经质', '开放性']
        angles = [n / float(len(categories)) * 2 * np.pi for n in range(len(categories))]
        angles += angles[:1]  # 闭合图形
        
        colors = ['b', 'r', 'g', 'orange', 'purple']
        for idx, (model, row) in enumerate(models_data.iterrows()):
            if idx < len(colors):
                values = row.values.flatten().tolist()
                values += values[:1]  # 闭合图形
                ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[idx])
                ax.fill(angles, values, alpha=0.25, color=colors[idx])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 5)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    plt.savefig(f"{viz_dir}/different_models_radar.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"图表已保存到: {viz_dir}")

def main():
    # 加载数据
    csv_path = "/home/user1/xbots/psy/big5_summary_scores.csv"
    df = load_data(csv_path)
    
    print(f"数据加载完成，共 {len(df)} 条记录")
    print(f"包含 {len(df['Model'].unique())} 个模型")
    print(f"包含 {len(df['Role'].unique())} 种角色")
    print(f"压力等级范围: {df['Interference_Level'].min()} - {df['Interference_Level'].max()}")
    
    # 执行三种分析
    print("\n开始执行分析...")
    
    # 分析1: 同模型同角色不同压力等级
    analysis1_results, analysis1_report = analysis_1_same_model_same_role_different_stress(df)
    
    # 分析2: 同模型不同角色同压力等级
    analysis2_results, analysis2_report = analysis_2_same_model_different_roles_same_stress(df)
    
    # 分析3: 不同模型同角色同压力等级
    analysis3_results, analysis3_report = analysis_3_different_models_same_role_same_stress(df)
    
    # 合并所有分析报告
    full_report = "# 大五人格测试三类对比分析报告\n\n"
    full_report += "## 分析概述\n\n"
    full_report += f"本报告基于 {len(df)} 个测试样本，对大语言模型的人格特质进行了三类对比分析。\n\n"
    full_report += f"涉及 {len(df['Model'].unique())} 个模型: {', '.join(df['Model'].unique())}\n\n"
    full_report += f"涉及 {len(df['Role'].unique())} 种角色: {', '.join(df['Role'].unique())}\n\n"
    
    full_report += analysis1_report + "\n" + analysis2_report + "\n" + analysis3_report
    
    # 保存分析报告
    report_path = "/home/user1/xbots/psy/big5_comparison_analysis_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(full_report)
    
    print(f"\n分析报告已保存到: {report_path}")
    
    # 生成可视化图表
    generate_visualizations(df)
    
    # 输出摘要
    print("\n=== 分析摘要 ===")
    print("1. 同模型同角色不同压力等级分析:")
    print(f"   - 发现 {len(analysis1_results)} 组具有多个压力等级的数据")
    
    print("2. 同模型不同角色同压力等级分析:")
    print(f"   - 发现 {len(analysis2_results)} 组具有多个角色的数据")
    
    print("3. 不同模型同角色同压力等级分析:")
    print(f"   - 发现 {len(analysis3_results)} 组具有多个模型的数据")

if __name__ == "__main__":
    main()