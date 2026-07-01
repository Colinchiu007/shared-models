#!/usr/bin/env python3
"""Export all shared-models Pydantic v2 models as JSON Schema files.

Usage:
    python scripts/export_schemas.py          # Export to .schemas/
    python scripts/export_schemas.py --check   # Verify schemas are up to date (CI mode)
"""

import json
import os
import sys
from pathlib import Path

# Ensure shared-models is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import shared_models
from pydantic import TypeAdapter

# ── Model registry ──────────────────────────────────────────────────────────
# Ordered by module for clean grouping
MODEL_GROUPS = {
    "auth": [
        shared_models.UserLoginRequest,
        shared_models.UserRegisterRequest,
        shared_models.TokenResponse,
        shared_models.RefreshRequest,
        shared_models.UserResponse,
        shared_models.UserProfile,
        shared_models.JWTPayload,
    ],
    "content": [
        shared_models.CollectRequest,
        shared_models.CollectResult,
        shared_models.RewriteRequest,
        shared_models.RewriteResult,
    ],
    "sentence": [
        shared_models.SentenceBlock,
        shared_models.SubtitleBlock,
        shared_models.SceneSegment,
        shared_models.SplitResult,
        shared_models.EraInfo,
    ],
    "prompt": [
        shared_models.OptimizeRequest,
        shared_models.OptimizeResult,
        shared_models.ReverseRequest,
        shared_models.ReverseResult,
        shared_models.BatchOptimizeRequest,
        shared_models.PromptRewriteRequest,
    ],
    "pipeline": [
        shared_models.PipelineStage,
        shared_models.ContentPacket,
        shared_models.ScenePrompt,
        shared_models.VideoAsset,
    ],
    "trendscope": [
        shared_models.PlatformModel,
        shared_models.TrendingTopicModel,
        shared_models.HotArticleModel,
        shared_models.TrendingPipelineItem,
        shared_models.TrendingListResponse,
    ],
    "llm": [
        shared_models.LLMProviderConfig,
        shared_models.ModelRoute,
        shared_models.UserLLMOverride,
        shared_models.LLMInvocationRequest,
        shared_models.LLMInvocationResponse,
        shared_models.LLMGlobalConfig,
    ],
    "viral": [
        shared_models.TitleStructure,
        shared_models.EmotionalTrigger,
        shared_models.ContentStructure,
        shared_models.ViralFactor,
        shared_models.TitleAnalysis,
        shared_models.EngagementMetrics,
        shared_models.ArticleViralProfile,
        shared_models.ViralAnalysisResult,
        shared_models.TrendingInsights,
        shared_models.ViralScoringConfig,
    ],
}


def export_all(output_dir: str = ".schemas", check: bool = False) -> bool:
    """Export all models to JSON Schema. Returns True if all up-to-date (check mode)."""
    output = Path(output_dir)
    all_ok = True

    for group_name, models in MODEL_GROUPS.items():
        group_dir = output / group_name
        for model_cls in models:
            if hasattr(model_cls, 'model_json_schema'):
                schema = model_cls.model_json_schema()
            elif isinstance(model_cls, type) and issubclass(model_cls, (str,)):
                # Enum types -- use TypeAdapter
                schema = TypeAdapter(model_cls).json_schema()
            else:
                # Skip non-Pydantic classes (e.g. JWTAuthManager)
                print(f"  -  {group_name}/{model_cls.__name__} -- SKIP (non-Pydantic)")
                continue
            model_name = model_cls.__name__
            target = group_dir / f"{model_name}.json"

            if check:
                if target.exists():
                    existing = json.loads(target.read_text())
                    if existing != schema:
                        print(f"  !! {group_name}/{model_name}.json — OUTDATED")
                        all_ok = False
                    else:
                        print(f"  ✓  {group_name}/{model_name}.json — up to date")
                else:
                    print(f"  !! {group_name}/{model_name}.json — MISSING")
                    all_ok = False
            else:
                group_dir.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    json.dumps(schema, indent=2, ensure_ascii=False) + "\n"
                )
                print(f"  ✓  {group_name}/{model_name}.json")

    return all_ok


def main():
    check = "--check" in sys.argv
    mode = "check" if check else "export"
    print(f"[shared-models] JSON Schema {mode}...")

    ok = export_all(check=check)

    if check:
        print()
        if ok:
            print("✅ All schemas up to date.")
            return 0
        else:
            print("❌ Some schemas are outdated. Run `python scripts/export_schemas.py` to regenerate.")
            return 1
    else:
                # Count actually written files
        written = sum(1 for _ in Path(".schemas").rglob("*.json"))
        print(f"\n✅ Exported {written} schemas to .schemas/")
        return 0


if __name__ == "__main__":
    sys.exit(main())
