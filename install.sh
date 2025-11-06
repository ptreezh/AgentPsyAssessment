#!/bin/bash
# Portable PsyAgent 一键安装脚本
# 支持 Ubuntu/Debian, CentOS/RHEL, macOS

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_success() {
    print_message "$GREEN" "✅ $1"
}

print_error() {
    print_message "$RED" "❌ $1"
}

print_warning() {
    print_message "$YELLOW" "⚠️  $1"
}

print_info() {
    print_message "$BLUE" "ℹ️  $1"
}

# 检查操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "ubuntu"
        elif [ -f /etc/redhat-release ]; then
            echo "centos"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 安装系统依赖
install_system_deps() {
    print_info "检查系统依赖..."

    local os=$(detect_os)

    case $os in
        "ubuntu")
            if ! command_exists curl; then
                sudo apt-get update
                sudo apt-get install -y curl git python3 python3-pip python3-venv
            else
                print_success "系统依赖已安装"
            fi
            ;;
        "centos")
            if ! command_exists curl; then
                sudo yum update -y
                sudo yum install -y curl git python3 python3-pip
            else
                print_success "系统依赖已安装"
            fi
            ;;
        "macos")
            if ! command_exists brew; then
                print_info "请先安装 Homebrew: https://brew.sh/"
                exit 1
            fi
            if ! command_exists python3; then
                brew install python3
            fi
            ;;
        *)
            print_error "不支持的操作系统: $OSTYPE"
            exit 1
            ;;
    esac
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."

    if command_exists python3; then
        local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        local major=$(echo $python_version | cut -d. -f1)
        local minor=$(echo $python_version | cut -d. -f2)

        if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; then
            print_success "Python版本: $python_version ✓"
            PYTHON_CMD="python3"
        else
            print_error "Python版本过低: $python_version (需要3.8+)"
            exit 1
        fi
    else
        print_error "未找到Python3，请先安装Python 3.8+"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    print_info "创建Python虚拟环境..."

    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_success "虚拟环境创建成功"
    else
        print_warning "虚拟环境已存在"
    fi

    # 激活虚拟环境
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "虚拟环境已激活"
    else
        print_error "虚拟环境激活失败"
        exit 1
    fi
}

# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖包..."

    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Python依赖安装完成"
    else
        print_error "未找到requirements.txt文件"
        exit 1
    fi
}

# 创建环境变量文件
setup_env() {
    print_info "设置环境变量..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "已创建.env配置文件"
            print_warning "请编辑.env文件，添加您的API密钥"
        else
            print_error "未找到.env.example文件"
            exit 1
        fi
    else
        print_warning ".env文件已存在"
    fi
}

# 创建必要目录
create_directories() {
    print_info "创建项目目录结构..."

    directories=(
        "data/input"
        "data/output"
        "logs"
        "checkpoints"
        "reports"
        "config"
        "test_results"
    )

    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "创建目录: $dir"
        fi
    done
}

# 测试安装
test_installation() {
    print_info "测试安装..."

    # 测试Python导入
    if python3 -c "import unified_api_client; print('✅ 统一API客户端导入成功')"; then
        print_success "核心模块测试通过"
    else
        print_error "核心模块测试失败"
        return 1
    fi

    # 测试配置文件
    if [ -f "config/models_config.json" ]; then
        print_success "配置文件测试通过"
    else
        print_error "配置文件测试失败"
        return 1
    fi

    print_success "安装测试完成"
}

