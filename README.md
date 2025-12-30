# Transaction Webhook Service

A production-ready FastAPI service for handling payment transaction webhooks with immediate acknowledgment and asynchronous processing.

## 🚀 Getting Started

### Prerequisites
- Python 3.13.7 or compatible version
- pip package manager

### Installation & Setup

1. **Clone the repository** (if not already done)
   ```bash
   git clone https://github.com/grajrb/WalnutFolks-Backend.git
   cd backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the service**
   ```bash
   python main.py
   ```

   The service will start on `http://localhost:8000`
   
   You should see:
   ```
   INFO:     Started server process
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

## 🧪 Testing Instructions

### Option 1: Automated Test Suite (Local)
Run the comprehensive test suite that validates all functionality:

```bash
python test_service.py
```

**Tests included:**
- Health check endpoint verification
- Single webhook processing (202 response < 500ms)
- Duplicate webhook handling (idempotency)
- Background processing completion (30+ seconds)
- Performance under multiple requests

**Expected output:** All 5 tests should pass with timing metrics.

### Option 2: Interactive Demo (Local)
Run the interactive demonstration to see the service in action:

```bash
python demo.py
```

**Demo scenarios:**
1. Single webhook processing
2. Duplicate webhook prevention
3. Multiple different transactions
4. Transaction status queries
5. List all transactions

### Option 3: Test Live Service

**Using PowerShell (Recommended for Windows):**

```powershell
# 1. Health Check
Invoke-WebRequest "https://walnutfolks-backend.onrender.com/" | ConvertFrom-Json

