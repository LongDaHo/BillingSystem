import jwt
import datetime

SECRET = "<CONSUMER_SECRET_KEY>"

def generate_jwt_token(customer_id, key):
    payload = {
        "customer_id": customer_id,
        "iat": int(datetime.datetime.now().timestamp()),
        "exp": int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()),
        "iss": key
    }
    print(payload)
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    return token

token = generate_jwt_token("<LAGO_USER_ID>", "<CONSUMER_KEY>")
print(token)
