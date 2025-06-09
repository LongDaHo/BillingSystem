import json
import time
import asyncio
from aiohttp import web
from threading import Thread
from aiortc import RTCPeerConnection, RTCConfiguration
from aiortc.contrib.media import MediaPlayer

from utils.logger_utils import get_logger
from utils.lago_utils import *
from modules.media.ice_servers import local_servers
from modules.media.utils.media_utils import *


logger = get_logger(__name__)
pcs = dict()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)
            await process_message(ws, data)
        elif msg.type == web.WSMsgType.ERROR:
            logger.error(f"WebSocket error: {ws.exception()}") 
    return ws     

async def process_message(ws: web.WebSocketResponse, data):
    if data["type"] == "customer_id":
        customer_id = data["customer_id"]
        config = RTCConfiguration(local_servers)
        pc = RTCPeerConnection(configuration=config)
        pc = setup_peer_connection(pc, ws)
        pcs.update({customer_id: pc})
        plan, subscription_id = get_user_plan(client, customer_id)
        if plan=="pay_as_you_go":
            balance = get_user_balance(client, customer_id)
            tracker_thread = Thread(target=usage_tracker_target, 
                                    args=(customer_id, subscription_id, balance))
            tracker_thread.start()
        logger.info("Created peer connection")

        player = MediaPlayer('sample_960x400_ocean_with_audio.mp4')
        if player.video:
            pc.addTrack(player.video)
        if player.audio:
            pc.addTrack(player.audio)

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        await ws.send_json({
            "type": offer.type,
            "sdp": offer.sdp
        })
        logger.info("Send offer!")
    elif data["type"] == "offer":
        logger.info("Receive offer!")
        customer_id = data["customer_id"]
        await process_offer(pcs[customer_id], ws, data)
    elif data["type"] == "answer":
        logger.info("Receive answer!")
        customer_id = data["customer_id"]
        await process_answer(pcs[customer_id], ws, data)
    elif data["type"] == "ice_candidate":
        try:
            customer_id = data["customer_id"]
            await process_ice_candidate(pcs[customer_id], ws, data)
        except:
            print("ICE negotiate successfully!")

def usage_tracker_target(customer_id, subscription_id, balance):
    asyncio.run(usage_tracker_thread(customer_id, subscription_id, balance))

async def usage_tracker_thread(customer_id, subscription_id, balance):
    """Thread that runs every second to track usage"""
    current_time = time.time()
    while True:
        time.sleep(1)
        seconds = time.time() - current_time
        fee = get_predicted_fee(client, subscription_id, "stream_media", {"seconds": seconds})
        logger.info(f"Balance: {balance} - Predicted fee: {fee}")
        if fee>=balance or pcs[customer_id].connectionState == "closed":
            logger.info("User is running out of credits or PeerConnection is closed!")
            await asyncio.gather(pcs[customer_id].close())
            send_usage(client, subscription_id, "stream_media", {"seconds": seconds})
            break   

async def on_shutdown(app):
    coros = [pcs[key].close() for key in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    