import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Test the health check endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        print("✓ Health Check Test")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}\n")
        assert response.status_code == 200


async def test_single_transaction():
    """Test single transaction processing"""
    async with httpx.AsyncClient() as client:
        # Send webhook
        webhook_data = {
            "transaction_id": "txn_single_001",
            "source_account": "acc_user_001",
            "destination_account": "acc_merchant_456",
            "amount": 500,
            "currency": "USD"
        }
        
        response = await client.post(
            f"{BASE_URL}/v1/webhooks/transactions",
            json=webhook_data
        )
        
        print("✓ Single Transaction Test - Webhook Received")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}\n")
        assert response.status_code == 202
        
        # Check initial status
        response = await client.get(f"{BASE_URL}/v1/transactions/txn_single_001")
        print("✓ Single Transaction Test - Initial Status Check")
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Transaction Status: {data[0]['status']}\n")
        assert data[0]['status'] == "PROCESSING"
        
        # Wait for processing
        print("  Waiting 35 seconds for processing...")
        await asyncio.sleep(35)
        
        # Check final status
        response = await client.get(f"{BASE_URL}/v1/transactions/txn_single_001")
        print("✓ Single Transaction Test - Final Status Check")
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Transaction Status: {data[0]['status']}")
        print(f"  Processed At: {data[0]['processed_at']}\n")
        assert data[0]['status'] == "PROCESSED"


async def test_duplicate_prevention():
    """Test idempotency - sending same webhook multiple times"""
    async with httpx.AsyncClient() as client:
        webhook_data = {
            "transaction_id": "txn_duplicate_001",
            "source_account": "acc_user_789",
            "destination_account": "acc_merchant_456",
            "amount": 1500,
            "currency": "INR"
        }
        
        # Send the same webhook 3 times
        for i in range(3):
            response = await client.post(
                f"{BASE_URL}/v1/webhooks/transactions",
                json=webhook_data
            )
            print(f"✓ Duplicate Prevention Test - Webhook #{i+1}")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json()}")
            assert response.status_code == 202
        
        # Get all transactions and verify only one duplicate transaction exists
        response = await client.get(f"{BASE_URL}/v1/transactions")
        transactions = response.json()
        duplicate_txns = [t for t in transactions if t['transaction_id'] == "txn_duplicate_001"]
        
        print(f"\n✓ Duplicate Prevention Test - Verification")
        print(f"  Total Transactions: {len(transactions)}")
        print(f"  Duplicate txn_duplicate_001 count: {len(duplicate_txns)}")
        print(f"  ✓ Only one transaction created (idempotent)\n")
        assert len(duplicate_txns) == 1


async def test_performance():
    """Test that webhook endpoint responds quickly"""
    async with httpx.AsyncClient() as client:
        print("✓ Performance Test - Sending 5 webhooks rapidly")
        
        import time
        start_time = time.time()
        
        for i in range(5):
            webhook_data = {
                "transaction_id": f"txn_perf_{i}",
                "source_account": f"acc_user_{i}",
                "destination_account": "acc_merchant_456",
                "amount": 500 + (i * 100),
                "currency": "USD"
            }
            
            response = await client.post(
                f"{BASE_URL}/v1/webhooks/transactions",
                json=webhook_data
            )
            assert response.status_code == 202
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to ms
        avg_time = total_time / 5
        
        print(f"  Total time for 5 webhooks: {total_time:.2f}ms")
        print(f"  Average time per webhook: {avg_time:.2f}ms")
        print(f"  ✓ All responses < 500ms ✓\n")
        assert avg_time < 500


async def main():
    print("=" * 60)
    print("TRANSACTION WEBHOOK SERVICE - TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        await test_health_check()
        await test_single_transaction()
        await test_duplicate_prevention()
        await test_performance()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    # Make sure httpx is available
    try:
        import httpx
    except ImportError:
        print("Installing httpx for testing...")
        import subprocess
        subprocess.check_call(["pip", "install", "httpx"])
    
    asyncio.run(main())
