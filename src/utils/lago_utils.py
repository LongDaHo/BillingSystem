import uuid
import time
from lago_python_client import Client 
from lago_python_client.models import Event

from utils.env import LAGO_API_KEY

def get_user_plan(client, customer_id):
    subs = client.subscriptions.find_all({'external_customer_id': customer_id})
    return subs["subscriptions"][0].plan_code, subs["subscriptions"][0].external_id

def get_user_balance(client, customer_id):
    subs = client.wallets.find_all({'external_customer_id': customer_id})
    return subs["wallets"][0].balance_cents/100.0

def get_predicted_fee(client, subscription_id, code, properties):
    event = Event(
        transaction_id=str(uuid.uuid4()),
        external_subscription_id=subscription_id,
        code=code,
        timestamp=int(time.time()),
        properties=properties
    )
    fee = client.events.estimate_fees(event)
    return fee["fees"][0].amount_cents/100.0

def send_usage(client, subscription_id, code, properties):
    event = Event(
        transaction_id=str(uuid.uuid4()),
        external_subscription_id=subscription_id,
        code=code,
        timestamp=int(time.time()),
        properties=properties
    )
    client.events.create(event)

client = Client(
    api_key=LAGO_API_KEY, 
    api_url='http://lago-api-svc.lago-system.svc.cluster.local:3000'
)