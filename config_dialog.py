from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QVBoxLayout, QLineEdit, QPushButton
from robot_db import fetch_all_tool_names, get_full_tool_data
from PyQt5.QtGui import QFont, QIcon
class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TuniBot - Robot Initilize -")
        self.resize(500, 400)
        self.setWindowIcon(QIcon("C:/Users/Emna/Downloads/lgo.jpeg"))
        self.tool_combo = QComboBox()
        self.tool_combo.addItems(fetch_all_tool_names())
        self.tool_combo.currentTextChanged.connect(self.update_display)

        self.ip_combo = QComboBox()
        self.ip_combo.addItems(["192.168.11.129", "192.168.0.23"])

        self.info_label = QLabel("Tool info here...")

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tool Name:"))
        layout.addWidget(self.tool_combo)
        layout.addWidget(QLabel("Robot IP:"))
        layout.addWidget(self.ip_combo)
        layout.addWidget(self.info_label)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

        self.update_display(self.tool_combo.currentText())

    def update_display(self, tool_name):
        data = get_full_tool_data(tool_name)
        kin = data['kinematics']
        dyn = data['dynamics']

        self.info_label.setText(f"""
Kinematics: {kin['kinematics_name']}
End Pos: ({kin['end_pos_x']}, {kin['end_pos_y']}, {kin['end_pos_z']})
End Ori: ({kin['end_ori_rx']}, {kin['end_ori_ry']}, {kin['end_ori_rz']})

Dynamics: {dyn['dynamics_name']}
Payload: {dyn['payload']}
Gravity Center: ({dyn['gravity_center_x']}, {dyn['gravity_center_y']}, {dyn['gravity_center_z']})
""")

    def save_settings(self):
        self.selected_tool = self.tool_combo.currentText()
        self.selected_ip = self.ip_combo.currentText()
        self.accept()
