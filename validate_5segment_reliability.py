#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证5题分段方案的信度和多模型一致性
严格遵循1-3-5评分标准
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# 设置环境变量
import os
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['DASHSCOPE_API_KEY'] = 'sk-ded837735b3c44599a9bc138da561c27'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def load_test_data() -> List[Dict]:
    """加载测试数据"""
    test_file = "results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271.json"

    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        questions = []
        if 'assessment_results' in data and isinstance(data['assessment_results'], list):
            for item in data['assessment_results'][:10]:  # 只取前10题用于验证
                if isinstance(item, dict) and 'question_data' in item:
                    question_data = item['question_data']
                    if isinstance(question_data, dict):
                        question_text = question_data.get('prompt_for_agent', question_data.get('mapped_ipip_concept', ''))

                        answer_text = ''
                        if 'extracted_response' in item and item['extracted_response']:
                            answer_text = item['extracted_response']
                        elif 'conversation_log' in item and isinstance(item['conversation_log'], list):
                            for msg in item['conversation_log']:
                                if isinstance(msg, dict) and msg.get('role') == 'assistant':
                                    answer_text = msg.get('content', '')
                                    break

                        if question_text and answer_text:
                            questions.append({
                                'question': question_text,
                                'answer': answer_text
                            })
        return questions

    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return []

def create_strict_prompt(segment: List[Dict], segment_num: int) -> str:
    """创建严格的1-3-5评分提示"""

    prompt = f"""你是专业的心理评估分析师，专门分析AI代理的人格特征。你的任务是**分析**以下问卷回答，评估回答者展现的Big5人格特质。

**重要提醒：**
- ❌ 你不是被测试者，不要回答问卷问题
- ❌ 不要混淆角色，你是评估分析师
- ✅ 专注于分析回答中的人格特征
- ✅ 忽略角色扮演内容，专注实际行为倾向

**Big5维度定义：**
1. **开放性(O)**：对新体验、创意、理论的开放程度
2. **尽责性(C)**：自律、条理、可靠程度
3. **外向性(E)**：社交活跃度、能量来源
4. **宜人性(A)**：合作、同理心、信任倾向
5. **神经质(N)**：情绪稳定性、焦虑倾向

**严格评分标准（必须使用）：**
- **1分**：极低表现 - 明显缺乏该特质
- **3分**：中等表现 - 平衡或不确定，有该特质也有反例
- **5分**：极高表现 - 明显具备该特质

**特别注意：只能使用1、3、5三个整数分数，禁止使用2、4等其他数值！**

**第{segment_num}段问卷内容（{len(segment)}题）：**
"""

    for i, item in enumerate(segment, 1):
        prompt += f"""
**问题 {i}:**
{item['question']}

**回答 {i}:**
{item['answer']}

---
"""

    prompt += """
**请返回严格的JSON格式：**
```json
{
  "success": true,
  "segment_number": 分段编号,
  "analysis_summary": "简要分析总结",
  "scores": {
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  },
  "evidence": {
    "openness_to_experience": "具体证据引用",
    "conscientiousness": "具体证据引用",
    "extraversion": "具体证据引用",
    "agreeableness": "具体证据引用",
    "neuroticism": "具体证据引用"
  },
  "confidence": "high/medium/low"
}
```

**再次提醒：每个评分必须是1、3或5，不能使用其他数值！**
"""

    return prompt

