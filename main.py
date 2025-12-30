from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging
import threading
from database import get_db, Transaction
from schemas import TransactionWebhook, TransactionResponse, HealthCheckResponse
from background_tasks import process_transaction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Transaction Webhook Service", version="1.0.0")


# Helper function to process transaction in a thread
def process_in_background(transaction_id: str):
    """Process transaction in a separate thread"""
    def run():
        import asyncio
        asyncio.run(process_transaction(transaction_id))
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()


@app.api_route("/", response_model=HealthCheckResponse, methods=["GET", "HEAD"])
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="HEALTHY",
        current_time=datetime.now(timezone.utc).isoformat() + "Z"
    )


@app.post("/v1/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(
    webhook: TransactionWebhook,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receive transaction webhook from payment processor.
    Responds with 202 Accepted immediately and processes in background.
    """
    transaction_id = webhook.transaction_id

    # Check if transaction already exists (idempotency check)
    existing = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id
    ).first()

    if existing:
        logger.info(f"Webhook received for existing transaction {transaction_id}, status: {existing.status}")
        # Return 202 Accepted even if already processing
        return {"message": "Webhook acknowledged", "transaction_id": transaction_id}

    # Create new transaction record
    transaction = Transaction(
        transaction_id=transaction_id,
        source_account=webhook.source_account,
        destination_account=webhook.destination_account,
        amount=webhook.amount,
        currency=webhook.currency,
        status="PROCESSING",
        created_at=datetime.now(timezone.utc),
        webhook_received_at=datetime.now(timezone.utc)
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    logger.info(f"Webhook received for transaction {transaction_id}, queuing for processing")

    # Start background processing (non-blocking)
    process_in_background(transaction_id)

    return {"message": "Webhook acknowledged", "transaction_id": transaction_id}


@app.get("/v1/transactions/{transaction_id}", response_model=list[TransactionResponse])
async def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """
    Retrieve transaction status.
    Returns a list with the transaction details.
    """
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return [TransactionResponse.model_validate(transaction)]


@app.get("/v1/transactions", response_model=list[TransactionResponse])
async def list_transactions(db: Session = Depends(get_db)):
    """
    List all transactions (useful for testing).
    """
    transactions = db.query(Transaction).order_by(
        Transaction.webhook_received_at.desc()
    ).all()

    return [TransactionResponse.model_validate(t) for t in transactions]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
