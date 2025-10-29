import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cloud_model_evaluator import main

if __name__ == "__main__":
    print("启动云模型评估器...")
    asyncio.run(main())