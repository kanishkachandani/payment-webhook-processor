from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import Response
from models import WebhookRequest, TransactionResponse, HealthCheckResponse
from database import get_supabase_client
from datetime import datetime, timezone
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Payment Webhook Processor")

# Get Supabase client
supabase = get_supabase_client()


async def process_transaction(transaction_data: dict):
    """
    Background task to process transaction with 30-second delay
    """
    transaction_id = transaction_data["transaction_id"]

    try:
        logger.info(f"Starting processing for transaction: {transaction_id}")

        # Simulate 30-second processing delay (external API calls)
        await asyncio.sleep(30)

        # Update transaction status to PROCESSED
        processed_at = datetime.now(timezone.utc).isoformat()

        response = supabase.table("transactions").update({
            "status": "PROCESSED",
            "processed_at": processed_at
        }).eq("transaction_id", transaction_id).execute()

        logger.info(f"Transaction {transaction_id} processed successfully")

    except Exception as e:
        logger.error(f"Error processing transaction {transaction_id}: {str(e)}")


@app.get("/", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthCheckResponse(
        status="HEALTHY",
        current_time=datetime.now(timezone.utc).isoformat()
    )


@app.post("/v1/webhooks/transactions", status_code=202)
async def receive_webhook(
    webhook_data: WebhookRequest,
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint to receive transaction data
    - Returns 202 Accepted immediately
    - Processes transaction in background
    - Implements idempotency (duplicate prevention)
    """
    try:
        # Check if transaction already exists (idempotency)
        existing = supabase.table("transactions").select("*").eq(
            "transaction_id", webhook_data.transaction_id
        ).execute()

        if existing.data:
            # Transaction already exists, return 202 without reprocessing
            logger.info(f"Duplicate transaction received: {webhook_data.transaction_id}")
            return Response(status_code=202)

        # Insert new transaction with PROCESSING status
        transaction_record = {
            "transaction_id": webhook_data.transaction_id,
            "source_account": webhook_data.source_account,
            "destination_account": webhook_data.destination_account,
            "amount": webhook_data.amount,
            "currency": webhook_data.currency,
            "status": "PROCESSING",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "processed_at": None
        }

        supabase.table("transactions").insert(transaction_record).execute()

        # Add background task for processing
        background_tasks.add_task(
            process_transaction,
            transaction_record
        )

        logger.info(f"Transaction {webhook_data.transaction_id} queued for processing")

        return Response(status_code=202)

    except Exception as e:
        logger.error(f"Error receiving webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/v1/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    """
    Query endpoint to retrieve transaction status
    """
    try:
        response = supabase.table("transactions").select("*").eq(
            "transaction_id", transaction_id
        ).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Transaction not found")

        transaction = response.data[0]

        return TransactionResponse(
            transaction_id=transaction["transaction_id"],
            source_account=transaction["source_account"],
            destination_account=transaction["destination_account"],
            amount=transaction["amount"],
            currency=transaction["currency"],
            status=transaction["status"],
            created_at=transaction["created_at"],
            processed_at=transaction.get("processed_at")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
