# error_popup.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton

class ErrorPopup(QDialog):
    def __init__(self, error_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Robot Error")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("⚠️ Robot Error Detected"))

        self.table = QTableWidget(1, 3)
        self.table.setHorizontalHeaderLabels(["Type", "Code", "Message"])
        self.table.setItem(0, 0, QTableWidgetItem(str(error_data.get("type"))))
        self.table.setItem(0, 1, QTableWidgetItem(str(error_data.get("code"))))
        self.table.setItem(0, 2, QTableWidgetItem(str(error_data.get("content"))))

        layout.addWidget(self.table)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)
