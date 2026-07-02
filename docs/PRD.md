# PROJECT-000：shared-models 统一数据契约层 — PRD

> **立项日期**: 2026-06-03
> **最后更新**: 2026-07-02
> **当前版本**: v0.2.0（审查补充 + 缺失模型定义）
> **产品定位**: 一站式视频生成平台统一数据契约层（Tier 0 基础设施）
> **目标用户**: 所有 9 个子项目的开发者（数据交换必须经此层）
> **技术架构**: Python 3.12+ / Pydantic v2 BaseModel / 纯数据契约（无业务逻辑）

---

## 一、产品概述

### 1.1 为什么需要数据契约层

在 9 个子项目各自独立演进的多项目体系中，模块间数据交换面临以下核心问题：

1. **格式不一致**：各模块自行定义接口模型，导致 A→B 的数据 B 需要做一次适配转换
2. **耦合隐忧**：直接引用其他模块的内部模型会在依赖树上产生不必要的耦合
3. **兼容性灾难**：一个模块的模型变更可能悄无声息地破坏下游多个模块
4. **重复定义**：JWT Payload、分句结果等跨模块概念在各项目中重复定义，细节不一致

**shared-models 作为 Tier 0 基础设施解决以上问题：**
- **唯一真理源**：所有跨模块数据交换必须使用本层定义的 Pydantic v2 模型
- **零适配成本**：数据产生方直接输出 shared-models 实例，消费方直接 `model_validate()`
- **接口冻结**：通过严格的向后兼容策略和 Tier 0 变更审批流程，保证管道稳定
- **CI 可验证**：144 个自动化测试确保每次变更不破坏现有契约

### 1.2 核心价值

| 维度 | 说明 |
|------|------|
| **统一契约** | 所有模块间数据交换格式统一，消除适配层 |
| **Editable Install** | 所有项目通过 `pip install -e .` 安装，修改即生效（无需重新构建） |
| **Pydantic v2 验证** | 运行时类型校验，不符合契约的数据在边界即被拒绝 |
| **独立测试套件** | 144 个测试覆盖全部 8 个数据域，不依赖任何外部模块 |
| **接口冻结** | Week 0 冻结核心管道契约，后续变更走 Tier 0 审批流程 |
| **无业务逻辑** | 纯数据模型，不含任何业务逻辑、IO、外部依赖 |
| **JSON Schema 导出** | CI 自动生成 Schema 文件，跨语言消费者可直接使用 |

### 1.3 产品边界

| 范围 | 说明 |
|------|------|
| **包含** | |
| | 认证模型（JWT Payload、JWTAuthManager、登录/注册请求与响应） |
| | 分句模型（SentenceBlock、SceneSegment、SplitResult） |
| | 内容模型（ContentFetchRequest、RewriteConfig、RewriteResult） |
| | 提示词模型（OptimizeRequest、ReverseResult） |
| | TrendScope 热榜模型（TrendingTopicModel、HotArticleModel） |
| | 管道核心契约（ContentPacket、VideoAsset、PipelineStage） |
| | LLM 配置模型（ProviderConfig、ModelRoute、GlobalConfig） |
| | Viral 分析模型（ViralFactor、ViralAnalysisResult、ScoringConfig） |
| **不包含** | |
| | 单个模块内部使用的私有模型（保留在各自项目中） |
| | 业务逻辑、验证规则之外的函数、类 |
| | 数据库 ORM 模型（SQLAlchemy / Tortoise-ORM 等） |
| | API 路由和端点定义 |
| | 配置、环境变量、密钥 |

---

## 二、数据契约分类

### 2.1 Auth 认证模型 (`shared_models/auth.py`)

提供 SSO 场景下的统一认证数据结构，所有子项目共用同一 JWT 载荷格式。

| 模型 | 用途 | 状态 |
|------|------|------|
| `UserLoginRequest` | 登录请求（密码/短信） | ✅ v0.1.0 |
| `UserRegisterRequest` | 注册请求 | ✅ v0.1.0 |
| `TokenResponse` | 令牌响应（access + refresh token） | ✅ v0.1.0 |
| `RefreshRequest` | 令牌刷新请求 | ✅ v0.1.0 |
| `UserResponse` | 公开用户信息（API 响应安全） | ✅ v0.1.0 |
| `UserProfile` | 扩展用户信息（含配额、偏好） | ✅ v0.1.0 |
| `JWTPayload` | 标准 JWT 载荷（user_id, username, role, exp） | ✅ v0.1.0 |
| `JWTAuthManager` | JWT 创建/验证 + bcrypt 密码工具类 | ✅ v0.1.1 |

**关键约定**：
- JWT 算法：HS256，所有项目共享 `PO_SECRET_KEY` 环境变量
- Token 结构：`{user_id, username, role, exp}`
- JWTAuthManager 实例化需要 `secret_key` 参数
- `model_config = {"extra": "allow"}` 保证前向兼容

### 2.2 Sentence 分句模型 (`shared_models/sentence.py`)

封装智能语义分句引擎的输出结果，供下游 prompt-engine 和 Story2Video 使用。

| 模型 | 用途 | 状态 |
|------|------|------|
| `SentenceBlock` | 单句完整元数据（文本、语言、置信度、边界标记） | ✅ v0.1.0 |
| `SubtitleBlock` | 字幕块（时间轴、时长） | ✅ v0.1.0 |
| `SceneSegment` | 场景段（含多句、字幕、角色、情绪） | ✅ v0.1.0 |
| `SplitResult` | 顶层分句结果（总时长、场景数、配置快照） | ✅ v0.1.0 |

