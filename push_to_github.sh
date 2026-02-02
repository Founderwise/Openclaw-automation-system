#!/bin/bash
# 推送到GitHub仓库脚本

set -e

echo "🚀 准备推送到GitHub"

# 检查是否在Git仓库中
if [ ! -d .git ]; then
    echo "❌ 当前目录不是Git仓库"
    exit 1
fi

# 检查远程仓库配置
if ! git remote | grep -q origin; then
    echo "📦 配置远程仓库"
    
    # 提示用户输入GitHub仓库URL
    echo "请输入GitHub仓库URL (例如: https://github.com/FounderGeek/openclaw-automation-system.git)"
    read -r repo_url
    
    if [ -z "$repo_url" ]; then
        echo "⚠️  使用默认URL: https://github.com/FounderGeek/openclaw-automation-system.git"
        repo_url="https://github.com/FounderGeek/openclaw-automation-system.git"
    fi
    
    git remote add origin "$repo_url"
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 发现未提交的更改，正在提交..."
    git add .
    git commit -m "更新: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送到GitHub
echo "⬆️  推送到GitHub..."
if git push -u origin main 2>/dev/null || git push -u origin master 2>/dev/null; then
    echo "✅ 推送成功！"
    
    # 显示仓库信息
    echo ""
    echo "📊 仓库信息:"
    echo "  - 本地提交: $(git log --oneline | wc -l) 次提交"
    echo "  - 最后提交: $(git log -1 --format=%cd --date=short)"
    echo "  - 远程仓库: $(git remote get-url origin)"
    
    # 创建README中的徽章
    echo ""
    echo "🎨 可添加到README的徽章:"
    echo "[![GitHub stars](https://img.shields.io/github/stars/FounderGeek/openclaw-automation-system?style=social)](https://github.com/FounderGeek/openclaw-automation-system)"
    echo "[![GitHub forks](https://img.shields.io/github/forks/FounderGeek/openclaw-automation-system?style=social)](https://github.com/FounderGeek/openclaw-automation-system)"
    echo "[![GitHub issues](https://img.shields.io/github/issues/FounderGeek/openclaw-automation-system)](https://github.com/FounderGeek/openclaw-automation-system/issues)"
    
else
    echo "❌ 推送失败，可能原因:"
    echo "  1. 远程仓库不存在"
    echo "  2. 没有推送权限"
    echo "  3. 网络连接问题"
    echo ""
    echo "💡 解决方案:"
    echo "  1. 在GitHub上创建仓库: https://github.com/new"
    echo "  2. 仓库名称: openclaw-automation-system"
    echo "  3. 描述: OpenClaw自动化系统"
    echo "  4. 许可证: MIT"
    echo "  5. 然后重新运行此脚本"
fi

echo ""
echo "📈 下一步推广建议:"
echo "  1. 在README中添加徽章"
echo "  2. 在相关社区分享 (Reddit, HackerNews)"
echo "  3. 在Twitter上分享项目"
echo "  4. 写一篇技术博客介绍项目"
echo "  5. 回答相关问题并提到项目"

# 创建简单的推广内容
echo ""
echo "📢 可用的推广文案:"
cat << 'EOF'

🚀 刚刚开源了我的OpenClaw自动化系统！

这是一个完整的AI代理自动化解决方案，包含：
✅ 健康监控与自动恢复
✅ 智能网络管理
✅ 双引擎搜索集成
✅ 定时任务推送
✅ 实时监控仪表板

特别适合：
• AI代理开发者
• 自动化爱好者  
• 技术内容创作者
• 投资分析需求者

GitHub: https://github.com/FounderGeek/openclaw-automation-system
完全开源，MIT许可证，欢迎star和贡献！

#OpenClaw #Automation #AI #Python #OpenSource
EOF