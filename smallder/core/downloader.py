import threading

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from smallder import Request, Response

# 禁用SSL证书验证警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Downloader:

    def __init__(self, spider):
        self.spider = spider
        self._thread_local = threading.local()
        self._sessions = []
        self._sessions_lock = threading.Lock()

    def _get_session(self):
        session = getattr(self._thread_local, "session", None)
        if session is None:
            session = requests.Session()
            self._thread_local.session = session
            with self._sessions_lock:
                self._sessions.append(session)
        return session

    def close(self):
        with self._sessions_lock:
            sessions, self._sessions = self._sessions, []
        for session in sessions:
            session.close()
        if hasattr(self._thread_local, "session"):
            del self._thread_local.session

    def fetch(self, request: Request):
        """
        @type request: Request
        """
        session = self._get_session()
        with session.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.params,
                data=request.data,
                json=request.json,
                cookies=request.cookies,
                timeout=request.timeout,
                proxies=request.proxies,
                verify=request.verify,
                allow_redirects=request.allow_redirects,
        ) as response:
            return Response(
                url=request.full_url(),
                status_code=response.status_code,
                content=response.content,
                request=request,
                cookies=response.cookies.get_dict(),
                elapsed=response.elapsed,
            )

    def download(self, request: Request):
        if request.fetch:
            response = request.fetch(request)
        else:
            response = self.fetch(request)
        return response