### 2.3 Content 内容模型 (`shared_models/content.py`)

content-aggregator 模块的输入输出契约。

| 模型 | 用途 | 状态 |
|------|------|------|
| `ContentFetchRequest` | 内容采集请求（URL + 来源 + 风格） | ✅ v0.1.0 |
| `RewriteConfig` | 改写配置（风格、长度、目标平台） | ✅ v0.1.0 |
| `RewriteResult` | 改写结果（标题、正文、词数、模型） | ✅ v0.1.0 |

### 2.4 Prompt 提示词模型 (`shared_models/prompt.py`)

prompt-engine 模块的输入输出契约，支持 7 平台提示词优化。

| 模型 | 用途 | 状态 |
|------|------|------|
| `OptimizeRequest` | 提示词优化请求（原始提示词、目标平台） | ✅ v0.1.0 |
| `OptimizeResult` | 优化结果（优化后提示词、平台适配） | ✅ v0.1.0 |
| `ReverseRequest` | 图片反推提示词请求 | ✅ v0.1.0 |
| `ReverseResult` | 反推结果（推测提示词、置信度） | ✅ v0.1.0 |

### 2.5 TrendScope 热榜模型 (`shared_models/trendscope/models.py`)

热榜聚合引擎的数据模型，作为管道的输入起点。

| 模型 | 用途 | 状态 |
|------|------|------|
| `PlatformModel` | 平台信息（编码、名称、分类） | ✅ v0.1.0 |
| `TrendingTopicModel` | 热榜话题（排名、热度值、分类） | ✅ v0.1.0 |
| `HotArticleModel` | 热门文章（含扩展互动指标：收藏、转采、粉丝数、爆款分） | ✅ v0.1.0 |
| `TrendingPipelineItem` | 送入管道的热榜项（TrendScope → aggregator） | ✅ v0.1.0 |
| `TrendingListResponse` | 热榜列表响应（分页） | ✅ v0.1.0 |

### 2.6 Pipeline 管道核心契约 (`shared_models/pipeline.py`)

**Week 0 接口冻结**的核心成果。定义了从"热榜发现 → 视频发布"整条管道的统一数据载体。

| 模型 | 用途 | 状态 |
|------|------|------|
| `PipelineStage` | 管道生命周期阶段枚举（8 阶段） | ✅ 冻结 |
| `ContentPacket` | 数据管道通用容器，携带从采集到发布的完整上下文 | ✅ 冻结 |
| `ScenePrompt` | 单场景提示词与字幕配置 | ✅ 冻结 |
| `VideoAsset` | 视频合成任务输入规格（prompt-engine → Story2Video） | ✅ 冻结 |

**ContentPacket 字段分组**（按管道阶段）：
| 字段组 | 写入方 | 主要内容 |
|--------|--------|----------|
| 来源信息 | trendscope | platform, url, title, content, hot_score |
| 改写结果 | content-aggregator | rewritten_title, rewritten_content, rewrite_style |
| 分句结果 | smart-sentence-splitter | split_result, total_scenes, total_duration |
| 提示词结果 | prompt-engine | optimized_prompts |
| 视频结果 | Story2Video | video_url, video_duration |
| 发布结果 | Multi-Publish | publish_results |

### 2.7 LLM 配置模型 (`shared_models/llm.py`)

统一 LLM 配置数据契约，桥接 4 套现有 LLM 配置实现。

| 模型 | 用途 | 状态 |
|------|------|------|
| `LLMProviderConfig` | 单个 LLM 提供商配置（类型、Base URL、API Key、模型列表） | ✅ v0.1.1 |
| `ModelRoute` | 语义类别 → (provider, model) 路由规则 | ✅ v0.1.1 |
| `UserLLMOverride` | 用户级 API Key 覆盖 | ✅ v0.1.1 |
| `LLMInvocationRequest` | 标准化 LLM 调用请求（直接/路由两种解析方式） | ✅ v0.1.1 |
| `LLMInvocationResponse` | 标准化 LLM 调用响应（内容、用量、性能） | ✅ v0.1.1 |
| `LLMGlobalConfig` | 聚合配置（providers + routing + overrides + 查找助手方法） | ✅ v0.1.1 |

**支持的 Provider 类型**：openai_compat、xfyun、minimax、gemini、doubao、qwen、anthropic

### 2.8 Viral 分析模型 (`shared_models/viral.py`)

爆款内容分析引擎数据契约，涵盖因子提取、评分、趋势聚合。

| 模型 | 用途 | 状态 |
|------|------|------|
| `TitleStructure` | 标题结构枚举（12 种模式） | ✅ v0.1.1 |
| `EmotionalTrigger` | 情感触发枚举（10 种类型） | ✅ v0.1.1 |
| `ContentStructure` | 正文结构枚举（9 种模式） | ✅ v0.1.1 |
| `ViralFactor` | 单因子维度（名称、分数、置信度、证据） | ✅ v0.1.1 |
| `TitleAnalysis` | 标题结构分析（模式检测、特征标记、情感） | ✅ v0.1.1 |
| `EngagementMetrics` | 互动指标（原始 + 归一化 + 聚合爆款分） | ✅ v0.1.1 |
| `ArticleViralProfile` | 单篇文章爆款因子分解 | ✅ v0.1.1 |
| `ViralAnalysisResult` | 主题级分析结果（趋势方向、平台对比、写作建议） | ✅ v0.1.1 |
| `TrendingInsights` | 平台级趋势洞察（分类/标题/情感分布） | ✅ v0.1.1 |
| `ViralScoringConfig` | 可配置评分权重（线性 + 对数 + 权威度混合） | ✅ v0.1.1 |

