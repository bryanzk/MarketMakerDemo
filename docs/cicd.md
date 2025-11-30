# CI/CD 流程文档 | CI/CD Process Documentation

![CI Status](https://github.com/bryanzk/MarketMakerDemo/actions/workflows/ci.yml/badge.svg)

## 概述 | Overview

AlphaLoop项目采用自动化的持续集成/持续部署（CI/CD）流程，确保代码质量和系统稳定性。

AlphaLoop uses an automated Continuous Integration/Continuous Deployment (CI/CD) process to ensure code quality and system stability.

## CI/CD架构 | CI/CD Architecture

### 使用的工具 | Tools Used

- **GitHub Actions**: 自动化工作流引擎
- **pytest**: 单元测试框架
- **pytest-cov**: 测试覆盖率工具
- **flake8**: Python代码检查工具
- **black**: 代码格式化工具
- **isort**: Import语句排序工具

### 工作流触发条件 | Workflow Triggers

CI/CD流程在以下情况下自动触发：
The CI/CD process is automatically triggered when:

1. **Push到主分支** | Push to main branch
   - 分支：`main`, `develop`
   
2. **Pull Request** | Pull Requests
   - 目标分支：`main`, `develop`

## CI流程详解 | CI Process Details

### 1. 测试任务 (Test Job)

**职责** | Responsibilities:
- 运行所有单元测试
- 生成覆盖率报告
- 验证覆盖率阈值

**步骤** | Steps:

```yaml
1. 检出代码 (Checkout code)
2. 设置Python 3.11环境 (Setup Python 3.11)
3. 安装依赖 (Install dependencies from requirements.txt)
4. 运行测试与覆盖率 (Run pytest with coverage)
   - 命令: pytest --cov=src tests/
   - 覆盖率阈值: 70%
5. 上传覆盖率报告到Codecov (Upload coverage to Codecov)
```

**覆盖率要求** | Coverage Requirements:
- **最低阈值**: 70%
- **核心模块目标**: 100% (agents, strategies, market)

### 2. 代码质量检查任务 (Lint Job)

**职责** | Responsibilities:
- 检查代码语法错误
- 验证代码格式
- 确保import语句排序

**步骤** | Steps:

```yaml
1. 检出代码 (Checkout code)
2. 设置Python 3.11环境 (Setup Python 3.11)
3. 安装代码检查工具 (Install linting tools)
4. Flake8语法检查 (Lint with flake8)
   - 检查致命错误 (E9, F63, F7, F82)
   - 复杂度限制: 10
   - 行长度限制: 127
5. Black格式检查 (Check formatting with black)
6. Isort导入排序检查 (Check import sorting with isort)
```

## 本地开发工作流 | Local Development Workflow

### 提交前检查 | Pre-commit Checklist

在提交代码前，开发者应该执行以下命令：
Before committing code, developers should run:

```bash
# 1. 运行所有测试 | Run all tests
pytest

# 2. 检查覆盖率 | Check coverage
pytest --cov=src tests/

# 3. 代码格式化 | Format code
black src
isort src

# 4. 语法检查 | Lint code
flake8 src
```

### 推荐的Git工作流 | Recommended Git Workflow

```bash
# 1. 创建功能分支 | Create feature branch
git checkout -b feature/your-feature-name

# 2. 开发并提交 | Develop and commit
git add .
git commit -m "描述你的改动"

# 3. 本地测试 | Local testing
pytest --cov=src tests/

# 4. 推送到远程 | Push to remote
git push origin feature/your-feature-name

# 5. 创建Pull Request | Create Pull Request
# CI自动运行，等待检查通过 | CI runs automatically
```

## 质量门禁 | Quality Gates

Pull Request必须满足以下条件才能合并：
Pull Requests must meet the following criteria to be merged:

- ✅ 所有测试通过 | All tests pass
- ✅ 覆盖率 ≥ 70% | Coverage ≥ 70%
- ✅ 无语法错误 | No syntax errors
- ✅ 代码格式符合规范 | Code formatting compliant
- ✅ Import语句已排序 | Imports properly sorted

## CD流程 (未来规划) | CD Process (Future Planning)

当前项目专注于CI流程。未来的CD流程将包括：
Currently focused on CI. Future CD process will include:

1. **自动部署到测试环境** | Auto-deploy to staging
   - 通过main分支测试后自动部署
   
2. **性能测试** | Performance testing
   - 模拟交易压力测试
   
3. **生产部署** | Production deployment
   - 手动审批后部署到生产环境

## 监控与告警 | Monitoring and Alerts

CI/CD系统会在以下情况发送通知：
The CI/CD system sends notifications when:

- ❌ 测试失败 | Tests fail
- ❌ 覆盖率低于阈值 | Coverage below threshold
- ❌ 代码质量检查失败 | Linting fails
- ✅ 成功合并到main | Successfully merged to main

## 故障排查 | Troubleshooting

### 常见问题 | Common Issues

**1. 测试失败**
```bash
# 本地复现 | Reproduce locally
pytest tests/test_specific.py -v

# 查看详细错误 | View detailed error
pytest tests/test_specific.py -vv --tb=long
```

**2. 覆盖率不足**
```bash
# 生成HTML覆盖率报告 | Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
# 在浏览器中打开 htmlcov/index.html
```

**3. 格式问题**
```bash
# 自动修复格式 | Auto-fix formatting
black src
isort src
```

## 参考资料 | References

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [pytest文档](https://docs.pytest.org/)
- [开发协议文档](./development_protocol.md)
