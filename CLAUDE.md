# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目定位

`shared-models` 是整个"一站式视频生成平台"的统一数据契约层。所有模块间的数据交换必须使用这里定义的 Pydantic v2 模型，确保数据格式一致。

## 目录结构

```
shared-models/
├── setup.py
├── shared_models/
│   ├── __init__.py
│   ├── auth.py              # JWT payload, 登录/注册请求模型
│   ├── sentence.py           # SentenceBlock, SceneSegment, SplitResult
│   ├── content.py            # ContentFetchRequest, RewriteResult
│   ├── prompt.py             # OptimizeRequest, ReverseResult
│   └── trendscope/
│       ├── __init__.py
│       └── models.py         # TrendingTopicModel, HotArticleModel, PipelineItem
```

## 约定

- **只放 Pydantic 模型**，不放业务逻辑
- **向后兼容**: 新增字段必须有默认值，不能删除已有字段
- **字段命名**: 使用 snake_case
- **类型标注**: 必须使用 Python 3.12+ 语法 (`str | None`, `list[dict]`)
- **被多个模块引用的模型**放在这里，**仅单个模块使用的模型**留在各自模块内

## 添加新模块的数据模型

1. 在 `shared_models/` 下创建子包目录，添加 `__init__.py` 和 `models.py`
2. 在 `setup.py` 中如果有新依赖则添加
3. 其他模块通过 `pip install -e .` 的 editable mode 自动生效
4. 通知相关模块开发者新模型可用

## 测试

目前无独立测试（模型验证集成在其他模块的测试中）。如需添加:
```bash
cd D:\Data\projects\shared-models
pip install pytest
pytest -v
```
