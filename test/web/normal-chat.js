const textInput = document.getElementById("chatInput");
const normalChatOutput = document.getElementById("chatMessages");

document.getElementById("sendTextBtn").addEventListener("click", async () => {
  const jwt = jwtInput.value;
  const msg = textInput.value;
  const payload = decodeJwtPayload(jwt);
  const customerId = payload?.customer_id;

  const res = await fetch("http://api.example.com/api/normal-chat", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${jwt}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({text: msg, customer_id: customerId})
  });

  const data = await res.json();
  normalChatOutput.value += msg + "\n";
  normalChatOutput.value += data.response + "\n";
});
