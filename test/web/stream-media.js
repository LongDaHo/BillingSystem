var pc = null;
var ws = null;
const video = document.getElementById("video");
const connectBtn = document.getElementById('connectBtn');
const configuration = {
  iceServers: [
    {
      urls: [
        'turn:192.168.49.2:3478?transport=udp',
        'turn:192.168.49.2:3478?transport=tcp'
      ],
      username: 'webrtc-user',
      credential: 'secure-password'
    }
  ]
};

function connect() {
  const jwt = jwtInput.value;
  ws = new WebSocket(`ws://api.example.com/api/stream-media?token=${jwt}`);
  const payload = decodeJwtPayload(jwt);
  const customerId = payload?.customer_id;

  ws.onopen = () => {
    console.log("Connected to server");
    ws.send(JSON.stringify({
      type: "customer_id",
      customer_id: customerId
    }));
    pc = new RTCPeerConnection(configuration);

    pc.ontrack = (event) => {
      console.log("Receiving video stream...");
      video.srcObject = event.streams[0];
    };
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        ws.send(JSON.stringify({
          type: 'ice-candidate',
          ice: event.candidate
        }));
      } else {
        console.log("ICE candidate gathering complete.");
      }
    };
  };

  ws.onclose = () => {
    console.log("Disconnected from server");
    pc.close();
  };

  ws.onerror = (event) => {
    console.log("Error: ", event);
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "answer") {
      handleAnswer(data);
    }
    else if (data.type === "offer"){
      handleOffer(data);
    }
    else if (data.type === "ice-candidate"){
      handleCandidate(data);
    };
  }
}

function handleAnswer(data) {
  const remoteDesc = new RTCSessionDescription({
    type: data.type,
    sdp: data.sdp
  });

  pc.setRemoteDescription(remoteDesc)
    .catch(error => {
      console.log(`Error when set remote description: ${error}`);
    });
}

async function handleOffer(data) {
  const offer = new RTCSessionDescription({
    type: data.type,
    sdp: data.sdp
  });

  pc.setRemoteDescription(offer)
    .catch(error => {
      console.log(`Error when set remote description: ${error}`);
    });

  // Tạo answer
  const answer = await pc.createAnswer();
  await pc.setLocalDescription(answer);

  // Gửi answer lại cho server
  ws.send(JSON.stringify({
    type: answer.type,
    sdp: answer.sdp
  }));
}

async function handleCandidate(data) {
  const candidateObj = new RTCIceCandidate({
    candidate: data.ice.candidate,
    sdpMid: data.ice.sdpMid,
    sdpMLineIndex: data.ice.sdpMLineIndex,
  });
  console.log(candidateObj);
  await pc.addIceCandidate(candidateObj);
}

connectBtn.addEventListener('click', function () {
  connect();
});
