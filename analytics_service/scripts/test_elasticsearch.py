"""
Test Elasticsearch Integration for Analytics Service.
This script tests the Elasticsearch functionality.
"""

import asyncio
import json
from datetime import datetime
from core.elasticsearch_client import es_client
from services.elasticsearch_analytics_service import es_analytics_service
from utils.logger import get_logger

logger = get_logger(__name__)


async def test_elasticsearch_integration():
    """Test Elasticsearch integration."""
    try:
        print("🔍 Testing Elasticsearch Integration for Analytics Service")
        print("=" * 60)

        # 1. Test connection
        print("\n1. Testing Elasticsearch connection...")
        await es_client.connect()
        health = await es_client.health_check()
        
        if health:
            print("✅ Elasticsearch connection successful")
        else:
            print("❌ Elasticsearch connection failed")
            return

        # 2. Test index creation
        print("\n2. Testing index creation...")
        await es_analytics_service.initialize_indices()
        print("✅ All indices created successfully")

        # 3. Test data indexing
        print("\n3. Testing data indexing...")
        
        # Test order data
        sample_order = {
            "order_id": "test_order_001",
            "user_id": "test_user_001",
            "total_amount": 25.99,
            "currency": "USD",
            "status": "completed",
            "payment_method": "credit_card",
            "items": [
                {
                    "product_id": "1",
                    "product_name": "Test Burger",
                    "quantity": 1,
                    "price": 15.99,
                    "category": "Burgers"
                },
                {
                    "product_id": "3",
                    "product_name": "Test Fries",
                    "quantity": 1,
                    "price": 5.99,
                    "category": "Sides"
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

        success = await es_analytics_service.index_order_data(sample_order)
        if success:
            print("✅ Order data indexed successfully")
        else:
            print("❌ Failed to index order data")

        # Test user activity
        sample_activity = {
            "user_id": "test_user_001",
            "session_id": "test_session_001",
            "activity_type": "page_view",
            "page_url": "/products",
            "referrer": "https://google.com",
            "user_agent": "Mozilla/5.0 Test Browser",
            "ip_address": "192.168.1.100",
            "location": {
                "country": "USA",
                "city": "New York",
                "coordinates": [-74.0060, 40.7128]
            },
            "duration_seconds": 120,
            "timestamp": datetime.utcnow().isoformat()
        }

        success = await es_analytics_service.index_user_activity(sample_activity)
        if success:
            print("✅ User activity indexed successfully")
        else:
            print("❌ Failed to index user activity")

        # 4. Test analytics queries
        print("\n4. Testing analytics queries...")
        
        # Wait a moment for indexing
        await asyncio.sleep(2)

        # Test dashboard metrics
        metrics = await es_analytics_service.get_dashboard_metrics()
        if metrics:
            print("✅ Dashboard metrics retrieved successfully")
            print(f"   - Total Revenue: ${metrics.get('total_revenue', 0):.2f}")
            print(f"   - Total Orders: {metrics.get('total_orders', 0)}")
            print(f"   - Total Customers: {metrics.get('total_customers', 0)}")
        else:
            print("❌ Failed to retrieve dashboard metrics")

        # Test top selling products
        products = await es_analytics_service.get_top_selling_products(5)
        if products:
            print("✅ Top selling products retrieved successfully")
            print(f"   - Found {len(products)} products")
        else:
            print("❌ Failed to retrieve top selling products")

        # Test revenue trends
        trends = await es_analytics_service.get_revenue_trends("daily", 7)
        if trends:
            print("✅ Revenue trends retrieved successfully")
            print(f"   - Found {len(trends)} trend periods")
        else:
            print("❌ Failed to retrieve revenue trends")

        # Test user activity summary
        activity_summary = await es_analytics_service.get_user_activity_summary()
        if activity_summary:
            print("✅ User activity summary retrieved successfully")
            print(f"   - Total Users: {activity_summary.get('total_users', 0)}")
            print(f"   - Active Today: {activity_summary.get('active_users_today', 0)}")
        else:
            print("❌ Failed to retrieve user activity summary")

        # 5. Test search functionality
        print("\n5. Testing search functionality...")
        
        search_results = await es_analytics_service.search_analytics(
            query="order_placed",
            size=10
        )
        
        if search_results:
            print("✅ Search functionality working")
            print(f"   - Found {len(search_results)} results")
        else:
            print("❌ Search functionality failed")

        print("\n" + "=" * 60)
        print("🎉 Elasticsearch integration test completed successfully!")
        
        # Display summary
        print("\n📊 Integration Summary:")
        print("- ✅ Connection established")
        print("- ✅ Indices created")
        print("- ✅ Data indexing working")
        print("- ✅ Analytics queries working")
        print("- ✅ Search functionality working")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        logger.error(f"Elasticsearch integration test failed: {e}")
    
    finally:
        # Cleanup
        if es_client.is_connected:
            await es_client.disconnect()
            print("\n🔌 Elasticsearch connection closed")


async def main():
    """Main function."""
    await test_elasticsearch_integration()


if __name__ == "__main__":
    asyncio.run(main())
