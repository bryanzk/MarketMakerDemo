# API Reference / API 参考

This page lists every API and code reference artifact available for the AlphaLoop Market Maker project.
本页列出了 AlphaLoop 做市项目中所有可用的 API 及代码参考资料。

## 📚 Documentation Resources / 文档资源

### 1. Auto-Generated Reference (pdoc) / 自动生成参考（pdoc）
Browse the complete API reference, including modules, classes, and functions, at **[docs/api/index.html](api/index.html)**.
访问 **[docs/api/index.html](api/index.html)** 可浏览包含模块、类和函数的完整 API 参考文档。

- **Highlights**: Generated from inline docstrings, includes type hints, refreshed on every push to `main`.
  **要点**：由代码注释自动生成，涵盖类型提示，并在每次推送到 `main` 时刷新。
- **Best Practice**: Keep docstrings updated so this reference never drifts from the code.
  **最佳实践**：及时维护 Docstring，确保文档与代码保持一致。

### 2. Interactive FastAPI Docs / FastAPI 交互式文档
Start the server (`python run.py` 或 `uvicorn server:app --port 3000`) to access the built-in interactive explorers.
启动服务器（`python run.py` 或 `uvicorn server:app --port 3000`）即可使用内置的交互式文档界面。

- **[Swagger UI](/docs)** offers a “Try it out” experience for every REST endpoint.
  **[Swagger UI](/docs)** 为所有 REST 接口提供 “Try it out” 交互体验。
- **[ReDoc](/redoc)** provides a reader-friendly rendering of the same OpenAPI spec.
  **[ReDoc](/redoc)** 以更易阅读的方式展示同一份 OpenAPI 规范。

## 🔧 Developer Workflow / 开发者工作流

### Generate Docs Locally / 本地生成文档
```bash
# Install dependencies if needed
pip install -r requirements.txt

# Build API docs with pdoc
./scripts/build_docs.sh

# Open the generated index
open docs/api/index.html
```
Run the script whenever you change public APIs, docstrings, or configuration to avoid stale references.
只要修改了公共 API、Docstring 或配置，就应运行该脚本以防参考资料过期。

### Documentation Standards / 文档标准
- **Docstrings**: Use Google- or NumPy-style docstrings for every public symbol.
  **Docstring**：所有公开符号使用 Google 或 NumPy 风格注释。
- **Type Hints**: Provide precise type annotations so pdoc can render accurate signatures.
  **类型提示**：提供准确的类型注解，方便 pdoc 输出正确签名。
- **Module Summaries**: Begin each module with a short statement of purpose.
  **模块摘要**：每个模块开头添加简短的用途说明。

### Auto-Documentation in CI/CD / CI/CD 自动生成
GitHub Actions regenerates and publishes the API documentation on every push to `main`, guaranteeing consistency between code and docs.
GitHub Actions 会在每次推送到 `main` 时重新生成并发布 API 文档，确保代码与文档同步。

## 📖 Related Documentation / 相关文档
- [README](../README.md) – Project overview and quick start.
  [README](../README.md) – 项目概览与快速上手。
- [CI/CD Guide](cicd.md) – Continuous integration and deployment pipeline.
  [CI/CD 指南](cicd.md) – 持续集成与部署流程。
- [Dashboard Guide](dashboard.md) – Monitoring metrics and charts.
  [Dashboard 指南](dashboard.md) – 监控指标与图表。
- [AlphaLoop Framework](alphaloop/framework_design.md) – Architecture and design reference.
  [AlphaLoop 框架](alphaloop/framework_design.md) – 架构与设计参考。
