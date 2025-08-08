#!/usr/bin/env python3
"""
Script kiểm tra tương tác giữa 8 services trong hệ thống Food Fast E-commerce
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cấu hình services
SERVICES = {
    "api_gateway": {"port": 8000, "name": "API Gateway"},
    "auth_service": {"port": 8001, "name": "Authentication Service"},
    "user_service": {"port": 8002, "name": "User Service"},
    "product_service": {"port": 8003, "name": "Product Service"},
    "order_service": {"port": 8004, "name": "Order Service"},
    "payment_service": {"port": 8005, "name": "Payment Service"},
    "notification_service": {"port": 8006, "name": "Notification Service"},
    "analytics_service": {"port": 8007, "name": "Analytics Service"},
}

BASE_URL = "http://localhost"


class ServiceInteractionChecker:
    """Kiểm tra tương tác giữa các services"""
    
    def __init__(self):
        self.test_results = []
        self.service_status = {}
        self.auth_token = None
        self.test_user_id = None
        self.test_order_id = None

    async def check_service_health(self, service_name: str, port: int) -> bool:
        """Kiểm tra health của một service"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{BASE_URL}:{port}/health")
                is_healthy = response.status_code == 200
                
                health_data = {}
                if is_healthy:
                    try:
                        health_data = response.json()
                    except:
                        health_data = {"status": "healthy"}
                
                self.service_status[service_name] = {
                    "healthy": is_healthy,
                    "response_time": response.elapsed.total_seconds(),
                    "data": health_data
                }
                
                return is_healthy
        except Exception as e:
            self.service_status[service_name] = {
                "healthy": False,
                "error": str(e),
                "response_time": None
            }
            return False

    async def check_all_services_health(self) -> Dict[str, bool]:
        """Kiểm tra health của tất cả services"""
        logger.info("🏥 Kiểm tra trạng thái health của tất cả services...")
        
        tasks = []
        for service_name, config in SERVICES.items():
            task = self.check_service_health(service_name, config["port"])
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # In kết quả
        for i, (service_name, config) in enumerate(SERVICES.items()):
            status = self.service_status.get(service_name, {})
            if status.get("healthy", False):
                logger.info(f"✅ {config['name']} (port {config['port']}) - Healthy "
                          f"(Response: {status.get('response_time', 0):.3f}s)")
            else:
                logger.error(f"❌ {config['name']} (port {config['port']}) - Unhealthy "
                           f"(Error: {status.get('error', 'Unknown')})")
        
        return self.service_status

    async def test_api_gateway_routing(self) -> bool:
        """Kiểm tra API Gateway routing đến các services"""
        logger.info("🌐 Kiểm tra API Gateway routing...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Kiểm tra API Gateway services list
                response = await client.get(f"{BASE_URL}:8000/services")
                
                if response.status_code == 200:
                    services_data = response.json()
                    logger.info(f"✅ API Gateway routing configured for services: {list(services_data.get('services', []))}")
                    
                    # Kiểm tra health check từ gateway
                    health_response = await client.get(f"{BASE_URL}:8000/services/health")
                    if health_response.status_code == 200:
                        health_data = health_response.json()
                        logger.info(f"✅ API Gateway health check: {health_data.get('status', 'unknown')}")
                        
                        # In trạng thái của từng service qua gateway
                        services_health = health_data.get('services', {})
                        for service, is_healthy in services_health.items():
                            status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
                            logger.info(f"   - {service}: {status}")
                    
                    return True
                else:
                    logger.error(f"❌ API Gateway services endpoint failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ API Gateway routing check failed: {str(e)}")
            return False

    async def test_auth_flow(self) -> bool:
        """Kiểm tra authentication flow"""
        logger.info("🔐 Kiểm tra authentication flow...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test user data
                test_user = {
                    "email": f"test_{int(time.time())}@foodfast.com",
                    "username": f"testuser_{int(time.time())}",
                    "full_name": "Test User",
                    "password": "SecureTestPassword123!"
                }
                
                # 1. Register thông qua API Gateway
                register_response = await client.post(
                    f"{BASE_URL}:8000/auth/register",
                    json=test_user
                )
                
                if register_response.status_code in [200, 201]:
                    user_data = register_response.json()
                    self.test_user_id = user_data.get("id")
                    logger.info("✅ User registration successful via API Gateway")
                    
                    # 2. Login thông qua API Gateway
                    login_response = await client.post(
                        f"{BASE_URL}:8000/auth/login",
                        json={
                            "email": test_user["email"],
                            "password": test_user["password"]
                        }
                    )
                    
                    if login_response.status_code == 200:
                        login_data = login_response.json()
                        self.auth_token = login_data.get("access_token")
                        logger.info("✅ User login successful via API Gateway")
                        
                        # 3. Verify token bằng cách truy cập protected endpoint
                        headers = {"Authorization": f"Bearer {self.auth_token}"}
                        profile_response = await client.get(
                            f"{BASE_URL}:8000/users/me",
                            headers=headers
                        )
                        
                        if profile_response.status_code == 200:
                            logger.info("✅ Token verification successful via API Gateway")
                            return True
                        else:
                            logger.error(f"❌ Token verification failed: {profile_response.status_code}")
                    else:
                        logger.error(f"❌ Login failed: {login_response.status_code}")
                else:
                    logger.error(f"❌ Registration failed: {register_response.status_code}")
                    
                return False
                
        except Exception as e:
            logger.error(f"❌ Auth flow test failed: {str(e)}")
            return False

    async def test_product_service_interaction(self) -> bool:
        """Kiểm tra tương tác với Product Service"""
        logger.info("🍕 Kiểm tra Product Service interaction...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Lấy danh sách sản phẩm (public endpoint)
                products_response = await client.get(f"{BASE_URL}:8000/products?limit=5")
                
                if products_response.status_code == 200:
                    products = products_response.json()
                    logger.info(f"✅ Retrieved {len(products)} products via API Gateway")
                    
                    # 2. Lấy categories
                    categories_response = await client.get(f"{BASE_URL}:8000/products/categories")
                    
                    if categories_response.status_code == 200:
                        categories = categories_response.json()
                        logger.info(f"✅ Retrieved {len(categories)} categories via API Gateway")
                        
                        # 3. Search products
                        search_response = await client.get(f"{BASE_URL}:8000/products/search?q=pizza")
                        
                        if search_response.status_code == 200:
                            search_results = search_response.json()
                            logger.info(f"✅ Search returned {len(search_results)} results via API Gateway")
                            return True
                        else:
                            logger.warning(f"⚠️ Product search failed: {search_response.status_code}")
                    else:
                        logger.warning(f"⚠️ Categories fetch failed: {categories_response.status_code}")
                else:
                    logger.error(f"❌ Products fetch failed: {products_response.status_code}")
                    
                return False
                
        except Exception as e:
            logger.error(f"❌ Product service interaction failed: {str(e)}")
            return False

    async def test_order_flow(self) -> bool:
        """Kiểm tra order flow với multiple services"""
        logger.info("📦 Kiểm tra Order flow với multiple services...")
        
        if not self.auth_token:
            logger.error("❌ Auth token required for order flow")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Tạo order
                order_data = {
                    "user_id": self.test_user_id,
                    "restaurant_id": 1,
                    "items": [
                        {
                            "product_id": 1,
                            "product_name": "Test Pizza",
                            "price": 25.99,
                            "quantity": 2
                        }
                    ],
                    "delivery_address": "123 Test Street, Test City",
                    "phone_number": "+1234567890",
                    "delivery_fee": 3.99,
                    "tax_amount": 4.15
                }
                
                order_response = await client.post(
                    f"{BASE_URL}:8000/orders",
                    json=order_data,
                    headers=headers
                )
                
                if order_response.status_code in [200, 201]:
                    order = order_response.json()
                    self.test_order_id = order.get("id")
                    logger.info(f"✅ Order created successfully: {order.get('order_number')}")
                    
                    # 2. Kiểm tra order status
                    status_response = await client.get(
                        f"{BASE_URL}:8000/orders/{self.test_order_id}",
                        headers=headers
                    )
                    
                    if status_response.status_code == 200:
                        logger.info("✅ Order status retrieved successfully")
                        return True
                    else:
                        logger.error(f"❌ Order status check failed: {status_response.status_code}")
                else:
                    logger.error(f"❌ Order creation failed: {order_response.status_code}")
                    
                return False
                
        except Exception as e:
            logger.error(f"❌ Order flow test failed: {str(e)}")
            return False

    async def test_payment_integration(self) -> bool:
        """Kiểm tra Payment Service integration"""
        logger.info("💳 Kiểm tra Payment Service integration...")
        
        if not self.auth_token or not self.test_order_id:
            logger.error("❌ Auth token and order ID required for payment flow")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Tạo payment intent
                payment_data = {
                    "order_id": self.test_order_id,
                    "amount": 51.98,  # 2 * 25.99
                    "currency": "usd",
                    "payment_method": "stripe"
                }
                
                payment_response = await client.post(
                    f"{BASE_URL}:8000/payments/create-intent",
                    json=payment_data,
                    headers=headers
                )
                
                if payment_response.status_code in [200, 201]:
                    payment_intent = payment_response.json()
                    logger.info(f"✅ Payment intent created: {payment_intent.get('payment_intent_id', 'N/A')}")
                    return True
                else:
                    logger.warning(f"⚠️ Payment intent creation failed: {payment_response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Payment integration test failed: {str(e)}")
            return False

    async def test_notification_integration(self) -> bool:
        """Kiểm tra Notification Service integration"""
        logger.info("📬 Kiểm tra Notification Service integration...")
        
        if not self.auth_token:
            logger.error("❌ Auth token required for notification test")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Gửi test notification
                notification_data = {
                    "user_id": self.test_user_id,
                    "order_id": self.test_order_id,
                    "order_data": {
                        "order_number": "TEST-ORDER-001",
                        "total_amount": 51.98
                    }
                }
                
                notification_response = await client.post(
                    f"{BASE_URL}:8000/notifications/order-confirmation",
                    json=notification_data,
                    headers=headers
                )
                
                if notification_response.status_code in [200, 201]:
                    logger.info("✅ Notification sent successfully")
                    return True
                else:
                    logger.warning(f"⚠️ Notification sending failed: {notification_response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Notification integration test failed: {str(e)}")
            return False

    async def test_analytics_integration(self) -> bool:
        """Kiểm tra Analytics Service integration"""
        logger.info("📊 Kiểm tra Analytics Service integration...")
        
        if not self.auth_token:
            logger.error("❌ Auth token required for analytics test")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Gửi analytics event
                analytics_data = {
                    "event_type": "order_created",
                    "user_id": self.test_user_id,
                    "order_id": self.test_order_id,
                    "data": {
                        "total_amount": 51.98,
                        "item_count": 2,
                        "restaurant_id": 1
                    }
                }
                
                analytics_response = await client.post(
                    f"{BASE_URL}:8000/analytics/events",
                    json=analytics_data,
                    headers=headers
                )
                
                if analytics_response.status_code in [200, 201]:
                    logger.info("✅ Analytics event recorded successfully")
                    
                    # 2. Lấy analytics data
                    stats_response = await client.get(
                        f"{BASE_URL}:8000/analytics/dashboard",
                        headers=headers
                    )
                    
                    if stats_response.status_code == 200:
                        logger.info("✅ Analytics dashboard data retrieved")
                        return True
                    else:
                        logger.warning(f"⚠️ Analytics dashboard failed: {stats_response.status_code}")
                else:
                    logger.warning(f"⚠️ Analytics event recording failed: {analytics_response.status_code}")
                    
                return False
                
        except Exception as e:
            logger.error(f"❌ Analytics integration test failed: {str(e)}")
            return False

    async def run_complete_test_suite(self):
        """Chạy tất cả các test"""
        logger.info("🚀 Bắt đầu kiểm tra tương tác giữa 8 services...")
        start_time = time.time()
        
        # 1. Kiểm tra health của tất cả services
        health_results = await self.check_all_services_health()
        healthy_services = sum(1 for status in health_results.values() if status.get("healthy", False))
        logger.info(f"📊 Services healthy: {healthy_services}/{len(SERVICES)}")
        
        if healthy_services < len(SERVICES):
            logger.warning("⚠️ Một số services không hoạt động, tiếp tục test với services khả dụng...")
        
        # 2. Kiểm tra API Gateway routing
        gateway_ok = await self.test_api_gateway_routing()
        
        # 3. Kiểm tra authentication flow
        auth_ok = await self.test_auth_flow()
        
        # 4. Kiểm tra product service
        product_ok = await self.test_product_service_interaction()
        
        # 5. Kiểm tra order flow
        order_ok = await self.test_order_flow()
        
        # 6. Kiểm tra payment integration
        payment_ok = await self.test_payment_integration()
        
        # 7. Kiểm tra notification integration
        notification_ok = await self.test_notification_integration()
        
        # 8. Kiểm tra analytics integration
        analytics_ok = await self.test_analytics_integration()
        
        # Tổng kết
        total_time = time.time() - start_time
        
        test_results = {
            "services_health": health_results,
            "api_gateway_routing": gateway_ok,
            "authentication_flow": auth_ok,
            "product_service": product_ok,
            "order_flow": order_ok,
            "payment_integration": payment_ok,
            "notification_integration": notification_ok,
            "analytics_integration": analytics_ok,
            "total_test_time": f"{total_time:.2f}s"
        }
        
        logger.info("\n" + "="*80)
        logger.info("📋 KẾT QUẢ KIỂM TRA TƯƠNG TÁC GIỮA 8 SERVICES")
        logger.info("="*80)
        
        # Services Health
        logger.info(f"🏥 Services Health ({healthy_services}/{len(SERVICES)} healthy):")
        for service_name, config in SERVICES.items():
            status = health_results.get(service_name, {})
            if status.get("healthy", False):
                logger.info(f"   ✅ {config['name']}")
            else:
                logger.info(f"   ❌ {config['name']} - {status.get('error', 'Unknown error')}")
        
        # Test Results
        logger.info(f"\n🧪 Integration Tests:")
        tests = [
            ("API Gateway Routing", gateway_ok),
            ("Authentication Flow", auth_ok),
            ("Product Service", product_ok),
            ("Order Flow", order_ok),
            ("Payment Integration", payment_ok),
            ("Notification Integration", notification_ok),
            ("Analytics Integration", analytics_ok),
        ]
        
        passed_tests = 0
        for test_name, result in tests:
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"   {status} {test_name}")
            if result:
                passed_tests += 1
        
        logger.info(f"\n📊 Tổng kết: {passed_tests}/{len(tests)} tests passed")
        logger.info(f"⏱️ Thời gian test: {total_time:.2f} seconds")
        logger.info("="*80)
        
        return test_results


async def main():
    """Main function"""
    checker = ServiceInteractionChecker()
    await checker.run_complete_test_suite()


if __name__ == "__main__":
    asyncio.run(main())
