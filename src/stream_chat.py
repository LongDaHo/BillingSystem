from aiohttp import web
from modules.stream_chat.ws_handlers import websocket_handler

app = web.Application()
app.router.add_get('/api/stream-chat', websocket_handler)

if __name__ == '__main__':
    web.run_app(app, port=8080)