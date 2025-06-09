from aiortc import RTCIceServer
from utils.env import TURN_USERNAME, TURN_PASSWORD

local_servers = [
    RTCIceServer(
        urls=[
            f"turn:coturn-service:3478?transport=udp",
            f"turn:coturn-service:3478?transport=tcp"
        ],
        username=TURN_USERNAME,
        credential=TURN_PASSWORD,
    ),
]