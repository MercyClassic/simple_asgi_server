import asyncio
import selectors
import socket
from functools import partial

from asgi_server.parser import HttpRequestParser


class ASGIServer:
    _parser: HttpRequestParser

    def __init__(
        self,
        app,
        host: str,
        port: int,
    ):
        self._app = app
        self._host = host
        self._port = port
        self._selector = selectors.DefaultSelector()

    def _create_server_socket(self) -> None:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self._host, self._port))
        server_socket.listen()

        self._selector.register(
            fileobj=server_socket,
            events=selectors.EVENT_READ,
            data=self._accept_connection,
        )

    async def _accept_connection(
        self,
        server_socket: socket.socket,
    ) -> None:
        client_socket, _ = server_socket.accept()

        self._selector.register(
            fileobj=client_socket,
            events=selectors.EVENT_READ,
            data=self._receive_message,
        )

    async def _receive_message(
        self,
        client_socket: socket.socket,
    ) -> None:
        try:
            data = client_socket.recv(4096)
        except ConnectionError:
            self._selector.unregister(fileobj=client_socket)
            return

        self._parser = HttpRequestParser(data)
        scope = self._parser.parse()
        response: bytes = await self._app(scope)

        self._selector.modify(
            fileobj=client_socket,
            events=selectors.EVENT_WRITE,
            data=partial(self._send_message, response=response),
        )

    async def _send_message(
        self,
        client_socket: socket.socket,
        response: bytes = None,
    ) -> None:
        client_socket.send(response)
        self._selector.modify(
            fileobj=client_socket,
            events=selectors.EVENT_READ,
            data=self._receive_message,
        )

    async def _run(self) -> None:
        self._create_server_socket()

        while True:
            events = self._selector.select()

            for key, _ in events:
                callback = key.data
                await callback(key.fileobj)

    def run(self) -> None:
        asyncio.run(self._run())
