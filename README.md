# Transaction Webhook Service

A production-ready FastAPI service for handling payment transaction webhooks.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```

Service runs at: http://localhost:8000

## API Endpoints

- `GET /` - Health check
- `POST /v1/webhooks/transactions` - Receive webhook (returns 202 Accepted)
- `GET /v1/transactions/{id}` - Get transaction status
- `GET /v1/transactions` - List all transactions

## Testing

```bash
# Run automated tests
python test_service.py

# Run interactive demo
python demo.py
```

## Deployment

### Docker
```bash
docker-compose up
```

### Railway
Connect your GitHub repo to Railway - deploys automatically.

### Heroku
```bash
git push heroku main
```

## Environment Variables

```
DATABASE_URL=sqlite:///./transactions.db
```

For PostgreSQL: `postgresql://user:pass@host/db`

## Features

- ✅ Fast response (< 5ms)
- ✅ Async background processing (30s)
- ✅ Idempotent (no duplicates)
- ✅ Persistent storage
- ✅ Error handling & logging
