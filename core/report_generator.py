import csv
import json
from fpdf import FPDF
import os
import logging


class ReportGenerator:
    def __init__(self, output_dir="reports/output"):
        """
        Initialize the report generator.
        :param output_dir: Directory to save the generated reports.
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger("ReportGenerator")
        logging.basicConfig(level=logging.INFO)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_csv(self, data, filename="report.csv"):
        """
        Generate a CSV report.
        :param data: List of dictionaries containing report data.
        :param filename: Name of the CSV file.
        """
        file_path = os.path.join(self.output_dir, filename)
        try:
            with open(file_path, mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            self.logger.info(f"CSV report generated: {file_path}")
        except Exception as e:
            self.logger.error(f"Error generating CSV report: {e}")

    def generate_pdf(self, data, filename="report.pdf"):
        """
        Generate a PDF report.
        :param data: List of dictionaries containing report data.
        :param filename: Name of the PDF file.
        """
        file_path = os.path.join(self.output_dir, filename)
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Scan Report", ln=True, align="C")
            pdf.ln(10)

            for entry in data:
                for key, value in entry.items():
                    pdf.cell(0, 10, txt=f"{key}: {value}", ln=True)
                pdf.ln(5)

            pdf.output(file_path)
            self.logger.info(f"PDF report generated: {file_path}")
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {e}")

    def generate_html(self, data, filename="report.html"):
        """
        Generate an HTML report.
        :param data: List of dictionaries containing report data.
        :param filename: Name of the HTML file.
        """
        file_path = os.path.join(self.output_dir, filename)
        try:
            with open(file_path, mode="w") as file:
                file.write("<html><head><title>Scan Report</title></head><body>")
                file.write("<h1>Scan Report</h1>")
                for entry in data:
                    file.write("<div style='margin-bottom: 20px;'>")
                    for key, value in entry.items():
                        file.write(f"<p><strong>{key}:</strong> {value}</p>")
                    file.write("</div>")
                file.write("</body></html>")
            self.logger.info(f"HTML report generated: {file_path}")
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")

    def save_report(self, data, formats=("csv", "pdf", "html")):
        """
        Save the report in multiple formats.
        :param data: List of dictionaries containing report data.
        :param formats: Tuple of formats to save (csv, pdf, html).
        """
        for fmt in formats:
            if fmt.lower() == "csv":
                self.generate_csv(data)
            elif fmt.lower() == "pdf":
                self.generate_pdf(data)
            elif fmt.lower() == "html":
                self.generate_html(data)


if __name__ == "__main__":
    # Example usage
    report_data = [
        {"Port": "22", "Service": "SSH", "Status": "Open", "Vulnerabilities": "None"},
        {"Port": "80", "Service": "HTTP", "Status": "Open", "Vulnerabilities": "None"},
        {"Port": "443", "Service": "HTTPS", "Status": "Open", "Vulnerabilities": "SSLv3 Supported"},
    ]

    generator = ReportGenerator()
    generator.save_report(report_data)
