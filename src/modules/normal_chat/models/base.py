from pydantic import BaseModel

class TextInput(BaseModel):
    text: str
    customer_id: str