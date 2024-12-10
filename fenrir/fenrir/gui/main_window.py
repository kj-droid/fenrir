
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtGui import QPixmap
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fenrir GUI")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        logo_label = QLabel()
        pixmap = QPixmap("gui/fenrir_logo.png")
        logo_label.setPixmap(pixmap)
        logo_label.setScaledContents(True)

        main_layout.addWidget(logo_label)
        main_layout.addWidget(QPushButton("Start Scan"))

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
