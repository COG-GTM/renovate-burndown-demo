"""ASGI middleware that caps the size of HTTP request bodies."""
import json


class BodyTooLarge(Exception):
    pass


class RequestBodyLimitMiddleware:
    def __init__(self, app, max_body_bytes: int):
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        for name, value in scope.get("headers", []):
            if name == b"content-length":
                try:
                    declared = int(value)
                except ValueError:
                    await _reject(send, 400, "invalid Content-Length")
                    return
                if declared > self.max_body_bytes:
                    await _reject(send, 413, "request body too large")
                    return

        received = 0
        too_large = False
        response_started = False

        async def limited_receive():
            nonlocal received, too_large
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_body_bytes:
                    too_large = True
                    raise BodyTooLarge()
            return message

        async def guarded_send(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                if response_started:
                    return
                response_started = True
                if too_large:
                    await _reject(send, 413, "request body too large")
                    return
            elif too_large:
                return
            await send(message)

        try:
            await self.app(scope, limited_receive, guarded_send)
        except BodyTooLarge:
            if not response_started:
                await _reject(send, 413, "request body too large")


async def _reject(send, status: int, detail: str) -> None:
    body = json.dumps({"detail": detail}).encode()
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
                (b"connection", b"close"),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})
