"""
Performance Monitoring Service
Monitors system performance metrics and alerts
"""

import time
import psutil
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from shared_code.utils.redis import get_redis_manager
from shared_code.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Data class for performance metrics."""

    timestamp: datetime
    service_name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    response_times: List[float]
    error_rate: float
    throughput: int


class PerformanceMonitor:
    """Monitor system and application performance."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.redis = get_redis_manager()
        self.metrics_history = []
        self.alert_thresholds = {
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "disk_threshold": 90.0,
            "response_time_threshold": 2.0,  # seconds
            "error_rate_threshold": 5.0,  # percentage
        }

    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_mb = memory.used / (1024 * 1024)

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_usage_percent = (disk.used / disk.total) * 100

            # Network metrics
            network_io = psutil.net_io_counters()
            network_data = {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
            }

            return {
                "timestamp": datetime.now(),
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "memory_percent": memory_percent,
                "memory_mb": memory_mb,
                "memory_total_mb": memory.total / (1024 * 1024),
                "disk_usage_percent": disk_usage_percent,
                "disk_total_gb": disk.total / (1024 * 1024 * 1024),
                "network_io": network_data,
            }

        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}

    async def collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-level performance metrics."""
        try:
            # Get metrics from Redis cache
            cache_key = f"app_metrics:{self.service_name}"
            cached_metrics = await self.redis.get(cache_key)

            if cached_metrics:
                return eval(
                    cached_metrics
                )  # In production, use proper JSON serialization

            # Default metrics if not cached
            return {
                "timestamp": datetime.now(),
                "active_connections": 0,
                "request_count": 0,
                "average_response_time": 0.0,
                "error_count": 0,
                "throughput_per_minute": 0,
            }

        except Exception as e:
            logger.error(f"Error collecting application metrics: {str(e)}")
            return {}

    async def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in Redis for monitoring."""
        try:
            # Store current metrics
            cache_key = f"performance:{self.service_name}:{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
            await self.redis.setex(cache_key, 3600, str(metrics))  # Store for 1 hour

            # Store latest metrics
            latest_key = f"performance:{self.service_name}:latest"
            await self.redis.setex(latest_key, 300, str(metrics))  # Store for 5 minutes

            logger.debug(f"Metrics stored for {self.service_name}")

        except Exception as e:
            logger.error(f"Error storing metrics: {str(e)}")

    async def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics against thresholds and generate alerts."""
        alerts = []

        try:
            # CPU alert
            if metrics.get("cpu_percent", 0) > self.alert_thresholds["cpu_threshold"]:
                alerts.append(
                    {
                        "type": "CPU_HIGH",
                        "severity": "WARNING",
                        "message": f"CPU usage is {metrics['cpu_percent']:.1f}%",
                        "threshold": self.alert_thresholds["cpu_threshold"],
                        "current_value": metrics["cpu_percent"],
                        "timestamp": datetime.now(),
                    }
                )

            # Memory alert
            if (
                metrics.get("memory_percent", 0)
                > self.alert_thresholds["memory_threshold"]
            ):
                alerts.append(
                    {
                        "type": "MEMORY_HIGH",
                        "severity": "WARNING",
                        "message": f"Memory usage is {metrics['memory_percent']:.1f}%",
                        "threshold": self.alert_thresholds["memory_threshold"],
                        "current_value": metrics["memory_percent"],
                        "timestamp": datetime.now(),
                    }
                )

            # Disk alert
            if (
                metrics.get("disk_usage_percent", 0)
                > self.alert_thresholds["disk_threshold"]
            ):
                alerts.append(
                    {
                        "type": "DISK_HIGH",
                        "severity": "CRITICAL",
                        "message": f"Disk usage is {metrics['disk_usage_percent']:.1f}%",
                        "threshold": self.alert_thresholds["disk_threshold"],
                        "current_value": metrics["disk_usage_percent"],
                        "timestamp": datetime.now(),
                    }
                )

            # Store alerts in Redis
            if alerts:
                alert_key = f"alerts:{self.service_name}:{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
                await self.redis.setex(
                    alert_key, 86400, str(alerts)
                )  # Store for 24 hours

                logger.warning(
                    f"Generated {len(alerts)} alerts for {self.service_name}"
                )

            return alerts

        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            return []

    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status of the service."""
        try:
            system_metrics = await self.collect_system_metrics()
            app_metrics = await self.collect_application_metrics()

            # Determine health status
            health_score = 100
            status = "healthy"
            issues = []

            # Check system health
            if system_metrics.get("cpu_percent", 0) > 70:
                health_score -= 20
                issues.append("High CPU usage")

            if system_metrics.get("memory_percent", 0) > 80:
                health_score -= 25
                issues.append("High memory usage")

            if system_metrics.get("disk_usage_percent", 0) > 85:
                health_score -= 30
                issues.append("High disk usage")

            # Determine status based on score
            if health_score >= 80:
                status = "healthy"
            elif health_score >= 60:
                status = "degraded"
            else:
                status = "unhealthy"

            return {
                "service": self.service_name,
                "status": status,
                "health_score": health_score,
                "timestamp": datetime.now(),
                "system_metrics": system_metrics,
                "application_metrics": app_metrics,
                "issues": issues,
            }

        except Exception as e:
            logger.error(f"Error getting health status: {str(e)}")
            return {
                "service": self.service_name,
                "status": "unknown",
                "health_score": 0,
                "timestamp": datetime.now(),
                "error": str(e),
            }

    async def run_monitoring_loop(self, interval: int = 60):
        """Run continuous monitoring loop."""
        logger.info(f"Starting performance monitoring for {self.service_name}")

        while True:
            try:
                # Collect metrics
                system_metrics = await self.collect_system_metrics()
                app_metrics = await self.collect_application_metrics()

                # Combine metrics
                all_metrics = {**system_metrics, **app_metrics}
                all_metrics["service_name"] = self.service_name

                # Store metrics
                await self.store_metrics(all_metrics)

                # Check for alerts
                alerts = await self.check_alerts(all_metrics)

                if alerts:
                    logger.warning(f"Performance alerts generated: {len(alerts)}")

                # Wait for next iteration
                await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(interval)

    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of metrics for the specified time period."""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)

            # Get metrics from Redis
            pattern = f"performance:{self.service_name}:*"
            keys = await self.redis.keys(pattern)

            metrics_data = []
            for key in keys:
                try:
                    data = await self.redis.get(key)
                    if data:
                        metric = eval(data)  # In production, use proper JSON
                        if isinstance(metric.get("timestamp"), datetime):
                            if start_time <= metric["timestamp"] <= end_time:
                                metrics_data.append(metric)
                except:
                    continue

            if not metrics_data:
                return {"message": "No metrics data available"}

            # Calculate summary statistics
            cpu_values = [m.get("cpu_percent", 0) for m in metrics_data]
            memory_values = [m.get("memory_percent", 0) for m in metrics_data]

            summary = {
                "period_hours": hours,
                "data_points": len(metrics_data),
                "cpu_stats": {
                    "avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                    "max": max(cpu_values) if cpu_values else 0,
                    "min": min(cpu_values) if cpu_values else 0,
                },
                "memory_stats": {
                    "avg": (
                        sum(memory_values) / len(memory_values) if memory_values else 0
                    ),
                    "max": max(memory_values) if memory_values else 0,
                    "min": min(memory_values) if memory_values else 0,
                },
                "timestamp": datetime.now(),
            }

            return summary

        except Exception as e:
            logger.error(f"Error getting metrics summary: {str(e)}")
            return {"error": str(e)}


# Utility functions for middleware integration
class ResponseTimeTracker:
    """Track response times for endpoints."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.redis = get_redis_manager()

    async def record_response_time(self, endpoint: str, response_time: float):
        """Record response time for an endpoint."""
        try:
            key = f"response_time:{self.service_name}:{endpoint}"
            await self.redis.lpush(key, response_time)
            await self.redis.ltrim(key, 0, 99)  # Keep last 100 response times
            await self.redis.expire(key, 3600)  # Expire after 1 hour

        except Exception as e:
            logger.error(f"Error recording response time: {str(e)}")

    async def get_avg_response_time(self, endpoint: str) -> float:
        """Get average response time for an endpoint."""
        try:
            key = f"response_time:{self.service_name}:{endpoint}"
            times = await self.redis.lrange(key, 0, -1)

            if times:
                float_times = [float(t) for t in times]
                return sum(float_times) / len(float_times)

            return 0.0

        except Exception as e:
            logger.error(f"Error getting avg response time: {str(e)}")
            return 0.0
