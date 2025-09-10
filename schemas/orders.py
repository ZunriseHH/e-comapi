from pydantic import BaseModel, Field, EmailStr, conint
from typing import List

class OrderItemIn(BaseModel):
    product_id: int
    qty: conint(gt=0) = Field(..., description="Cantidad > 0")

class CustomerIn(BaseModel):
    email: EmailStr
    name: str

class OrderCreateIn(BaseModel):
    customer: CustomerIn
    items: List[OrderItemIn]

class OrderOut(BaseModel):
    id: int
    status: str
    total: float
    class Config:
        from_attributes = True
        
class OrderItemOut(BaseModel):
    product_id: int
    title: str
    qty: int
    unit_price: float
    line_total: float
    class Config:
        from_attributes = True

class OrderDetailOut(OrderOut):
    items: List[OrderItemOut] = []