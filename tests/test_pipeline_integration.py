"""全链路集成验证 — 通过实际模型定义验证共享数据契约端到端一致性。

每个测试使用 shared-models 的实际 Pydantic 模型，验证：
1. 模型可正确创建（字段匹配消费方期望）
2. JSON 序列化/反序列化兼容
3. ContentPacket 作为管道载体的完整生命周期
"""
import json
from datetime import datetime, timezone

from shared_models.auth import AuthTokenResponse, LoginRequest, RegisterRequest
from shared_models.content import RewriteRequest, RewriteResult
from shared_models.pipeline import ContentPacket, PipelineStage
from shared_models.prompt import OptimizeRequest, OptimizeResult
from shared_models.sentence import (
    EraInfo,
    SceneSegment,
    SentenceBlock,
    SplitResult,
    SubtitleBlock,
)
from shared_models.trendscope.models import (
    HotArticleModel,
    TrendingTopicModel,
    ApiResponse,
    HotArticleListResponse,
)


# ── Stage 1: TrendScope 热榜 ──────────────────────────────────────────────


class TestTrendScopeStage:
    """trendscope 序列化输出 → shared-models 模型"""

    def test_trending_topic_from_serializer(self):
        """模拟 trendscope._serialize_topic() 输出的 dict 直接实例化"""
        data = {
            "id": 42,
            "platform": {"code": "weibo", "name": "微博", "icon_url": ""},
            "rank": 1,
            "title": "热搜话题",
            "hot_value": "1000000",
            "hot_value_norm": 95.5,
            "topic_url": "https://weibo.com/topic",
            "category": "娱乐",
            "snapshot_at": "2026-06-27T10:00:00",
        }
        topic = TrendingTopicModel(**data)
        assert topic.platform["code"] == "weibo"
        assert topic.snapshot_at == "2026-06-27T10:00:00"
        assert topic.hot_value == "1000000"

    def test_hot_article_from_serializer(self):
        """模拟 trendscope._serialize_article() 输出直接实例化"""
        data = {
            "id": 1,
            "platform": {"code": "douyin", "name": "抖音", "icon_url": ""},
            "title": "搞笑视频",
            "summary": "太好笑了",
            "images": [{"url": "https://example.com/img.jpg"}],
            "video_url": "https://douyin.com/play/123",
            "author_name": "创作者",
            "author_avatar": "",
            "source_url": "https://douyin.com/v/123",
            "read_count": 50000,
            "like_count": 10000,
            "comment_count": 500,
            "share_count": 2000,
            "favor_count": 3000,
            "collected_count": 1000,
            "author_followers": 100000,
            "viral_score": 85.0,
            "viral_score_norm": 90.5,
            "publish_at": "2026-06-27T09:00:00",
            "snapshot_at": "2026-06-27T10:00:00",
        }
        article = HotArticleModel(**data)
        assert article.platform["code"] == "douyin"
        assert article.video_url == "https://douyin.com/play/123"

    def test_api_response_roundtrip(self):
        """ApiResponse + HotArticleListResponse JSON 序列化"""
        articles = [
            HotArticleModel(platform={"code": "weibo"}, title="A",
                            source_url="https://a.com"),
            HotArticleModel(platform={"code": "weibo"}, title="B",
                            source_url="https://b.com"),
        ]
        list_resp = HotArticleListResponse(items=articles, total=2, page=1, page_size=20)
        api_resp = ApiResponse(code=200, message="success", data=list_resp.model_dump())
        serialized = api_resp.model_dump()
        assert serialized["code"] == 200
        assert len(serialized["data"]["items"]) == 2


# ── Stage 2: ContentPacket 管道载体 ──────────────────────────────────────


class TestContentPacketStage:
    """ContentPacket 全链路生命周期"""

    def test_basic_creation(self):
        """ContentPacket 基本创建"""
        packet = ContentPacket(
            id="pkt-001",
            source_platform="weibo",
            source_url="https://weibo.com/topic/1",
            source_title="热搜话题",
            source_content="这是热搜正文内容……",
        )
        assert packet.stage == PipelineStage.COLLECTED
        assert packet.source_platform == "weibo"

    def test_stage_progression(self):
        """COLLECTED → REWRITTEN → SPLIT → PROMPTED"""
        packet = ContentPacket(
            id="pkt-002",
            source_platform="weibo",
            source_url="https://weibo.com/topic/2",
            source_title="话题2",
            source_content="内容正文",
        )
        packet.stage = PipelineStage.REWRITTEN
        assert packet.stage == PipelineStage.REWRITTEN

        packet.stage = PipelineStage.SPLIT
        assert packet.stage == PipelineStage.SPLIT

        packet.stage = PipelineStage.PROMPTED
        assert packet.stage == PipelineStage.PROMPTED

    def test_json_roundtrip(self):
        """ContentPacket JSON 序列化兼容"""
        packet = ContentPacket(
            id="pkt-003",
            source_platform="baidu",
            source_url="https://baidu.com/article/1",
            source_title="百度文章",
            source_content="百度正文内容……",
        )
        raw = packet.model_dump_json()
        restored = ContentPacket.model_validate_json(raw)
        assert restored.source_url == packet.source_url
        assert restored.source_title == packet.source_title

    def test_aggregator_writes_to_packet(self):
        """模拟 content-aggregator 向 ContentPacket 写入改写结果"""
        packet = ContentPacket(
            id="pkt-004",
            source_platform="weibo",
            source_url="https://weibo.com/topic/4",
            source_title="测试话题",
            source_content="原始正文",
        )
        packet.stage = PipelineStage.REWRITTEN
        packet.rewritten_title = "改写标题"
        packet.rewritten_content = "改写正文……"
        packet.rewrite_style = "eye-catching"
        assert packet.rewritten_title == "改写标题"
        assert packet.rewrite_style == "eye-catching"


