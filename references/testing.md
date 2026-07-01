# shared-models — 测试规范

## TDD 流程

```
RED   -> 在 tests/ 下写失败测试（验证新模型可序列化/反序列化）
GREEN -> 实现 Pydantic 模型让测试通过
REFACTOR -> 重构校验器/字段顺序等，保持测试通过
```

