import asyncio
import json

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceServer, RTCIceCandidate, RTCConfiguration, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer
from loguru import logger
import time
from threading import Thread

from lago_utils import *

pcs = dict()
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

            if data["type"] == "customer_id":
                customer_id = data["customer_id"]
                ice_servers = [
                    RTCIceServer(
                        urls=[
                            f"turn:192.168.49.2:3478?transport=udp",
                            f"turn:192.168.49.2:3478?transport=tcp"
                        ],
                        username="webrtc-user",
                        credential="secure-password",
                    ),
                ]

                config = RTCConfiguration(ice_servers)
                pc = RTCPeerConnection(configuration=config)
                pcs.update({customer_id: pc})
                plan, subscription_id = get_user_plan(client, customer_id)
                if plan=="pay_as_you_go":
                    balance = get_user_balance(client, customer_id)
                    tracker_thread = Thread(target = usage_tracker_thread, args = (customer_id, subscription_id, balance, ))
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

                @pc.on("icecandidate")
                async def on_icecandidate(candidate):
                    if candidate:
                        logger.info(f"Generated ICE candidate: {candidate}")
                        
                        # Format candidate for sending to client
                        candidate_dict = {
                            "type": "ice-candidate",
                            "ice": {
                                "candidate": f"candidate:{candidate.foundation} {candidate.component} {candidate.protocol} {candidate.priority} {candidate.ip} {candidate.port} typ {candidate.type}",
                                "sdpMid": candidate.sdpMid,
                                "sdpMLineIndex": candidate.sdpMLineIndex
                            }
                        }
                        
                        # Send to client via WebSocket
                        await ws.send_json(candidate_dict)
                    else:
                        logger.info("All ICE candidates have been generated")

                @pc.on("datachannel")
                def on_datachannel(channel):
                    @channel.on("message")
                    def on_message(message):
                        logger.info(f"Received message: {message}")

            elif data["type"] == "offer":
                logger.info("Receive offer!")
                offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await pc.setRemoteDescription(offer)
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await ws.send_json({
                    "type": answer.type,
                    "sdp": answer.sdp
                })
            elif data["type"] == "answer":
                logger.info("Receive answer!")
                answer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await pc.setRemoteDescription(answer)
            elif data["type"] == "ice-candidate":
                try:
                    ice = data["ice"]
                    logger.info(ice)
                    ip = ice['candidate'].split(' ')[4]
                    port = int(ice['candidate'].split(' ')[5])
                    protocol = ice['candidate'].split(' ')[2]
                    priority = int(ice['candidate'].split(' ')[3])
                    component = int(ice['candidate'].split(' ')[1] )
                    foundation = ice['candidate'].split(' ')[0].split(':')[1]
                    type = ice['candidate'].split(' ')[7]
                    candidate = RTCIceCandidate(
                        ip=ip,
                        port=port,
                        protocol=protocol,
                        priority=priority,
                        foundation=foundation,
                        component=component,
                        type=type,
                        sdpMid=ice['sdpMid'],
                        sdpMLineIndex=ice['sdpMLineIndex']
                    )

                    await pc.addIceCandidate(candidate)
                except:
                    print("ICE negotiate successfully!")
        elif msg.type == web.WSMsgType.ERROR:
            logger.error(f"WebSocket error: {ws.exception()}")
    
    return ws
    

def usage_tracker_thread(customer_id, subscription_id, balance):
    """Thread that runs every second to track usage"""
    current_time = time.time()
    while True:
        time.sleep(1)
        seconds = time.time() - current_time
        fee = get_predicted_fee(client, subscription_id, "stream_media", {"seconds": seconds})
        logger.info(f"Balance: {balance} - Predicted fee: {fee}")
        if fee>=balance or pcs[customer_id].connectionState == "closed":
            logger.info("User is running out of credits or PeerConnection is closed!")
            send_usage(client, subscription_id, "stream_media", {"seconds": seconds})
            break        

async def on_shutdown(app):
    coros = [pcs[key].close() for key in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


app = web.Application()
app.router.add_get('/api/stream-media', websocket_handler)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, port=8080)
