from pydantic import BaseModel
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

    class Config:
        from_attributes = True
