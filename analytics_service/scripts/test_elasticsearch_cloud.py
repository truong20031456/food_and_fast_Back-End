"""
Test Elasticsearch Cloud Connection.
This script specifically tests connection to Google Cloud Elasticsearch.
"""

import asyncio
import os
from core.elasticsearch_client import es_client
from core.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


async def test_cloud_connection():
    """Test connection to Elasticsearch cloud."""
    try:
        print("🔗 Testing Elasticsearch Cloud Connection")
        print("=" * 50)
        
        # Display configuration (hide sensitive data)
        print(f"Host: {settings.elasticsearch.host}")
        print(f"Port: {settings.elasticsearch.port}")
        print(f"Scheme: {settings.elasticsearch.scheme}")
        print(f"Verify Certs: {settings.elasticsearch.verify_certs}")
        
        if settings.elasticsearch.api_key:
            print(f"API Key: {'*' * 20}...{settings.elasticsearch.api_key[-4:]}")
        elif settings.elasticsearch.username:
            print(f"Username: {settings.elasticsearch.username}")
            print(f"Password: {'*' * len(settings.elasticsearch.password or '')}")
        
        print("\n1. Attempting to connect...")
        
        # Test connection
        await es_client.connect()
        print("✅ Connection established successfully!")
        
        # Test cluster health
        print("\n2. Checking cluster health...")
        if es_client.client:
            try:
                health = await es_client.client.cluster.health()
                print("✅ Cluster health check successful!")
                print(f"   - Cluster Name: {health.get('cluster_name', 'Unknown')}")
                print(f"   - Status: {health.get('status', 'Unknown')}")
                print(f"   - Number of Nodes: {health.get('number_of_nodes', 0)}")
                print(f"   - Number of Data Nodes: {health.get('number_of_data_nodes', 0)}")
                print(f"   - Active Primary Shards: {health.get('active_primary_shards', 0)}")
                print(f"   - Active Shards: {health.get('active_shards', 0)}")
            except Exception as e:
                print(f"❌ Cluster health check failed: {e}")
        
        # Test cluster info
        print("\n3. Getting cluster info...")
        try:
            info = await es_client.client.info()
            print("✅ Cluster info retrieved successfully!")
            print(f"   - Version: {info.get('version', {}).get('number', 'Unknown')}")
            print(f"   - Build: {info.get('version', {}).get('build_hash', 'Unknown')[:8]}")
            print(f"   - Lucene Version: {info.get('version', {}).get('lucene_version', 'Unknown')}")
        except Exception as e:
            print(f"❌ Failed to get cluster info: {e}")
        
        # Test index operations
        print("\n4. Testing index operations...")
        test_index = "test_connection_index"
        
        try:
            # Create a test index
            mapping = {
                "properties": {
                    "message": {"type": "text"},
                    "timestamp": {"type": "date"}
                }
            }
            
            success = await es_client.create_index(test_index, mapping)
            if success:
                print("✅ Test index created successfully!")
            
            # Index a test document
            test_doc = {
                "message": "Test connection successful",
                "timestamp": "2025-08-08T12:00:00Z"
            }
            
            success = await es_client.index_document(test_index, test_doc, "test_doc_1")
            if success:
                print("✅ Test document indexed successfully!")
            
            # Search for the document
            query = {"match": {"message": "connection"}}
            result = await es_client.search(test_index, query)
            
            if result.get("hits", {}).get("total", {}).get("value", 0) > 0:
                print("✅ Test document search successful!")
            else:
                print("❌ Test document not found in search")
            
            # Cleanup: Delete test index
            try:
                if es_client.client:
                    await es_client.client.indices.delete(index=test_index)
                    print("✅ Test index cleaned up successfully!")
            except Exception as cleanup_error:
                print(f"⚠️  Warning: Failed to cleanup test index: {cleanup_error}")
                
        except Exception as e:
            print(f"❌ Index operations test failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Elasticsearch Cloud connection test completed!")
        
    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        logger.error(f"Elasticsearch cloud connection test failed: {e}")
        
        # Troubleshooting tips
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if the Elasticsearch URL is correct")
        print("2. Verify the API key is valid and has proper permissions")
        print("3. Ensure network connectivity to the cloud endpoint")
        print("4. Check if SSL certificates are properly configured")
        
    finally:
        # Always disconnect
        if es_client.is_connected:
            await es_client.disconnect()
            print("\n🔌 Disconnected from Elasticsearch")


async def main():
    """Main function."""
    await test_cloud_connection()


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(main())
