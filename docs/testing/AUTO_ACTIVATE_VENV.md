# Shell 配置文件自动激活虚拟环境指南 / Auto-Activate Virtual Environment Guide

## 概述 / Overview

本指南说明如何在 shell 配置文件中设置自动激活虚拟环境，这样每次打开终端时都会自动激活项目的虚拟环境。

This guide explains how to configure your shell to automatically activate the virtual environment when opening a terminal.

## 方法 1：项目特定自动激活（推荐）

### 对于 zsh (macOS 默认)

编辑 `~/.zshrc` 文件：

```bash
# 打开配置文件
nano ~/.zshrc
# 或
code ~/.zshrc
```

添加以下内容：

```bash
# 自动激活 MarketMakerDemo 虚拟环境
# Auto-activate MarketMakerDemo virtual environment
function auto_activate_venv() {
    local project_dir="/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo"
    
    # 如果当前目录在项目目录或其子目录中
    # If current directory is in project directory or subdirectory
    if [[ "$PWD" == "$project_dir"* ]]; then
        # 如果虚拟环境存在且未激活
        # If virtual environment exists and is not activated
        if [ -f "$project_dir/.venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
            source "$project_dir/.venv/bin/activate"
            echo "✓ 虚拟环境已激活 / Virtual environment activated: $project_dir/.venv"
        fi
    # 如果离开项目目录，自动停用
    # If leaving project directory, auto-deactivate
    elif [ -n "$VIRTUAL_ENV" ] && [[ "$VIRTUAL_ENV" == "$project_dir/.venv" ]]; then
        deactivate
        echo "✓ 虚拟环境已停用 / Virtual environment deactivated"
    fi
}

# 每次切换目录时检查
# Check on every directory change
autoload -U add-zsh-hook
add-zsh-hook chpwd auto_activate_venv

# 初始加载时也检查
# Also check on initial load
auto_activate_venv
```

### 对于 bash

编辑 `~/.bashrc` 文件：

```bash
# 打开配置文件
nano ~/.bashrc
# 或
code ~/.bashrc
```

添加以下内容：

```bash
# 自动激活 MarketMakerDemo 虚拟环境
# Auto-activate MarketMakerDemo virtual environment
function auto_activate_venv() {
    local project_dir="/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo"
    
    # 如果当前目录在项目目录或其子目录中
    if [[ "$PWD" == "$project_dir"* ]]; then
        # 如果虚拟环境存在且未激活
        if [ -f "$project_dir/.venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
            source "$project_dir/.venv/bin/activate"
            echo "✓ 虚拟环境已激活 / Virtual environment activated: $project_dir/.venv"
        fi
    # 如果离开项目目录，自动停用
    elif [ -n "$VIRTUAL_ENV" ] && [[ "$VIRTUAL_ENV" == "$project_dir/.venv" ]]; then
        deactivate
        echo "✓ 虚拟环境已停用 / Virtual environment deactivated"
    fi
}

# 每次切换目录时检查
# Check on every directory change
PROMPT_COMMAND="auto_activate_venv; $PROMPT_COMMAND"

# 初始加载时也检查
# Also check on initial load
auto_activate_venv
```

## 方法 2：简单版本（仅在项目目录时激活）

如果您只想在进入项目目录时激活，可以使用更简单的版本：

### zsh 版本

```bash
# 添加到 ~/.zshrc
cd() {
    builtin cd "$@"
    
    # 检查是否在项目目录中
    if [[ -f ".venv/bin/activate" ]] && [[ -z "$VIRTUAL_ENV" ]]; then
        source .venv/bin/activate
        echo "✓ 虚拟环境已激活 / Virtual environment activated"
    elif [[ -n "$VIRTUAL_ENV" ]] && [[ ! -f ".venv/bin/activate" ]]; then
        # 离开项目目录时停用
        deactivate
        echo "✓ 虚拟环境已停用 / Virtual environment deactivated"
    fi
}
```

### bash 版本

```bash
# 添加到 ~/.bashrc
cd() {
    builtin cd "$@"
    
    # 检查是否在项目目录中
    if [[ -f ".venv/bin/activate" ]] && [[ -z "$VIRTUAL_ENV" ]]; then
        source .venv/bin/activate
        echo "✓ 虚拟环境已激活 / Virtual environment activated"
    elif [[ -n "$VIRTUAL_ENV" ]] && [[ ! -f ".venv/bin/activate" ]]; then
        # 离开项目目录时停用
        deactivate
        echo "✓ 虚拟环境已停用 / Virtual environment deactivated"
    fi
}
```

## 方法 3：使用 direnv（高级，推荐用于多项目）

`direnv` 是一个更强大的工具，可以为不同项目自动加载环境变量和激活虚拟环境。

### 安装 direnv

```bash
# macOS
brew install direnv

# 或使用 pip
pip install direnv
```

### 配置 shell