# 2. Send webhook
$body = @{
    transaction_id = "txn_test_$(Get-Random)"
    amount = 100.50
    currency = "USD"
    status = "completed"
    customer_id = "cust_456"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "https://walnutfolks-backend.onrender.com/v1/webhooks/transactions" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body

$response.Content | ConvertFrom-Json

# 3. Wait 30 seconds for processing
Start-Sleep -Seconds 30

# 4. Check transaction status
Invoke-WebRequest "https://walnutfolks-backend.onrender.com/v1/transactions/txn_test_123" | ConvertFrom-Json

# 5. List all transactions
Invoke-WebRequest "https://walnutfolks-backend.onrender.com/v1/transactions" | ConvertFrom-Json
```

**Using curl (Any terminal):**

```bash
# 1. Health Check
curl https://walnutfolks-backend.onrender.com/

# 2. Send webhook (single line)
curl -X POST https://walnutfolks-backend.onrender.com/v1/webhooks/transactions -H "Content-Type: application/json" -d "{\"transaction_id\":\"txn_live_123\",\"amount\":100.50,\"currency\":\"USD\",\"status\":\"completed\",\"customer_id\":\"cust_456\",\"timestamp\":\"2025-12-30T10:00:00Z\"}"

# 3. Wait 30+ seconds then check status
curl https://walnutfolks-backend.onrender.com/v1/transactions/txn_live_123

# 4. List all transactions
curl https://walnutfolks-backend.onrender.com/v1/transactions
```

**Using Browser:**
- **Health Check:** https://walnutfolks-backend.onrender.com/
- **Interactive API Docs:** https://walnutfolks-backend.onrender.com/docs
- **Alternative Docs:** https://walnutfolks-backend.onrender.com/redoc

## 📊 API Endpoints

| Method | Endpoint | Description | Response Time |
|--------|----------|-------------|---------------|
| `GET` | `/` | Health check | < 5ms |
| `POST` | `/v1/webhooks/transactions` | Receive webhook | < 500ms (typically 16-76ms) |
| `GET` | `/v1/transactions/{id}` | Get transaction by ID | < 50ms |
| `GET` | `/v1/transactions` | List all transactions | < 100ms |

### Webhook Request Format
```json
{
  "transaction_id": "txn_unique_123",
  "amount": 100.50,
  "currency": "USD",
  "status": "completed",
  "customer_id": "cust_456",
  "timestamp": "2025-12-30T10:00:00Z"
}
```

### Webhook Response (202 Accepted)
```json
{
  "status": "accepted",
  "message": "Webhook received and queued for processing"
}
```

## 🏗️ Technical Choices

### Framework: FastAPI
**Why chosen:**
- High-performance async framework (one of the fastest Python frameworks available)
- Built-in request validation via Pydantic
- Automatic OpenAPI documentation
- Native async/await support for non-blocking operations
- Type hints for better code quality and IDE support

### Server: Uvicorn with standard extras
**Why chosen:**
- ASGI server optimized for async applications
- Fast response times (critical for < 500ms requirement)
- Production-ready with proper logging
- Standard extras include `uvloop` and `httptools` for enhanced performance

### Database: SQLAlchemy 2.0.35 + SQLite/PostgreSQL
**Why chosen:**
- **SQLAlchemy 2.0.35**: Specifically chosen for Python 3.13 compatibility (versions 2.0.36+ have breaking changes)
- ORM abstraction allows easy migration from SQLite (dev) to PostgreSQL (production)
- Proper transaction support for data consistency
- Database indexes on `transaction_id` for fast lookups (idempotency checks)
- Status field indexed for efficient filtering

### Background Processing: Threading + asyncio
**Why chosen:**
- **Threading**: Spawns background task without blocking webhook response (achieves < 500ms)
- **asyncio.sleep(30)**: Non-blocking delay that simulates processing without consuming CPU
- Allows service to continue handling new webhooks while processing others
- Proper error handling and status updates during processing

### Validation: Pydantic v2
**Why chosen:**
- Type-safe request/response validation
- Automatic error messages for invalid data
- Performance improvements in v2
- Seamless FastAPI integration

### Testing: httpx + async
**Why chosen:**
- Async HTTP client matching FastAPI's async nature
- Clean test syntax for API testing
- Production-like testing without mocking

### Architecture Decisions

1. **Immediate 202 Response Pattern**
   - Webhook endpoint returns immediately after validation and queuing
   - Meets < 500ms requirement (typically 16-76ms in tests)
   - Background thread handles 30-second processing asynchronously

2. **Idempotency via Database Constraints**
   - `transaction_id` is unique in database schema
   - Duplicate webhooks are rejected at database level
   - Safe even under concurrent requests

3. **Three-Status Lifecycle**
   - `pending`: Initial state when webhook received
   - `processing`: Status during 30-second background task
   - `processed`: Final state after completion
   - Allows clients to track progress via status API

4. **Error Handling Strategy**
   - Comprehensive try-catch blocks at all levels
   - Detailed logging for debugging
   - Graceful degradation (errors in background don't affect new webhooks)
   - HTTP exception handling with appropriate status codes

5. **Database Design**
   - Indexed fields (`transaction_id`, `status`) for fast queries
   - Timestamps for audit trail
   - Flexible schema supporting multiple currencies and statuses

## � Live Service

**Your service is now live on Render:**
```
🎉 https://walnutfolks-backend.onrender.com
```

### Quick Test
```bash
# Health check
curl https://walnutfolks-backend.onrender.com/

# Interactive API docs
https://walnutfolks-backend.onrender.com/docs
```

## 🐳 Deployment (Render)

Your service is already deployed on **Render** and live in production!

### Deployment Details
- **Platform:** [Render.com](https://render.com)
- **URL:** https://walnutfolks-backend.onrender.com
- **Auto-Deploy:** Connected to GitHub (pushes automatically redeploy)
- **Database:** SQLite (dev) / PostgreSQL (optional)

### How It's Deployed
1. GitHub repository connected to Render
2. Render auto-detects Dockerfile
3. Builds and deploys on every git push
4. Service is automatically restarted
5. Free tier available with some limitations

### Manual Redeployment (if needed)
```bash
# Push to GitHub to trigger auto-redeploy
git add .
git commit -m "Update message"
git push origin main
```

### Add PostgreSQL Database (Optional)
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "PostgreSQL"
3. Create database
4. Copy connection string
5. Add as environment variable: `DATABASE_URL=postgresql://...`
6. Redeploy service

---

## 🔧 Environment Variables

```bash
# Development (default)
DATABASE_URL=sqlite:///./transactions.db

# Production (PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

The service automatically switches from SQLite to PostgreSQL based on the `DATABASE_URL` environment variable.

## ✨ Features

- ✅ **Fast Response**: < 500ms acknowledgment (typically 16-76ms)
- ✅ **Async Processing**: 30-second background processing
- ✅ **Idempotent**: Duplicate webhooks automatically handled
- ✅ **Persistent Storage**: SQLite (dev) / PostgreSQL (prod)
- ✅ **Error Handling**: Comprehensive error logging
- ✅ **Production Ready**: Docker + health checks
- ✅ **Type Safe**: Full type hints and validation
- ✅ **Observable**: Detailed logging at every step

## 📈 Performance Metrics

From test results:
- **Initial Response**: 16-274ms (avg: 52-76ms) ✅ Well under 500ms requirement
- **Background Processing**: Exactly 30+ seconds as specified
- **Idempotency**: 100% duplicate prevention (3 webhooks → 1 transaction)
- **Reliability**: Zero errors in automated test suite

## 📝 Logging

The service logs all operations:
- Incoming webhook details
- Background task start/completion
- Database operations
- Errors and exceptions

View logs in the terminal where the service is running.

