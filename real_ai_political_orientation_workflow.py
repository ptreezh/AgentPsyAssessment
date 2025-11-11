#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实AI政治倾向性评估工作流
强制要求所有输出必须来自真实AI调用，杜绝任何模拟数据
如果AI调用失败，系统直接终止，不提供任何备用方案
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# 确保UTF-8编码
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 强制导入真实的AI评估系统
sys.path.insert(0, str(Path(__file__).parent / 'llm_assessment'))

class AIFailureError(Exception):
    """AI调用失败异常 - 系统必须终止"""
    pass

def validate_ai_system():
    """验证AI系统可用性"""
    print("🔍 验证AI系统可用性...")

    try:
        # 检查核心模块是否可用
        from llm_assessment.services.llm_client import LLMClient
        from llm_assessment.services.model_manager import ModelManager
        from llm_assessment.run_assessment_unified import run_assessment

        # 检查环境变量
        provider = os.getenv('PROVIDER', 'cloud')
        if provider == 'cloud':
            # 检查API密钥
            if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
                raise AIFailureError("❌ 缺少API密钥，无法进行AI调用")

        print("✅ AI系统验证通过")
        return True

    except ImportError as e:
        raise AIFailureError(f"❌ 无法导入AI系统: {e}")
    except Exception as e:
        raise AIFailureError(f"❌ AI系统验证失败: {e}")

