# Smoke Tests / 冒烟测试

This directory contains smoke tests for quick system health verification.  
此目录包含用于快速系统健康验证的冒烟测试。

## Owner / 负责人

This directory is owned by **Agent QA**.  
此目录由 **Agent QA** 负责。

## Running Tests / 运行测试

```bash
# Run smoke tests / 运行冒烟测试
pytest tests/smoke/ -v

# Or use the smoke test script / 或使用冒烟测试脚本
./scripts/smoke_test.sh
```

## What Smoke Tests Check / 冒烟测试检查内容

1. Server starts successfully / 服务器启动成功
2. API endpoints respond / API 端点响应
3. Core functionality works / 核心功能正常
4. No critical errors / 无严重错误


