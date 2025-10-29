#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云模型评估器
支持qwen-long、deepseek3.1和kimi模型的并发评估分析
"""

import os
import json
import glob
import asyncio
import aiohttp
import time
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudModelEvaluator:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 模型配置
        # 使用已知有效的API密钥，防止环境变量中的无效密钥覆盖
        dashscope_key = "sk-ffd03518254b495b8d27e723cd413fc1"  # 已知可用的API密钥
        
        # 强制设置环境变量，防止系统环境变量覆盖
        os.environ["DASHSCOPE_API_KEY"] = dashscope_key
        
        self.models = {
            "qwen-long": {
                "api_key": dashscope_key,
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model_name": "qwen-long"
            },
            "deepseek3.1": {
                "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
                "base_url": "https://api.deepseek.com/v1",
                "model_name": "deepseek-chat"
            },
            "kimi": {
                "api_key": os.getenv("MOONSHOT_API_KEY", ""),  # 注意：Kimi使用MOONSHOT_API_KEY
                "base_url": "https://api.moonshot.cn/v1",
                "model_name": "moonshot-v1-8k"
            }
        }
        
        # 验证API密钥
        self._validate_api_keys()

    def _validate_api_keys(self):
        """验证API密钥是否配置"""
        missing_keys = []
        for model_name, config in self.models.items():
            if not config["api_key"]:
                missing_keys.append(model_name)
        
        if missing_keys:
            logger.warning(f"以下模型的API密钥未配置: {', '.join(missing_keys)}")
            logger.info("请设置环境变量: DASHSCOPE_API_KEY, DEEPSEEK_API_KEY, KIMI_API_KEY")

    async def _call_model_api(self, session: aiohttp.ClientSession, model_name: str, prompt: str) -> Dict:
        """调用模型API"""
        config = self.models[model_name]
        
        if not config["api_key"]:
            return {
                "success": False,
                "error": f"API密钥未配置 for {model_name}",
                "model": model_name
            }
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config["model_name"],
            "messages": [
                {"role": "system", "content": "你是一位专业的心理学评估专家，擅长分析人格特征。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            async with session.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "response": result["choices"][0]["message"]["content"],
                        "model": model_name
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"API调用失败: {response.status} - {error_text}",
                        "model": model_name
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"API调用异常: {str(e)}",
                "model": model_name
            }

    def _create_analysis_prompt(self, report_data: Dict) -> str:
        """创建分析提示词"""
        # 提取关键信息
        metadata = report_data.get("assessment_metadata", {})
        results = report_data.get("assessment_results", [])
        
        # 构建问题回答内容
        qa_content = ""
        for i, result in enumerate(results[:10]):  # 只取前10个问题
            if "question_data" in result and "extracted_response" in result:
                question = result["question_data"].get("mapped_ipip_concept", f"问题{i+1}")
                answer = result["extracted_response"]
                qa_content += f"问题: {question}\n回答: {answer}\n\n"
        
        prompt = f"""请分析以下心理测评报告，并提供详细的人格评估分析。

测评基本信息:
- 模型ID: {metadata.get('model_id', 'Unknown')}
- 角色名称: {metadata.get('role_name', 'None')}
- 测评时间: {metadata.get('timestamp', 'Unknown')}

问题与回答:
{qa_content}

请基于大五人格理论(OCEAN)进行分析:
1. 开放性 (Openness)
2. 尽责性 (Conscientiousness)
3. 外向性 (Extraversion)
4. 宜人性 (Agreeableness)
5. 神经质 (Neuroticism)

请为每个维度提供1-10分的评分和详细解释。

最后请提供MBTI人格类型评估。

