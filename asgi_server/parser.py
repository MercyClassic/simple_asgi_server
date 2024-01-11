import json
from typing import Dict, List, Tuple

from asgi_server.request import Request


class HttpRequestParser:
    def __init__(self, request: bytes):
        self._request = request.decode('utf-8')

    def parse(self) -> Request:
        method, path, http_version = self.parse_start_line()
        headers = self.parse_headers()
        path_without_query_params, query_params = self.parse_query_params(path)
        content_type = headers.get('Content-Type')
        body = self.parse_body(content_type)
        request = Request(
            http_version=http_version,
            method=method,
            path=path_without_query_params,
            query_params=query_params,
            headers=headers,
            body=body,
        )
        return request

    def parse_start_line(self) -> List[str]:
        start_line = self.pop('\r\n').split(' ')
        return start_line

    def parse_headers(self) -> Dict[str, str]:
        header_lines = self.pop('\r\n\r\n').split('\r\n')
        headers = {}
        for header in header_lines:
            key, value = header.split(': ')
            headers.update({key: value})
        return headers

    def parse_query_params(self, path: str) -> Tuple[str, Dict[str, str]]:
        splitted = path.split('?', maxsplit=1)
        if len(splitted) == 1 or (len(splitted) == 2 and splitted[1] == ''):
            return splitted[0], {}
        else:
            path_without_query_params, queries = splitted[0], splitted[1]

        query_params = {}
        for kv in queries.split('&'):
            key, value = kv.split('=')
            query_params[key] = value
        return path_without_query_params, query_params

    def parse_body(self, content_type: str) -> Dict[str, str]:
        if content_type == 'application/json':
            return self._parse_as_json()
        elif content_type == 'application/x-www-form-urlencoded':
            return self._parse_as_form_urlencoded()

    def _parse_as_json(self) -> Dict:
        return json.loads(self._request) if self._request else {}

    def _parse_as_form_urlencoded(self) -> Dict:
        body = {}
        data = self._request.split('&')
        for kv in data:
            key, value = kv.split('=')
            body[key] = value
        return body

    def pop(self, separator: str = ' ') -> str:
        line, other_lines = self._request.split(separator, maxsplit=1)
        self._request = other_lines
        return line
