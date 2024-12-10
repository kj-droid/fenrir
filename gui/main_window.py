import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QCheckBox,
    QWidget, QHBoxLayout, QFileDialog, QTextEdit, QDialog, QFormLayout, QLineEdit, QSpinBox, QListWidget, QMessageBox
)
from PyQt5.QtGui import QPixmap, QDesktopServices
from PyQt5.QtCore import Qt, QUrl



class ModuleSettingsDialog(QDialog):
    def __init__(self, module_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{module_name} Configuration")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Example settings for demonstration purposes
        self.thread_count = QSpinBox()
        self.thread_count.setRange(1, 1000)
        self.thread_count.setValue(100)
        form_layout.addRow("Thread Count:", self.thread_count)

        self.scan_range = QLineEdit("1-65535")
        form_layout.addRow("Port Range:", self.scan_range)

        layout.addLayout(form_layout)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        thread_count = self.thread_count.value()
        scan_range = self.scan_range.text()
        print(f"Settings saved: Thread Count = {thread_count}, Port Range = {scan_range}")
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fenrir")
        self.setGeometry(100, 100, 1024, 768)

        # Main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Logo with hyperlink
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        if os.path.exists("gui/fenrir_logo_b.png"):
            pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "fenrir_logo_b.png")).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("Fenrir")

        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        logo_label.setStyleSheet("margin-right: 10px;")

        hyperlink_label = QLabel('<a href="https://fenrir-docs.example.com" style="color: white;">Fenrir Documentation</a>')
        hyperlink_label.setOpenExternalLinks(True)
        hyperlink_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        hyperlink_label.setStyleSheet("color: white; font-size: 14px;")

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(hyperlink_label)
        main_layout.addLayout(logo_layout)

        # Target configuration
        target_label = QLabel("Target Configuration:")
        target_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        main_layout.addWidget(target_label)

        target_input_layout = QHBoxLayout()

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter IP, hostname, or network range (e.g., 192.168.1.1/24)")
        target_input_layout.addWidget(self.target_input)

        add_target_button = QPushButton("Add Target")
        add_target_button.clicked.connect(self.add_target)
        target_input_layout.addWidget(add_target_button)

        main_layout.addLayout(target_input_layout)

        self.target_list = QListWidget()
        main_layout.addWidget(self.target_list)

        target_button_layout = QHBoxLayout()

        remove_target_button = QPushButton("Remove Selected")
        remove_target_button.clicked.connect(self.remove_selected_target)
        target_button_layout.addWidget(remove_target_button)

        clear_targets_button = QPushButton("Clear All")
        clear_targets_button.clicked.connect(self.clear_targets)
        target_button_layout.addWidget(clear_targets_button)

        main_layout.addLayout(target_button_layout)

        # Module selection
        module_label = QLabel("Select Modules to Run:")
        module_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        main_layout.addWidget(module_label)

        self.module_checkboxes = {
            "Port Scanner": QCheckBox("Port Scanner"),
            "Web Scanner": QCheckBox("Web Scanner"),
            "Vulnerability Identifier": QCheckBox("Vulnerability Identifier"),
            "Exploit Finder": QCheckBox("Exploit Finder"),
            "Threat Intelligence": QCheckBox("Threat Intelligence"),
            "IoT Scanner": QCheckBox("IoT Scanner"),
            "Mobile Scanner": QCheckBox("Mobile Scanner"),
            "Cloud Scanner": QCheckBox("Cloud Scanner"),
        }

        for name, checkbox in self.module_checkboxes.items():
            module_layout = QHBoxLayout()
            module_layout.addWidget(checkbox)

            help_button = QPushButton("?")
            help_button.setFixedWidth(30)
            help_button.clicked.connect(lambda _, n=name: self.show_help(n))
            module_layout.addWidget(help_button)

            configure_button = QPushButton("Configure")
            configure_button.clicked.connect(lambda _, n=name: self.open_settings(n))
            module_layout.addWidget(configure_button)

            main_layout.addLayout(module_layout)

        # Output folder selection
        output_button = QPushButton("Select Output Folder")
        output_button.clicked.connect(self.select_output_folder)
        main_layout.addWidget(output_button)

        self.output_folder_label = QLabel("Output Folder: Not Selected")
        self.output_folder_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.output_folder_label)

        # Start Scan button
        start_scan_button = QPushButton("Start Scan")
        start_scan_button.clicked.connect(self.start_scan)
        main_layout.addWidget(start_scan_button)

        # Monitoring section
        monitor_label = QLabel("Monitoring:")
        monitor_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        main_layout.addWidget(monitor_label)

        self.monitoring_area = QTextEdit()
        self.monitoring_area.setReadOnly(True)
        self.monitoring_area.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        main_layout.addWidget(self.monitoring_area)

    def set_background(self, image_path="gui/fenrir_logo_c.png", transparency=0.5):
        """
        Set the background image with adjustable transparency.
        :param image_path: Path to the background image file.
        :param transparency: Transparency level (0.0 to 1.0). Default is 1.0 (opaque).
        """
        if os.path.exists(gui/fenrir_logo_c.png):
            #pixmap = QPixmap(gui/fenrir_logo_c.png)
            pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "fenrir_logo_c.png"))
            
            # Scale the image to fit the window size
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            # Create a transparent pixmap
            transparent_image = QImage(scaled_pixmap.size(), QImage.Format_ARGB32)
            transparent_image.fill(Qt.transparent)

            # Apply transparency using QPainter
            painter = QPainter(transparent_image)
            painter.setOpacity(transparency)
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.end()

            # Convert the transparent QImage back to QPixmap
            transparent_pixmap = QPixmap.fromImage(transparent_image)

            # Set the transparent pixmap as the background
            palette = QPalette()
            palette.setBrush(QPalette.Background, QBrush(transparent_pixmap))
            self.setPalette(palette)
        else:
            print(f"Error: Background image not found at {image_path}")

    def add_target(self):
        """Add a target to the list."""
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Error", "Target cannot be empty!")
            return
        self.target_list.addItem(target)
        self.target_input.clear()

    def remove_selected_target(self):
        """Remove the selected target from the list."""
        selected_items = self.target_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "No target selected!")
            return
        for item in selected_items:
            self.target_list.takeItem(self.target_list.row(item))

    def clear_targets(self):
        """Clear all targets from the list."""
        self.target_list.clear()

    def open_settings(self, module_name):
        """Open configuration dialog for the selected module."""
        dialog = ModuleSettingsDialog(module_name, self)
        dialog.exec_()

    def show_help(self, module_name):
        """Show a help dialog with information about the module."""
        help_texts = {
            "Port Scanner": "Scans the target for open ports and services.",
            "Web Scanner": "Analyzes websites for vulnerabilities and misconfigurations.",
            "Vulnerability Identifier": "Matches detected services with known vulnerabilities.",
            "Exploit Finder": "Finds exploits for identified vulnerabilities.",
            "Threat Intelligence": "Gathers data from external threat intelligence sources.",
            "IoT Scanner": "Scans IoT protocols and devices for security issues.",
            "Mobile Scanner": "Analyzes mobile app APIs and permissions for risks.",
            "Cloud Scanner": "Identifies misconfigurations in cloud environments.",
        }
        help_message = help_texts.get(module_name, "No help available for this module.")
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{module_name} Help")
        layout = QVBoxLayout()
        label = QLabel(help_message)
        label.setWordWrap(True)
        layout.addWidget(label)
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def select_output_folder(self):
        """Select an output folder for saving scan results."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder_label.setText(f"Output Folder: {folder}")
            print(f"Output folder selected: {folder}")

    def start_scan(self):
        """Start the scan with selected modules and the specified targets."""
        targets = [self.target_list.item(i).text() for i in range(self.target_list.count())]
        if not targets:
            self.monitoring_area.append("Error: No targets specified.")
            return

        selected_modules = [name for name, checkbox in self.module_checkboxes.items() if checkbox.isChecked()]
        if not selected_modules:
            self.monitoring_area.append("Error: No modules selected.")
            return

        self.monitoring_area.append(f"Starting scan on targets: {', '.join(targets)}")
        self.monitoring_area.append(f"Modules: {', '.join(selected_modules)}")
        # Add scanning logic here


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
