"""
Test Elasticsearch Authentication Methods
"""

import asyncio
import os
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import AuthenticationException

# Load environment variables
load_dotenv()

async def test_authentication_methods():
    """Test different authentication methods for Google Cloud Elasticsearch."""
    
    host = os.getenv('ELASTICSEARCH_HOST')
    port = int(os.getenv('ELASTICSEARCH_PORT', 443))
    scheme = os.getenv('ELASTICSEARCH_SCHEME', 'https')
    api_key = os.getenv('ELASTICSEARCH_API_KEY')
    
    print(f"Testing connection to: {scheme}://{host}:{port}")
    print(f"API Key: {api_key[:10]}...{api_key[-10:] if api_key else 'None'}")
    print("=" * 60)
    
    # Method 1: API Key authentication
    print("\n1. Testing API Key authentication...")
    try:
        client = AsyncElasticsearch(
            hosts=[{
                'host': host,
                'port': port,
                'scheme': scheme
            }],
            api_key=api_key,
            verify_certs=True,
            request_timeout=30
        )
        
        info = await client.info()
        print("✅ API Key authentication successful!")
        print(f"   Cluster: {info.get('cluster_name', 'Unknown')}")
        print(f"   Version: {info.get('version', {}).get('number', 'Unknown')}")
        await client.close()
        return True
        
    except AuthenticationException as e:
        print(f"❌ API Key authentication failed: {e}")
    except Exception as e:
        print(f"❌ API Key connection error: {e}")
    
    # Method 2: Try with Authorization header format
    print("\n2. Testing Authorization header format...")
    try:
        client = AsyncElasticsearch(
            hosts=[{
                'host': host,
                'port': port,
                'scheme': scheme
            }],
            headers={'Authorization': f'ApiKey {api_key}'},
            verify_certs=True,
            request_timeout=30
        )
        
        info = await client.info()
        print("✅ Authorization header authentication successful!")
        await client.close()
        return True
        
    except AuthenticationException as e:
        print(f"❌ Authorization header authentication failed: {e}")
    except Exception as e:
        print(f"❌ Authorization header connection error: {e}")
    
    # Method 3: Try basic connection without auth (will fail but shows connection)
    print("\n3. Testing basic connection (no auth)...")
    try:
        client = AsyncElasticsearch(
            hosts=[{
                'host': host,
                'port': port,
                'scheme': scheme
            }],
            verify_certs=True,
            request_timeout=30
        )
        
        info = await client.info()
        print("✅ Basic connection successful (unexpected!)")
        await client.close()
        return True
        
    except AuthenticationException as e:
        print(f"✅ Basic connection reached server (expected auth error): {e}")
    except Exception as e:
        print(f"❌ Basic connection failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🔍 Testing Elasticsearch Authentication Methods")
    success = asyncio.run(test_authentication_methods())
    
    if not success:
        print("\n⚠️  All authentication methods failed.")
        print("💡 Suggestions:")
        print("   1. Check if API key is still valid in Google Cloud Console")
        print("   2. Verify API key has proper permissions")
        print("   3. Generate a new API key from Kibana -> Stack Management -> API Keys")
        print("   4. Check if cluster requires specific authentication format")
