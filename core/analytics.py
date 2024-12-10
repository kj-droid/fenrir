import matplotlib.pyplot as plt
import os
import logging


class Analytics:
    def __init__(self, output_dir="reports/output"):
        """
        Initialize the Analytics module.
        :param output_dir: Directory to save analytics visualizations.
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger("Analytics")
        logging.basicConfig(level=logging.INFO)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def plot_severity_distribution(self, vulnerabilities, filename="severity_distribution.png"):
        """
        Generate a bar chart showing the distribution of vulnerabilities by severity.
        :param vulnerabilities: List of vulnerabilities with their severities.
        :param filename: Name of the output image file.
        """
        severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        severity_count = {severity: 0 for severity in severities}

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "LOW").upper()
            if severity in severity_count:
                severity_count[severity] += 1

        x_labels = list(severity_count.keys())
        y_values = list(severity_count.values())

        plt.figure(figsize=(8, 5))
        plt.bar(x_labels, y_values, color=["green", "yellow", "orange", "red"])
        plt.title("Vulnerability Severity Distribution")
        plt.xlabel("Severity")
        plt.ylabel("Count")
        plt.tight_layout()

        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path)
        self.logger.info(f"Severity distribution plot saved: {output_path}")
        plt.close()

    def plot_service_distribution(self, services, filename="service_distribution.png"):
        """
        Generate a pie chart showing the distribution of services discovered.
        :param services: List of services discovered during scans.
        :param filename: Name of the output image file.
        """
        service_count = {}
        for service in services:
            service_name = service.get("service", "Unknown Service")
            service_count[service_name] = service_count.get(service_name, 0) + 1

        labels = list(service_count.keys())
        sizes = list(service_count.values())

        plt.figure(figsize=(8, 5))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
        plt.title("Service Distribution")
        plt.tight_layout()

        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path)
        self.logger.info(f"Service distribution plot saved: {output_path}")
        plt.close()

    def generate_analytics(self, vulnerabilities, services):
        """
        Generate all analytics visualizations.
        :param vulnerabilities: List of vulnerabilities with severities.
        :param services: List of services discovered during scans.
        """
        self.logger.info("Generating analytics visualizations...")
        self.plot_severity_distribution(vulnerabilities)
        self.plot_service_distribution(services)


if __name__ == "__main__":
    # Example usage
    vulnerabilities = [
        {"id": "CVE-2023-0001", "severity": "HIGH"},
        {"id": "CVE-2023-0002", "severity": "MEDIUM"},
        {"id": "CVE-2023-0003", "severity": "CRITICAL"},
        {"id": "CVE-2023-0004", "severity": "LOW"},
        {"id": "CVE-2023-0005", "severity": "HIGH"},
    ]

    services = [
        {"port": 22, "service": "SSH"},
        {"port": 80, "service": "HTTP"},
        {"port": 443, "service": "HTTPS"},
        {"port": 21, "service": "FTP"},
        {"port": 80, "service": "HTTP"},
    ]

    analytics = Analytics()
    analytics.generate_analytics(vulnerabilities, services)
