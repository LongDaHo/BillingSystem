import asyncio
from aiohttp import web
from modules.media.ws_handlers import websocket_handler, on_shutdown

app = web.Application()
app.router.add_get('/api/stream-media', websocket_handler)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, port=8080)