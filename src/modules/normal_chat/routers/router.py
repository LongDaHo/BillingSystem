from fastapi import APIRouter
from utils.lago_utils import *
from utils.logger_utils import get_logger
from modules.normal_chat.models.base import TextInput

logger = get_logger(__name__)
router = APIRouter()

@router.post("/api/normal-chat")
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