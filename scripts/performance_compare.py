#!/usr/bin/env python3
"""
Performance Regression Testing Tool
Compares current performance metrics with baseline
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import statistics


class PerformanceComparator:
    """Compares performance metrics between test runs"""

    def __init__(self, current_path: str, baseline_path: str):
        self.current_path = Path(current_path)
        self.baseline_path = Path(baseline_path)
        self.thresholds = {
            "response_time_regression": 0.20,  # 20% increase is critical
            "error_rate_increase": 0.05,  # 5% increase in errors
            "throughput_decrease": 0.15,  # 15% decrease in RPS
        }

    def load_results(self, path: Path) -> Dict:
        """Load test results from file"""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Results file not found: {path}")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in file: {path}")
            return {}

    def extract_metrics(self, results: Dict) -> Dict:
        """Extract key performance metrics from test results"""
        metrics = {
            "response_time_avg": 0,
            "response_time_95th": 0,
            "error_rate": 0,
            "requests_per_second": 0,
            "total_requests": 0,
            "total_failures": 0,
        }

        # Try to extract from Locust output format
        if "stdout" in results:
            output = results["stdout"]

            # Parse response times
            if "Average" in output:
                try:
                    avg_line = [
                        line for line in output.split("\n") if "Average" in line
                    ][0]
                    metrics["response_time_avg"] = float(avg_line.split()[1])
                except:
                    pass

            # Parse 95th percentile
            if "95%" in output:
                try:
                    p95_line = [line for line in output.split("\n") if "95%" in line][0]
                    metrics["response_time_95th"] = float(p95_line.split()[1])
                except:
                    pass

            # Parse request rate
            if "RPS" in output or "requests/s" in output:
                try:
                    rps_lines = [
                        line
                        for line in output.split("\n")
                        if "requests/s" in line or "RPS" in line
                    ]
                    if rps_lines:
                        metrics["requests_per_second"] = float(rps_lines[0].split()[0])
                except:
                    pass

        return metrics

    def compare_metrics(self, current: Dict, baseline: Dict) -> Dict:
        """Compare current metrics with baseline"""
        comparison = {}

        for metric, current_value in current.items():
            baseline_value = baseline.get(metric, 0)

            if baseline_value == 0:
                comparison[metric] = {
                    "current": current_value,
                    "baseline": baseline_value,
                    "change_percent": 0,
                    "status": "no_baseline",
                }
                continue

            change_percent = ((current_value - baseline_value) / baseline_value) * 100

            # Determine status based on metric type and thresholds
            status = "stable"

            if metric in ["response_time_avg", "response_time_95th"]:
                if change_percent > self.thresholds["response_time_regression"] * 100:
                    status = "regression"
                elif change_percent < -10:  # 10% improvement
                    status = "improvement"

            elif metric == "error_rate":
                if change_percent > self.thresholds["error_rate_increase"] * 100:
                    status = "regression"
                elif change_percent < -5:
                    status = "improvement"

            elif metric == "requests_per_second":
                if change_percent < -self.thresholds["throughput_decrease"] * 100:
                    status = "regression"
                elif change_percent > 10:
                    status = "improvement"

            comparison[metric] = {
                "current": current_value,
                "baseline": baseline_value,
                "change_percent": round(change_percent, 2),
                "status": status,
            }

        return comparison

    def generate_report(self, service_comparisons: Dict) -> str:
        """Generate markdown report"""

        report = """# 📊 Performance Regression Test Report

## Summary

"""

        total_services = len(service_comparisons)
        regression_count = 0
        improvement_count = 0

        for service, comparison in service_comparisons.items():
            has_regression = any(
                m["status"] == "regression" for m in comparison.values()
            )
            has_improvement = any(
                m["status"] == "improvement" for m in comparison.values()
            )

            if has_regression:
                regression_count += 1
            elif has_improvement:
                improvement_count += 1

        # Overall status
        if regression_count > 0:
            overall_status = "🔴 REGRESSION DETECTED"
        elif improvement_count > 0:
            overall_status = "🟢 PERFORMANCE IMPROVED"
        else:
            overall_status = "🟡 STABLE PERFORMANCE"

        report += f"""
**Overall Status:** {overall_status}

- **Total Services Tested:** {total_services}
- **Services with Regressions:** {regression_count}
- **Services with Improvements:** {improvement_count}
- **Stable Services:** {total_services - regression_count - improvement_count}

