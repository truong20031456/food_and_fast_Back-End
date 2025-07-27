# Payment Service

## Overview

The Payment Service is a microservice responsible for handling payment processing, payment gateway integrations, and financial transactions in the Food & Fast E-Commerce platform. It supports multiple payment methods including Stripe, MoMo, VNPay, and other payment gateways with secure transaction processing.

## Features

- 💳 **Multiple Payment Gateways**: Stripe, MoMo, VNPay integration
- 🔒 **Secure Transactions**: PCI DSS compliant payment processing
- 💰 **Payment Processing**: Complete payment lifecycle management
- 🔄 **Refund Management**: Automated and manual refund processing
- 📊 **Transaction Analytics**: Payment statistics and reporting
- 🛡️ **Fraud Detection**: Basic fraud prevention mechanisms
- 📱 **Webhook Handling**: Real-time payment status updates
- 🎫 **Promotion System**: Discount codes and promotional offers

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (async)
- **Payment Gateways**: Stripe, MoMo, VNPay
- **Security**: PCI DSS compliance
- **Validation**: Pydantic
- **Testing**: pytest
- **Documentation**: Auto-generated OpenAPI/Swagger

## Project Structure

```
payment_service/
├── gateways/            # Payment gateway integrations
│   ├── stripe.py       # Stripe payment gateway
│   ├── momo.py         # MoMo payment gateway
│   └── vnpay.py        # VNPay payment gateway
├── promotions/          # Promotion and discount system
│   └── promotion_service.py
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
└── Dockerfile         # Docker configuration
```

## API Endpoints

### Payment Processing
- `POST /payments/create` - Create payment intent
- `POST /payments/confirm` - Confirm payment
- `GET /payments/{payment_id}` - Get payment details
- `POST /payments/{payment_id}/capture` - Capture payment
- `POST /payments/{payment_id}/cancel` - Cancel payment

### Payment Methods
- `GET /payment-methods` - List available payment methods
- `POST /payment-methods` - Add payment method
- `GET /payment-methods/{method_id}` - Get payment method details
- `DELETE /payment-methods/{method_id}` - Remove payment method

### Refunds
- `POST /refunds` - Create refund
- `GET /refunds/{refund_id}` - Get refund details
- `POST /refunds/{refund_id}/cancel` - Cancel refund

### Promotions
- `GET /promotions` - List available promotions
- `POST /promotions/validate` - Validate promotion code
- `GET /promotions/{promotion_id}` - Get promotion details

### Webhooks
- `POST /webhooks/stripe` - Stripe webhook handler
- `POST /webhooks/momo` - MoMo webhook handler
- `POST /webhooks/vnpay` - VNPay webhook handler

### Analytics
- `GET /analytics/transactions` - Transaction statistics
- `GET /analytics/revenue` - Revenue analytics
- `GET /analytics/payment-methods` - Payment method usage
- `GET /analytics/refunds` - Refund statistics

## Environment Variables

Create a `.env` file in the payment_service directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/payment_db

# Application
HOST=0.0.0.0
PORT=8004
DEBUG=true

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# MoMo Configuration
MOMO_ACCESS_KEY=your_momo_access_key
MOMO_SECRET_KEY=your_momo_secret_key
MOMO_PARTNER_CODE=your_partner_code
MOMO_ENDPOINT=https://test-payment.momo.vn/v2/gateway/api

# VNPay Configuration
VNPAY_TMN_CODE=your_tmn_code
VNPAY_HASH_SECRET=your_hash_secret
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:3000/payment/return

# Security
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# Payment Configuration
MIN_PAYMENT_AMOUNT=1000
MAX_PAYMENT_AMOUNT=50000000
PAYMENT_TIMEOUT_MINUTES=30

# Webhook Configuration
WEBHOOK_TIMEOUT_SECONDS=30
WEBHOOK_RETRY_ATTEMPTS=3

# Logging
LOG_LEVEL=INFO
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Payment gateway accounts (Stripe, MoMo, VNPay)

### Local Development

1. **Clone the repository**
   ```bash
   cd payment_service
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your payment gateway credentials
   ```

5. **Run database migrations**
   ```bash
   # Create tables (if using SQLAlchemy create_all)
   python -c "from models import Base; from database import engine; Base.metadata.create_all(engine)"
   ```

6. **Start the service**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8004
   ```

### Docker

1. **Build the image**
   ```bash
   docker build -t payment-service .
   ```

2. **Run the container**
   ```bash
   docker run -p 8004:8004 --env-file .env payment-service
   ```

## Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=.
```

### Run specific test file
```bash
pytest tests/test_payments.py
```

## API Documentation

