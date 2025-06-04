let chatSocket = null;
const streamTextInput = document.getElementById("streamChatInput");
const streamChatOutput = document.getElementById("streamChatMessages");

document.getElementById("sendStreamTextBtn").addEventListener("click", async () => {
  const jwt = jwtInput.value;
  const msg = streamTextInput.value;
  const payload = decodeJwtPayload(jwt);
  const customerId = payload?.customer_id;
  if (streamChatOutput.value === '')
    streamChatOutput.value += msg + "\n";
  else
    streamChatOutput.value += "\n" + msg + "\n"

  if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) {
    chatSocket = new WebSocket(`ws://api.example.com/api/stream-chat?token=${jwt}`);
    chatSocket.onmessage = (e) => {
        streamChatOutput.value += `${e.data} `;
    };
    chatSocket.onopen = () => {
      chatSocket.send(JSON.stringify({
        type: 'customer_id',
        customer_id: customerId
      }));
      chatSocket.send(JSON.stringify({
        type: 'message',
        message: msg
      }));
    };
  } else {
    chatSocket.send(JSON.stringify({
      type: 'message',
      message: msg
    }));
  }
});