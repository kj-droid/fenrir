import sys
import os
import json
import ipaddress
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QCheckBox,
    QWidget, QHBoxLayout, QFileDialog, QTextEdit, QMenuBar, QAction, QMessageBox, QLineEdit,
    QListWidget, QDialog, QDialogButtonBox, QAbstractItemView
)
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt
from .tasks import ScanWorker, DiscoveryWorker
from .results_window import ResultsWindow
from core.module_coordinator import ModuleCoordinator

class FenrirGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fenrir")
        self.setGeometry(100, 100, 800, 600)
        
        self.worker = None
        self.discovery_worker = None
        self.coordinator = ModuleCoordinator()
        self.output_folder = os.path.join(os.getcwd(), "fenrir_scans")
        self.last_scan_results = None
        # --- FIX: Initialize current_scan_folder to ensure it always exists ---
        self.current_scan_folder = None
        self.background_pixmap = None
        self.network_interfaces = {}
        background_path = os.path.join("gui", "assets", "background.png")
        if os.path.exists(background_path):
            self.background_pixmap = QPixmap(background_path)
        
        self.setup_ui()

    def setup_ui(self):
        """Initializes all UI components."""
        icon_path = os.path.join("gui", "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)
        
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        open_action = QAction('&Open Previous Scan...', self)
        open_action.triggered.connect(self.open_scan_results)
        file_menu.addAction(open_action)

        logo_path = os.path.join("gui", "assets", "logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaled(200, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            main_layout.addWidget(logo_label)

        main_layout.addWidget(QLabel("Targets (IP, Hostname, or CIDR Range e.g., 192.168.1.0/24):"))
        target_input_layout = QHBoxLayout()
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target or range and press 'Add'")
        target_input_layout.addWidget(self.target_input)
        add_target_button = QPushButton("Add")
        add_target_button.clicked.connect(self.add_target)
        target_input_layout.addWidget(add_target_button)
        
        self.discover_button = QPushButton("Discover Network")
        self.discover_button.clicked.connect(self.run_network_discovery)
        target_input_layout.addWidget(self.discover_button)
        main_layout.addLayout(target_input_layout)

        self.target_list_widget = QListWidget()
        self.target_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        main_layout.addWidget(self.target_list_widget)
        
        target_button_layout = QHBoxLayout()
        remove_target_button = QPushButton("Remove Selected")
        remove_target_button.clicked.connect(self.remove_target)
        clear_targets_button = QPushButton("Clear All")
        clear_targets_button.clicked.connect(self.target_list_widget.clear)
        target_button_layout.addWidget(remove_target_button)
        target_button_layout.addWidget(clear_targets_button)
        main_layout.addLayout(target_button_layout)

        main_layout.addWidget(QLabel("Modules:"))
        self.module_checkboxes = {}
        for name in self.coordinator.get_available_module_names():
            self.module_checkboxes[name] = QCheckBox(name.replace("_", " ").title())
            main_layout.addWidget(self.module_checkboxes[name])
        
        main_layout.addWidget(QLabel("Base Output Folder:"))
        output_layout = QHBoxLayout()
        self.output_folder_label = QLabel(self.output_folder)
        select_folder_button = QPushButton("Select Folder")
        select_folder_button.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.output_folder_label)
        output_layout.addWidget(select_folder_button)
        main_layout.addLayout(output_layout)

        button_layout = QHBoxLayout()
        self.start_scan_button = QPushButton("Start Scan")
        self.start_scan_button.clicked.connect(self.start_scan)
        self.view_results_button = QPushButton("View Results")
        self.view_results_button.clicked.connect(self.show_results_window)
        self.view_results_button.hide()
        button_layout.addWidget(self.start_scan_button)
        button_layout.addWidget(self.view_results_button)
        main_layout.addLayout(button_layout)
        
        self.monitoring_area = QTextEdit()
        self.monitoring_area.setReadOnly(True)
        main_layout.addWidget(self.monitoring_area)

    def run_network_discovery(self):
        from modules.network_discover import NetworkDiscover
        discover_module = NetworkDiscover()
        self.network_interfaces = discover_module.get_available_interfaces()
        if not self.network_interfaces:
            QMessageBox.information(self, "Network Discovery", "No scannable local network interfaces were found.")
            return
        dialog = InterfaceSelectionDialog(self.network_interfaces, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_ranges = dialog.get_selected_ranges()
            if not selected_ranges:
                self.monitoring_area.append("[-] Network discovery cancelled. No interfaces selected.")
                return
            self.monitoring_area.append(f"[*] Starting network discovery on: {', '.join(selected_ranges)}")
            self.discover_button.setEnabled(False)
            self.discovery_worker = DiscoveryWorker(selected_ranges)
            self.discovery_worker.signals.network_scan_finished.connect(self.handle_discovery_results)
            self.discovery_worker.start()

    def handle_discovery_results(self, found_ips):
        self.discover_button.setEnabled(True)
        if not found_ips: self.monitoring_area.append("[-] Discovery finished. No hosts found."); return
        if "ERROR" in found_ips[0]: self.monitoring_area.append(f"[-] {found_ips[0]}"); return
        self.monitoring_area.append(f"[+] Discovery complete. Found {len(found_ips)} hosts.")
        for ip in found_ips:
            if not self.target_list_widget.findItems(ip, Qt.MatchExactly): self.target_list_widget.addItem(ip)

    def resizeEvent(self, event):
        if self.background_pixmap:
            scaled_pixmap = self.background_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            palette = QPalette(); palette.setBrush(QPalette.Window, QBrush(scaled_pixmap)); self.setPalette(palette)
        QMainWindow.resizeEvent(self, event)

    def add_target(self):
        target_text = self.target_input.text().strip()
        if target_text: self.target_list_widget.addItem(target_text); self.target_input.clear()

    def remove_target(self):
        for item in self.target_list_widget.selectedItems(): self.target_list_widget.takeItem(self.target_list_widget.row(item))

    def parse_targets(self):
        final_targets = []
        for i in range(self.target_list_widget.count()):
            item_text = self.target_list_widget.item(i).text()
            try:
                if '/' in item_text:
                    network = ipaddress.ip_network(item_text, strict=False)
                    for ip in network.hosts(): final_targets.append(str(ip))
                else: final_targets.append(item_text)
            except ValueError: self.monitoring_area.append(f"Skipping invalid target: {item_text}")
        return final_targets

    def start_scan(self):
        targets = self.parse_targets()
        if not targets: QMessageBox.warning(self, "Input Error", "Please add at least one valid target."); return
        selected_modules = [name for name, checkbox in self.module_checkboxes.items() if checkbox.isChecked()]
        if 'port_scanner' not in selected_modules: selected_modules.insert(0, 'port_scanner')
        self.monitoring_area.clear(); self.start_scan_button.setEnabled(False); self.view_results_button.hide(); self.last_scan_results = None
        self.monitoring_area.append(f"Starting scan on {len(targets)} target(s)...")
        self.discovery_file_path = os.path.join(self.output_folder, "discovered_hosts.txt")
        with open(self.discovery_file_path, "w") as f: f.write(f"Host Discovery Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "="*40 + "\n")
        self.worker = ScanWorker(targets, selected_modules)
        self.worker.signals.progress.connect(self.monitoring_area.append)
        self.worker.signals.host_discovered.connect(self.handle_host_discovery)
        self.worker.signals.finished.connect(self.scan_finished)
        self.worker.start()

    def handle_host_discovery(self, target, discovery_data):
        status = discovery_data.get('status', 'down').upper(); os_info = discovery_data.get('os', 'unknown')
        with open(self.discovery_file_path, "a") as f: f.write(f"IP Address: {target}\nStatus: {status}\nOS Guess: {os_info}\n\n")

    def scan_finished(self, results_data):
        self.monitoring_area.append("\n--- ALL SCANS COMPLETE ---"); self.start_scan_button.setEnabled(True); self.last_scan_results = results_data
        
        # --- NEW: Create a single folder for the entire scan run ---
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        scan_folder_name = f"scan_{timestamp}"
        self.current_scan_folder = os.path.join(self.output_folder, scan_folder_name)
        os.makedirs(self.current_scan_folder, exist_ok=True)
        
        for target, modules in results_data.items():
            if modules.get('status') == 'down': continue
            
            for module_name, result in modules.items():
                # --- NEW: Save files as <target_ip>_<module_name>.json ---
                safe_target = target.replace(".", "-")
                filename = f"{safe_target}_{module_name}.json"
                output_file = os.path.join(self.current_scan_folder, filename)
                with open(output_file, "w") as f: json.dump(result, f, indent=4)
        
        self.monitoring_area.append(f"Results saved to: '{self.current_scan_folder}'"); self.view_results_button.show()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Base Output Folder", self.output_folder)
        if folder: self.output_folder = folder; self.output_folder_label.setText(self.output_folder)

    def open_scan_results(self):
        scan_dir = QFileDialog.getExistingDirectory(self, "Select a Previous Scan Folder", self.output_folder)
        if not scan_dir: return
        
        # --- FIX: Set the current_scan_folder when opening a previous scan ---
        self.current_scan_folder = scan_dir
        
        loaded_results = {}
        # --- FIX: More robust logic to load all JSON files from the folder ---
        for filename in os.listdir(scan_dir):
            if filename.endswith(".json"):
                try:
                    # Assumes filename format: <target_ip_with_dashes>_<module_name>.json
                    parts = filename.replace('.json', '').rsplit('_', 1)
                    target_ip = parts[0].replace('-', '.')
                    module_name = parts[1]
                    
                    if target_ip not in loaded_results:
                        loaded_results[target_ip] = {}
                    
                    with open(os.path.join(scan_dir, filename), 'r') as f:
                        loaded_results[target_ip][module_name] = json.load(f)
                except (IndexError, json.JSONDecodeError) as e:
                    self.monitoring_area.append(f"Could not load or parse file {filename}: {e}")
        
        if loaded_results:
            self.last_scan_results = loaded_results
            self.show_results_window()
        else:
            QMessageBox.warning(self, "No Results", "The selected directory does not contain valid .json result files.")

    def show_results_window(self):
        if self.last_scan_results:
            # Pass the current_scan_folder to the results window
            results_dialog = ResultsWindow(self.last_scan_results, self.current_scan_folder, self)
            results_dialog.exec_()
        else: QMessageBox.information(self, "No Results", "No scan results to display.")

class InterfaceSelectionDialog(QDialog):
    def __init__(self, interfaces, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Network Interfaces to Scan")
        self.layout = QVBoxLayout(self)
        self.checkboxes = {}
        self.interfaces_data = interfaces
        if not interfaces: self.layout.addWidget(QLabel("No scannable network interfaces found."))
        else:
            self.layout.addWidget(QLabel("Please select the network(s) you want to scan:"))
            for interface, cidr_string in interfaces.items():
                checkbox = QCheckBox(f"{interface} ({cidr_string})")
                self.checkboxes[interface] = checkbox
                self.layout.addWidget(checkbox)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
    def get_selected_ranges(self):
        selected_ranges = []
        for interface, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                ranges_str = self.interfaces_data[interface]
                selected_ranges.extend([r.strip() for r in ranges_str.split(',')])
        return selected_ranges
