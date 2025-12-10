---
name: Add DevOps Agent
overview: 创建 DevOps Agent 并将其集成到现有的 9-Agent 体系中，负责 CI/CD 管道、环境管理、基础设施监控和部署自动化等完整 DevOps 职责。
todos:
  - id: create_devops_doc
    content: Create docs/agents/AGENT_DEVOPS.md with full responsibilities, file ownership, and workflows
    status: completed
  - id: update_cursorrules_agent_system
    content: Update .cursorrules to add DevOps Agent to agent system table and update count from 9 to 10
    status: completed
  - id: update_cursorrules_step14
    content: Update .cursorrules Step 14 ownership from Human to Agent DevOps in pipeline steps and decision matrix
    status: completed
  - id: update_cursorrules_file_ownership
    content: Add DevOps Agent file ownership rules to .cursorrules file ownership matrix section
    status: completed
  - id: update_readme_agent_count
    content: Update docs/agents/README.md to change agent count from 9 to 10 and add DevOps Agent to all tables
    status: completed
  - id: create_env_example
    content: Create or update .env.example with all required and optional environment variables
    status: completed
---

# Add DevOps Agent to Multi-Agent System / 将 DevOps Agent 添加到多 Agent 系统

## Overview / 概述

将当前的 9-Agent 系统扩展为 **10-Agent 系统**，新增 **Agent DevOps** 负责完整的 DevOps 职责，包括 CI/CD 管道维护、环境管理、基础设施监控、部署自动化等。

## Current State / 当前状态

- **Agent 数量**: 9 个 Agent（3 个管理层 + 4 个开发层 + 2 个质量层）
- **Step 14 负责人**: Human（人工审查 CI/CD 结果）
- **CI/CD 管理**: `.github/workflows/ci.yml` 无专门维护者
- **环境管理**: 分散在多个脚本中（`start_server.sh`, `scripts/verify_server_env.sh`）

## Proposed Changes / 提议的变更

### 1. Create Agent DevOps Documentation / 创建 Agent DevOps 文档

**File**: `docs/agents/AGENT_DEVOPS.md`

**Content / 内容**:
- Agent 身份和职责范围
- 核心职责（CI/CD、环境管理、部署、监控、日志、安全）
- 文件归属矩阵（EXCLUSIVE/COORDINATED/SHARED-APPEND）
- Pipeline Step 14 责任（`ci_cd_passed`）
- 与其他 Agent 的协作关系
- 常用命令和工作流程

**Key Responsibilities / 核心职责**:
1. **CI/CD Pipeline Management / CI/CD 管道管理**
   - Maintain `.github/workflows/ci.yml`
   - 维护 `.github/workflows/ci.yml`
   - Optimize test, lint, and docs jobs
   - 优化测试、代码检查和文档任务
   - Monitor CI/CD pass rate and performance
   - 监控 CI/CD 通过率和性能

2. **Environment Management / 环境管理**
   - Manage `.env.example` and environment templates
   - 管理 `.env.example` 和环境模板
   - Coordinate `requirements.txt` and `pyproject.toml` changes
   - 协调 `requirements.txt` 和 `pyproject.toml` 变更
   - Ensure environment consistency across agents
   - 确保跨 Agent 的环境一致性

3. **Infrastructure Scripts / 基础设施脚本**
   - Maintain `start_server.sh` and related startup scripts
   - 维护 `start_server.sh` 和相关启动脚本
   - Manage `scripts/verify_server_env.sh` and environment verification
   - 管理 `scripts/verify_server_env.sh` 和环境验证
   - Create and maintain deployment scripts
   - 创建和维护部署脚本

4. **Logging and Monitoring / 日志和监控**
   - Manage log rotation and retention policies
   - 管理日志轮转和保留策略
   - Monitor server performance and resource usage
   - 监控服务器性能和资源使用
   - Set up infrastructure alerts (future)
   - 设置基础设施告警（未来）

5. **Security Configuration / 安全配置**
   - Manage secret management best practices
   - 管理密钥管理最佳实践
   - Ensure secure environment variable handling
   - 确保安全的环境变量处理
   - Review security-related infrastructure changes
   - 审查安全相关的基础设施变更

6. **Deployment Automation / 部署自动化**
   - Design deployment pipelines (future)
   - 设计部署管道（未来）
   - Manage staging and production environments
   - 管理预发布和生产环境
   - Coordinate with Agent QA for deployment testing
   - 与 Agent QA 协调部署测试

### 2. Update .cursorrules / 更新 .cursorrules

**Location**: Section "🤖 Agent 体系 (9 Agents)" → "🤖 Agent 体系 (10 Agents)"

**Changes / 变更**:
1. **Add DevOps Agent to Agent System Table / 将 DevOps Agent 添加到 Agent 系统表**
   - Add new row in "Infrastructure Layer / 基础设施层" or create new "Operations Layer / 运维层"
   - 在"基础设施层"添加新行或创建新的"运维层"

2. **Update Pipeline Step 14 / 更新流程步骤 14**
   - Change from `Human` to `Agent DevOps`
   - 从 `Human` 改为 `Agent DevOps`
   - Update decision responsibility matrix
   - 更新决策责任矩阵

