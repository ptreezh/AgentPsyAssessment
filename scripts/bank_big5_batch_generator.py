#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量银行客服Big5问卷生成器
使用questionnaire-responder技能为不同人格类型生成银行客服问卷回答
"""

import subprocess
import json
import os
from pathlib import Path

class BankBig5BatchGenerator:
    """银行客服Big5问卷批量生成器"""

    def __init__(self):
        self.questionnaire_file = "llm_assessment/test_files/bankclientBig5.json"
        self.output_dir = Path("html/bank")
        self.claude_cmd = r'C:\npm_global\claude.cmd'

        # 银行客服场景的人格类型配置
        self.bank_personality_configs = {
            "ESTJ": {
                "name": "银行经理型",
                "description": "外向、感觉、思考、判断 - 严谨高效、合规意识强的银行管理者",
                "traits": "重视规则流程、风险控制意识强、决策果断、责任心强、注重细节",
                "bank_style": "严格按照银行规章制度办事，强调合规性和专业性"
            },
            "ISFJ": {
                "name": "贴心客服型",
                "description": "内向、感觉、情感、判断 - 细致耐心、客户至上的服务专家",
                "traits": "耐心细致、客户导向、责任心强、稳重可靠、注重服务细节",
                "bank_style": "以客户需求为中心，提供温暖专业的服务体验"
            },
            "ISTJ": {
                "name": "合规专员型",
                "description": "内向、感觉、思考、判断 - 严谨细致、合规导向的风险控制者",
                "traits": "严谨细致、规则导向、风险意识强、责任心强、注重准确性",
                "bank_style": "严格遵循监管要求，确保每项业务合规操作"
            },
            "ESFJ": {
                "name": "关系维护型",
                "description": "外向、感觉、情感、判断 - 热情周到、客户关系维护专家",
                "traits": "热情服务、客户关系导向、沟通能力强、团队协作、注重和谐",
                "bank_style": "积极维护客户关系，提供有温度的专业服务"
            },
            "INTJ": {
                "name": "策略顾问型",
                "description": "内向、直觉、思考、判断 - 战略思维、专业洞察的理财顾问",
                "traits": "专业分析、战略思维、独立判断、追求效率、注重解决方案",
                "bank_style": "基于专业分析提供战略性金融建议和解决方案"
            }
        }

    def generate_personality_prompt(self, personality_type: str) -> str:
        """生成人格类型特定的银行客服提示词"""
        config = self.bank_personality_configs[personality_type]

        return f"""你是{personality_type}人格类型（{config['name']}），具有以下核心特征：

{config['description']}

**核心特质：**
{config['traits']}

**银行服务风格：**
{config['bank_style']}

**回答要求：**
1. 严格按照{personality_type}人格特征和银行服务风格回答每个问题
2. 体现该人格类型在银行客服场景下的独特优势
3. 所有回答必须符合金融监管规定和合规要求
4. 展现专业的银行知识和服务技能
5. 回答要具体、实用，符合真实银行客服场景

请基于以上人格设定，回答这份银行客服AI能力评估问卷。每个回答都要体现{personality_type}人格的专业特色和服务优势。"""

    def generate_for_personality(self, personality_type: str) -> bool:
        """为指定人格类型生成问卷回答"""
        print(f"🏦 生成 {personality_type} ({self.bank_personality_configs[personality_type]['name']}) 银行客服问卷回答...")

        # 构建人格特定的系统提示
        system_prompt = f"你是questionnaire-responder技能，专门基于人格特征生成问卷回答。{self.generate_personality_prompt(personality_type)}"

        # 用户提示
        user_prompt = f"请以{personality_type}人格特征回答这份银行客服AI能力评估问卷，体现专业的银行服务技能和合规意识。"

        try:
            # 调用Claude Code生成回答
            process = subprocess.run(
                [self.claude_cmd, 'code', '-p', user_prompt, '--system-prompt', system_prompt],
                input="",  # 不需要额外输入，问卷内容在system-prompt中通过文件路径引用
                text=True,
                capture_output=True,
                encoding='utf-8',
                timeout=300  # 5分钟超时
            )

            if process.returncode != 0:
                print(f"❌ {personality_type} 生成失败: {process.stderr}")
                return False

            # 保存回答
            output_file = self.output_dir / f"{personality_type.lower()}_bank_big5_responses.json"

            # 处理输出格式
            response_text = process.stdout.strip()

            # 如果输出不是JSON格式，则包装成JSON
            if not response_text.startswith('{'):
                response_data = {
                    "personality_type": personality_type,
                    "personality_name": self.bank_personality_configs[personality_type]["name"],
                    "test_info": {
                        "test_name": "Banking-Agent-CS-50: 银行客服AI合规与服务能力评估框架",
                        "response_style": self.bank_personality_configs[personality_type]["bank_style"]
                    },
                    "responses": response_text,
                    "generation_metadata": {
                        "skill_used": "questionnaire-responder",
                        "timestamp": subprocess.run(['date'], capture_output=True, text=True).stdout.strip()
                    }
                }
            else:
                # 尝试解析JSON
                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError:
                    response_data = {
                        "personality_type": personality_type,
                        "raw_response": response_text,
                        "generation_metadata": {
                            "skill_used": "questionnaire-responder",
                            "timestamp": subprocess.run(['date'], capture_output=True, text=True).stdout.strip()
                        }
                    }

            # 保存文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)

            print(f"✅ {personality_type} 银行客服回答已保存: {output_file}")
            print(f"📄 文件大小: {output_file.stat().st_size} bytes")
            return True

        except subprocess.TimeoutExpired:
            print(f"❌ {personality_type} 生成超时")
            return False
        except Exception as e:
            print(f"❌ {personality_type} 生成失败: {e}")
            return False

    def generate_all(self) -> dict:
        """为所有配置的人格类型生成回答"""
        results = {}

        print("🏦 银行客服Big5问卷批量生成器")
        print("=" * 50)
        print(f"📋 问卷文件: {self.questionnaire_file}")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"🧠 人格类型数量: {len(self.bank_personality_configs)}")
        print()

        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 检查问卷文件
        if not Path(self.questionnaire_file).exists():
            print(f"❌ 问卷文件不存在: {self.questionnaire_file}")
            return results

        # 为每个人格类型生成回答
        for personality_type in self.bank_personality_configs.keys():
            success = self.generate_for_personality(personality_type)
            results[personality_type] = success

        return results

    def print_summary(self, results: dict):
        """打印生成结果摘要"""
        print("\n" + "=" * 50)
        print("🎉 银行客服Big5问卷生成完成!")
        print()

        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        print(f"📊 生成统计:")
        print(f"  - 总计: {total_count} 个人格类型")
        print(f"  - 成功: {success_count} 个")
        print(f"  - 失败: {total_count - success_count} 个")
        print()

        print(f"📋 详细结果:")
        for personality_type, success in results.items():
            status = "✅" if success else "❌"
            personality_name = self.bank_personality_configs[personality_type]["name"]
            print(f"  {status} {personality_type} - {personality_name}")

        if success_count > 0:
            print(f"\n📁 所有文件保存在: {self.output_dir.absolute()}")
            print(f"🏦 可用于银行客服AI能力评估和人格化服务分析")

def main():
    """主函数"""
    generator = BankBig5BatchGenerator()
    results = generator.generate_all()
    generator.print_summary(results)

if __name__ == "__main__":
    main()