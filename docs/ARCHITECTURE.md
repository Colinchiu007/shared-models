# shared-models 架构设计

> 一站式视频生成平台统一数据契约层架构说明。

## 系统定位

shared-models 位于所有模块的最底层（Tier 0），通过 pip install -e . 供给所有消费者：

```
shared-models (Pydantic v2 数据契约层)
  |
  +-> content-aggregator      (内容采集+改写)
  +-> smart-sentence-splitter (分句引擎)
  +-> prompt-engine           (提示词优化)
  +-> platform-orchestrator   (整合层)
  +-> Story2Video             (视频生成)
  +-> Multi-Publish           (多平台发布)
```

## 模块组织

按管道域分文件：

| 文件 | 域 | 核心模型 |
|------|-----|---------|
| auth.py | 认证 | UserLoginRequest, TokenResponse, JWTPayload, JWTAuthManager |
| sentence.py | 分句 | SentenceBlock, SceneSegment, SplitResult |
| content.py | 内容 | ContentFetchRequest, RewriteConfig, RewriteResult |
| prompt.py | 提示词 | OptimizeRequest, ReverseResult |
| trendscope/models.py | 热榜 | TrendingTopicModel, HotArticleModel |
| pipeline.py | 管道编排 | ContentPacket, VideoAsset, PipelineStage |
| llm.py | LLM 配置 | ProviderConfig, ModelRoute |
| viral.py | 爆款分析 | ViralFactor, ViralAnalysisResult |

## 向后兼容策略

| 等级 | 变更类型 | 版本号 |
|------|---------|--------|
| MAJOR | 删除/重命名/修改类型 | MAJOR bump |
| MINOR | 新增模型/可选字段 | MINOR bump |
| PATCH | 文档/校验器修复 | PATCH bump |

MAJOR 变更前必须在旧字段旁标注 @deprecated，保留至少 1 个 MINOR 版本。

## 无业务逻辑约束

允许：
- Pydantic field_validator（纯数据校验）
- JWTAuthManager 工具类（JWT 编解码 + bcrypt）
- JSON Schema 生成

禁止：
- 数据库访问（SQL / ORM）
- HTTP 调用
- 文件 IO
- 环境变量读取
- 业务规则判断