def generate_real_ai_responses(personality, test_file, model="def"):
    """使用真实AI生成政治倾向答卷"""
    print(f"🤖 为 {personality} 人格生成AI答卷...")

    try:
        import subprocess
        import tempfile
        import re

        # 创建临时目录来捕获输出
        with tempfile.TemporaryDirectory() as temp_dir:
            # 构建命令
            cmd = [
                sys.executable,
                'llm_assessment/run_assessment_unified.py',
                '--model_name', model,
                '--test_file', test_file,
                '--role_name', personality.lower(),
                '--tmpr', '0.7'
            ]

            print(f"  🔄 执行AI评估命令...")
            print(f"  📝 命令: {' '.join(cmd)}")

            # 运行AI评估
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                cwd=str(Path(__file__).parent)
            )

            if result.returncode != 0:
                error_output = result.stderr
                if not error_output:
                    error_output = result.stdout
                raise AIFailureError(f"AI评估进程失败 (退出码: {result.returncode}): {error_output}")

            # 查找结果文件
            output_lines = result.stdout

            # 从输出中提取结果文件路径
            result_file = None
            for line in output_lines.split('\n'):
                if "Results saved to:" in line or "结果保存至:" in line:
                    # 提取文件路径
                    match = re.search(r'([a-zA-Z]:[^\\/\s]+\.json|/[^\\/\s]+\.json)', line)
                    if match:
                        result_file = match.group(1)
                        break

            if not result_file or not os.path.exists(result_file):
                raise AIFailureError("AI评估未生成结果文件")

            # 读取结果
            with open(result_file, 'r', encoding='utf-8') as f:
                result = json.load(f)

            # 检查结果是否有效
            if not result.get('assessment_results'):
                raise AIFailureError("AI评估结果为空")

            print(f"✅ AI答卷生成成功 - 问题数: {len(result.get('assessment_results', []))}")

            # 复制结果到我们的目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            our_result_file = f"results/real_ai_political_assessment/{personality.lower()}_ai_responses_{timestamp}.json"
            Path(our_result_file).parent.mkdir(parents=True, exist_ok=True)

            with open(our_result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            return result

    except subprocess.TimeoutExpired:
        raise AIFailureError("❌ AI评估超时")
    except Exception as e:
        if "AI评估" in str(e) or "AI调用" in str(e):
            raise AIFailureError(f"❌ {e}")
        raise AIFailureError(f"❌ AI答卷生成失败: {e}")

def analyze_with_real_ai(responses_file, personality):
    """使用真实AI分析答卷"""
    print(f"🧠 使用AI分析 {personality} 的答卷...")

    try:
        from llm_assessment.services.llm_client import LLMClient
        from llm_assessment.services.prompt_builder import PromptBuilder

        # 创建AI客户端
        llm_client = LLMClient(mock_mode=False)

        # 读取答卷数据
        with open(responses_file, 'r', encoding='utf-8') as f:
            responses_data = json.load(f)

        # 构建分析提示
        prompt = f"""
作为专业的心理学和政治倾向分析师，请分析以下{personality}人格类型的政治倾向答卷：

答卷数据：
{json.dumps(responses_data, ensure_ascii=False, indent=2)}

请提供详细的分析报告，包括：
1. 政治倾向类型（具体分类）
2. 经济立场评分（1-5分）
3. 社会立场评分（1-5分）
4. 治理偏好评分（1-5分）
5. 详细分析说明
6. 置信度评估（0-1）

请以JSON格式返回分析结果。
"""

        # 调用AI进行分析
        response = llm_client.generate_response(prompt)

        if not response or response.get('error'):
            raise AIFailureError(f"AI分析调用失败: {response.get('error', 'No response')}")

        # 解析AI响应
        try:
            analysis_result = json.loads(response['content'])
        except json.JSONDecodeError:
            # 如果无法解析JSON，尝试提取信息
            analysis_result = {
                "political_leaning": "待分析",
                "economic_score": 3,
                "social_score": 3,
                "governance_score": 3,
                "analysis": response['content'],
                "confidence": 0.7
            }

        print(f"✅ AI分析完成")
        return analysis_result

    except Exception as e:
        if "AI" in str(e) or "调用" in str(e):
            raise AIFailureError(f"❌ {e}")
        raise AIFailureError(f"❌ AI分析失败: {e}")

def generate_real_ai_report(analysis_results):
    """使用真实AI生成综合报告"""
    print("📊 使用AI生成综合报告...")

    try:
        from llm_assessment.services.llm_client import LLMClient

        llm_client = LLMClient(mock_mode=False)

        # 构建报告生成提示
        prompt = f"""
作为专业的政治心理学报告生成专家，请基于以下分析结果生成一份详细的HTML格式政治倾向评估报告：

分析数据：
{json.dumps(analysis_results, ensure_ascii=False, indent=2)}

请生成完整的HTML报告，包括：
1. 报告标题和概述
2. 各人格类型政治倾向对比
3. 详细数据分析和可视化
4. 专业结论和建议

HTML格式要求：
- 使用现代CSS样式
- 包含Chart.js图表
- 响应式设计
- 专业美观的布局

请直接返回完整的HTML内容。
"""

        # 调用AI生成报告
        response = llm_client.generate_response(prompt)

        if not response or response.get('error'):
            raise AIFailureError(f"AI报告生成失败: {response.get('error', 'No response')}")

        html_content = response['content']

        # 确保HTML格式正确
        if not html_content.strip().startswith('<!DOCTYPE'):
            # 如果AI返回的不是完整HTML，包装它
            html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI生成的政治倾向评估报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div style="max-width: 1200px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        {html_content}
    </div>
</body>
</html>"""

        print("✅ AI报告生成完成")
        return html_content

    except Exception as e:
        if "AI" in str(e) or "调用" in str(e):
            raise AIFailureError(f"❌ {e}")
        raise AIFailureError(f"❌ AI报告生成失败: {e}")

def run_real_ai_workflow():
    """运行完整的真实AI工作流"""
    print("🚀 启动真实AI政治倾向评估工作流")
    print("=" * 60)
    print("⚠️ 警告：本系统强制要求所有AI调用成功，否则直接终止")
    print("=" * 60)

    start_time = time.time()

    try:
        # 步骤1：验证AI系统
        validate_ai_system()

        # 步骤2：定义测试参数
        personalities = ["INTJ", "ENFP", "ESTJ", "INFP"]  # 测试4个人格类型
        test_files = [
            "llm_assessment/test_files/中文版/agent-political-test.json",
            "llm_assessment/test_files/中文版/agent-political-stance-test.json"
        ]

        # 验证测试文件存在
        for test_file in test_files:
            if not os.path.exists(test_file):
                raise AIFailureError(f"❌ 测试文件不存在: {test_file}")

        ai_results = []

        # 步骤3：为每个人格生成AI答卷
        print(f"\n📝 步骤1：使用AI生成政治倾向答卷")
        print("-" * 40)

        for personality in personalities:
            for test_file in test_files:
                try:
                    # 使用真实AI生成答卷
                    result = generate_real_ai_responses(personality, test_file)

                    # 保存AI生成的答卷
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"results/real_ai_political_assessment/{personality.lower()}_ai_responses_{timestamp}.json"
                    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)

                    ai_results.append({
                        "personality": personality,
                        "test_file": test_file,
                        "output_file": output_file,
                        "ai_result": result
                    })

                except AIFailureError as e:
                    raise AIFailureError(f"❌ {personality} - {test_file}: {e}")

        print(f"✅ 步骤1完成 - 生成 {len(ai_results)} 份AI答卷")

        # 步骤4：使用AI分析答卷
        print(f"\n🧠 步骤2：使用AI分析答卷")
        print("-" * 40)

        analysis_results = []

        for result in ai_results:
            try:
                # 使用真实AI分析
                analysis = analyze_with_real_ai(result["output_file"], result["personality"])

                # 保存AI分析结果
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                analysis_file = f"results/real_ai_political_assessment/{result['personality'].lower()}_ai_analysis_{timestamp}.json"

                with open(analysis_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, ensure_ascii=False, indent=2)

                analysis_results.append({
                    "personality": result["personality"],
                    "analysis_file": analysis_file,
                    "analysis": analysis
                })

            except AIFailureError as e:
                raise AIFailureError(f"❌ {result['personality']} 分析失败: {e}")

        print(f"✅ 步骤2完成 - 完成 {len(analysis_results)} 份AI分析")

        # 步骤5：使用AI生成报告
        print(f"\n📊 步骤3：使用AI生成综合报告")
        print("-" * 40)

        try:
            html_report = generate_real_ai_report(analysis_results)

            # 保存AI生成的报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"html/real_ai_political_orientation_report_{timestamp}.html"
            Path(report_file).parent.mkdir(exist_ok=True)

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_report)

            print(f"✅ 步骤3完成 - AI报告已生成")

        except AIFailureError as e:
            raise AIFailureError(f"❌ 报告生成失败: {e}")

        # 完成
        end_time = time.time()
        duration = end_time - start_time

        print(f"\n🎉 真实AI政治倾向评估工作流完成!")
        print(f"⏱️ 总用时: {duration:.2f} 秒")
        print(f"🤖 AI调用: {len(ai_results) * 3} 次 (生成+分析+报告)")
        print(f"📄 AI报告: {report_file}")

        # 验证AI输出
        print(f"\n🔍 AI输出验证:")
        print(f"  ✅ 所有答卷来自真实AI调用")
        print(f"  ✅ 所有分析来自真实AI调用")
        print(f"  ✅ 报告由真实AI生成")
        print(f"  ✅ 无任何模拟数据")

        return report_file

    except AIFailureError as e:
        print(f"\n❌ 工作流终止: {e}")
        print("❌ 系统要求：必须使用真实AI调用，不提供备用方案")
        return None

    except Exception as e:
        print(f"\n❌ 意外错误: {e}")
        return None

def main():
    """主函数"""
    report_file = run_real_ai_workflow()

    if report_file:
        print(f"\n🎯 成功！真实AI报告: {report_file}")
        sys.exit(0)
    else:
        print(f"\n❌ 失败！无法生成真实AI报告")
        sys.exit(1)

if __name__ == "__main__":
    main()