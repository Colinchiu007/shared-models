# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-29

### Added
- JSON Schema 自动导出脚本 (`scripts/export_schemas.py`) — 47 模型导出至 `.schemas/` 目录
- TypeScript 类型声明生成脚本 (`scripts/generate_types.py`) — 输出 `types/` 目录

### Changed
- 版本号 0.1.1 → 0.2.0

## [0.1.1] - 2026-06-26

### Changed
- Week 0 接口冻结（ContentPacket, VideoAsset, SplitResult）
- INT-002 模型一致化清理（去掉 src/ 重复定义）
- Pydantic v2 sum type 枚举规范

## [0.1.0] - 2026-06-25

### Added
- 初始版本，Pydantic v2 数据契约定义
- auth/sentence/content/prompt/trendscope 模型
