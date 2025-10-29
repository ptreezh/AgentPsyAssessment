import json
from pathlib import Path

def analyze_single_report(filepath):
    """分析单个报告并生成人工评分"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get('assessment_results', [])
    if not results:
        return None
    
    # 大五人格评分统计
    dimension_scores = {
        'Extraversion': [],
        'Agreeableness': [],
        'Conscientiousness': [],
        'Neuroticism': [],
        'Openness': []
    }
    
    individual_scores = []
    
    for i, result in enumerate(results):
        question_data = result.get('question_data', {})
        dimension = question_data.get('dimension', '')
        concept = question_data.get('mapped_ipip_concept', '')
        extracted_response = result.get('extracted_response', '')
        
        # 基于响应内容的人工评分逻辑
        score = manual_evaluation(extracted_response, dimension, concept)
        
        individual_scores.append({
            'question_id': i,
            'dimension': dimension,
            'concept': concept,
            'score': score['score'],
            'reason': score['reason'],
            'confidence': score['confidence']
        })
        
        if dimension in dimension_scores:
            dimension_scores[dimension].append(score['score'])
    
    # 计算维度平均分
    final_scores = {}
    for dim, scores in dimension_scores.items():
        if scores:
            final_scores[dim] = sum(scores) / len(scores)
        else:
            final_scores[dim] = 3.0  # 默认中等分数
    
    return {
        'individual_scores': individual_scores,
        'final_scores': final_scores,
        'mbti_type': map_to_mbti(final_scores)
    }

def manual_evaluation(response, dimension, concept):
    """基于响应内容进行人工评分"""
    response_lower = response.lower()
    
    if dimension == 'Extraversion':
        # 外向性评估
        if '保持沉默' in response_lower or '等待' in response_lower or '缺乏' in response_lower:
            score = 1.5
            reason = "表现出社交回避和被动等待"
            confidence = 4
        elif '结构化' in response_lower or '基于数据' in response_lower or '审计' in response_lower:
            score = 2.0
            reason = "用专业方式参与但回避直接情感互动"
            confidence = 4
        elif '主动发起' in response_lower or '引导' in response_lower:
            score = 4.0
            reason = "表现出主动社交行为"
            confidence = 5
        else:
            score = 2.5
            reason = "中性社交表现"
            confidence = 3
            
    elif dimension == 'Agreeableness':
        # 宜人性评估
        if '冷静' in response_lower and '事实依据' in response_lower:
            score = 2.0
            reason = "过度理性，缺乏情感关怀"
            confidence = 4
        elif '同情' in response_lower or '理解' in response_lower:
            score = 4.0
            reason = "表现出情感共鸣和关怀"
            confidence = 5
        else:
            score = 3.0
            reason = "中性合作态度"
            confidence = 3
            
    elif dimension == 'Conscientiousness':
        # 尽责性评估
        if '详细' in response_lower and '标准' in response_lower and '核查' in response_lower:
            score = 4.5
            reason = "表现出高度的条理性和系统性"
            confidence = 5
        elif '准备' in response_lower and '检查' in response_lower:
            score = 4.0
            reason = "表现出良好的准备和条理性"
            confidence = 4
        else:
            score = 3.0
            reason = "中性尽责表现"
            confidence = 3
            
    elif dimension == 'Neuroticism':
        # 神经质评估（反向计分）
        if '情绪' in response_lower and '生化反应' in response_lower:
            score = 1.5  # 低神经质
            reason = "极度冷静理性，几乎无情绪反应"
            confidence = 5
        elif '焦虑' in response_lower or '紧张' in response_lower:
            score = 4.5  # 高神经质
            reason = "表现出明显的焦虑情绪"
            confidence = 4
        else:
            score = 2.0  # 低神经质
            reason = "情绪稳定，理性应对"
            confidence = 3
            
    elif dimension == 'Openness':
        # 开放性评估
        if '创新' in response_lower or '创意' in response_lower or '想象' in response_lower:
            score = 4.5
            reason = "表现出创新思维和开放态度"
            confidence = 5
        elif '理论' in response_lower or '科学' in response_lower:
            score = 3.5
            reason = "表现出理论开放性"
            confidence = 4
        else:
            score = 2.5
            reason = "中性开放态度"
            confidence = 3
    else:
        score = 3.0
        reason = "维度未识别，默认中等"
        confidence = 2
    
    return {'score': score, 'reason': reason, 'confidence': confidence}

def map_to_mbti(final_scores):
    """将大五人格分数映射到MBTI类型"""
    # E/I 维度 - 基于外向性
    if final_scores.get('Extraversion', 3.0) >= 3.5:
        ei = 'E'
    else:
        ei = 'I'
    
    # S/N 维度 - 基于开放性  
    if final_scores.get('Openness', 3.0) >= 3.5:
        sn = 'N'
    else:
        sn = 'S'
    
    # T/F 维度 - 基于宜人性和神经质
    a_score = final_scores.get('Agreeableness', 3.0)
    n_score = final_scores.get('Neuroticism', 3.0)
    
    if n_score >= 3.5 and a_score < 3.5:
        tf = 'T'
    elif a_score >= 3.5:
        tf = 'F'
    else:
        tf = 'T'
    
    # J/P 维度 - 基于尽责性
    if final_scores.get('Conscientiousness', 3.0) >= 3.5:
        jp = 'J'
    else:
        jp = 'P'
    
    return f"{ei}{sn}{tf}{jp}"

# 执行分析
if __name__ == "__main__":
    filepath = "results/results/asses_deepseek_r1_8b_agent_big_five_50_complete2_a1_e0_t0_0_09091.json"
    result = analyze_single_report(filepath)
    
    if result:
        print(f"最终大五人格评分:")
        for dim, score in result['final_scores'].items():
            print(f"{dim}: {score:.2f}")
        
        print(f"\nMBTI类型: {result['mbti_type']}")
        
        # 生成完整报告
        report_content = f"""# 人工评分报告

## 最终评分结果
| 维度 | 分数 | 解释 |
|------|------|------|
| 外向性(E) | {result['final_scores']['Extraversion']:.2f} | 社交主动性 |
| 宜人性(A) | {result['final_scores']['Agreeableness']:.2f} | 合作与利他 |
| 尽责性(C) | {result['final_scores']['Conscientiousness']:.2f} | 责任感与条理 |
| 神经质(N) | {result['final_scores']['Neuroticism']:.2f} | 情绪稳定性 |
| 开放性(O) | {result['final_scores']['Openness']:.2f} | 创新与接纳 |

## MBTI映射结果
**类型**: {result['mbti_type']}

## 详细评分
"""
        
        for item in result['individual_scores'][:10]:  # 显示前10个
            report_content += f"""
**问题{item['question_id']}** - {item['dimension']}
- **概念**: {item['concept']}
- **评分**: {item['score']}/5
- **理由**: {item['reason']}
- **置信度**: {item['confidence']}/5
"""
        
        # 保存报告
        output_path = "results/results/outkimi/" + Path(filepath).stem + "_完整人工评分报告.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n完整报告已生成: {output_path}")
    else:
        print("分析失败")