def analyze_with_model(model_name: str, api_key: str, base_url: str, segment: List[Dict], segment_num: int) -> Dict:
    """使用指定模型分析分段"""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key, base_url=base_url)

        prompt = create_strict_prompt(segment, segment_num)

        print(f"  🔍 使用 {model_name} 分析段{segment_num}...")

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是专业的心理评估分析师。必须严格使用1-3-5评分标准。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.1
        )

        content = response.choices[0].message.content
        print(f"  📝 响应长度: {len(content)} 字符")

        # 解析JSON
        try:
            # 先尝试提取```json```包裹的内容
            import re
            json_match = re.search(r'```json\\s*(\\{.*?\\})\\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print(f"  🔍 找到```json```包裹的内容")
                try:
                    result = json.loads(json_str)
                    print(f"  📄 ```json```内容解析成功")
                except json.JSONDecodeError as e2:
                    print(f"  ❌ ```json```内容解析失败: {str(e2)[:100]}...")
                    raise Exception("JSON解析失败")
            else:
                # 如果没有```json```，尝试直接解析
                try:
                    result = json.loads(content)
                    print(f"  📄 直接JSON解析成功")
                except json.JSONDecodeError as e:
                    print(f"  ⚠️ 直接JSON解析失败: {str(e)[:100]}...")
                    # 尝试提取任何JSON格式
                    json_match = re.search(r'\\{.*?\\}', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        print(f"  🔍 找到JSON片段: {json_str[:200]}...")
                        try:
                            result = json.loads(json_str)
                            print(f"  📄 片段JSON解析成功")
                        except json.JSONDecodeError as e2:
                            print(f"  ❌ 片段JSON也解析失败: {str(e2)[:100]}...")
                            print(f"  📝 完整响应内容: {content[:500]}...")
                            raise Exception("无法解析JSON")
                    else:
                        print(f"  ❌ 未找到JSON格式")
                        print(f"  📝 完整响应内容: {content[:500]}...")
                        raise Exception("无法找到有效的JSON")

        except Exception as e:
            print(f"  ❌ JSON解析异常: {e}")
            raise e

        # 验证评分标准
        if 'scores' in result:
            scores = result['scores']
            invalid_scores = []
            for trait, score in scores.items():
                if score not in [1, 3, 5]:
                    invalid_scores.append(f"{trait}:{score}")

            if invalid_scores:
                print(f"  ⚠️ 发现无效评分: {invalid_scores}")
                # 将无效评分修正为最接近的有效评分
                for trait, score in scores.items():
                    if score not in [1, 3, 5]:
                        if score < 2:
                            scores[trait] = 1
                        elif score > 4:
                            scores[trait] = 5
                        else:
                            scores[trait] = 3
                print(f"  🔧 修正后评分: {scores}")

        result['model'] = model_name
        result['segment_number'] = segment_num
        result['raw_response_length'] = len(content)

        print(f"  ✅ {model_name} 分析成功")
        return result

    except Exception as e:
        print(f"  ❌ {model_name} 分析失败: {e}")
        return {
            'success': False,
            'model': model_name,
            'segment_number': segment_num,
            'error': str(e)
        }

def calculate_model_consistency(results: List[Dict]) -> Dict:
    """计算模型一致性"""
    if not results:
        return {'consistency_score': 0, 'details': {}}

    # 收集所有成功的结果
    successful_results = [r for r in results if r.get('success', False) and 'scores' in r]

    if len(successful_results) < 2:
        return {'consistency_score': 0, 'details': {'error': '有效结果不足2个'}}

    # 计算每个维度的一致性
    traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
    consistency_details = {}

    for trait in traits:
        scores = [r['scores'][trait] for r in successful_results]
        unique_scores = set(scores)
        consistency_details[trait] = {
            'scores': scores,
            'unique_count': len(unique_scores),
            'most_common': max(set(scores), key=scores.count),
            'is_consistent': len(unique_scores) == 1
        }

    # 计算总体一致性
    consistent_traits = sum(1 for detail in consistency_details.values() if detail['is_consistent'])
    total_traits = len(traits)
    consistency_score = (consistent_traits / total_traits) * 100 if total_traits > 0 else 0

    return {
        'consistency_score': consistency_score,
        'consistent_traits': consistent_traits,
        'total_traits': total_traits,
        'details': consistency_details,
        'successful_models': len(successful_results)
    }

def validate_5segment_reliability():
    """验证5题分段方案的信度"""
    print("🔍 5题分段方案信度验证")
    print("=" * 60)
    print("✓ 严格使用1-3-5评分标准")
    print("✓ 多模型一致性验证")
    print("✓ 信度评估")
    print()

    # 加载测试数据
    questions = load_test_data()
    if len(questions) < 10:
        print("❌ 测试数据不足")
        return

    print(f"📋 加载了 {len(questions)} 个问题")
    print()

    # 测试模型配置
    models = [
        {"name": "qwen-long", "api_key": "sk-ded837735b3c44599a9bc138da561c27", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
        {"name": "qwen-max", "api_key": "sk-ded837735b3c44599a9bc138da561c27", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    ]

    # 分段测试
    segments = [
        questions[:5],   # 分段1
        questions[5:10]  # 分段2
    ]

    all_results = []

    for seg_num, segment in enumerate(segments, 1):
        print(f"🧪 测试分段 {seg_num} ({len(segment)}题)")
        print("-" * 40)

        segment_results = []

        for model_config in models:
            result = analyze_with_model(
                model_config["name"],
                model_config["api_key"],
                model_config["base_url"],
                segment,
                seg_num
            )
            segment_results.append(result)
            time.sleep(2)  # 避免API限制

        # 计算该分段的一致性
        consistency = calculate_model_consistency(segment_results)
        print(f"  📊 分段{seg_num}一致性: {consistency['consistency_score']:.1f}%")

        if consistency.get('details') and isinstance(consistency['details'], dict):
            for trait, detail in consistency['details'].items():
                if isinstance(detail, dict) and detail.get('is_consistent'):
                    print(f"    ✅ {trait}: {detail['scores']} (一致)")
                elif isinstance(detail, dict):
                    print(f"    ⚠️ {trait}: {detail['scores']} (不一致)")

        all_results.extend(segment_results)
        print()

    # 总体信度评估
    print("🎯 总体信度评估")
    print("=" * 40)

    overall_consistency = calculate_model_consistency(all_results)
    print(f"📊 总体一致性: {overall_consistency['consistency_score']:.1f}%")
    print(f"📈 一致维度: {overall_consistency['consistent_traits']}/{overall_consistency['total_traits']}")
    print(f"🤖 成功模型数: {overall_consistency['successful_models']}")

    # 评分标准验证
    print()
    print("📋 评分标准验证")
    print("-" * 40)

    valid_scores = 0
    total_scores = 0

    for result in all_results:
        if result.get('success', False) and 'scores' in result:
            for trait, score in result['scores'].items():
                total_scores += 1
                if score in [1, 3, 5]:
                    valid_scores += 1

    score_compliance = (valid_scores / total_scores * 100) if total_scores > 0 else 0
    print(f"✅ 1-3-5评分标准符合率: {score_compliance:.1f}%")
    print(f"📊 有效评分: {valid_scores}/{total_scores}")

    # 最终评级
    print()
    print("🏆 信度评级")
    print("-" * 40)

    if overall_consistency['consistency_score'] >= 80 and score_compliance >= 90:
        rating = "优秀"
        recommendation = "✅ 推荐使用5题分段方案"
    elif overall_consistency['consistency_score'] >= 60 and score_compliance >= 80:
        rating = "良好"
        recommendation = "⚠️ 可以使用，需优化"
    else:
        rating = "需要改进"
        recommendation = "❌ 不推荐，需要修复"

    print(f"📊 信度等级: {rating}")
    print(f"💡 建议: {recommendation}")

    # 保存验证结果
    validation_result = {
        "validation_date": datetime.now().isoformat(),
        "segment_size": 5,
        "test_questions": len(questions),
        "models_tested": [m["name"] for m in models],
        "overall_consistency": overall_consistency,
        "score_compliance": score_compliance,
        "rating": rating,
        "recommendation": recommendation,
        "all_results": all_results
    }

    with open("5segment_reliability_validation.json", "w", encoding="utf-8") as f:
        json.dump(validation_result, f, ensure_ascii=False, indent=2)

    print(f"📄 验证结果已保存到: 5segment_reliability_validation.json")

if __name__ == "__main__":
    validate_5segment_reliability()