# shared-models — 开发流程规范

> Pydantic v2 统一数据契约层的开发流程与编码约定。AI 工具启动时自动读取。

---

## 核心原则

1. **唯一事实来源**：所有跨模块数据交换必须使用本层定义的 Pydantic v2 模型
2. **向后兼容**：新增字段必须有默认值，不能删除已有字段
3. **无业务逻辑**：只放 Pydantic 模型，不放业务逻辑、IO、外部依赖
4. **TDD**：模型变更必须附测试
5. **三组 ACK**：shared-models 变更必须三组 Agent 全部 ACK + 协调者批准

## AI 角色分工

| 角色 | 阶段 | 产出物 |
|------|------|--------|
| **PM（需求方）** | 需求分析 | 新模型/字段的需求说明、消费者列表 |
| **架构师** | 技术设计 | 文件位置、命名规则、向后兼容方案 |
| **开发工程师** | 编码实现 | Pydantic 模型 + 单元测试（TDD） |
| **QA** | 质量验证 | 测试覆盖：序列化/反序列化/校验器/兼容性 |
| **CTO** | 代码评审 | 审查兼容性、命名规范、不引入业务逻辑 |

## 7 阶段开发流程

### 阶段 1：需求识别（PM）
谁需要什么数据？哪个模块的消费者受影响？确认：
- 新增模型还是扩展现有模型
- 消费者列表（至少 1 个下游模块确认需要）
- 如果不走 shared-models 的直接后果

### 阶段 2：规格定义（PM）
产出：更新 shared-models PRD 或编写变更说明
明确：
- 模型字段清单（名称、类型、必填/可选、默认值、约束）
- 示例数据和边界值
- 如果 MAJOR 变更：迁移方案

### 阶段 3：技术设计（架构师）
产出：文件位置、命名规则、校验逻辑
原则：
- **选最简单的方案**：能不新增文件就不新增
- **优先扩展现有模型**，避免创建新模型
- **extra="allow"** 所有模型必须开启
- **向后兼容**优先于完美命名

### 阶段 4：开发计划（PM）
把变更拆成 <=2h 的任务：
- 新增模型 -> 写测试 -> 实现模型 -> 更新 __init__.py 导出
- 扩展现有模型 -> 更新测试 -> 更新字段

### 阶段 5：编码实现（开发 + TDD）
- 先写测试，再写模型
- pip install -e . 后所有消费者自动生效
- 测试验证：序列化 -> 反序列化 -> 字段约束 -> extra="allow" 行为 -> 向后兼容

### 阶段 6：代码评审（CTO）
必检项：
- 是否包含业务逻辑（禁止）
- 新增字段是否有默认值（向后兼容）
- 是否删除或重命名了已有字段（禁止）
- 字段命名是否符合 snake_case
- 类型标注是否使用 Python 3.12+ 语法
- 是否有 model_config = {"extra": "allow"}
- 校验器逻辑是否合理

### 阶段 7：发布（运维）
- 更新 CHANGELOG.md（遵循 SemVer）
- MAJOR 变更：通知所有消费者
- git tag（vMAJOR.MINOR.PATCH）

## 质量门禁

**规格阶段**：消费者确认 / 向后兼容方案明确
**设计阶段**：最简单方案 / 字段命名规范
**开发阶段**：测试全通过 / editable install 验证 / 向后兼容验证
**Review 阶段**：无业务逻辑 / 三组 Agent ACK
**发布阶段**：CHANGELOG 更新 / git 已提交并 tag

## TDD 流程

```
RED   -> 在 tests/ 下写失败测试（验证新模型可序列化/反序列化）
GREEN -> 实现 Pydantic 模型让测试通过
REFACTOR -> 重构校验器/字段顺序等，保持测试通过
```

## 提交规范

```
feat(auth): 添加 RefreshRequest 模型
fix(content): 修复 RewriteResult model_dump 字段顺序
docs: 更新 PRD 数据契约分类
refactor: 统一 field_validator 风格
```

## 文档清单

| 文件 | 路径 | 说明 |
|------|------|------|
| AGENTS.md | ./AGENTS.md | 本文件，开发流程规范 |
| CLAUDE.md | ./CLAUDE.md | 项目上下文和开发命令 |
| .clinerules | ./.clinerules | 硬约束规则 |
| PRD.md | ./docs/PRD.md | 产品需求文档 |
| ARCHITECTURE.md | ./docs/ARCHITECTURE.md | 架构设计文档 |
| DESIGN.md | ./docs/DESIGN.md | 设计原则和命名规范 |

## 版本

遵循 Semantic Versioning：
- MAJOR：删除或重命名字段
- MINOR：新增模型或字段
- PATCH：文档更新、校验逻辑修复

## 常用命令

```bash
pip install -e .
pytest tests/ -v
```
