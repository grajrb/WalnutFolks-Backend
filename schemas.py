from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TransactionWebhook(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str


class TransactionResponse(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HealthCheckResponse(BaseModel):
    status: str
    current_time: str
