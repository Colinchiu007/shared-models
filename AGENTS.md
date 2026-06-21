# shared-models — 开发规范

> Pydantic v2 共享数据模型的贡献指南。

## 核心原则

1. **唯一事实来源**：shared-models 是管道数据契约的唯一定义。各模块的数据结构变化必须同步到这里。
2. **向后兼容**：新增字段必须设置合理默认值，不破坏现有消费者。
3. **`extra="allow"`**：所有模型必须开启此选项，容忍上游模块传回未定义的字段。
4. **只定义管道间传递的结构**：模块内部使用的私有数据结构不放入这里。

## 添加新模型

### 1. 确定所属域

按管道位置确定文件：
- 管道输入 → `article.py`
- 分句 → `splitter.py`
- 提示词 → `prompt.py`
- 认证 → `auth.py`
- 任务编排 → `pipeline.py`
- 发布 → `publish.py`

如果是全新域，创建新文件（如 `tts.py`）并在 `__init__.py` 中导出。

### 2. 模型规范

```python
from pydantic import BaseModel, Field

class NewModel(BaseModel):
    """清晰的文档字符串，说明用途。"""

    required_field: str = Field(..., description="必填字段")
    optional_field: str = Field(default="default", description="可选字段")
    constrained_field: int = Field(default=5, ge=1, le=10, description="有约束字段")

    # ⚠️ 必须设置
    model_config = {"extra": "allow"}
```

### 3. 枚举使用

```python
from enum import Enum

class NewEnum(str, Enum):
    VALUE_ONE = "value_one"
    VALUE_TWO = "value_two"
```

枚举值使用小写蛇形命名，便于 JSON 序列化。

### 4. 校验器

```python
from pydantic import field_validator

@field_validator("field_name")
@classmethod
def validate_field(cls, v: str) -> str:
    valid = frozenset({"a", "b", "c"})
    if v not in valid:
        raise ValueError(f"must be one of {valid}")
    return v
```

### 5. 导出

在 `__init__.py` 中添加导入：

```python
from shared_models.new_file import NewModel

# 同时在 __all__ 中添加
__all__ = [..., "NewModel"]
```

## 命名规则

| 类型 | 规则 | 示例 |
|------|------|------|
| 模型类 | PascalCase | `SentenceBlock` |
| 请求模型 | 后缀 `Request` | `OptimizeRequest` |
| 响应模型 | 后缀 `Response` 或 `Result` | `ArticleResponse`, `OptimizeResult` |
| 枚举类 | 后缀 `Type` 或 `Status` | `PlatformType`, `PipelineStatus` |
| 文件名 | snake_case | `splitter.py`, `pipeline.py` |
| 字段名 | snake_case | `estimated_duration` |

## 与模块同步

当上游模块的数据结构发生变化时：

1. 在模块仓库中修改
2. 同步更新 shared-models 中对应的 Pydantic 模型
3. 在模块中添加 `to_shared_model()` 方法（可选，转换层）
4. 更新本文档的模型清单

## 版本

遵循 [Semantic Versioning](https://semver.org/)：
- **MAJOR**：删除或重命名字段
- **MINOR**：新增模型或字段
- **PATCH**：文档更新、校验逻辑修复

## 测试

```bash
cd /srv/projects/shared-models
python -m pytest tests/ -v
```
