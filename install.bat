@echo off
REM Portable PsyAgent Windows一键安装脚本
REM 支持 Windows 10/11

setlocal enabledelayedexpansion

echo.
echo 🧠 Portable PsyAgent Windows安装脚本
echo =====================================
echo.

REM 检查是否在项目根目录
if not exist "unified_api_client.py" (
    echo ❌ 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 检查Python是否安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 获取Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

REM 检查pip是否可用
echo 🔍 检查pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip不可用，请检查Python安装
    pause
    exit /b 1
)

echo ✅ pip可用

REM 创建虚拟环境
echo 🏗️  创建Python虚拟环境...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
) else (
    echo ⚠️  虚拟环境已存在
)

REM 激活虚拟环境
echo 🔌 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

REM 升级pip
echo ⬆️  升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 📦 安装Python依赖包...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    echo ✅ Python依赖安装完成
) else (
    echo ❌ 未找到requirements.txt文件
    pause
    exit /b 1
)

REM 创建环境变量文件
echo ⚙️  设置环境变量...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo ✅ 已创建.env配置文件
        echo ⚠️  请编辑.env文件，添加您的API密钥
    ) else (
        echo ❌ 未找到.env.example文件
        pause
        exit /b 1
    )
) else (
    echo ⚠️  .env文件已存在
)

REM 创建必要目录
echo 📁 创建项目目录结构...
set "directories=data/input data\output logs checkpoints reports config test_results"

for %%d in (%directories%) do (
    if not exist "%%d" (
        mkdir "%%d"
        echo ✅ 创建目录: %%d
    )
)

REM 测试安装
echo 🧪 测试安装...

REM 测试Python导入
python -c "import unified_api_client; print('✅ 统一API客户端导入成功')" >nul 2>&1
if errorlevel 1 (
    echo ❌ 核心模块测试失败
    pause
    exit /b 1
) else (
    echo ✅ 核心模块测试通过
)

REM 测试配置文件
if exist "config\models_config.json" (
    echo ✅ 配置文件测试通过
) else (
    echo ❌ 配置文件测试失败
    pause
    exit /b 1
)

echo ✅ 安装测试完成

REM 创建Windows启动脚本
echo 🔨 创建Windows启动脚本...

(
echo @echo off
echo REM Portable PsyAgent Windows启动脚本
echo.
echo REM 激活虚拟环境
echo call venv\Scripts\activate.bat
echo.
echo REM 检查环境变量
echo if not exist ".env" ^(
echo     echo ❌ 未找到.env配置文件
echo     echo 请先运行: copy .env.example .env
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo 🧠 Portable PsyAgent 启动中...
echo echo 选择运行模式:
echo echo 1^) 快速演示
echo echo 2^) 批量处理
echo echo 3^) 测试OpenRouter集成
echo echo 4^) 退出
echo echo.
echo set /p choice="请选择 ^(1-4^): "
echo.
echo if "%%choice%%"=="1" ^(
echo     echo 🚀 运行快速演示...
echo     python -c "from unified_api_client import create_unified_client; print('🧠 Portable PsyAgent 演示\n' + '='*30); client = create_unified_client(); connections = client.test_connection(); print(f'OpenRouter: {\"✅\" if connections.get(\"openrouter\") else \"❌\"}'); print(f'Ollama: {\"✅\" if connections.get(\"ollama\") else \"❌\"}'); models = client.get_recommended_models('evaluation'); print(f'推荐模型: {models[0][\"model\"]}' if models else '无推荐模型'); print('✅ 系统运行正常')"
echo ^) else if "%%choice%%"=="2" ^(
echo     echo 📦 启动批量处理...
echo     set /p input_dir="输入目录路径 (默认: data\input): "
echo     set /p output_dir="输出目录路径 (默认: data\output): "
echo     if "%%input_dir%%"=="" set input_dir=data\input
echo     if "%%output_dir%%"=="" set output_dir=data\output
echo     python optimized_batch_processor.py --input-dir "%%input_dir%%" --output-dir "%%output_dir%%" --enhanced
echo ^) else if "%%choice%%"=="3" ^(
echo     echo 🔗 测试OpenRouter集成...
echo     python test_openrouter_integration.py
echo ^) else if "%%choice%%"=="4" ^(
echo     echo 👋 退出
echo     exit /b 0
echo ^) else ^(
echo     echo ❌ 无效选择
echo     exit /b 1
echo ^)
echo.
echo pause
) > start.bat

echo ✅ 启动脚本创建完成: start.bat

REM 创建快速演示脚本
(
echo @echo off
echo REM Portable PsyAgent 快速演示
echo.
echo call venv\Scripts\activate.bat
echo.
echo echo 🧠 Portable PsyAgent 快速演示
echo echo ========================
echo echo.
echo.
echo python -c "
echo from unified_api_client import create_unified_client
echo try:
echo     print('正在初始化系统...')
echo     client = create_unified_client()
echo     connections = client.test_connection()
echo     print(f'OpenRouter: {\"✅ 连接正常\" if connections.get(\"openrouter\") else \"❌ 连接失败\"}')
echo     print(f'Ollama: {\"✅ 连接正常\" if connections.get(\"ollama\") else \"❌ 连接失败\"}')
echo
echo     models = client.get_recommended_models('evaluation')
echo     if models:
echo         print(f'推荐评估模型: {models[0][\"model\"]}')
echo         print(f'模型说明: {models[0][\"reason\"]}')
echo
echo     print()
echo     print('🎉 系统运行正常！可以进行心理评估分析。')
echo except Exception as e:
echo     print(f'❌ 系统错误: {e}')
echo     print('请检查.env配置文件中的API密钥设置')
echo "
echo.
echo pause
) > quick_demo.bat

echo ✅ 快速演示脚本创建完成: quick_demo.bat

echo.
echo 🎉 Portable PsyAgent 安装完成！
echo.
echo 📋 下一步操作：
echo 1. 编辑配置文件: notepad .env
echo 2. 添加OpenRouter API密钥
echo 3. 运行启动脚本: start.bat
echo 4. 或运行快速演示: quick_demo.bat
echo.
echo 📚 文档资源：
echo - 快速起步指南: 快速起步指南.md
echo - OpenRouter设置: OPENROUTER_SETUP_GUIDE.md
echo - 项目README: README.md
echo.
echo 🆘 获取帮助：
echo - 官网: https://agentpsy.com
echo - 作者: ptreezh <3061176@qq.com>
echo - GitHub Issues: https://github.com/ptreezh/AgentPsyAssessment/issues
echo - 测试集成: python test_openrouter_integration.py
echo.
echo 🚀 开始您的心理评估之旅！
echo.
pause