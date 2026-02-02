#!/usr/bin/env python3
"""
OpenClaw自动化系统 - 基础设置示例
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """设置环境变量"""
    print("🔧 设置OpenClaw自动化系统环境")
    
    # 创建.env文件示例
    env_example = """# OpenClaw自动化系统配置
# 复制此文件为.env并填写你的API密钥

# 搜索API配置
TAVILY_API_KEY=your_tavily_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# 消息平台配置
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
FEISHU_BOT_TOKEN=your_feishu_bot_token_here

# 系统配置
TIMEZONE=Asia/Shanghai
LOG_LEVEL=INFO
LOG_FILE=logs/system.log

# 定时任务配置
TECH_HEADLINES_SCHEDULE=0 8 * * *  # 每天8:00
INVESTMENT_ANALYSIS_SCHEDULE=0 18 * * *  # 每天18:00
HEALTH_CHECK_SCHEDULE=*/30 * * * *  # 每30分钟

# 网络配置
HTTP_PROXY=http://127.0.0.1:4780
HTTPS_PROXY=http://127.0.0.1:4780
NO_PROXY=localhost,127.0.0.1,baidu.com,taobao.com

# 数据存储
DATA_DIR=./data
CACHE_DIR=./cache
BACKUP_DIR=./backups
"""
    
    env_path = project_root / ".env.example"
    env_path.write_text(env_example)
    print(f"✅ 创建环境变量示例文件: {env_path}")
    
    # 创建必要的目录
    directories = ["logs", "data", "cache", "backups", "config"]
    for dir_name in directories:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")

def check_dependencies():
    """检查依赖"""
    print("\n📦 检查Python依赖")
    
    required_packages = [
        "aiohttp",
        "requests", 
        "beautifulsoup4",
        "schedule",
        "psutil",
        "pandas",
        "yfinance",
        "flask",
        "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} (未安装)")
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖已安装")
    return True

def create_config_files():
    """创建配置文件"""
    print("\n⚙️ 创建配置文件")
    
    # 定时任务配置
    schedule_config = {
        "tech_headlines": {
            "enabled": True,
            "schedule": "0 8 * * *",
            "timezone": "Asia/Shanghai",
            "format": "bilingual",
            "sections": ["AI", "quantum", "materials", "web3", "security"]
        },
        "investment_analysis": {
            "enabled": True,
            "schedule": "0 18 * * *",
            "timezone": "Asia/Shanghai",
            "markets": ["A股", "港股", "美股", "加密货币"],
            "virtual_capital": 100000
        },
        "health_check": {
            "enabled": True,
            "schedule": "*/30 * * * *",
            "checks": ["openclaw_status", "network", "disk", "memory"]
        }
    }
    
    import json
    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)
    
    schedule_path = config_dir / "schedule.json"
    schedule_path.write_text(json.dumps(schedule_config, indent=2, ensure_ascii=False))
    print(f"✅ 创建定时任务配置: {schedule_path}")
    
    # 创建日志配置
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "simple": {
                "format": "%(levelname)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": "logs/system.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # root logger
                "level": "INFO",
                "handlers": ["console", "file"]
            },
            "monitor": {
                "level": "DEBUG",
                "handlers": ["file"],
                "propagate": False
            },
            "network": {
                "level": "DEBUG",
                "handlers": ["file"],
                "propagate": False
            }
        }
    }
    
    log_config_path = config_dir / "logging.json"
    log_config_path.write_text(json.dumps(log_config, indent=2))
    print(f"✅ 创建日志配置: {log_config_path}")

def create_basic_scripts():
    """创建基础脚本"""
    print("\n📜 创建管理脚本")
    
    # 启动脚本
    start_script = """#!/bin/bash
# OpenClaw自动化系统启动脚本

set -e

echo "🚀 启动OpenClaw自动化系统"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

# 检查依赖
echo "📦 检查Python依赖..."
python3 -c "import aiohttp, requests, schedule, psutil" || {
    echo "❌ 缺少依赖，正在安装..."
    pip install -r requirements.txt
}

# 检查环境变量
if [ ! -f .env ]; then
    echo "⚠️  未找到.env文件，使用示例配置"
    cp .env.example .env
    echo "请编辑.env文件配置API密钥"
fi

# 加载环境变量
export $(grep -v '^#' .env | xargs)

# 启动监控系统
echo "🔧 启动健康监控..."
python3 -m monitor.founder_health_monitor &

# 启动网络管理
echo "🌐 启动网络管理..."
python3 -m network.founder_network_manager &

# 启动Web仪表板
echo "📊 启动监控仪表板..."
python3 dashboard/founder_dashboard.py &

echo "✅ 系统启动完成"
echo "📱 监控仪表板: http://localhost:8080"
echo "📝 查看日志: tail -f logs/system.log"
"""
    
    start_path = project_root / "start.sh"
    start_path.write_text(start_script)
    start_path.chmod(0o755)
    print(f"✅ 创建启动脚本: {start_path}")
    
    # 停止脚本
    stop_script = """#!/bin/bash
# OpenClaw自动化系统停止脚本

echo "🛑 停止OpenClaw自动化系统"

# 停止所有相关进程
pkill -f "founder_health_monitor" || true
pkill -f "founder_network_manager" || true
pkill -f "founder_dashboard" || true

echo "✅ 系统已停止"
"""
    
    stop_path = project_root / "stop.sh"
    stop_path.write_text(stop_script)
    stop_path.chmod(0o755)
    print(f"✅ 创建停止脚本: {stop_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("OpenClaw自动化系统 - 初始化设置")
    print("=" * 60)
    
    # 执行设置步骤
    setup_environment()
    
    if not check_dependencies():
        print("\n⚠️  请先安装缺失的依赖包")
        return
    
    create_config_files()
    create_basic_scripts()
    
    print("\n" + "=" * 60)
    print("🎉 初始化完成！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 复制 .env.example 为 .env")
    print("2. 编辑 .env 文件，填写你的API密钥")
    print("3. 运行 ./start.sh 启动系统")
    print("4. 访问 http://localhost:8080 查看监控仪表板")
    print("\n更多信息请查看 README.md")
    print("=" * 60)

if __name__ == "__main__":
    main()