---

## 三、非功能需求

### 3.1 向后兼容

| 规则 | 说明 | 强制程度 |
|------|------|----------|
| 新增字段必须有默认值 | 不允许无默认值的非 Optional 新增字段 | **硬性** |
| 不删除已有字段 | 已发布的字段永不下线；如需废弃，标注 deprecated + 文档说明 | **硬性** |
| 不修改已有字段类型 | 字段类型变更视为 breaking change，必须走 Tier 0 审批 | **硬性** |
| 枚举值只增不减 | `PipelineStage` 等枚举只允许追加新值，不允许修改或删除已有值 | **硬性** |
| `extra = "allow"` | 关键模型开启此配置，允许消费者携带模型未定义的额外字段 | 建议 |

### 3.2 Pydantic v2 Only

| 规则 | 说明 |
|------|------|
| 禁止使用 v1 风格 | 所有模型使用 `BaseModel`（v2），不使用 v1 的 `Validator`、`root_validator` 等 |
| 类型标注语法 | 必须使用 Python 3.10+ 联合类型语法（`str \| None`，`list[dict]`） |
| Field 配置 | 使用 `model_config` 字典（而非 v1 的 `Config` 内部类） |
| 验证方式 | 使用 `@field_validator` / `@model_validator`（而非 v1 的 `@validator`） |

### 3.3 测试覆盖

| 模块 | 文件 | 测试数 | 覆盖率 |
|------|------|--------|--------|
| Auth | `tests/test_auth.py` | 40 | 所有模型 + JWTAuthManager 完整路径 |
| Content | `tests/test_content.py` | 7 | 请求/配置/结果模型 |
| Sentence | `tests/test_sentence.py` | 10 | 句子/字幕/场景/分句结果 |
| Prompt | `tests/test_prompt.py` | 10 | 优化/反向模型 |
| Pipeline | `tests/test_pipeline.py` | 16 | 枚举/管道契约/场景/视频资产 |
| LLM | `tests/test_llm.py` | 20 | 提供商/路由/覆盖/请求/响应/聚合配置 |
| Viral | `tests/test_viral.py` | 23 | 枚举/因子/分析/评分配置 |
| TrendScope | `tests/test_trendscope.py` | 10 | 平台/话题/文章/管道项/列表响应 |
| **合计** | | **144** | 独立运行，零外部依赖 |

测试原则：
- 纯单元测试，不依赖其他模块
- 不调用真实 HTTP/DB — 纯模型构造 + 字段验证
- 覆盖正常路径 + 异常路径（空值、越界、非法枚举）
- 所有模型测试只需 `pip install -e .` 即可运行

### 3.4 依赖约束

| 约束 | 说明 |
|------|------|
| 最小依赖 | `pydantic>=2.0` + `email-validator>=2.0` |
| 严禁引入 | FastAPI、SQLAlchemy、Django、aiohttp 等框架依赖 |
| 测试依赖 | `pytest`（仅 dev 依赖，不纳入运行时） |
| Python 版本 | Python 3.11+（统一使用 3.12+ 语法特性） |

### 3.5 安装方式

```bash
# 所有消费者项目通过 editable install 安装
pip install -e /path/to/shared-models

# 修改 shared-models 源码后，消费者项目立即可见新模型
# 无需重新 pip install
```

---

## 四、变更流程

### 4.1 Tier 0 审批流程

shared-models 是**无主基础设施（Tier 0）**，不为任何一个团队的某一个项目拥有。任何变更必须走以下审批流程：

```
发起变更 Issue（描述变更内容和影响范围）
    │
    ├─ 影响判断：
    │    ├─ 新增非核心模型（非管道契约）→ 简单审批（2 个团队 ACK）
    │    ├─ 修改/废弃已有字段 → 全量审批（3 个团队 ACK + 架构师批准）
    │    └─ 修改管道核心契约（pipeline.py）→ 全量审批 + 接口冻结重新计时
    │
    ├─ 团队 A ACK（content-aggregator 团队）
    ├─ 团队 B ACK（smart-sentence-splitter / prompt-engine 团队）
    ├─ 团队 C ACK（Story2Video / Multi-Publish / TrendScope 团队）
    │
    ├─ 架构师批准
    │
    └─ 合并 PR → 通知所有消费者更新
```

### 4.2 变更必须附带测试

所有 shared-models 变更**必须**附带或更新测试：
- 新增模型 → 新增对应测试类，验证构造、字段默认值、非法输入
- 修改字段 → 更新测试字段断言，兼容新旧值
- 测试运行命令：`pytest tests/ -v`（零外部依赖）

### 4.3 三团队划分

| 团队 | 负责项目 | 审批范围 |
|------|----------|----------|
| **团队 A** | content-aggregator、content-aggregator-shared | 内容/改写相关模型 |
| **团队 B** | smart-sentence-splitter、prompt-engine | 分句/提示词相关模型 |
| **团队 C** | Story2Video、Multi-Publish、TrendScope | 视频/发布/热榜相关模型 |

所有团队共同审批 pipeline.py（管道核心契约）。

### 4.4 紧急变更

