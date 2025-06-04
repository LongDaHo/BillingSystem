from aiohttp import web
import asyncio
from loguru import logger
from lago_utils import *
import json

client = LagoClient(
    api_key='50f33d9c-375a-4f09-9697-c26363387cd9', 
    api_url='http://lago-api-svc.lago-system.svc.cluster.local:3000'
)

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    customer_id = ""
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)
            if data["type"] == "message":
                text = data["message"].strip()
                words = text.split()
                plan, subscription_id = get_user_plan(client, customer_id)
                if plan=="pay_as_you_go":
                    balance = get_user_balance(client, customer_id)
                    if balance<=0:
                        logger.info("User are running out of money!")
                        return {"response": "You are running out of money!"}
                    logger.info(f"Response has {len(words)} words.")
                    send_usage(client, subscription_id, "stream_chat", {"words": len(words)})

                for word in words:
                    await ws.send_str(word)
                    await asyncio.sleep(0.1)
            elif data["type"] == "customer_id":
                customer_id = data["customer_id"]

        elif msg.type == web.WSMsgType.ERROR:
            logger.error(f'WS connection closed with exception {ws.exception()}')
    return ws

app = web.Application()
app.router.add_get('/api/stream-chat', websocket_handler)

if __name__ == '__main__':
    web.run_app(app, port=8080)
