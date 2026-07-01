# shared-models — Pydantic v2 共享数据模型

> platform-orchestrator 管道的数据契约层。定义各模块间传递的标准数据结构。

## 定位

`shared-models` 是 platform-orchestrator 整合架构的**唯一事实来源**。5 个独立模块（content-aggregator、smart-sentence-splitter、prompt-engine、Story2Video、Multi-Publish）通过本包定义的 Pydantic v2 模型进行数据交换。

**核心原则**：各模块内部保留自己的数据结构，管道间传递使用 shared-models 定义的统一格式。

## 安装

```bash
pip install -e /srv/projects/shared-models/
```

## 模型清单

### splitter — 分句引擎

| 模型 | 说明 |
|------|------|
| `SentenceBlock` | 单句结果（文本、索引、词数、置信度） |
| `SceneSegment` | 场景段（含句子列表、字幕块、时长估算） |
| `SubtitleBlock` | 字幕块（文本、起止时间、显示顺序） |
| `EraInfo` | 时代检测结果（现代/古代/混排 + 关键词） |
| `SplitResult` | 分句顶层结果（所有句子/场景/字幕汇总） |

### prompt — 提示词引擎

| 模型 | 说明 |
|------|------|
| `PlatformType` | 目标图片平台枚举（7 个：midjourney, stable_diffusion, dalle, tongyi, yizhang, jimeng, generic） |
| `StyleType` | 艺术风格枚举（14 种：写实、动漫、赛博朋克…） |
| `StyleCategory` | MJ 25 维风格维度 |
| `OptimizeRequest` | 提示词优化请求（文本、平台、风格、创意度…） |
| `OptimizeResult` | 优化结果（优化后提示词、候选版本、错误信息） |
| `ReverseRequest` / `ReverseResult` | 逆向工程（图片→提示词） |

### article — 文章内容

| 模型 | 说明 |
|------|------|
| `ArticleCreate` | 创建文章（来源类型、URL/文本内容） |
| `ArticleResponse` | 文章详情（含改写结果） |
| `ArticleListItem` | 文章列表项（摘要视图） |
| `RewriteRequest` | 改写请求（风格：轻松易懂/正式严谨/吸引眼球/深度分析） |
| `CollectURLRequest` | URL 采集请求 |
| `CollectResponse` | 采集结果（标题、正文、作者、字数） |

### auth — 认证与用户

| 模型 | 说明 |
|------|------|
| `UserRegisterRequest` | 注册请求（用户名、邮箱、密码） |
| `UserLoginRequest` | 登录请求 |
| `UserResponse` | 用户公开信息（含订阅类型：free/basic/pro/enterprise） |
| `TokenResponse` | JWT 令牌响应 |
| `UserProfile` | 扩展用户资料（配额、偏好设置） |

### pipeline — 任务编排

| 模型 | 说明 |
|------|------|
| `PipelineStatus` | 管道状态枚举（pending/processing/done/failed） |
| `PipelineJob` | 通用管道任务（输入/输出/状态/错误） |
| `VideoJobStatus` | 视频任务细粒度状态（6 个阶段：排队→TTS→生图→合成→完成/失败） |
| `VideoJob` | 视频生成任务（场景列表、进度、输出路径） |

### publish — 多平台发布

| 模型 | 说明 |
|------|------|
| `PublishPlatformType` | 发布平台枚举（12 个：公众号、知乎、微博、抖音…） |
| `PublishTaskStatus` | 任务状态枚举（pending/queued/running/success/failed/cancelled） |
| `PublishResult` | 单平台发布结果（成功/失败、文章 ID、URL、错误） |
| `PublishTask` | 多平台发布任务（标题、内容、目标平台、重试） |
| `PlatformAccount` | 平台账号配置（ID、凭据、状态） |

## 设计原则

1. **Pydantic v2 原生**：所有模型继承 `BaseModel`，利用类型校验和序列化
2. **`extra="allow"`**：所有模型开启额外字段容忍，确保从模块传回的额外字段不丢失
3. **`from_attributes=True`**：ORM 兼容的模型支持从 SQLAlchemy 对象直接构造
4. **`@field_validator`**：关键字段（era、style、length）有枚举约束校验
5. **零运行时依赖（除 pydantic）**：不引入任何模块依赖，纯数据结构

## 使用示例

```python
from shared_models import (
    SentenceBlock, SceneSegment, SplitResult,
    OptimizeRequest, PlatformType, StyleType,
    ArticleCreate, UserRegisterRequest,
    PipelineJob, PipelineStatus,
    PublishTask, PublishPlatformType,
)

# 创建分句结果
split_result = SplitResult(
    sentences=[SentenceBlock(text="你好世界", index=0)],
    scenes=[SceneSegment(
        text="你好世界",
        segment_id=0,
        estimated_duration=3.0,
        target_words=20,
    )],
    total_duration=3.0,
    total_words=4,
    total_scenes=1,
)

# 创建优化请求
optimize_req = OptimizeRequest(
    prompt="一只猫在窗台上晒太阳",
    platform=PlatformType.MIDJOURNEY,
    style=StyleType.REALISTIC,
    creative_level=7,
)
```

## 与现有模块的对应关系

| shared-models | 原模块数据类型 |
|---------------|--------------|
| `SentenceBlock` | `splitter.models.sentence.SentenceBlock` (dataclass) |
| `SplitResult` | `splitter.models.result.SplitResult` (dataclass) |
| `OptimizeRequest` | `prompt_engine.models.OptimizeRequest` (Pydantic) |
| `OptimizeResult` | `prompt_engine.models.OptimizeResult` (Pydantic) |
| `ArticleCreate` | `content-aggregator backend schemas` |

## 版本

**0.1.0** — Phase 0 初始版本，覆盖 6 个数据域，30+ 个 Pydantic v2 模型。