线上管道因数据契约问题阻塞时，可发起紧急变更：
1. 相关团队在变更 Issue 下紧急 ACK（放宽至 2 团队 + 架构师 4h 内）
2. 变更合入后 24h 内补全常规审批
3. 紧急变更必须同时写入 postmortem

### 4.5 接口冻结里程碑

| 冻结事件 | 日期 | 冻结范围 | 解冻条件 |
|----------|------|----------|----------|
| Week 0 接口冻结 | 2026-06-25 | ContentPacket、VideoAsset、PipelineStage | 下次里程碑规划 |

---

## 五、当前状态

### 5.1 项目信息

| 项目 | 值 |
|------|-----|
| 当前版本 | v0.2.0 |
| Python 版本 | >=3.11 |
| 核心依赖 | Pydantic >=2.0, email-validator >=2.0 |
| 测试依赖 | pytest |
| 测试数量 | 144（全部通过，零外部依赖） |
| 安装方式 | `pip install -e .`（editable） |
| 许可证 | MIT |
| 开发状态 | Alpha |
| 发布方式 | git submodule / editable install |

### 5.2 数据契约覆盖矩阵

| 数据域 | 文件 | 模型数 | 测试数 | 状态 |
|--------|------|--------|--------|------|
| 认证 | `auth.py` | 8 | 40 | ✅ 稳定 |
| 分句 | `sentence.py` | 4 | 10 | ✅ 稳定 |
| 内容 | `content.py` | 3 | 7 | ✅ 稳定 |
| 提示词 | `prompt.py` | 4 | 10 | ✅ 稳定 |
| 热榜 | `trendscope/models.py` | 5 | 10 | ✅ 稳定 |
| 管道核心 | `pipeline.py` | 4 | 16 | ✅ 冻结 |
| LLM 配置 | `llm.py` | 6 | 20 | ✅ v0.1.1 |
| Viral 分析 | `viral.py` | 10 | 23 | ✅ v0.1.1 |

### 5.3 目录结构

```
shared-models/
├── pyproject.toml            # 项目元数据 + 构建配置
├── setup.py                  # 兼容性安装入口
├── CLAUDE.md                 # AI 开发指南
├── AGENTS.md                 # Agent 开发指南
├── README.md
├── docs/
│   └── PRD.md                # 本文档
├── tests/                    # 独立测试套件
│   ├── conftest.py           # 共享 fixtures
│   ├── test_auth.py          # Auth 模型（40）
│   ├── test_content.py       # 内容模型（7）
│   ├── test_llm.py           # LLM 配置模型（20）
│   ├── test_pipeline.py      # 管道核心契约（16）
│   ├── test_prompt.py        # 提示词模型（10）
│   ├── test_sentence.py      # 分句模型（10）
│   ├── test_trendscope.py    # 热榜模型（10）
│   └── test_viral.py         # Viral 分析模型（23）
└── shared_models/            # 数据模型源码
    ├── __init__.py            # 统一导出入口
    ├── auth.py                # 认证模型
    ├── sentence.py            # 分句模型
    ├── content.py             # 内容模型
    ├── prompt.py              # 提示词模型
    ├── pipeline.py            # 管道核心契约（冻结）
    ├── llm.py                 # LLM 配置模型
    ├── viral.py               # Viral 分析模型
    └── trendscope/
        ├── __init__.py
        └── models.py          # 热榜模型
```

### 5.4 Roadmap

| 阶段 | 内容 | 状态 |
|------|------|------|
| **v0.1.0 Alpha** | 基础模型定义、Week 0 接口冻结 | ✅ 已完成 |
| **v0.1.1** | LLM 配置模型、Viral 分析模型、144 独立测试套件 | ✅ 已完成 |
| **v0.2.0** | 审查补充：缺失模型定义、边界规范、错误码枚举、冻结策略修订 | ✅ 已完成 |
| **v1.0.0** | 接口稳定版本、变更审批流程正式运行、消费者全部迁移完成 | 📅 待规划 |

---

## 六、风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| 变更审批流程导致交付延迟 | 中 | 紧急变更通道 + 明确小型变更的简化流程 |
| 各团队对模型理解不一致 | 高 | Week 0 冻结的 pipeline.py 作为基线，所有变更必须附带测试 |
| 非 breaking 变更无声破坏下游 | 中 | 144 测试全覆盖，breaking change 自动化阻断 |
| 模型膨胀（存放本应私有的模型） | 低 | CLAUDE.md 和审查流程明确"仅跨模块模型"原则 |
| 前端 JS/TS 同步滞后 | 中 | JSON Schema 导出 + 自动生成 TypeScript 类型（v0.2.0） |

---

## 七、验收标准

### v0.1.0 Alpha（Week 0 接口冻结）

- [x] **pipeline.py 核心契约**：ContentPacket、VideoAsset、PipelineStage 冻结
- [x] **6 个数据域覆盖**：auth / sentence / content / prompt / trendscope / pipeline
- [x] **Pydantic v2 纯验证**：全部模型使用 Pydantic BaseModel v2，无 v1 兼容代码
- [x] **统一导出入口**：`shared_models/__init__.py` 提供 `__all__` 白名单
- [x] **editable install 验证**：所有 9 个子项目通过 `pip install -e .` 引用
- [x] **向后兼容基线**：所有字段设置默认值或为 Optional

### v0.1.1（独立测试套件）

