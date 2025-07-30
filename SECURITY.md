# Security Configuration Guide

## Overview
This document outlines the security configuration for the Food & Fast e-commerce microservices platform.

## Environment Variables

### Critical Security Note
**NEVER commit `.env` files to version control!** All sensitive data is stored in environment variables.

### Setup Instructions

1. **Copy Example Files**
   ```bash
   cp .env.example .env
   cp .env.dev .env.dev  # for development
   ```

2. **Update Secret Values**
   Replace all placeholder values in `.env` files with secure, production-ready values:

   - `DATABASE_PASSWORD`: Use a strong database password (20+ characters)
   - `SECRET_KEY`: Generate using `openssl rand -hex 32`
   - `JWT_SECRET_KEY`: Generate using `openssl rand -hex 32`
   - `GRAFANA_ADMIN_PASSWORD`: Use a strong admin password
   - `SMTP_PASSWORD`: Use app-specific password for email service
   - `STRIPE_SECRET_KEY`: Production Stripe secret key
   - `MOMO_SECRET_KEY`: Production MoMo secret key
   - `TWILIO_AUTH_TOKEN`: Production Twilio auth token

### Service-Specific Environment Files

Each service has its own `.env` file:
- `api_gateway/.env` - API Gateway configuration
- `auth_service/.env` - Authentication service
- `user_service/.env` - User management service
- `product_service/.env` - Product catalog service
- `order_service/.env` - Order processing service
- `payment_service/.env` - Payment gateway integration
- `notification_service/.env` - Email/SMS notifications
- `analytics_service/.env` - Analytics and reporting

## CI/CD Security

### GitHub Secrets
Configure the following secrets in your GitHub repository:

1. **Authentication Secrets**
   - `AUTH_SECRET_KEY`: Auth service secret key
   - `JWT_SECRET_KEY`: JWT signing key
   - `API_GATEWAY_SECRET_KEY`: API Gateway secret key

2. **Database Secrets**
   - `DATABASE_PASSWORD`: Production database password

3. **External Service Secrets**
   - `STRIPE_SECRET_KEY`: Stripe payment processing
   - `TWILIO_AUTH_TOKEN`: SMS notifications
   - `SMTP_PASSWORD`: Email service password

### Docker Registry
Configure Docker registry credentials for image publishing:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD` or `GITHUB_TOKEN`

## Docker Compose Security

### Production Configuration
The `infrastructure/docker-compose.yml` file uses environment variables:

```yaml
environment:
  POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
  GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
```

### Development Configuration
Use `docker-compose.dev.yml` for development with `.env.dev`:

```bash
docker-compose -f docker-compose.dev.yml --env-file .env.dev up
```

## Security Best Practices

### 1. Password Policies
- Minimum 20 characters for production secrets
- Use combination of letters, numbers, and special characters
- Rotate secrets regularly (quarterly)

### 2. Database Security
- Use dedicated database users per service
- Enable SSL/TLS for database connections in production
- Regular security updates and patches

### 3. API Security
- All services use JWT authentication
- Rate limiting enabled on all endpoints
- CORS properly configured for frontend origins

### 4. Container Security
- Non-root users in all Docker containers
- Regular base image updates
- Security scanning in CI/CD pipeline

### 5. Network Security
- Services communicate through internal Docker network
- Only necessary ports exposed to host
- Load balancer/reverse proxy for production

## Security Monitoring

### Available Tools
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **CodeQL**: Code security analysis (GitHub)

### Health Checks
All services include health check endpoints:
- Database connectivity
- Redis connectivity
- External service availability

## Incident Response

### Security Issue Reporting
1. **DO NOT** commit sensitive data
2. **DO NOT** expose secrets in logs
3. Rotate compromised secrets immediately
4. Update all affected environments

### Emergency Procedures
1. Revoke compromised API keys immediately
2. Rotate database passwords
3. Update JWT secret keys (will invalidate all tokens)
4. Notify security team and stakeholders

## Compliance

### Data Protection
- GDPR compliance for EU users
- Data encryption at rest and in transit
- Audit logging for sensitive operations
- User consent management

### PCI DSS (Payment Processing)
- Tokenized payment data
- Secure payment gateway integration
- No storage of sensitive card data
- Regular security assessments

## Security Checklist

### Before Deployment
- [ ] All `.env` files updated with production values
- [ ] GitHub secrets configured correctly
- [ ] Database passwords rotated
- [ ] SSL/TLS certificates installed
- [ ] Security scanning completed
- [ ] Penetration testing performed
- [ ] Backup and recovery procedures tested

### Regular Maintenance
- [ ] Security patches applied monthly
- [ ] Dependency updates reviewed
- [ ] Access logs monitored
- [ ] Vulnerability scans performed
- [ ] Secret rotation quarterly
- [ ] Security training completed

## Contact

For security concerns or questions, contact:
- Security Team: security@foodfast.com
- DevOps Team: devops@foodfast.com

---

**Remember**: Security is everyone's responsibility. Always follow the principle of least privilege and never commit secrets to version control.