import asyncio
import logging
from datetime import datetime, timezone
from database import SessionLocal, Transaction

logger = logging.getLogger(__name__)


async def process_transaction(transaction_id: str):
    """
    Background task to process a transaction.
    Includes 30-second delay to simulate external API calls.
    """
    db = SessionLocal()
    try:
        # Fetch the transaction
        transaction = db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()

        if not transaction:
            logger.warning(f"Transaction {transaction_id} not found")
            return

        # Check if already processing to prevent race conditions
        if transaction.status in ["PROCESSED", "FAILED"]:
            logger.info(f"Transaction {transaction_id} already {transaction.status}")
            return

        # Mark as processing
        transaction.is_processing = True
        transaction.processing_started_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Starting processing for transaction {transaction_id}")

        # Simulate 30-second external API call
        await asyncio.sleep(30)

        # Mark as processed
        transaction.status = "PROCESSED"
        transaction.processed_at = datetime.now(timezone.utc)
        transaction.is_processing = False
        db.commit()

        logger.info(f"Successfully processed transaction {transaction_id}")

    except Exception as e:
        logger.error(f"Error processing transaction {transaction_id}: {str(e)}")
        transaction = db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()
        if transaction:
            transaction.status = "FAILED"
            transaction.error_message = str(e)
            transaction.is_processing = False
            db.commit()
    finally:
        db.close()


def start_background_task(transaction_id: str):
    """
    Create a background task for transaction processing.
    Uses asyncio to run without blocking the request.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(process_transaction(transaction_id))
    # Don't close the loop, it will continue running in the background
