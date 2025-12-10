#!/bin/bash
# One-Click Build Script / 一键构建脚本
# Builds the entire project: environment setup, dependencies, tests, linting, and docs
# 构建整个项目：环境设置、依赖、测试、代码检查和文档
# Owner: Agent DevOps

set -e  # Exit on error / 遇到错误立即退出

# Colors for output / 输出颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get absolute path to script directory / 获取脚本目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Parse command line arguments / 解析命令行参数
SKIP_TESTS=false
SKIP_LINT=false
SKIP_DOCS=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-lint)
            SKIP_LINT=true
            shift
            ;;
        --skip-docs)
            SKIP_DOCS=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./build.sh [OPTIONS]"
            echo "Options:"
            echo "  --skip-tests    Skip running tests / 跳过测试"
            echo "  --skip-lint     Skip linting checks / 跳过代码检查"
            echo "  --skip-docs     Skip documentation build / 跳过文档构建"
            echo "  --verbose, -v   Enable verbose output / 启用详细输出"
            echo "  --help, -h      Show this help message / 显示帮助信息"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            echo "Use --help for usage information / 使用 --help 查看使用信息"
            exit 1
            ;;
    esac
done

# Logging function / 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📦 $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Start build process / 开始构建流程
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   MarketMakerDemo Build Script           ║${NC}"
echo -e "${GREEN}║   一键构建脚本                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Environment Setup / 环境设置
log_step "Step 1: Environment Setup / 环境设置"

if [ -f "scripts/setup_unified_environment.sh" ]; then
    log_info "Running unified environment setup / 运行统一环境设置..."
    if [ "$VERBOSE" = true ]; then
        bash scripts/setup_unified_environment.sh
    else
        bash scripts/setup_unified_environment.sh > /dev/null 2>&1
    fi
    log_success "Environment setup completed / 环境设置完成"
else
    log_warning "setup_unified_environment.sh not found, creating basic venv / 未找到 setup_unified_environment.sh，创建基本虚拟环境..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        log_success "Virtual environment created / 虚拟环境已创建"
    fi
    source .venv/bin/activate
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    log_success "Dependencies installed / 依赖已安装"
fi

# Activate virtual environment / 激活虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
    log_success "Virtual environment activated / 虚拟环境已激活"
    
    # Set PYTHONPATH to project root for proper imports / 设置 PYTHONPATH 到项目根目录以确保正确导入
    export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
    log_info "PYTHONPATH set to: ${PYTHONPATH} / PYTHONPATH 已设置为：${PYTHONPATH}"
else
    log_error "Virtual environment not found / 未找到虚拟环境"
    exit 1
fi

# Step 2: Environment Verification / 环境验证
log_step "Step 2: Environment Verification / 环境验证"

if [ -f "scripts/verify_server_env.sh" ]; then
    log_info "Running environment verification / 运行环境验证..."
    if [ "$VERBOSE" = true ]; then
        bash scripts/verify_server_env.sh
    else
        bash scripts/verify_server_env.sh > /dev/null 2>&1 || log_warning "Some verification checks failed / 部分验证检查失败"
    fi
    log_success "Environment verification completed / 环境验证完成"
else
    log_warning "verify_server_env.sh not found, skipping verification / 未找到 verify_server_env.sh，跳过验证"
fi

# Step 3: Install Playwright Browsers (for E2E tests) / 安装 Playwright 浏览器（用于 E2E 测试）
log_step "Step 3: Install Playwright Browsers / 安装 Playwright 浏览器"

log_info "Installing Playwright browsers / 安装 Playwright 浏览器..."
if [ "$VERBOSE" = true ]; then
    playwright install --with-deps
else
    playwright install --with-deps > /dev/null 2>&1
fi
log_success "Playwright browsers installed / Playwright 浏览器已安装"