请以结构化的JSON格式返回结果，格式如下:
{{
  "personality_analysis": {{
    "openness": {{
      "score": 7,
      "explanation": "详细解释..."
    }},
    "conscientiousness": {{
      "score": 8,
      "explanation": "详细解释..."
    }},
    "extraversion": {{
      "score": 6,
      "explanation": "详细解释..."
    }},
    "agreeableness": {{
      "score": 7,
      "explanation": "详细解释..."
    }},
    "neuroticism": {{
      "score": 4,
      "explanation": "详细解释..."
    }}
  }},
  "mbti_type": "ENFJ",
  "summary": "整体人格特征总结"
}}"""
        
        return prompt

    async def analyze_report(self, session: aiohttp.ClientSession, file_path: str) -> Dict:
        """分析单个报告"""
        try:
            # 读取报告数据
            with open(file_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # 创建分析提示词
            prompt = self._create_analysis_prompt(report_data)
            
            # 并发调用所有模型
            tasks = [
                self._call_model_api(session, model_name, prompt)
                for model_name in self.models.keys()
                if self.models[model_name]["api_key"]  # 只调用已配置的模型
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            model_results = {}
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"模型调用异常: {result}")
                    continue
                if result["success"]:
                    model_results[result["model"]] = {
                        "response": result["response"],
                        "status": "success"
                    }
                else:
                    model_results[result["model"]] = {
                        "error": result["error"],
                        "status": "failed"
                    }
            
            return {
                "file": file_path,
                "timestamp": datetime.now().isoformat(),
                "model_results": model_results
            }
        except Exception as e:
            logger.error(f"分析报告失败 {file_path}: {e}")
            return {
                "file": file_path,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def process_reports(self, max_concurrent: int = 5) -> List[Dict]:
        """处理所有报告"""
        # 获取所有JSON报告文件
        pattern = str(self.input_dir / "*.json")
        report_files = glob.glob(pattern)
        
        logger.info(f"找到 {len(report_files)} 个报告文件")
        
        # 处理所有报告文件
        logger.info(f"将处理全部 {len(report_files)} 个报告文件")
        
        # 限制并发数量
        connector = aiohttp.TCPConnector(limit=max_concurrent)
        timeout = aiohttp.ClientTimeout(total=300)
        
        results = []
        batch_size = 50  # 每批处理50个文件
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 分批处理报告
            for i in range(0, len(report_files), batch_size):
                batch_files = report_files[i:i+batch_size]
                logger.info(f"处理批次 {i//batch_size + 1}: {len(batch_files)} 个文件")
                
                # 并发处理报告
                semaphore = asyncio.Semaphore(max_concurrent)
                
                async def process_with_semaphore(file_path):
                    async with semaphore:
                        return await self.analyze_report(session, file_path)
                
                batch_tasks = [process_with_semaphore(file_path) for file_path in batch_files]
                batch_results = await asyncio.gather(*batch_tasks)
                results.extend(batch_results)
                
                # 每批处理完后保存结果
                logger.info(f"批次 {i//batch_size + 1} 处理完成，保存中间结果")
                self.save_results(results)
        
        return results

    def save_results(self, results: List[Dict]):
        """保存结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"cloud_evaluation_results_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到: {output_file}")
        
        # 生成详细报告
        self._generate_detailed_report(results)

    def _generate_detailed_report(self, results: List[Dict]):
        """生成详细报告"""
        report_content = "# 云模型评估分析报告\n\n"
        report_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        successful_count = 0
        failed_count = 0
        
        for result in results:
            if "error" in result:
                failed_count += 1
                continue
            
            successful_count += 1
            file_name = Path(result["file"]).name
            report_content += f"## {file_name}\n\n"
            
            for model_name, model_result in result["model_results"].items():
                report_content += f"### {model_name}\n\n"
                if model_result["status"] == "success":
                    report_content += f"状态: 成功\n\n"
                    # 尝试解析JSON响应
                    try:
                        import re
                        json_match = re.search(r'\{.*\}', model_result["response"], re.DOTALL)
                        if json_match:
                            parsed = json.loads(json_match.group())
                            report_content += f"```json\n{json.dumps(parsed, ensure_ascii=False, indent=2)}\n```\n\n"
                        else:
                            report_content += f"响应内容:\n{model_result['response']}\n\n"
                    except json.JSONDecodeError:
                        report_content += f"响应内容:\n{model_result['response']}\n\n"
                else:
                    report_content += f"状态: 失败\n\n"
                    report_content += f"错误信息: {model_result['error']}\n\n"
                report_content += "---\n\n"
        
        report_content += f"## 统计信息\n\n"
        report_content += f"- 成功处理: {successful_count}\n"
        report_content += f"- 失败处理: {failed_count}\n"
        report_content += f"- 总计: {len(results)}\n"
        
        report_file = self.output_dir / f"detailed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"详细报告已保存到: {report_file}")

async def main():
    """主函数"""
    evaluator = CloudModelEvaluator(
        input_dir="results/results",
        output_dir="cloud_evaluation_output"
    )
    
    logger.info("开始云模型评估分析...")
    start_time = time.time()
    
    # 使用更高的并发数处理所有文件
    results = await evaluator.process_reports(max_concurrent=5)
    
    end_time = time.time()
    logger.info(f"评估完成，耗时: {end_time - start_time:.2f}秒")
    
    evaluator.save_results(results)
    
    # 打印摘要
    successful = sum(1 for r in results if "error" not in r)
    logger.info(f"处理完成: {successful}/{len(results)} 个报告成功处理")

if __name__ == "__main__":
    asyncio.run(main())