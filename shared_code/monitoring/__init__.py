"""
Monitoring Module for Food Fast E-commerce

This module provides monitoring and observability tools for all microservices.

Components:
- performance_monitor: Service performance monitoring
- health_checks: Health check implementations
- metrics: Custom metrics collection
- alerting: Alert management system

Usage:
    from shared_code.monitoring import PerformanceMonitor
    
    monitor = PerformanceMonitor('service_name')
    await monitor.start_monitoring()
"""

__all__ = []
