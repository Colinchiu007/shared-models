# shared-models 设计规范

> Pydantic 模型的设计原则、命名规范和最佳实践。

## 设计原则

### 1. 向后兼容优先

```python
# 新增字段必须有默认值
class UserResponse(BaseModel):
    username: str = Field(...)
    email: str = Field(...)
    display_name: str | None = Field(default=None)  # 不影响现有消费者

# 不能删除已有字段
# 不能修改已有字段的类型（除非是同类扩展，如 str -> str | None）
```

### 2. extra="allow"

所有模型必须开启 extra="allow"，容忍上游传递未定义的字段：

```python
class MyModel(BaseModel):
    field_a: str = Field(...)
    model_config = {"extra": "allow"}
```

### 3. 纯数据，无逻辑

模型不含业务方法：

```python
# 纯数据结构
class SplitResult(BaseModel):
    blocks: list[SentenceBlock]
    stats: dict

# 不允许
class SplitResult(BaseModel):
    blocks: list[SentenceBlock]
    def get_average_length(self) -> int: ...  # 不允许
```

## 字段命名规范

| 场景 | 规则 | 示例 |
|------|------|------|
| 通用 | snake_case | article_id |
| 可空 | str \| None 非 Optional[str] | display_name: str \| None = None |
| 列表 | list[T] 非 List[T] | tags: list[str] = Field(default_factory=list) |
| 枚举值 | 小写 snake_case | class Status(str, Enum): pending = "pending" |

## 版本兼容示例

```python
# v0.1.0
class UserResponse(BaseModel):
    username: str
    email: str

# v0.2.0 - 新增 display_name，消费者无需改
class UserResponse(BaseModel):
    username: str
    email: str
    display_name: str | None = Field(default=None)

# v1.0.0 - 删除 display_name
class UserResponse(BaseModel):
    username: str
    email: str
```
