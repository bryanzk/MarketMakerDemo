#!/bin/bash
# 自动激活虚拟环境配置脚本 / Auto-Activate Virtual Environment Setup Script
# 将自动激活功能添加到 shell 配置文件中 / Add auto-activate function to shell config file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== 自动激活虚拟环境配置 / Auto-Activate Virtual Environment Setup ==="
echo ""

# 检测 shell 类型
if [[ -n "$ZSH_VERSION" ]]; then
    SHELL_TYPE="zsh"
    CONFIG_FILE="$HOME/.zshrc"
elif [[ -n "$BASH_VERSION" ]]; then
    SHELL_TYPE="bash"
    CONFIG_FILE="$HOME/.bashrc"
else
    echo "⚠ 无法检测 shell 类型，默认使用 zsh"
    SHELL_TYPE="zsh"
    CONFIG_FILE="$HOME/.zshrc"
fi

echo "检测到 shell: $SHELL_TYPE"
echo "配置文件: $CONFIG_FILE"
echo ""

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "创建配置文件: $CONFIG_FILE"
    touch "$CONFIG_FILE"
fi

# 检查是否已配置
if grep -q "auto_activate_venv.*MarketMakerDemo" "$CONFIG_FILE" 2>/dev/null; then
    echo "⚠ 配置已存在，是否要更新？(y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "已取消 / Cancelled"
        exit 0
    fi
    # 删除旧配置
    sed -i.bak '/# MarketMakerDemo auto-activate venv/,/# End MarketMakerDemo auto-activate venv/d' "$CONFIG_FILE"
fi

# 生成配置代码
CONFIG_CODE="# MarketMakerDemo auto-activate venv
# Auto-activate virtual environment for MarketMakerDemo project
function auto_activate_venv() {
    local project_dir=\"$PROJECT_ROOT\"
    local venv_path=\"\$project_dir/.venv\"
    
    # 检查是否在项目目录中
    if [[ \"\$PWD\" == \"\$project_dir\"* ]]; then
        # 如果虚拟环境存在且未激活
        if [ -f \"\$venv_path/bin/activate\" ] && [ -z \"\$VIRTUAL_ENV\" ]; then
            source \"\$venv_path/bin/activate\"
            if [[ \$- == *i* ]]; then
                echo \"✓ 虚拟环境已激活: MarketMakerDemo\"
            fi
        fi
    # 如果离开项目目录，自动停用
    elif [ -n \"\$VIRTUAL_ENV\" ] && [[ \"\$VIRTUAL_ENV\" == \"\$venv_path\" ]]; then
        deactivate
        if [[ \$- == *i* ]]; then
            echo \"✓ 虚拟环境已停用\"
        fi
    fi
}

# zsh 配置
if [[ -n \"\$ZSH_VERSION\" ]]; then
    autoload -U add-zsh-hook
    add-zsh-hook chpwd auto_activate_venv
    auto_activate_venv
fi

# bash 配置
if [[ -n \"\$BASH_VERSION\" ]]; then
    PROMPT_COMMAND=\"auto_activate_venv; \$PROMPT_COMMAND\"
    auto_activate_venv
fi
# End MarketMakerDemo auto-activate venv"

# 添加配置到文件
echo "" >> "$CONFIG_FILE"
echo "$CONFIG_CODE" >> "$CONFIG_FILE"

echo "✓ 配置已添加到 $CONFIG_FILE"
echo ""

# 备份原文件
if [ ! -f "$CONFIG_FILE.bak" ]; then
    cp "$CONFIG_FILE" "$CONFIG_FILE.bak"
    echo "✓ 已创建备份: $CONFIG_FILE.bak"
fi

echo ""
echo "=== 配置完成 / Setup Complete ==="
echo ""
echo "下一步 / Next steps:"
echo "1. 重新加载 shell 配置:"
echo "   source $CONFIG_FILE"
echo ""
echo "2. 或重新打开终端窗口"
echo ""
echo "3. 进入项目目录验证:"
echo "   cd $PROJECT_ROOT"
echo "   # 应该看到: ✓ 虚拟环境已激活"
echo ""
echo "4. 检查虚拟环境:"
echo "   which python"
echo "   # 应该显示: $PROJECT_ROOT/.venv/bin/python"
