"""
Configuration Checker for Analytics Service.
Validates Elasticsearch configuration and connectivity.
"""

import os
import asyncio
from typing import Dict, Any
from core.config import settings
from core.elasticsearch_client import es_client
from utils.logger import get_logger

logger = get_logger(__name__)


class ConfigurationChecker:
    """Check and validate service configuration."""

    def __init__(self):
        self.issues = []
        self.warnings = []

    def check_environment_variables(self) -> Dict[str, Any]:
        """Check required environment variables."""
        print("🔧 Checking Environment Variables...")
        
        required_vars = [
            'APP_NAME',
            'PORT',
            'DB_HOST',
            'DB_PORT', 
            'DB_USERNAME',
            'DB_PASSWORD',
            'DB_NAME',
            'ELASTICSEARCH_HOST',
            'ELASTICSEARCH_PORT',
            'ELASTICSEARCH_SCHEME'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.issues.append(f"Missing environment variables: {', '.join(missing_vars)}")
            print(f"❌ Missing variables: {missing_vars}")
        else:
            print("✅ All required environment variables present")
        
        # Check Elasticsearch authentication
        has_api_key = bool(os.getenv('ELASTICSEARCH_API_KEY'))
        has_credentials = bool(os.getenv('ELASTICSEARCH_USERNAME')) and bool(os.getenv('ELASTICSEARCH_PASSWORD'))
        
        if not has_api_key and not has_credentials:
            self.warnings.append("No Elasticsearch authentication configured")
            print("⚠️  Warning: No Elasticsearch authentication configured")
        elif has_api_key:
            print("✅ Elasticsearch API Key configured")
        else:
            print("✅ Elasticsearch username/password configured")
        
        return {
            'required_vars_present': len(missing_vars) == 0,
            'missing_vars': missing_vars,
            'has_es_auth': has_api_key or has_credentials
        }

    def check_configuration_values(self) -> Dict[str, Any]:
        """Check configuration values."""
        print("\n📋 Checking Configuration Values...")
        
        config_issues = []
        
        # Check Elasticsearch configuration
        es_config = settings.elasticsearch
        
        if es_config.scheme not in ['http', 'https']:
            config_issues.append(f"Invalid Elasticsearch scheme: {es_config.scheme}")
        
        if es_config.port <= 0 or es_config.port > 65535:
            config_issues.append(f"Invalid Elasticsearch port: {es_config.port}")
        
        # Check for cloud vs local configuration
        is_cloud = es_config.host != 'localhost' and not es_config.host.startswith('127.')
        
        if is_cloud:
            print(f"🌐 Cloud Elasticsearch detected: {es_config.host}")
            if es_config.scheme != 'https':
                self.warnings.append("Cloud Elasticsearch should use HTTPS")
            if not es_config.verify_certs:
                self.warnings.append("Certificate verification disabled for cloud")
        else:
            print(f"🏠 Local Elasticsearch detected: {es_config.host}")
        
        if config_issues:
            self.issues.extend(config_issues)
            print(f"❌ Configuration issues: {config_issues}")
        else:
            print("✅ Configuration values are valid")
        
        return {
            'valid_config': len(config_issues) == 0,
            'is_cloud': is_cloud,
            'issues': config_issues
        }

    async def check_elasticsearch_connectivity(self) -> Dict[str, Any]:
        """Check Elasticsearch connectivity."""
        print("\n🔗 Testing Elasticsearch Connectivity...")
        
        try:
            # Attempt connection
            await es_client.connect()
            print("✅ Successfully connected to Elasticsearch")
            
            # Test cluster health
            if es_client.client:
                health = await es_client.client.cluster.health()
                cluster_status = health.get('status', 'unknown')
                
                if cluster_status == 'green':
                    print("✅ Cluster status is GREEN")
                elif cluster_status == 'yellow':
                    print("⚠️  Cluster status is YELLOW")
                    self.warnings.append("Elasticsearch cluster status is YELLOW")
                else:
                    print("❌ Cluster status is RED")
                    self.issues.append("Elasticsearch cluster status is RED")
                
                return {
                    'connected': True,
                    'cluster_status': cluster_status,
                    'cluster_info': health
                }
            else:
                self.issues.append("Elasticsearch client is None after connection")
                return {'connected': False}
                
        except Exception as e:
            error_msg = f"Failed to connect to Elasticsearch: {str(e)}"
            self.issues.append(error_msg)
            print(f"❌ {error_msg}")
            return {'connected': False, 'error': str(e)}
        
        finally:
            if es_client.is_connected:
                await es_client.disconnect()

    async def run_full_check(self) -> Dict[str, Any]:
        """Run complete configuration check."""
        print("🚀 Analytics Service Configuration Check")
        print("=" * 50)
        
        # Check environment variables
        env_result = self.check_environment_variables()
        
        # Check configuration values
        config_result = self.check_configuration_values()
        
        # Test Elasticsearch connectivity
        connectivity_result = await self.check_elasticsearch_connectivity()
        
        # Summary
        print("\n📊 Configuration Check Summary")
        print("-" * 30)
        
        if not self.issues:
            print("✅ No critical issues found!")
        else:
            print("❌ Critical issues found:")
            for issue in self.issues:
                print(f"   - {issue}")
        
        if self.warnings:
            print("⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if connectivity_result.get('connected'):
            print("✅ Elasticsearch is ready for use")
        else:
            print("❌ Fix Elasticsearch connectivity before starting the service")
        
        if config_result.get('is_cloud'):
            print("🌐 Using cloud Elasticsearch - ensure API keys are properly secured")
        else:
            print("🏠 Using local Elasticsearch - good for development")
        
        return {
            'environment': env_result,
            'configuration': config_result,
            'connectivity': connectivity_result,
            'issues': self.issues,
            'warnings': self.warnings,
            'ready': len(self.issues) == 0 and connectivity_result.get('connected', False)
        }


async def main():
    """Main function."""
    checker = ConfigurationChecker()
    result = await checker.run_full_check()
    
    if result['ready']:
        print("\n🎉 Analytics Service is ready to start!")
        return 0
    else:
        print("\n❌ Please fix the issues before starting the service")
        return 1


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    exit_code = asyncio.run(main())
    exit(exit_code)
