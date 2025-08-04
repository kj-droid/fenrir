import os
import shutil
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QTextEdit, QDialogButtonBox,
    QCheckBox, QLabel, QScrollArea, QPushButton, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt
from .result_formatters import RESULT_FORMATTERS, format_default

class ResultsWindow(QDialog):
    def __init__(self, results_data, scan_folder_path, parent=None):
        """
        A dialog window to display scan results, with a special interactive
        tab for copying exploit scripts.
        """
        super().__init__(parent)
        self.setWindowTitle("Scan Results")
        self.setGeometry(150, 150, 700, 500)
        self.scan_folder_path = scan_folder_path # Store the path for copying
        
        self.background_pixmap = None
        background_path = os.path.join("gui", "assets", "background.png")
        if os.path.exists(background_path):
            self.background_pixmap = QPixmap(background_path)

        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        self.populate_results(results_data)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.accept)
        self.layout.addWidget(self.buttons)
        
    def resizeEvent(self, event):
        if self.background_pixmap:
            scaled_pixmap = self.background_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            palette = QPalette(); palette.setBrush(QPalette.Window, QBrush(scaled_pixmap)); self.setPalette(palette)
        QDialog.resizeEvent(self, event)

    def populate_results(self, results_data):
        """
        Creates a tab for each module's results. The exploit_finder tab is interactive.
        """
        for target, modules in results_data.items():
            for module_name, result_data in modules.items():
                
                # --- NEW: Special handling for the exploit finder tab ---
                if module_name == 'exploit_finder':
                    tab = self.create_exploit_tab(result_data)
                else:
                    tab = self.create_standard_tab(module_name, result_data)
                
                tab_title = f"{target} - {module_name.replace('_', ' ').title()}"
                self.tabs.addTab(tab, tab_title)

    def create_standard_tab(self, module_name, result_data):
        """Creates a standard read-only text tab."""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        results_text = QTextEdit()
        results_text.setReadOnly(True)
        results_text.setStyleSheet("background-color: rgba(30, 30, 42, 0.8);")
        formatter = RESULT_FORMATTERS.get(module_name, format_default)
        formatted_text = formatter(result_data)
        results_text.setText(formatted_text)
        tab_layout.addWidget(results_text)
        return tab

    def create_exploit_tab(self, result_data):
        """Creates the interactive tab with checkboxes for exploits."""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.exploit_layout = QVBoxLayout(scroll_content) # Store layout to access checkboxes later

        if not isinstance(result_data, dict) or not result_data:
            self.exploit_layout.addWidget(QLabel("No exploits found."))
        else:
            for reference, exploits in result_data.items():
                self.exploit_layout.addWidget(QLabel(f"<b>Reference: {reference}</b>"))
                for exploit in exploits:
                    path = exploit.get("Path")
                    title = exploit.get("Title", "No Title")
                    cb = QCheckBox(f"{title} (EDB-ID: {exploit.get('EDB-ID')})")
                    # Store the full path in a property for later retrieval
                    cb.setProperty("exploit_path", path)
                    self.exploit_layout.addWidget(cb)
        
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)

        copy_button = QPushButton("Copy Selected Exploits to Scan Folder")
        copy_button.clicked.connect(self.copy_selected_exploits)
        tab_layout.addWidget(copy_button)
        
        return tab

    def copy_selected_exploits(self):
        """
        Finds all checked exploits and copies their source files to the scan folder.
        """
        if not self.scan_folder_path:
            QMessageBox.critical(self, "Error", "Scan folder path is not set. Cannot copy exploits.")
            return

        exploits_to_copy = []
        # Iterate through all widgets in the exploit layout
        for i in range(self.exploit_layout.count()):
            widget = self.exploit_layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                exploits_to_copy.append(widget.property("exploit_path"))

        if not exploits_to_copy:
            QMessageBox.information(self, "No Selection", "No exploits were selected to copy.")
            return

        # Create a dedicated 'exploits' subfolder
        exploits_dest_folder = os.path.join(self.scan_folder_path, "exploits")
        os.makedirs(exploits_dest_folder, exist_ok=True)
        
        copied_count = 0
        errors = []
        
        # The base path of the locally cloned exploit-db repo
        exploit_db_base_path = os.path.join("data", "exploit-db")

        for exploit_path in exploits_to_copy:
            source_path = os.path.join(exploit_db_base_path, exploit_path)
            dest_path = os.path.join(exploits_dest_folder, os.path.basename(exploit_path))
            try:
                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)
                    copied_count += 1
                else:
                    errors.append(f"Source file not found: {source_path}")
            except Exception as e:
                errors.append(f"Failed to copy {exploit_path}: {e}")

        message = f"Successfully copied {copied_count} of {len(exploits_to_copy)} selected exploits."
        if errors:
            message += "\n\nErrors occurred:\n" + "\n".join(errors)
        
        QMessageBox.information(self, "Copy Complete", message)