- [x] **LLM 配置模型**：6 个模型（ProviderConfig、ModelRoute、UserOverride、Invocation Request/Response、GlobalConfig）
- [x] **Viral 分析模型**：10 个模型（枚举 + 因子 + 分析 + 评分配置）
- [x] **JWTAuthManager**：完整的 JWT 工具类（创建/验证/密码哈希）
- [x] **独立测试套件**：144 个测试，覆盖 8 个数据域，零外部依赖
- [x] **所有测试通过**：`pytest tests/ -v` → 144 passed

### v1.0.0 目标

- [ ] JSON Schema CI 自动导出（`schemas/` 目录）
- [ ] TypeScript 类型声明自动生成
- [ ] 所有消费者项目完成从私有模型到 shared-models 的迁移
- [ ] 变更审批流程正式运行满 2 个迭代
---

## 五、Story2Video / Multi-Publish / Orchestrator 契约补充

> **背景**：审查报告指出 shared-models 声称覆盖"9 个子项目"，但实际仅有 6 个数据域模型。Story2Video、Multi-Publish、platform-orchestrator 三个项目的跨模块模型缺失，导致它们绕过 shared-models 直接定义私有模型，全局契约的强制力被打破。

### 5.1 新增模型清单

| 模型 | 文件 | 用途 | 消费方 |
|------|------|------|--------|
| `PublishResult` | `publish.py` | 单平台发布结果（URL、状态、错误信息） | Multi-Publish → orchestrator |
| `PublishSubStage` | `publish.py` | 发布子阶段枚举（uploading/processing/published/failed） | Multi-Publish → orchestrator |
| `MultiPublishRequest` | `publish.py` | 多平台发布请求（目标平台列表 + 视频资产引用） | orchestrator → Multi-Publish |
| `MultiPublishResponse` | `publish.py` | 多平台发布聚合响应（各平台 PublishResult 列表） | Multi-Publish → orchestrator |
| `AudioInput` | `video.py` | 音频输入规格（TTS 音色、语速、背景音乐） | prompt-engine → Story2Video |
| `VideoJob` | `video.py` | 视频生成任务追踪（任务 ID、状态、进度百分比） | Story2Video → orchestrator |
| `VideoJobStatus` | `video.py` | 视频任务状态枚举（pending/generating/done/failed/cancelled） | Story2Video → orchestrator |
| `OrchestratorContext` | `orchestrator.py` | 编排上下文（当前阶段、耗时统计、重试计数） | orchestrator 内部跨阶段 |

### 5.2 模型定义摘要

#### PublishResult

```python
class PublishSubStage(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"

class PublishResult(BaseModel):
    platform: str = Field(..., description="目标平台代号")
    status: PublishSubStage = Field(default=PublishSubStage.UPLOADING)
    url: Optional[str] = Field(default=None, description="发布后的内容链接")
    error: Optional[str] = Field(default=None, description="失败原因")
    published_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

#### MultiPublishRequest / Response

```python
class MultiPublishRequest(BaseModel):
    video_asset_id: str = Field(..., description="引用的 VideoAsset ID")
    target_platforms: List[str] = Field(..., min_length=1, description="目标平台列表")
    override_title: Optional[str] = None
    override_description: Optional[str] = None
    scheduled_at: Optional[datetime] = Field(default=None, description="定时发布时间")

class MultiPublishResponse(BaseModel):
    request_id: str
    results: List[PublishResult] = Field(default_factory=list)
    total_count: int = 0
    success_count: int = 0
    failed_count: int = 0
```

#### AudioInput

```python
class AudioInput(BaseModel):
    voice_type: str = Field(default="标准女声", description="TTS 音色")
    voice_rate: float = Field(default=1.0, ge=0.5, le=2.0, description="语速倍率")
    voice_pitch: float = Field(default=0.0, ge=-1.0, le=1.0, description="音高偏移")
    background_music: Optional[str] = Field(default=None, description="BGM 路径/URL")
    bgm_volume: float = Field(default=0.3, ge=0.0, le=1.0, description="BGM 音量占比")
    silence_padding: float = Field(default=0.5, ge=0.0, le=2.0, description="句间静音填充(秒)")
```

#### VideoJob / VideoJobStatus

```python
class VideoJobStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VideoJob(BaseModel):
    job_id: str = Field(..., description="任务唯一 ID")
    video_asset_id: str = Field(..., description="引用的 VideoAsset ID")
    status: VideoJobStatus = Field(default=VideoJobStatus.PENDING)
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="进度百分比")
    output_url: Optional[str] = Field(default=None, description="生成的视频 URL")
    error: Optional[str] = Field(default=None)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

#### OrchestratorContext

