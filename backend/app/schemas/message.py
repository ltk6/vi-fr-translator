from pydantic import BaseModel

class Payload(BaseModel):
    text: str