**zsh:**
```bash
# 添加到 ~/.zshrc
eval "$(direnv hook zsh)"
```

**bash:**
```bash
# 添加到 ~/.bashrc
eval "$(direnv hook bash)"
```

### 在项目根目录创建 `.envrc`

```bash
# 在项目根目录创建
cd /Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo
cat > .envrc << 'EOF'
# 激活虚拟环境
source .venv/bin/activate

# 设置 PYTHONPATH
export PYTHONPATH="${PWD}:${PYTHONPATH}"
EOF

# 允许 direnv 加载
direnv allow
```

## 应用配置

### 步骤 1：编辑配置文件

```bash
# 对于 zsh (macOS 默认)
nano ~/.zshrc

# 或使用编辑器
code ~/.zshrc
```

### 步骤 2：添加配置代码

选择上面方法 1 或方法 2 的代码，添加到文件末尾。

### 步骤 3：重新加载配置

```bash
# 重新加载 shell 配置
source ~/.zshrc
# 或
source ~/.bashrc
```

### 步骤 4：验证

```bash
# 进入项目目录
cd /Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo

# 应该看到激活消息
# 检查虚拟环境
which python
# 应该显示: /path/to/MarketMakerDemo/.venv/bin/python

# 离开项目目录
cd ~

# 应该看到停用消息（如果使用方法 1）
```

## 当前项目路径

根据您的项目位置，使用以下路径：

```bash
/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo
```

## 注意事项 / Notes

### 1. 性能考虑

- 方法 1 会在每次切换目录时检查，可能稍微影响性能
- 如果项目很多，考虑使用方法 3 (direnv)

### 2. 多项目支持

如果您有多个项目，可以修改函数支持多个项目：

```bash
function auto_activate_venv() {
    # 项目列表
    local projects=(
        "/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo"
        "/path/to/other/project"
    )
    
    for project_dir in "${projects[@]}"; do
        if [[ "$PWD" == "$project_dir"* ]]; then
            if [ -f "$project_dir/.venv/bin/activate" ] && [ -z "$VIRTUAL_ENV" ]; then
                source "$project_dir/.venv/bin/activate"
                echo "✓ 虚拟环境已激活: $project_dir/.venv"
                return
            fi
        fi
    done
    
    # 如果不在任何项目目录中，停用
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
        echo "✓ 虚拟环境已停用"
    fi
}
```

### 3. 禁用自动激活

如果某个终端会话不想自动激活，可以：

```bash
# 临时禁用函数
unset -f auto_activate_venv

# 或手动停用
deactivate
```

### 4. 检查当前配置

```bash
# 查看是否已配置
grep -n "auto_activate_venv\|direnv" ~/.zshrc ~/.bashrc 2>/dev/null

# 查看当前虚拟环境
echo $VIRTUAL_ENV
```

## 推荐配置（完整版）

以下是一个完整的、生产就绪的配置：

```bash
# ============================================
# 自动虚拟环境管理 / Auto Virtual Environment Management
# ============================================

function auto_activate_venv() {
    # 项目配置 / Project configuration
    local project_dir="/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo"
    local venv_path="$project_dir/.venv"
    
    # 检查是否在项目目录中 / Check if in project directory
    if [[ "$PWD" == "$project_dir"* ]]; then
        # 检查虚拟环境是否存在 / Check if virtual environment exists
        if [ -f "$venv_path/bin/activate" ]; then
            # 如果未激活，则激活 / Activate if not already activated
            if [ -z "$VIRTUAL_ENV" ] || [[ "$VIRTUAL_ENV" != "$venv_path" ]]; then
                source "$venv_path/bin/activate"
                # 可选：显示提示（仅在交互式 shell 中）
                # Optional: Show prompt (only in interactive shell)
                if [[ $- == *i* ]]; then
                    echo "✓ 虚拟环境已激活: $(basename $project_dir)"
                fi
            fi
        fi
    # 如果离开项目目录，停用 / Deactivate if leaving project directory
    elif [ -n "$VIRTUAL_ENV" ] && [[ "$VIRTUAL_ENV" == "$venv_path" ]]; then
        deactivate
        if [[ $- == *i* ]]; then
            echo "✓ 虚拟环境已停用"
        fi
    fi
}

# zsh 配置 / zsh configuration
if [[ -n "$ZSH_VERSION" ]]; then
    autoload -U add-zsh-hook
    add-zsh-hook chpwd auto_activate_venv
    # 初始加载时检查 / Check on initial load
    auto_activate_venv
fi

# bash 配置 / bash configuration
if [[ -n "$BASH_VERSION" ]]; then
    PROMPT_COMMAND="auto_activate_venv; $PROMPT_COMMAND"
    # 初始加载时检查 / Check on initial load
    auto_activate_venv
fi
```

## 快速设置脚本

我也可以为您创建一个快速设置脚本，自动添加到您的 shell 配置文件中。需要我创建吗？
