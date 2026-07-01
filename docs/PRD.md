# PROJECT-000：shared-models 统一数据契约层 — PRD

> **立项日期**: 2026-06-03
> **最后更新**: 2026-06-27
> **当前版本**: v0.2.0（JSON Schema + TypeScript 声明）
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
| **v0.2.0** | JSON Schema CI 自动导出、TypeScript 类型声明生成 | ✅ 已完成 |
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

- [x] JSON Schema CI 自动导出（`.schemas/` 目录）
- [x] TypeScript 类型声明自动生成
- [ ] 所有消费者项目完成从私有模型到 shared-models 的迁移
- [ ] 变更审批流程正式运行满 2 个迭代

