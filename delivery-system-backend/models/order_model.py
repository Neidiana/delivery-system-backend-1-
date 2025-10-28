from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, condecimal, conint
from enum import Enum

# Enum para status do pedido
class OrderStatus(str, Enum):
    pending = "pending"
    preparing = "preparing"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    canceled = "canceled"

# ---------------------------
# Schemas para OrderItem
# ---------------------------
class OrderItemBase(BaseModel):
    product_id: int
    quantity: conint(gt=0)
    price: condecimal(gt=0, decimal_places=2)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int

    class Config:
        orm_mode = True

# ---------------------------
# Schemas para Order
# ---------------------------
class OrderBase(BaseModel):
    user_id: int
    status: Optional[OrderStatus] = OrderStatus.pending

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus]

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True