# ── Stage 3: content-aggregator 改写 ─────────────────────────────────────


class TestRewriteStage:
    """改写阶段模型一致性"""

    def test_rewrite_request(self):
        req = RewriteRequest(
            content="这是需要改写的正文内容……",
            title="原标题",
            style="eye-catching",
        )
        assert req.title == "原标题"
        assert req.style == "eye-catching"

    def test_rewrite_result(self):
        result = RewriteResult(
            rewritten_content="改写后的内容",
            rewritten_title="新标题",
            style="eye-catching",
            word_count=120,
        )
        assert result.rewritten_title == "新标题"
        assert result.style == "eye-catching"


# ── Stage 4: smart-sentence-splitter 分句 ────────────────────────────────


class TestSplitStage:
    """分句阶段模型一致性"""

    def test_split_result_with_sentences(self):
        sentences = [
            SentenceBlock(index=0, text="今天天气真好。"),
            SentenceBlock(index=1, text="我们出去玩吧！"),
        ]
        result = SplitResult(sentences=sentences, total_scenes=1)
        assert len(result.sentences) == 2
        assert result.total_scenes == 1
        assert result.language == "zh"
        assert result.tier_used == "tier3_rule"

    def test_split_result_with_scenes(self):
        sentences = [SentenceBlock(index=0, text="今天天气真好。")]
        scenes = [
            SceneSegment(
                segment_id=0,
                text="户外场景",
                estimated_duration=5.0,
                target_words=50,
                sentences=sentences,
                era_info=EraInfo(era="modern", confidence=0.95),
            ),
        ]
        result = SplitResult(sentences=sentences, scenes=scenes, total_scenes=1)
        assert result.scenes[0].era_info.era == "modern"
        assert len(result.scenes[0].sentences) == 1

    def test_json_roundtrip(self):
        sentences = [
            SentenceBlock(index=0, text="你好"),
            SentenceBlock(index=1, text="世界"),
        ]
        result = SplitResult(sentences=sentences)
        raw = result.model_dump_json()
        restored = SplitResult.model_validate_json(raw)
        assert restored.sentences[0].text == "你好"

    def test_session_channel_tier_terminology(self):
        """验证分句器术语对齐——SentenceBlock 有 tier/confidence/length_status"""
        block = SentenceBlock(
            index=0, text="测试句子",
            tier="tier3_rule", confidence=0.95,
            length_status="ok",
        )
        assert block.tier == "tier3_rule"
        assert block.length_status == "ok"


# ── Stage 5: prompt-engine ────────────────────────────────────────────────


class TestPromptStage:
    """prompt-engine 阶段模型一致性"""

    def test_optimize_request(self):
        req = OptimizeRequest(
            prompt="一只猫在阳光下睡觉",
            platform="Midjourney",
        )
        assert req.platform == "Midjourney"
        assert len(req.prompt) > 0

    def test_optimize_result(self):
        result = OptimizeResult(
            optimized_prompt="A cat sleeping in warm sunlight, cozy atmosphere",
            platform="Midjourney",
            reasoning="English prompt for Midjourney",
            tokens_used=50,
            model_used="gpt-4o",
        )
        assert result.model_used == "gpt-4o"
        assert result.platform == "Midjourney"


# ── Auth models ───────────────────────────────────────────────────────────


class TestAuthModels:
    """跨模块认证模型一致性"""

    def test_register_login_flow(self):
        req = RegisterRequest(username="newuser", password="pass123",
                              email="user@example.com")
        assert req.username == "newuser"

        login = LoginRequest(username="newuser", password="pass123")
        assert login.password == "pass123"

    def test_token_response(self):
        resp = AuthTokenResponse(
            access_token="eyJ...",
            refresh_token="eyJ...",
            expires_in=3600,
            user={"id": "uuid", "username": "user",
                  "subscription_type": "free", "tier": 1},
        )
        assert resp.token_type == "bearer"
        assert resp.expires_in == 3600


# ── 全链路模拟 ────────────────────────────────────────────────────────────


class TestFullPipeline:
    """完整管道模拟 — ContentPacket 贯穿所有阶段"""

    def test_pipeline_contentpacket(self):
        """从 TrendScope(COLLECTED) 到 prompt-engine(PROMPTED)"""
        topic = TrendingTopicModel(
            platform={"code": "weibo", "name": "微博"},
            rank=1, title="热搜话题", hot_value="1000000",
        )
        packet = ContentPacket(
            id="pipeline-e2e-001",
            source_platform="weibo",
            source_url=topic.topic_url or "https://weibo.com/topic/1",
            source_title=topic.title,
            source_content=topic.title,
        )
        assert packet.stage == PipelineStage.COLLECTED

        # Phase 2: content-aggregator 改写
        packet.stage = PipelineStage.REWRITTEN
        packet.rewritten_content = "改写后的内容……"
        packet.rewritten_title = "新标题"
        assert packet.rewritten_title == "新标题"

        # Phase 3: 分句
        packet.stage = PipelineStage.SPLIT
        split = SplitResult(
            sentences=[SentenceBlock(index=0, text="改写后的内容……")],
        )
        packet.split_result = split.model_dump()
        assert packet.split_result["sentences"][0]["text"] == "改写后的内容……"

        # Phase 4: 提示词优化
        packet.stage = PipelineStage.PROMPTED
        assert packet.stage == PipelineStage.PROMPTED

        # JSON 回环验证
        final_json = packet.model_dump_json()
        restored = ContentPacket.model_validate_json(final_json)
        assert restored.source_title == "热搜话题"
        assert restored.split_result["sentences"][0]["text"] == "改写后的内容……"
