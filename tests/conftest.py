import json
import logging
from pathlib import Path
import pytest
import asyncio
import sys


# =============================================================================
# Pytest Markers Registration
# =============================================================================
def pytest_configure(config):
    """Register custom markers to avoid warnings."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires real Feishu API)"
    )


# =============================================================================
# Snapshot Fixtures (Track 1 - Snapshot-based Unit Testing)
# =============================================================================
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "snapshots"


@pytest.fixture
def load_snapshot():
    """
    Load a JSON snapshot file from tests/fixtures/snapshots/.
    
    Usage:
        def test_example(load_snapshot):
            data = load_snapshot("work_item_list.json")
    """
    def _load(filename: str) -> dict:
        filepath = FIXTURES_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Snapshot not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return _load


@pytest.fixture
def save_snapshot():
    """
    Save API response as JSON snapshot for Track 1 tests.
    Used by integration tests to capture real responses.
    
    Usage:
        def test_example(save_snapshot):
            response = await api.get_items()
            save_snapshot("work_item_list.json", response)
    """
    def _save(filename: str, data: dict) -> None:
        FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
        filepath = FIXTURES_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return _save


# =============================================================================
# Logging Configuration
# =============================================================================
# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)
logger.info("Test logging configured: level=DEBUG")


# Enable asyncio support for pytest
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    logger.debug("Creating event loop for test session")
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    logger.debug("Closing event loop")
    loop.close()


@pytest.fixture(autouse=True)
def log_test_start(request):
    """Log test start and end for each test."""
    logger.info("=" * 80)
    logger.info("Starting test: %s", request.node.name)
    yield
    logger.info("Completed test: %s", request.node.name)
    logger.info("=" * 80)
