import pytest
from unittest.mock import MagicMock, Mock, patch

from smallder import Request, Response
from smallder import Downloader


@pytest.fixture
def downloader():
    """创建一个示例 Downloader 对象"""
    return Downloader(spider=None)

def make_mock_response():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"response content"
    mock_response.cookies.get_dict.return_value = {}
    mock_response.elapsed = 0.1
    return mock_response


@patch("smallder.core.downloader.requests.Session")
def test_download_reuses_session(mock_session_cls, downloader):
    mock_response = make_mock_response()
    session = Mock()
    request_context = MagicMock()
    request_context.__enter__.return_value = mock_response
    request_context.__exit__.return_value = False
    session.request.return_value = request_context
    mock_session_cls.return_value = session

    first_response = downloader.download(Request(method="GET", url="http://example.com"))
    second_response = downloader.download(Request(method="GET", url="http://example.com/2"))

    assert isinstance(first_response, Response)
    assert isinstance(second_response, Response)
    assert mock_session_cls.call_count == 1
    assert session.request.call_count == 2


@patch("smallder.core.downloader.requests.Session")
def test_fetch_passes_json_payload(mock_session_cls, downloader):
    mock_response = make_mock_response()
    session = Mock()
    request_context = MagicMock()
    request_context.__enter__.return_value = mock_response
    request_context.__exit__.return_value = False
    session.request.return_value = request_context
    mock_session_cls.return_value = session

    request = Request(method="POST", url="http://example.com", json={"key": "value"})
    response = downloader.fetch(request)

    session.request.assert_called_once_with(
        method="POST",
        url="http://example.com",
        headers=None,
        params=None,
        data=None,
        json={"key": "value"},
        cookies=None,
        timeout=5,
        proxies=None,
        verify=False,
        allow_redirects=True,
    )
    assert response.status_code == 200
    assert response.content == b"response content"
