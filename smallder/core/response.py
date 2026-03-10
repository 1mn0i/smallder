import json
from json import JSONDecodeError
from urllib.parse import parse_qsl, urljoin, urlparse

import chardet
from lxml import etree

from smallder.utils.utils import guess_json_utf


class Response:
    attributes = [
        "url",
        "status_code",
        # "headers",
        "content",
        # "flags",
        "request",
        "encoding",
        "cookies",
        "elapsed"
        # "ip_address",
        # "protocol",
    ]

    def __init__(self, url=None, status_code=200, content=None, request=None, encoding="utf-8", cookies=None,
                 elapsed=0):
        if request is None:
            raise ValueError("Request cannot be None")
        self.url = url or request.full_url()
        self.content = content
        self.request = request
        self.status_code = status_code
        self.encoding = encoding
        self.cookies = cookies or {}
        self.elapsed = elapsed
        self._text_cache = {}
        self._root = None
        self._detected_encoding = None

    def __repr__(self):
        parts = ["<Response"]
        if self.status_code is not None:
            parts.append(f" status_code = {self.status_code},")

        if self.url is not None:
            parts.append(f" url = '{self.url}'")

        if self.referer:
            parts.append(f" referer = '{self.referer}'")

        parts.append(">")

        return "".join(parts)

    @property
    def meta(self):
        try:
            return self.request.meta
        except AttributeError:
            raise AttributeError(
                "Response.meta not available, this response "
                "is not tied to any request"
            )

    @property
    def referer(self):
        try:
            return self.request.referer
        except AttributeError:
            raise AttributeError(
                "Response.referer not available, this response "
                "is not tied to any request"
            )

    def text(self, encoding=None):
        """Decode content to text with specified or auto-detected encoding."""
        resolved_encoding = encoding or self.encoding or "utf-8"
        cached_text = self._text_cache.get(resolved_encoding)
        if cached_text is not None:
            return cached_text
        try:
            text = self.content.decode(resolved_encoding)
        except UnicodeDecodeError:
            try:
                detected_encoding = self._auto_char_code() or "utf-8"
                text = self.content.decode(detected_encoding, errors="ignore")
            except (UnicodeDecodeError, TypeError):
                raise UnicodeDecodeError("codec", b"", 0, 1, "can't decode content")
        self._text_cache[resolved_encoding] = text
        return text

    @property
    def ok(self):
        return self.status_code == 200

    def _auto_char_code(self):
        if self._detected_encoding is None:
            char_code = chardet.detect(self.content)
            self._detected_encoding = char_code.get("encoding", "utf-8")
        return self._detected_encoding

    def params(self):

        if self.request.params:
            return self.request.params
        parsed_url = urlparse(self.url)
        params_list = parse_qsl(parsed_url.query)
        # 转换为字典
        return dict(params_list)


    def urljoin(self, url):

        return urljoin(self.url, url)

    def json(self, **kwargs):
        if not self.encoding and self.content and len(self.content) > 3:
            # No encoding set. JSON RFC 4627 section 3 states we should expect
            # UTF-8, -16 or -32. Detect which one to use; If the detection or
            # decoding fails, fall back to `self.text` (using charset_normalizer to make
            # a best guess).
            encoding = guess_json_utf(self.content)
            if encoding is not None:
                try:
                    return json.loads(self.content.decode(encoding), **kwargs)
                except JSONDecodeError as e:
                    raise JSONDecodeError(e.msg, e.doc, e.pos)

        try:
            return json.loads(self.text(), **kwargs)
        except JSONDecodeError as e:
            raise JSONDecodeError(e.msg, e.doc, e.pos)

    def replace(self, *args, **kwargs):
        """Create a new Response with the same attributes except for those given new values"""
        for x in self.attributes:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop("cls", self.__class__)
        return cls(*args, **kwargs)

    @property
    def root(self):
        if self._root is None:
            self._root = etree.HTML(self.text())
        return self._root