# 创建快速启动脚本
create_start_script() {
    print_info "创建快速启动脚本..."

    cat > start.sh << 'EOF'
#!/bin/bash
# Portable PsyAgent 启动脚本

# 激活虚拟环境
source venv/bin/activate

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "❌ 未找到.env配置文件"
    echo "请先运行: cp .env.example .env"
    exit 1
fi

echo "🧠 Portable PsyAgent 启动中..."
echo "选择运行模式:"
echo "1) 快速演示"
echo "2) 批量处理"
echo "3) 测试OpenRouter集成"
echo "4) 退出"

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "🚀 运行快速演示..."
        python3 -c "
from unified_api_client import create_unified_client
print('🧠 Portable PsyAgent 演示')
print('=' * 30)

try:
    client = create_unified_client()
    connections = client.test_connection()
    print(f'OpenRouter: {\"✅\" if connections.get(\"openrouter\") else \"❌\"}')
    print(f'Ollama: {\"✅\" if connections.get(\"ollama\") else \"❌\"}')

    models = client.get_recommended_models('evaluation')
    if models:
        print(f'推荐模型: {models[0][\"model\"]}')

    print('✅ 系统运行正常')
except Exception as e:
    print(f'❌ 系统错误: {e}')
"
        ;;
    2)
        echo "📦 启动批量处理..."
        read -p "输入目录路径: " input_dir
        read -p "输出目录路径: " output_dir

        if [ -z "$input_dir" ] || [ -z "$output_dir" ]; then
            input_dir="data/input"
            output_dir="data/output"
        fi

        python3 optimized_batch_processor.py \
            --input-dir "$input_dir" \
            --output-dir "$output_dir" \
            --enhanced
        ;;
    3)
        echo "🔗 测试OpenRouter集成..."
        python3 test_openrouter_integration.py
        ;;
    4)
        echo "👋 退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
EOF

    chmod +x start.sh
    print_success "启动脚本创建完成: start.sh"
}

# 创建systemd服务文件（可选）
create_systemd_service() {
    if command_exists systemctl; then
        print_info "是否创建systemd服务? (y/n)"
        read -r create_service

        if [ "$create_service" = "y" ] || [ "$create_service" = "Y" ]; then
            local current_dir=$(pwd)
            local user=$(whoami)

            sudo tee /etc/systemd/system/portable-psyagent.service > /dev/null << EOF
[Unit]
Description=Portable PsyAgent Service
After=network.target

[Service]
Type=simple
User=$user
WorkingDirectory=$current_dir
Environment=PATH=$current_dir/venv/bin
ExecStart=$current_dir/venv/bin/python optimized_batch_processor.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

            sudo systemctl daemon-reload
            print_success "systemd服务创建完成"
            print_info "启动服务: sudo systemctl start portable-psyagent"
            print_info "开机自启: sudo systemctl enable portable-psyagent"
        fi
    fi
}

# 显示安装完成信息
show_completion_info() {
    print_success "🎉 Portable PsyAgent 安装完成！"
    echo
    echo "📋 下一步操作："
    echo "1. 编辑配置文件: nano .env"
    echo "2. 添加OpenRouter API密钥"
    echo "3. 运行启动脚本: ./start.sh"
    echo
    echo "📚 文档资源："
    echo "- 快速起步指南: 快速起步指南.md"
    echo "- OpenRouter设置: OPENROUTER_SETUP_GUIDE.md"
    echo "- 项目README: README.md"
    echo
    echo "🆘 获取帮助："
    echo "- 官网: https://agentpsy.com"
    echo "- 作者: ptreezh <3061176@qq.com>"
    echo "- GitHub Issues: https://github.com/ptreezh/AgentPsyAssessment/issues"
    echo "- 测试集成: python3 test_openrouter_integration.py"
    echo
    echo "🚀 开始您的心理评估之旅！"
}

# 主安装流程
main() {
    echo "🧠 Portable PsyAgent 一键安装脚本"
    echo "====================================="
    echo

    # 检查是否在项目根目录
    if [ ! -f "unified_api_client.py" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi

    print_info "开始安装 Portable PsyAgent..."
    echo

    # 安装步骤
    install_system_deps
    check_python
    create_venv
    install_python_deps
    setup_env
    create_directories
    test_installation
    create_start_script
    create_systemd_service

    echo
    show_completion_info
}

# 错误处理
trap 'print_error "安装过程中发生错误，请检查上述输出"; exit 1' ERR

# 运行主程序
main "$@"