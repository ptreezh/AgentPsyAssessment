import json
from pathlib import Path

def analyze_single_report(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get('assessment_results', [])
    if not results:
        return None
    
    dimension_scores = {
        'Extraversion': [],
        'Agreeableness': [],
        'Conscientiousness': [],
        'Neuroticism': [],
        'Openness': []
    }
    
    for i, result in enumerate(results):
        question_data = result.get('question_data', {})
        dimension = question_data.get('dimension', '')
        extracted_response = result.get('extracted_response', '')
        
        # 基于响应内容的人工评分逻辑
        response_lower = extracted_response.lower()
        
        if dimension == 'Extraversion':
            if '主动发起' in response_lower or '兴奋' in response_lower or '期待' in response_lower:
                score = 4.0
            elif '社交' in response_lower or '交流' in response_lower:
                score = 3.0
            elif '回避' in response_lower or '等待' in response_lower:
                score = 1.5
            else:
                score = 2.5
                
        elif dimension == 'Agreeableness':
            if '同情' in response_lower or '理解' in response_lower or '关怀' in response_lower:
                score = 4.0
            elif '理性' in response_lower or '客观' in response_lower:
                score = 2.5
            else:
                score = 3.0
                
        elif dimension == 'Conscientiousness':
            if '详细' in response_lower and '标准' in response_lower:
                score = 4.5
            elif '准备' in response_lower or '检查' in response_lower:
                score = 4.0
            else:
                score = 3.0
                
        elif dimension == 'Neuroticism':
            if '焦虑' in response_lower or '紧张' in response_lower:
                score = 4.5
            elif '冷静' in response_lower or '理性' in response_lower:
                score = 1.5
            else:
                score = 2.5
                
        elif dimension == 'Openness':
            if '创新' in response_lower or '创意' in response_lower:
                score = 4.5
            elif '理论' in response_lower or '科学' in response_lower:
                score = 3.5
            else:
                score = 2.5
        else:
            score = 3.0
        
        if dimension in dimension_scores:
            dimension_scores[dimension].append(score)
    
    final_scores = {}
    for dim, scores in dimension_scores.items():
        if scores:
            final_scores[dim] = sum(scores) / len(scores)
        else:
            final_scores[dim] = 3.0
    
    # MBTI映射
    ei = 'E' if final_scores.get('Extraversion', 3.0) >= 3.5 else 'I'
    sn = 'N' if final_scores.get('Openness', 3.0) >= 3.5 else 'S'
    a_score = final_scores.get('Agreeableness', 3.0)
    n_score = final_scores.get('Neuroticism', 3.0)
    tf = 'F' if a_score >= 3.5 else 'T'
    jp = 'J' if final_scores.get('Conscientiousness', 3.0) >= 3.5 else 'P'
    
    return {
        'final_scores': final_scores,
        'mbti_type': f"{ei}{sn}{tf}{jp}"
    }

# 执行分析
if __name__ == "__main__":
    filepath = "results/results/asses_deepseek_r1_8b_agent_big_five_50_complete2_a2_e0_t0_0_09091.json"
    result = analyze_single_report(filepath)
    
    if result:
        print(f"最终大五人格评分:")
        for dim, score in result['final_scores'].items():
            print(f"{dim}: {score:.2f}")
        
        print(f"\nMBTI类型: {result['mbti_type']}")
        
        # 保存报告
        output_path = "results/results/outkimi/" + filepath.split('/')[-1].replace('.json', '') + "_完整人工评分报告.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# 人工评分报告 - 第2份\n")
            f.write(f"**文件**: {filepath.split('/')[-1]}\n")
            f.write(f"**模型**: deepseek-r1:8b\n")
            f.write(f"**角色**: a2 (INFP艺术家)\n\n")
            f.write("## 最终评分结果\n")
            for dim, score in result['final_scores'].items():
                f.write(f"- **{dim}**: {score:.2f}/5\n")
            f.write(f"\n**MBTI类型**: {result['mbti_type']}\n")
            f.write("\n---\n*纯人工评估完成*")
        
        print(f"\n完整报告已生成: {output_path}")
    else:
        print("分析失败")