```python
class OrchestratorContext(BaseModel):
    packet_id: str = Field(..., description="关联的 ContentPacket ID")
    current_stage: PipelineStage
    stage_started_at: Optional[datetime] = None
    total_elapsed_seconds: float = Field(default=0.0, ge=0.0)
    retry_count: int = Field(default=0, ge=0, description="当前阶段重试次数")
    max_retries: int = Field(default=3, ge=0)
    error_history: List[Dict[str, Any]] = Field(default_factory=list, description="历次错误记录")
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### 5.3 与现有 ContentPacket 的集成

新增模型通过以下方式与 `ContentPacket` 关联：

- `ContentPacket.publish_results` 字段应从 `Dict[str, Any]` 升级为 `Optional[List[PublishResult]]`（向后兼容，旧格式 Dict 仍可通过 `extra = "allow"` 传入）
- `VideoJob` 通过 `video_asset_id` 关联 `VideoAsset`，不嵌入 `ContentPacket`
- `OrchestratorContext` 作为 orchestrator 内部的阶段追踪模型，通过 `packet_id` 关联 `ContentPacket`

---

## 六、JWTAuthManager 边界规范

> **背景**：JWTAuthManager 当前包含 `hash_password` / `verify_password` 等业务逻辑方法，与"纯数据契约（无业务逻辑）"的产品边界产生矛盾。审查报告要求明确划分边界。

### 6.1 边界定义

| 层级 | 职责 | 示例 |
|------|------|------|
| **Shared-Models（数据层）** | 数据结构定义、序列化/反序列化、字段验证 | `JWTPayload` 模型、`TokenResponse` 模型 |
| **Shared-Models（工具类）** | JWT 编解码、密码哈希 — **仅限密码学原语操作** | `JWTAuthManager.create_access_token()`、`JWTAuthManager.hash_password()` |
| **各子项目（业务层）** | 认证策略、角色校验、权限管理、会话管理 | 用户锁定、登录限流、角色 ACL |

### 6.2 明确禁止

`JWTAuthManager` 中**不允许**出现以下业务逻辑：

- ❌ 数据库查询（用户是否存在、密码是否匹配）
- ❌ 角色/权限业务判断（`is_admin()`、`check_permission()`）
- ❌ 会话管理（Redis 存储、Token 黑名单）
- ❌ 速率限制（登录尝试计数、IP 限制）
- ❌ FastAPI 依赖注入（`get_current_user` 中的 DB 查询）

### 6.3 当前 `get_current_user` 重新分类

当前 `JWTAuthManager.get_current_user()` 仅执行 `decode_token` + 检查 `sub` claim，不含 DB 查询，**属于合法的数据层操作**。但方法名容易误导，建议在文档中标注：

> `get_current_user()` 是一个便捷解码方法（非业务方法），不访问数据库。业务层的 `get_current_user` 应由各子项目自行实现。

### 6.4 JWTPayload 字段扩展

新增 `iss` 和 `aud` 字段，支持跨模块 Token 签发来源识别：

```python
class JWTPayload(BaseModel):
    user_id: int
    username: str
    role: str = "user"
    exp: int | None = None
    iss: str = Field(default="platform-orchestrator", description="Token 签发者")
    aud: str = Field(default="shared", description="Token 受众（服务标识）")
```

**iss 取值规范**：

| 值 | 签发来源 |
|----|----------|
| `platform-orchestrator` | 主认证服务（SSO 入口） |
| `trendscope` | TrendScope API（内部服务间调用） |
| `content-aggregator` | Content Aggregator（异步任务 Token） |

**aud 取值规范**：

| 值 | 含义 |
|----|------|
| `shared` | 通用受众（默认，所有服务接受） |
| `trendscope` | 仅 TrendScope 服务接受 |
| `orchestrator` | 仅 Orchestrator 服务接受 |

### 6.5 向后兼容

- `iss` 和 `aud` 均设默认值，**不破坏现有 Token 解码**
- 各子项目可选择性验证 `iss`/`aud`（非强制）
- v1.0.0 后可升级为强制验证

---

## 七、错误码枚举模型

> **背景**：各子项目当前分散定义错误码，格式不一致（字符串 / 数字 / HTTP 状态码混用），导致跨模块错误处理混乱。需要统一的错误码枚举。

### 7.1 错误码分类

| 域 | 前缀 | 范围 | 示例 |
|----|------|------|------|
| 通用 | `GEN` | 1000-1999 | `GEN_VALIDATION_ERROR`, `GEN_INTERNAL_ERROR` |
| 认证 | `AUTH` | 2000-2999 | `AUTH_TOKEN_EXPIRED`, `AUTH_INVALID_CREDENTIALS` |
| 内容 | `CONTENT` | 3000-3999 | `CONTENT_FETCH_FAILED`, `CONTENT_REWRITE_TIMEOUT` |
| 分句 | `SENTENCE` | 4000-4999 | `SENTENCE_SPLIT_FAILED`, `SENTENCE_INVALID_LANGUAGE` |
| 提示词 | `PROMPT` | 5000-5999 | `PROMPT_OPTIMIZE_FAILED`, `PROMPT_UNSUPPORTED_PLATFORM` |
| 视频 | `VIDEO` | 6000-6999 | `VIDEO_GENERATION_FAILED`, `VIDEO_QUOTA_EXCEEDED` |
| 发布 | `PUBLISH` | 7000-7999 | `PUBLISH_PLATFORM_ERROR`, `PUBLISH_RATE_LIMITED` |
| 管道 | `PIPELINE` | 8000-8999 | `PIPELINE_STAGE_FAILED`, `PIPELINE_TIMEOUT` |
| 热榜 | `TREND` | 9000-9999 | `TREND_FETCH_FAILED`, `TREND_RATE_LIMITED` |

### 7.2 模型定义

```python
class ErrorCode(str, Enum):
    # -- 通用 (1xxx) --
    GEN_VALIDATION_ERROR = "GEN_1001"
    GEN_INTERNAL_ERROR = "GEN_1002"
    GEN_NOT_FOUND = "GEN_1003"
    GEN_RATE_LIMITED = "GEN_1004"
    GEN_TIMEOUT = "GEN_1005"
    GEN_DEPENDENCY_UNAVAILABLE = "GEN_1006"

    # -- 认证 (2xxx) --
    AUTH_TOKEN_EXPIRED = "AUTH_2001"
    AUTH_TOKEN_INVALID = "AUTH_2002"
    AUTH_INVALID_CREDENTIALS = "AUTH_2003"
    AUTH_USER_NOT_FOUND = "AUTH_2004"
    AUTH_USER_DISABLED = "AUTH_2005"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_2006"

    # -- 内容 (3xxx) --
    CONTENT_FETCH_FAILED = "CONTENT_3001"
    CONTENT_FETCH_TIMEOUT = "CONTENT_3002"
    CONTENT_REWRITE_FAILED = "CONTENT_3003"
    CONTENT_REWRITE_TIMEOUT = "CONTENT_3004"
    CONTENT_INVALID_URL = "CONTENT_3005"

    # -- 分句 (4xxx) --
    SENTENCE_SPLIT_FAILED = "SENTENCE_4001"
    SENTENCE_INVALID_INPUT = "SENTENCE_4002"
    SENTENCE_LANGUAGE_UNSUPPORTED = "SENTENCE_4003"

    # -- 提示词 (5xxx) --
    PROMPT_OPTIMIZE_FAILED = "PROMPT_5001"
    PROMPT_UNSUPPORTED_PLATFORM = "PROMPT_5002"
    PROMPT_REVERSE_FAILED = "PROMPT_5003"

    # -- 视频 (6xxx) --
    VIDEO_GENERATION_FAILED = "VIDEO_6001"
    VIDEO_QUOTA_EXCEEDED = "VIDEO_6002"
    VIDEO_INVALID_SCENES = "VIDEO_6003"
    VIDEO_TIMEOUT = "VIDEO_6004"

    # -- 发布 (7xxx) --
    PUBLISH_PLATFORM_ERROR = "PUBLISH_7001"
    PUBLISH_RATE_LIMITED = "PUBLISH_7002"
    PUBLISH_AUTH_FAILED = "PUBLISH_7003"
    PUBLISH_CONTENT_REJECTED = "PUBLISH_7004"

    # -- 管道 (8xxx) --
    PIPELINE_STAGE_FAILED = "PIPELINE_8001"
    PIPELINE_TIMEOUT = "PIPELINE_8002"
    PIPELINE_DEPENDENCY_FAILED = "PIPELINE_8003"

    # -- 热榜 (9xxx) --
    TREND_FETCH_FAILED = "TREND_9001"
    TREND_RATE_LIMITED = "TREND_9002"
    TREND_DATABASE_ERROR = "TREND_9003"


