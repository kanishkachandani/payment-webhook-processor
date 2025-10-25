# Payment Webhook Processor

A high-performance, production-ready webhook processor for payment transactions built with FastAPI and Supabase.

## 🚀 Features

- **Fast Response**: All webhook requests return `202 Accepted` in <500ms
- **Background Processing**: 30-second transaction processing simulation
- **Idempotency**: Duplicate webhooks are handled gracefully without reprocessing
- **Persistent Storage**: All transactions stored in Supabase PostgreSQL
- **Error Handling**: Robust error handling and logging
- **RESTful API**: Clean API design with health checks and status queries

## 📋 API Endpoints

### Health Check
```bash
GET /
```
Returns service health status and current time.

### Receive Webhook
```bash
POST /v1/webhooks/transactions
```
Accepts transaction webhooks and returns 202 immediately.

**Request Body:**
```json
{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500,
  "currency": "INR"
}
```

### Query Transaction Status
```bash
GET /v1/transactions/{transaction_id}
```
Retrieves transaction status and details.

**Response:**
```json
{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500.0,
  "currency": "INR",
  "status": "PROCESSED",
  "created_at": "2024-01-15T10:30:00Z",
  "processed_at": "2024-01-15T10:30:30Z"
}
```

## 🛠️ Technical Choices

### Framework: FastAPI
- **Why**: Modern, fast, async-first Python framework
- **Benefits**:
  - Built-in async support for background tasks
  - Automatic API documentation (Swagger UI)
  - Fast performance with async I/O
  - Type validation with Pydantic

### Database: Supabase (PostgreSQL)
- **Why**: Managed PostgreSQL with real-time capabilities
- **Benefits**:
  - Cloud-hosted, production-ready
  - Easy to scale
  - Built-in REST API
  - Free tier available

### Background Processing: FastAPI BackgroundTasks
- **Why**: Simple, built-in async background task execution
- **Benefits**:
  - No additional infrastructure needed
  - Perfect for medium-load scenarios
  - Async/await support
  - Clean integration with FastAPI

### Alternative Considered
For high-scale production (>10k webhooks/minute), consider:
- **Celery + Redis**: Distributed task queue for horizontal scaling
- **AWS SQS/Lambda**: Serverless event-driven architecture

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- Supabase account

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd payment-webhook-processor
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Supabase

1. Create a Supabase project at https://supabase.com
2. Go to SQL Editor and run:

```sql
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    source_account TEXT NOT NULL,
    destination_account TEXT NOT NULL,
    amount FLOAT NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PROCESSING',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
```

### 5. Configure Environment Variables

Create a `.env` file:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 6. Run the Application
```bash
uvicorn main:app --reload
```

Server will start at `http://localhost:8000`

## 🧪 Testing

### Run Automated Tests
```bash
python test_criteria.py
```

This comprehensive test suite validates:
- ✅ Single transaction processing (~30s delay)
- ✅ Duplicate prevention (idempotency)
- ✅ Performance (<500ms response time)
- ✅ Error handling & reliability

### Manual Testing

**1. Send a webhook:**
```bash
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_test_123",
    "source_account": "acc_user_001",
    "destination_account": "acc_merchant_001",
    "amount": 1500,
    "currency": "INR"
  }'
```

**2. Check status immediately:**
```bash
curl http://localhost:8000/v1/transactions/txn_test_123
```

**3. Wait 30 seconds and check again:**
```bash
sleep 30
curl http://localhost:8000/v1/transactions/txn_test_123
```

## 🌐 Deployment

### Render.com (Recommended)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
5. Deploy!

### Alternative Platforms
- **Railway**: `railway up`
- **Fly.io**: `fly launch`
- **Heroku**: Use `Procfile`

## 📊 Success Criteria ✅

| Criterion | Status | Details |
|-----------|--------|---------|
| Single Transaction | ✅ | Webhook processed after ~30 seconds |
| Duplicate Prevention | ✅ | Same webhook handled without reprocessing |
| Performance | ✅ | All responses <500ms |
| Reliability | ✅ | Errors handled gracefully, no data loss |

## 🏗️ Architecture

```
Webhook Request → FastAPI Endpoint (202 Response <500ms)
                       ↓
                 Insert to Supabase (PROCESSING)
                       ↓
                 Background Task Queue
                       ↓
                 30-second delay (simulated processing)
                       ↓
                 Update to Supabase (PROCESSED)
```

## 📝 License

MIT License

## 👤 Author

Built for payment webhook processing assessment.

---

**Live API**: [Your deployed URL will go here]
# payment-webhook-processor