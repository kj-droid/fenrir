import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QCheckBox,
    QWidget, QHBoxLayout, QFileDialog, QTextEdit, QDialog, QListWidget, QMessageBox, QLineEdit
)
from .tasks import ScanWorker
from core.module_coordinator import ModuleCoordinator

class FenrirGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fenrir")
        self.setGeometry(100, 100, 800, 600)
        self.worker = None
        self.coordinator = ModuleCoordinator()
        self.vulnerability_count = 0
        self.output_folder = os.path.join(os.getcwd(), "fenrir_results")

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Target Configuration
        main_layout.addWidget(QLabel("Target:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter IP, hostname, or network range")
        main_layout.addWidget(self.target_input)
        add_target_button = QPushButton("Add Target")
        add_target_button.clicked.connect(self.add_target)
        main_layout.addWidget(add_target_button)
        self.target_list = QListWidget()
        main_layout.addWidget(self.target_list)

        # Module Selection
        main_layout.addWidget(QLabel("Modules:"))
        self.module_checkboxes = {}
        for name in self.coordinator.get_available_module_names():
            self.module_checkboxes[name] = QCheckBox(name.replace("_", " ").title())
            main_layout.addWidget(self.module_checkboxes[name])

        # Output Folder Selection
        main_layout.addWidget(QLabel("Output Destination:"))
        output_layout = QHBoxLayout()
        self.output_folder_label = QLabel(f"{self.output_folder}")
        self.output_folder_label.setStyleSheet("border: 1px solid grey; padding: 4px;")
        select_folder_button = QPushButton("Select Folder")
        select_folder_button.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.output_folder_label)
        output_layout.addWidget(select_folder_button)
        main_layout.addLayout(output_layout)

        # --- NEW: Filename Inputs ---
        main_layout.addWidget(QLabel("Output Filenames:"))
        filename_layout = QHBoxLayout()
        self.ports_filename_input = QLineEdit("open_ports.txt")
        self.vulns_filename_input = QLineEdit("vulnerabilities.json")
        filename_layout.addWidget(QLabel("Ports:"))
        filename_layout.addWidget(self.ports_filename_input)
        filename_layout.addWidget(QLabel("Vulns:"))
        filename_layout.addWidget(self.vulns_filename_input)
        main_layout.addLayout(filename_layout)
        # --- End of Filename Inputs ---

        self.start_scan_button = QPushButton("Start Scan")
        self.start_scan_button.clicked.connect(self.start_scan)
        main_layout.addWidget(self.start_scan_button)

        self.monitoring_area = QTextEdit()
        self.monitoring_area.setReadOnly(True)
        main_layout.addWidget(self.monitoring_area)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder)
        if folder:
            self.output_folder = folder
            self.output_folder_label.setText(self.output_folder)

    def add_target(self):
        target = self.target_input.text().strip()
        if target:
            self.target_list.addItem(target)
            self.target_input.clear()

    def start_scan(self):
        targets = [self.target_list.item(i).text() for i in range(self.target_list.count())]
        if not targets:
            QMessageBox.warning(self, "Input Error", "Please add at least one target.")
            return

        selected_modules = [name for name, checkbox in self.module_checkboxes.items() if checkbox.isChecked()]
        if not selected_modules:
            QMessageBox.warning(self, "Input Error", "Please select at least one module.")
            return
            
        # Get filenames from input fields
        ports_filename = self.ports_filename_input.text().strip()
        vulns_filename = self.vulns_filename_input.text().strip()
        if not ports_filename or not vulns_filename:
            QMessageBox.warning(self, "Input Error", "Output filenames cannot be empty.")
            return

        self.monitoring_area.clear()
        self.start_scan_button.setEnabled(False)
        self.vulnerability_count = 0
        self.monitoring_area.append("Starting scan...")

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # Use custom filenames for output files
        ports_file = os.path.join(self.output_folder, ports_filename)
        vulns_file = os.path.join(self.output_folder, vulns_filename)
        if os.path.exists(ports_file): os.remove(ports_file)
        if os.path.exists(vulns_file): os.remove(vulns_file)

        self.worker = ScanWorker(targets, selected_modules)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.open_ports_found.connect(self.handle_open_ports)
        self.worker.signals.vulnerabilities_found.connect(self.handle_vulnerabilities)
        self.worker.signals.finished.connect(self.scan_finished)
        self.worker.start()

    def update_progress(self, message):
        if "[*]" in message or "[+]" in message:
             self.monitoring_area.append(message)

    def handle_open_ports(self, ports_data):
        # The data is now correctly structured: {'target_ip': {'ports': [...]}}
        target = list(ports_data.keys())[0]
        host_data = ports_data[target]
        
        output_file = os.path.join(self.output_folder, self.ports_filename_input.text())
        with open(output_file, "a") as f:
            f.write(f"Target: {target}\n")
            if 'ports' in host_data and host_data['ports']:
                for port_info in host_data['ports']:
                    product = port_info.get('product', 'unknown')
                    version = port_info.get('version', '')
                    name = port_info.get('name', '')
                    f.write(f"  - Port {port_info['port']} ({name}): {product} {version}\n")
            f.write("\n")
            
        self.monitoring_area.append(f"Found open ports on {target}:")
        if 'ports' in host_data and host_data['ports']:
            for port_info in host_data['ports']:
                self.monitoring_area.append(f"  - Port {port_info['port']} ({port_info.get('product', 'unknown')})")

    def handle_vulnerabilities(self, vulns_data):
        target = list(vulns_data.keys())[0]
        vulns_info = vulns_data[target]
        
        output_file = os.path.join(self.output_folder, self.vulns_filename_input.text())
        with open(output_file, "a") as f:
            json.dump({target: vulns_info}, f, indent=4)
            f.write("\n")

        count = sum(len(v) for v in vulns_info.values())
        self.vulnerability_count += count

    def scan_finished(self, message):
        self.monitoring_area.append(f"\n--- SCAN COMPLETE ---")
        self.monitoring_area.append(f"Total vulnerabilities found: {self.vulnerability_count}")
        self.monitoring_area.append(f"Results saved to '{self.output_folder}'")
        self.start_scan_button.setEnabled(True)