class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str = Field(..., description="人类可读的错误描述")
    detail: Optional[str] = Field(default=None, description="调试信息（生产环境不暴露）")
    field: Optional[str] = Field(default=None, description="出错字段（验证类错误）")
    timestamp: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    request_id: Optional[str] = Field(default=None, description="请求追踪 ID")
```

### 7.3 使用规范

- 各子项目内部错误**必须**映射到 `ErrorCode` 枚举后暴露给跨模块调用方
- `ErrorDetail.detail` 字段仅用于调试，生产环境应为 `None`
- 新增错误码需走 Tier 0 审批流程（属于枚举追加，不破坏兼容性）
- 前端/客户端通过 `code` 字段做 i18n 错误映射

---

## 八、ProviderConfig Rate Limit / Quota 字段

> **背景**：LLM Provider 缺少速率限制和配额管理字段，导致各子项目自行实现限流逻辑，策略不一致。

### 8.1 扩展字段定义

在 `LLMProviderConfig` 模型中新增以下字段组：

```python
class LLMProviderConfig(BaseModel):
    # ... 现有字段 ...

    # -- 速率限制 & 配额 --
    rate_limit_rpm: int = Field(
        default=60, ge=0,
        description="每分钟最大请求数 (requests per minute)，0 = 不限制"
    )
    rate_limit_tpm: int = Field(
        default=0, ge=0,
        description="每分钟最大 Token 数 (tokens per minute)，0 = 不限制"
    )
    daily_quota_tokens: int = Field(
        default=0, ge=0,
        description="每日 Token 配额，0 = 不限制"
    )
    daily_quota_requests: int = Field(
        default=0, ge=0,
        description="每日请求数配额，0 = 不限制"
    )
    monthly_quota_tokens: int = Field(
        default=0, ge=0,
        description="每月 Token 配额，0 = 不限制"
    )
    concurrency_limit: int = Field(
        default=10, ge=0,
        description="最大并发请求数，0 = 不限制"
    )
    retry_after_seconds: int = Field(
        default=60, ge=0,
        description="触发限流后的建议等待时间(秒)"
    )
```

### 8.2 向后兼容

- 所有新字段均有默认值（不设限），**不影响现有配置**
- 未配置限流的 Provider 行为与 v0.1.x 完全一致
- 限流策略的执行逻辑属于各子项目业务层，shared-models 仅定义数据契约

---

## 九、RewriteResult 质量评分字段

> **背景**：改写结果缺少质量评估指标，下游消费者（Story2Video、Multi-Publish）无法判断改写内容是否达标，也无法基于质量分数做路由决策。

### 9.1 新增字段

在 `RewriteResult` 模型中新增质量评分相关字段：

```python
class RewriteResult(BaseModel):
    # ... 现有字段 ...

    # -- 质量评分 (v0.2.0 新增) --
    quality_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="综合质量评分 (0.0-1.0)，由多维度加权计算"
    )
    quality_breakdown: Optional[Dict[str, float]] = Field(
        default=None,
        description="质量评分明细 {fluency, coherence, originality, platform_fit}"
    )
    readability_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="可读性评分"
    )
    originality_score: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="原创性评分（与原文的差异化程度）"
    )
