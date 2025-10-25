from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WebhookRequest(BaseModel):
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
    created_at: str
    processed_at: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str
    current_time: str
