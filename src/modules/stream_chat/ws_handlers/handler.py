import json
import asyncio
from aiohttp import web

from utils.logger_utils import get_logger
from utils.lago_utils import *

logger = get_logger(__name__)

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