```

### 9.2 quality_score 计算规范

| 维度 | 权重 | 说明 |
|------|------|------|
| `fluency` | 30% | 语言流畅度（语法、连贯性） |
| `coherence` | 25% | 逻辑连贯性（段落结构、主题一致） |
| `originality` | 25% | 原创性（与原文查重率、新意程度） |
| `platform_fit` | 20% | 平台适配度（字数、风格与目标平台匹配） |

> **注意**：计算逻辑属于 content-aggregator 业务层，shared-models 仅定义评分字段和取值范围。

### 9.3 下游使用建议

- **Story2Video**：`quality_score < 0.4` 时可跳过该内容（不生成视频）
- **Multi-Publish**：`quality_score` 可作为平台选择的参考因子
- **orchestrator**：可基于 `quality_score` 做管道质量门禁

---

## 十、TrendingTopicModel 关联字段

> **背景**：TrendingTopicModel 缺少与 Pipeline 的关联字段，热榜话题进入管道后无法回溯来源，也无法追踪管道处理状态。

### 10.1 新增字段

在 `TrendingTopicModel` 模型中新增以下字段：

```python
class TrendingTopicModel(BaseModel):
    # ... 现有字段 ...

    # -- Pipeline 关联 (v0.2.0 新增) --
    pipeline_packet_id: Optional[str] = Field(
        default=None,
        description="关联的 ContentPacket ID（进入管道后填入）"
    )
    pipeline_status: Optional[str] = Field(
        default=None,
        description="当前管道处理阶段（进入管道后填入）"
    )
    content_aggregator_id: Optional[str] = Field(
        default=None,
        description="关联的内容采集任务 ID"
    )
    selected_for_pipeline: bool = Field(
        default=False,
        description="是否已被选入管道"
    )
    selected_at: Optional[str] = Field(
        default=None,
        description="被选入管道的时间"
    )
```

### 10.2 HotArticleModel 关联字段

同理，`HotArticleModel` 也需补充关联字段：

```python
class HotArticleModel(BaseModel):
    # ... 现有字段 ...

    # -- Pipeline 关联 (v0.2.0 新增) --
    pipeline_packet_id: Optional[str] = Field(
        default=None,
        description="关联的 ContentPacket ID"
    )
    selected_for_pipeline: bool = Field(default=False)
```

### 10.3 数据流向

```
TrendingTopicModel (selected_for_pipeline=True)
    |
    +-- trendscope.api 写入 pipeline_packet_id
    |
    v
ContentPacket (source 字段段)
    |
    +-- orchestrator 回写 pipeline_status
    |
    v
TrendingTopicModel (pipeline_status=PUBLISHED)  <-- 完成闭环
```

---

## 十一、接口冻结策略（修订）

> **背景**：原"Week 0 接口冻结"策略定义过于简单，缺少对紧急 bug fix 的处理流程，也未明确冻结范围的层级划分。

### 11.1 冻结层级

| 层级 | 范围 | 冻结强度 | 变更条件 |
|------|------|----------|----------|
| **L1 核心管道** | `ContentPacket`, `VideoAsset`, `PipelineStage` | **硬冻结** — 禁止任何非向后兼容变更 | 全量审批 + 接口冻结重新计时 2 周 |
| **L2 公共契约** | `JWTPayload`, `ErrorDetail`, `ErrorCode` | **软冻结** — 仅允许追加字段（必须有默认值） | 简单审批（2 团队 ACK） |
| **L3 辅助模型** | 新增模型（`PublishResult`, `VideoJob` 等） | **无冻结** — 自由新增 | 标准 PR 流程 |

### 11.2 紧急 Bug Fix 通道

管道因数据契约 bug 阻塞线上时，可启用紧急通道：

```
紧急 Bug Fix 流程：
    |
    +-- 1. 发起紧急 Issue（标注 [URGENT] + 影响范围 + 修复方案）
    |
    +-- 2. 最小审批（1 团队 ACK + 架构师 ACK，4 小时内完成）
    |
    +-- 3. 合入修复 + 关联 Postmortem Issue
    |
    +-- 4. 24 小时内补全常规审批（3 团队 ACK）
    |
    +-- 5. 7 天内补全回归测试
```

**紧急修复限制**：

- 仅限向后兼容变更（新增可选字段、修复验证逻辑）
- 不允许在紧急通道中做 breaking change
- 紧急修复必须同时附带回归测试的 PR
- 同一模块 30 天内最多触发 2 次紧急通道

### 11.3 冻结重置条件

| 事件 | 影响 |
|------|------|
| L1 核心管道 breaking change | 冻结计时器重置为 2 周 |
| 新增 L1 核心字段 | 不影响冻结计时器（向后兼容） |
| 3 个月内无变更 | 冻结状态自动延续（无到期机制） |
| 紧急 Bug Fix | 不影响冻结计时器（不构成架构变更） |

### 11.4 与原策略的差异

| 原策略 | 修订后 |
|--------|--------|
| 单一"冻结"概念 | 分 L1/L2/L3 三级冻结 |
| 无紧急通道 | 新增紧急 Bug Fix 流程（带约束） |
| 冻结范围不清晰 | 明确冻结到具体模型和字段 |
| 冻结无到期机制 | 引入冻结重置条件 |
