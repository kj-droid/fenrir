from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QSpinBox, QFormLayout


class ModuleSettings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Module Settings")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        # Example settings form
        form_layout = QFormLayout()
        self.port_range = QLineEdit("1-65535")
        self.thread_count = QSpinBox()
        self.thread_count.setRange(1, 1000)
        self.thread_count.setValue(100)

        form_layout.addRow("Port Range:", self.port_range)
        form_layout.addRow("Thread Count:", self.thread_count)
        layout.addLayout(form_layout)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        """Save the module settings."""
        port_range = self.port_range.text()
        thread_count = self.thread_count.value()
        print(f"Settings saved: Port Range = {port_range}, Thread Count = {thread_count}")
        self.close()
