**<h1> Implementation of simple ASGI Server </h1>**
**<h2> Server created via python core module selectors </h2>**

**<h2> To use this server you need to create async callable object
which receive Request and returns valid encoded http response<br><br>
For example:</h2>**
```python
from asgi_server import ASGIServer, Request


class App:
    async def __call__(self, request: Request) -> bytes:
        return (
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: plain/text\r\n'
            b'Content-Length: 12\r\n\r\n'
            b'Hello world!'
        )


app = App()
server = ASGIServer(app, '127.0.0.1', 8000)
server.run()
```
