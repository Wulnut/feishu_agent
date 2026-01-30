import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from src.providers.lark_project.api.attachment import AttachmentAPI


@pytest.fixture
def mock_client():
    client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"err_code": 0, "data": {}}
    mock_response.raise_for_status.return_value = None
    mock_response.content = b"fake_content"
    mock_response.headers = {"content-type": "application/octet-stream"}
    client.post.return_value = mock_response
    return client


@pytest.mark.asyncio
async def test_upload_file_success(mock_client):
    api = AttachmentAPI(client=mock_client)

    # Mock file existence and opening
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=b"file_content")),
    ):
        mock_client.post.return_value.json.return_value = {
            "err_code": 0,
            "data": {"file_token": "token123"},
        }

        result = await api.upload_file("proj_key", "test.txt")

        assert result["file_token"] == "token123"
        mock_client.post.assert_called_once()
        # Verify call args contain 'files' and 'data'
        _, kwargs = mock_client.post.call_args
        assert "files" in kwargs
        assert "data" in kwargs
        assert kwargs["data"]["parent_type"] == "work_item"


@pytest.mark.asyncio
async def test_upload_file_not_found(mock_client):
    api = AttachmentAPI(client=mock_client)

    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            await api.upload_file("proj", "missing.txt")


@pytest.mark.asyncio
async def test_download_file_success(mock_client):
    api = AttachmentAPI(client=mock_client)

    # Mock binary response
    mock_client.post.return_value.content = b"binary_data"
    mock_client.post.return_value.headers = {}  # Not json

    result = await api.download_file("proj", "token123")

    assert result == b"binary_data"
    mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_download_file_error_json(mock_client):
    api = AttachmentAPI(client=mock_client)

    # Mock error response disguised as success status code but json body
    mock_client.post.return_value.headers = {"content-type": "application/json"}
    mock_client.post.return_value.json.return_value = {
        "err_code": 1,
        "err_msg": "Download failed",
    }

    with pytest.raises(Exception, match="下载附件失败: Download failed"):
        await api.download_file("proj", "token123")
