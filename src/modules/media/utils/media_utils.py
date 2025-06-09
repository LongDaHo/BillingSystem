from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from utils.logger_utils import get_logger

logger = get_logger(__name__)

def setup_peer_connection(pc: RTCPeerConnection, ws: web.WebSocketResponse):
    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        if candidate:
            logger.info(f"Generated ICE candidate: {candidate}")
            
            # Format candidate for sending to client
            candidate_dict = {
                "type": "ice_candidate",
                "ice": {
                    "candidate": " ".join([
                        f"candidate:{candidate.foundation}",
                        str(candidate.component),
                        candidate.protocol,
                        str(candidate.priority),
                        candidate.ip,
                        str(candidate.port),
                        "typ",
                        candidate.type
                    ]),
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

    return pc

async def process_offer(pc: RTCPeerConnection, ws: web.WebSocketResponse, data):
    offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await ws.send_json({
        "type": answer.type,
        "sdp": answer.sdp
    })

async def process_answer(pc: RTCPeerConnection, ws: web.WebSocketResponse, data):
    answer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
    await pc.setRemoteDescription(answer)

async def process_ice_candidate(pc: RTCPeerConnection, ws: web.WebSocketResponse, data):
    candidate = parse_ice_candidate(data)
    await pc.addIceCandidate(candidate)

def parse_ice_candidate(data):
    ice = data["ice"]
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
    return candidate
