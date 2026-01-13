"""
Integration Test Configuration
集成测试配置 - Track 2: Live Integration Testing

测试环境:
- 项目: 主流程测试空间
- project_key: 从环境变量 FEISHU_PROJECT_KEY 读取，默认为 66bb463229e5e58856b4ed19
- 工作项类型: Issue管理
"""
import pytest
from src.core.config import settings


# =============================================================================
# Integration Test Constants
# =============================================================================
# 优先从环境变量读取，否则使用默认值
TEST_PROJECT_KEY = settings.FEISHU_PROJECT_KEY or "66bb463229e5e58856b4ed19"
TEST_PROJECT_NAME = "主流程测试空间"
TEST_WORK_ITEM_TYPE = "Issue管理"


# =============================================================================
# Skip Condition: Check if credentials are available
# =============================================================================
def _has_credentials() -> bool:
    """Check if Feishu credentials are configured."""
    return bool(
        settings.FEISHU_PROJECT_USER_TOKEN
        and settings.FEISHU_PROJECT_USER_KEY
    )


skip_without_credentials = pytest.mark.skipif(
    not _has_credentials(),
    reason="Feishu credentials not configured (FEISHU_PROJECT_USER_TOKEN, FEISHU_PROJECT_USER_KEY)"
)


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def test_project_key():
    """Return the test project key (from env or default)."""
    return TEST_PROJECT_KEY


@pytest.fixture
def test_project_name():
    """Return the test project name."""
    return TEST_PROJECT_NAME


@pytest.fixture
def test_work_item_type():
    """Return the test work item type."""
    return TEST_WORK_ITEM_TYPE
