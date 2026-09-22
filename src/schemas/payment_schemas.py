from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CreateOrderRequest(BaseModel):
    course_id: int


class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int  # in paise
    currency: str
    key_id: str
    course_id: int


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    course_id: int


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    amount: float
    razorpay_order_id: str
    razorpay_payment_id: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)