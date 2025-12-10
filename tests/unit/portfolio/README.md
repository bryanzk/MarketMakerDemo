# Portfolio Module Unit Tests / 组合管理模块单元测试

This directory contains unit tests for the Portfolio management module.  
此目录包含组合管理模块的单元测试。

## Owner / 负责人

**Agent PORTFOLIO**

## Test Files / 测试文件

- `test_api.py` - Portfolio API tests / Portfolio API 测试
- `test_health.py` - Portfolio health tests / Portfolio 健康度测试
- `test_metrics.py` - Metrics tests / 指标测试
- `test_risk_indicators.py` - Risk indicators tests / 风险指标测试
- `test_risk_manager.py` - Risk manager tests / 风险管理器测试
- `test_sync.py` - Portfolio sync tests / Portfolio 同步测试

## Running Tests / 运行测试

```bash
# Run all Portfolio module tests / 运行所有 Portfolio 模块测试
pytest tests/unit/portfolio/ -v

# Run specific test file / 运行特定测试文件
pytest tests/unit/portfolio/test_api.py -v
```