"""

        # Detailed service analysis
        report += "## Service Analysis\n\n"

        for service, comparison in service_comparisons.items():
            report += f"### {service.replace('_', ' ').title()}\n\n"

            # Service status
            service_regressions = [
                m for m in comparison.values() if m["status"] == "regression"
            ]
            service_improvements = [
                m for m in comparison.values() if m["status"] == "improvement"
            ]

            if service_regressions:
                report += "🔴 **Status:** Performance Regression Detected\n\n"
            elif service_improvements:
                report += "🟢 **Status:** Performance Improved\n\n"
            else:
                report += "🟡 **Status:** Stable Performance\n\n"

            # Metrics table
            report += "| Metric | Current | Baseline | Change | Status |\n"
            report += "|--------|---------|----------|--------|--------|\n"

            for metric, data in comparison.items():
                status_emoji = {
                    "regression": "🔴",
                    "improvement": "🟢",
                    "stable": "🟡",
                    "no_baseline": "⚫",
                }.get(data["status"], "❓")

                change_str = (
                    f"{data['change_percent']:+.1f}%"
                    if data["change_percent"] != 0
                    else "0%"
                )

                report += f"| {metric.replace('_', ' ').title()} | {data['current']:.2f} | {data['baseline']:.2f} | {change_str} | {status_emoji} {data['status'].title()} |\n"

            report += "\n"

            # Recommendations
            if service_regressions:
                report += "**🔧 Recommendations:**\n"
                for metric, data in comparison.items():
                    if data["status"] == "regression":
                        if "response_time" in metric:
                            report += (
                                f"- Investigate response time increase in {metric}\n"
                            )
                        elif "error_rate" in metric:
                            report += f"- Check for new bugs or configuration issues\n"
                        elif "requests_per_second" in metric:
                            report += f"- Analyze throughput bottlenecks\n"
                report += "\n"

        # Thresholds section
        report += """## Alert Thresholds

The following thresholds are used to determine performance regressions:

- **Response Time Regression:** > 20% increase
- **Error Rate Increase:** > 5% increase  
- **Throughput Decrease:** > 15% decrease

## Next Steps

"""

        if regression_count > 0:
            report += """
1. **Immediate Actions:**
   - Review recent code changes
   - Check infrastructure metrics
   - Analyze database performance
   - Review recent deployments

2. **Investigation:**
   - Run targeted performance tests
   - Profile application code
   - Check resource utilization
   - Review logs for errors

3. **Remediation:**
   - Roll back problematic changes if needed
   - Optimize identified bottlenecks
   - Scale resources if necessary
   - Update performance baselines after fixes
"""
        else:
            report += """
1. **Update Baselines:** Consider updating performance baselines if improvements are consistent
2. **Monitoring:** Continue monitoring performance metrics
3. **Documentation:** Document any performance optimizations made
"""

        return report

    def run_comparison(self) -> bool:
        """Run the full performance comparison"""

        print("🔍 Starting performance regression analysis...")

        # Find all result files
        current_files = list(self.current_path.glob("*.json"))
        baseline_files = (
            list(self.baseline_path.glob("*.json"))
            if self.baseline_path.exists()
            else []
        )

        if not current_files:
            print(f"❌ No current result files found in {self.current_path}")
            return False

        if not baseline_files:
            print(f"⚠️  No baseline files found in {self.baseline_path}")
            print("This will be treated as the first test run.")

        service_comparisons = {}

        # Process each service
        for current_file in current_files:
            service_name = current_file.stem.split("_")[
                0
            ]  # Extract service name from filename

            print(f"📊 Analyzing {service_name}...")

            # Load current results
            current_results = self.load_results(current_file)
            current_metrics = self.extract_metrics(current_results)

            # Find corresponding baseline file
            baseline_file = None
            for bf in baseline_files:
                if bf.stem.startswith(service_name):
                    baseline_file = bf
                    break

            if baseline_file:
                baseline_results = self.load_results(baseline_file)
                baseline_metrics = self.extract_metrics(baseline_results)
            else:
                baseline_metrics = {}

            # Compare metrics
            comparison = self.compare_metrics(current_metrics, baseline_metrics)
            service_comparisons[service_name] = comparison

        # Generate report
        report = self.generate_report(service_comparisons)

        # Save report
        report_file = self.current_path / "performance-report.md"
        with open(report_file, "w") as f:
            f.write(report)

        print(f"📋 Report generated: {report_file}")

        # Check if there are any regressions
        has_regressions = any(
            any(m["status"] == "regression" for m in comparison.values())
            for comparison in service_comparisons.values()
        )

        if has_regressions:
            print("🔴 Performance regressions detected!")
            return False
        else:
            print("🟢 No performance regressions found!")
            return True


def main():
    parser = argparse.ArgumentParser(description="Performance Regression Testing")
    parser.add_argument(
        "--current", "-c", required=True, help="Path to current test results"
    )
    parser.add_argument(
        "--baseline", "-b", required=True, help="Path to baseline test results"
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit with code 1 if regression detected",
    )

    args = parser.parse_args()

    comparator = PerformanceComparator(args.current, args.baseline)
    success = comparator.run_comparison()

    if args.fail_on_regression and not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