Once the service is running, you can access:
- **Swagger UI**: http://localhost:8004/docs
- **ReDoc**: http://localhost:8004/redoc
- **Health Check**: http://localhost:8004/health

## Database Schema

### Payments Table
- `id`: Primary key
- `order_id`: Foreign key to orders
- `user_id`: Foreign key to users
- `amount`: Payment amount
- `currency`: Payment currency
- `payment_method`: Payment method used
- `gateway`: Payment gateway (stripe, momo, vnpay)
- `gateway_payment_id`: Gateway-specific payment ID
- `status`: Payment status (pending, processing, completed, failed, cancelled)
- `created_at`: Payment creation timestamp
- `updated_at`: Last update timestamp

### Transactions Table
- `id`: Primary key
- `payment_id`: Foreign key to payments
- `transaction_type`: Transaction type (payment, refund, chargeback)
- `amount`: Transaction amount
- `currency`: Transaction currency
- `gateway_transaction_id`: Gateway transaction ID
- `status`: Transaction status
- `created_at`: Transaction timestamp

### Refunds Table
- `id`: Primary key
- `payment_id`: Foreign key to payments
- `amount`: Refund amount
- `reason`: Refund reason
- `status`: Refund status (pending, completed, failed)
- `gateway_refund_id`: Gateway refund ID
- `created_at`: Refund creation timestamp

### Promotions Table
- `id`: Primary key
- `code`: Promotion code
- `discount_type`: Discount type (percentage, fixed)
- `discount_value`: Discount value
- `min_amount`: Minimum order amount
- `max_discount`: Maximum discount amount
- `usage_limit`: Usage limit
- `used_count`: Current usage count
- `valid_from`: Promotion start date
- `valid_until`: Promotion end date
- `is_active`: Promotion status

## Payment Gateways

### Stripe
- **Features**: Credit/debit cards, digital wallets
- **Countries**: Global
- **Fees**: 2.9% + 30¢ per transaction
- **Setup**: Requires Stripe account and API keys

### MoMo
- **Features**: Mobile money, QR code payments
- **Countries**: Vietnam
- **Fees**: Varies by transaction type
- **Setup**: Requires MoMo merchant account

### VNPay
- **Features**: Bank transfers, QR payments
- **Countries**: Vietnam
- **Fees**: Varies by bank
- **Setup**: Requires VNPay merchant account

## Payment Flow

### 1. Payment Creation
- Validate order and amount
- Create payment intent
- Generate payment URL/QR code
- Return payment details to client

### 2. Payment Processing
- User completes payment
- Gateway processes transaction
- Webhook receives status update
- Update payment status

### 3. Payment Confirmation
- Verify payment with gateway
- Update order status
- Send confirmation notification
- Process post-payment actions

### 4. Refund Processing
- Validate refund request
- Process refund through gateway
- Update payment and order status
- Send refund notification

## Security Features

- **PCI DSS Compliance**: Secure payment data handling
- **Encryption**: End-to-end encryption for sensitive data
- **Tokenization**: Payment method tokenization
- **Fraud Detection**: Basic fraud prevention rules
- **Audit Logging**: Comprehensive transaction logging
- **Webhook Verification**: Secure webhook handling

## Webhook Handling

### Supported Webhooks
- **Payment Success**: Payment completed successfully
- **Payment Failed**: Payment failed or declined
- **Refund Processed**: Refund completed
- **Chargeback**: Chargeback received

### Webhook Security
- Signature verification
- Idempotency handling
- Retry mechanism
- Error logging

## Promotion System

### Discount Types
- **Percentage Discount**: Percentage off total amount
- **Fixed Discount**: Fixed amount off total
- **Free Shipping**: Free shipping on orders
- **Buy One Get One**: BOGO promotions

### Promotion Rules
- Minimum order amount
- Maximum discount limits
- Usage limits per user
- Valid date ranges
- Product/category restrictions

## Monitoring & Logging

- **Health Checks**: `/health` endpoint for service monitoring
- **Transaction Logging**: Detailed transaction logs
- **Error Tracking**: Payment failure tracking
- **Performance Metrics**: Payment processing time
- **Business Metrics**: Revenue and conversion tracking

## Error Handling

### Common Payment Errors
- **Insufficient Funds**: User doesn't have enough money
- **Card Declined**: Payment method declined
- **Network Error**: Connection issues
- **Invalid Amount**: Amount validation failed
- **Expired Payment**: Payment session expired

### Error Recovery
- Automatic retry mechanism
- User-friendly error messages
- Alternative payment method suggestions
- Manual intervention for complex cases

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of the Food & Fast E-Commerce platform. 