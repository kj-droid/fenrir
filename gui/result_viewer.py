from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton


class ResultViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Results")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setText("Scan results will appear here...")
        layout.addWidget(self.results_display)

        # Refresh button
        refresh_button = QPushButton("Refresh Results")
        refresh_button.clicked.connect(self.refresh_results)
        layout.addWidget(refresh_button)

        self.setLayout(layout)

    def refresh_results(self):
        """Refresh the results display."""
        # Placeholder for loading results from output folder
        self.results_display.setText("Updated scan results will appear here...")