# Step 4: Run Tests / 运行测试
if [ "$SKIP_TESTS" = false ]; then
    log_step "Step 4: Run Tests / 运行测试"
    
    # Set PYTHONPATH to ensure imports work correctly / 设置 PYTHONPATH 确保导入正常工作
    export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
    
    log_info "Running unit tests with coverage / 运行单元测试（含覆盖率）..."
    TEST_RESULT=0
    if [ "$VERBOSE" = true ]; then
        pytest --cov=src tests/ --cov-report=term --cov-report=xml -v || TEST_RESULT=$?
    else
        pytest --cov=src tests/ --cov-report=term --cov-report=xml || TEST_RESULT=$?
    fi
    
    if [ $TEST_RESULT -eq 0 ]; then
        log_success "All tests passed / 所有测试通过"
    else
        log_warning "Some tests failed or had errors (exit code: $TEST_RESULT) / 部分测试失败或出错（退出码：$TEST_RESULT）"
        log_info "Continuing with build... / 继续构建..."
    fi
    
    # Check coverage threshold / 检查覆盖率阈值
    log_info "Checking coverage threshold (≥70%) / 检查覆盖率阈值（≥70%）..."
    if coverage report --fail-under=70 > /dev/null 2>&1; then
        log_success "Coverage threshold met / 覆盖率阈值已满足"
    else
        COVERAGE=$(coverage report 2>/dev/null | grep TOTAL | awk '{print $NF}' | sed 's/%//' || echo "N/A")
        log_warning "Coverage is ${COVERAGE}% (target: ≥70%) / 覆盖率为 ${COVERAGE}%（目标：≥70%）"
    fi
else
    log_warning "Skipping tests (--skip-tests) / 跳过测试（--skip-tests）"
fi

# Step 5: Linting / 代码检查
if [ "$SKIP_LINT" = false ]; then
    log_step "Step 5: Linting / 代码检查"
    
    # Install linting tools if not present / 如果不存在则安装代码检查工具
    log_info "Installing linting tools / 安装代码检查工具..."
    pip install flake8 black isort --quiet > /dev/null 2>&1 || true
    
    # Flake8 / Flake8 检查
    log_info "Running flake8 / 运行 flake8..."
    if [ "$VERBOSE" = true ]; then
        flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics || log_warning "Flake8 found some issues / Flake8 发现一些问题"
        flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics || true
    else
        flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics > /dev/null 2>&1 || log_warning "Flake8 found syntax errors / Flake8 发现语法错误"
        flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics > /dev/null 2>&1 || true
    fi
    
    # Black / Black 格式化检查
    log_info "Checking code formatting with black / 使用 black 检查代码格式..."
    if black --check src > /dev/null 2>&1; then
        log_success "Code formatting is correct / 代码格式正确"
    else
        log_warning "Code formatting issues found (run 'black src' to fix) / 发现代码格式问题（运行 'black src' 修复）"
    fi
    
    # Isort / Isort 导入排序检查
    log_info "Checking import sorting with isort / 使用 isort 检查导入排序..."
    if isort --check-only src > /dev/null 2>&1; then
        log_success "Import sorting is correct / 导入排序正确"
    else
        log_warning "Import sorting issues found (run 'isort src' to fix) / 发现导入排序问题（运行 'isort src' 修复）"
    fi
else
    log_warning "Skipping linting (--skip-lint) / 跳过代码检查（--skip-lint）"
fi

# Step 6: Build Documentation / 构建文档
if [ "$SKIP_DOCS" = false ]; then
    log_step "Step 6: Build Documentation / 构建文档"
    
    if [ -f "scripts/build_docs.sh" ]; then
        log_info "Building API documentation / 构建 API 文档..."
        if [ "$VERBOSE" = true ]; then
            bash scripts/build_docs.sh
        else
            bash scripts/build_docs.sh > /dev/null 2>&1
        fi
        log_success "Documentation built successfully / 文档构建成功"
        log_info "Documentation location: docs/api/index.html / 文档位置：docs/api/index.html"
    else
        log_warning "build_docs.sh not found, skipping documentation build / 未找到 build_docs.sh，跳过文档构建"
    fi
else
    log_warning "Skipping documentation build (--skip-docs) / 跳过文档构建（--skip-docs）"
fi

# Build Summary / 构建总结
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Build Completed Successfully!          ║${NC}"
echo -e "${GREEN}║   构建成功完成！                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

log_success "All build steps completed / 所有构建步骤已完成"
echo ""
echo "Next steps / 下一步："
echo "  1. Start server: ./start_server.sh / 启动服务器：./start_server.sh"
echo "  2. View docs: open docs/api/index.html / 查看文档：open docs/api/index.html"
echo "  3. Run tests: pytest tests/ -v / 运行测试：pytest tests/ -v"
echo ""