3. **Add File Ownership Rules / 添加文件所有权规则**
   - `.github/workflows/` → Agent DevOps (EXCLUSIVE)
   - `.env.example` → Agent DevOps (EXCLUSIVE)
   - `scripts/` (infrastructure-related) → Agent DevOps (COORDINATED)
   - `logs/` (log management) → Agent DevOps (COORDINATED)
   - `requirements.txt`, `pyproject.toml` → COORDINATED (via `agent_requests.json`)

4. **Update Agent Responsibility Matrix / 更新 Agent 职责矩阵**
   - Add Step 14: `ci_cd_passed` → Agent DevOps
   - Update automatic role identification section
   - 更新自动角色识别部分

### 3. Update docs/agents/README.md / 更新 docs/agents/README.md

**Changes / 变更**:
1. **Update Agent Count / 更新 Agent 数量**
   - Change "9-Agent system" to "10-Agent system"
   - 将"9 个 Agent 系统"改为"10 个 Agent 系统"

2. **Add DevOps Agent to Tables / 将 DevOps Agent 添加到表格**
   - Add to "Infrastructure Layer" or new "Operations Layer"
   - 添加到"基础设施层"或新的"运维层"
   - Add to pipeline steps table (Step 14)
   - 添加到流程步骤表（步骤 14）
   - Add to file ownership table
   - 添加到文件所有权表

3. **Update Quick Reference / 更新快速参考**
   - Add DevOps Agent row with pipeline steps and owned directories
   - 添加 DevOps Agent 行，包含流程步骤和拥有的目录

### 4. Create Initial DevOps Artifacts / 创建初始 DevOps 工件

**Files to Create / 要创建的文件**:
1. **`.env.example`** (if not exists)
   - Template for environment variables
   - 环境变量模板
   - Document all required and optional variables
   - 记录所有必需和可选变量

2. **`docs/devops/ci_cd_guide.md`** (optional)
   - CI/CD pipeline documentation
   - CI/CD 管道文档
   - Troubleshooting guide
   - 故障排除指南

## Implementation Steps / 实施步骤

1. **Create `docs/agents/AGENT_DEVOPS.md`**
   - Define agent identity, responsibilities, and workflows
   - 定义 Agent 身份、职责和工作流程
   - Document file ownership and collaboration rules
   - 记录文件所有权和协作规则

2. **Update `.cursorrules`**
   - Add DevOps Agent to agent system section
   - 将 DevOps Agent 添加到 Agent 系统部分
   - Update Step 14 ownership
   - 更新步骤 14 所有权
   - Add file ownership rules
   - 添加文件所有权规则

3. **Update `docs/agents/README.md`**
   - Update agent count and tables
   - 更新 Agent 数量和表格
   - Add DevOps Agent to quick reference
   - 将 DevOps Agent 添加到快速参考

4. **Create `.env.example`** (if needed)
   - Document all environment variables
   - 记录所有环境变量

5. **Update `status/roadmap.json`** (if applicable)
   - Add any DevOps-related features
   - 添加任何 DevOps 相关功能

## File Ownership Matrix / 文件所有权矩阵

### 🔴 EXCLUSIVE (DevOps Agent Only) / 独占（仅 DevOps Agent）

- `.github/workflows/` - CI/CD pipeline configuration
- `.env.example` - Environment variable template
- `docs/devops/` - DevOps documentation (if created)

### 🟡 COORDINATED (Requires Request) / 需协调（需要请求）

- `requirements.txt` - Python dependencies
- `pyproject.toml` - Project configuration
- `scripts/` - Infrastructure scripts (coordinate with other agents)
- `logs/` - Log management (coordinate with Agent QA for test logs)

### 🟢 SHARED-APPEND (Shared with Others) / 共享追加（与他人共享）

- `status/roadmap.json` - Can update `status.ci_cd_passed` field
- `status/agent_requests.json` - Can create CONFIG/INFRASTRUCTURE requests

## Collaboration with Other Agents / 与其他 Agent 的协作

- **Agent PM**: Coordinate infrastructure changes, update progress tracking
- **Agent ARCH**: Coordinate shared platform infrastructure changes
- **Agent QA**: Coordinate deployment testing and log management
- **Dev Agents**: Handle CONFIG requests for dependency changes
- **Agent REVIEW**: Review infrastructure code changes

## Verification / 验证

After implementation, verify:
实施后，验证：

1. ✅ `docs/agents/AGENT_DEVOPS.md` exists and follows same format as other agent docs
2. ✅ `.cursorrules` updated with DevOps Agent in all relevant sections
3. ✅ `docs/agents/README.md` shows 10-Agent system
4. ✅ Step 14 ownership changed to Agent DevOps
5. ✅ File ownership matrix includes DevOps Agent files
6. ✅ Agent can be initialized using standard prompt format

## Notes / 注意事项

- DevOps Agent should follow the same initialization pattern as other agents
- DevOps Agent 应遵循与其他 Agent 相同的初始化模式
- Step 14 responsibility transfer from Human to DevOps Agent requires clear documentation
- 步骤 14 责任从 Human 转移到 DevOps Agent 需要清晰的文档
- File ownership rules should prevent conflicts with existing agents
- 文件所有权规则应防止与现有 Agent 的冲突
- DevOps Agent should coordinate closely with Agent QA for testing infrastructure
- DevOps Agent 应与 Agent QA 密切协调测试基础设施