from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from loguru import logger
from lago_utils import *

app = FastAPI()
client = LagoClient(
    api_key='50f33d9c-375a-4f09-9697-c26363387cd9', 
    api_url='http://lago-api-svc.lago-system.svc.cluster.local:3000'
)

class TextInput(BaseModel):
    text: str
    customer_id: str

@app.post("/api/normal-chat")
async def echo_text(input_data: TextInput):
    customer_id = input_data.customer_id
    text = input_data.text
    plan, subscription_id = get_user_plan(client, customer_id)
    if plan=="pay_as_you_go":
        balance = get_user_balance(client, customer_id)
        if balance<=0:
            logger.info("User are running out of money!")
            return {"response": "You are running out of money!"}
        words = len(text.split())
        logger.info(f"Response has {words} words.")
        send_usage(client, subscription_id, "normal_chat", {"words": words})
    return {"response": text}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
