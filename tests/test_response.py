from unittest.mock import patch

from smallder import Request, Response


def make_response(content=b"<html><body>ok</body></html>", encoding="utf-8"):
    request = Request(url="http://example.com")
    return Response(request=request, content=content, encoding=encoding)


def test_text_caches_detected_encoding():
    response = make_response(content=b"\xe9", encoding=None)

    with patch("smallder.core.response.chardet.detect", return_value={"encoding": "latin-1"}) as detect:
        assert response.text() == "\xe9"
        assert response.text() == "\xe9"

    detect.assert_called_once_with(b"\xe9")


def test_root_is_cached():
    response = make_response()

    with patch("smallder.core.response.etree.HTML", return_value=object()) as html:
        first_root = response.root
        second_root = response.root

    assert first_root is second_root
    html.assert_called_once_with("<html><body>ok</body></html>")
