from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QListWidget, QPushButton
from robot_db import fetch_all_tool_names, get_full_tool_data
from PyQt5.QtGui import QIcon

class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TuniBot - Robot Initilize -")
        self.resize(500, 400)
        self.setWindowIcon(QIcon("/root/桌面/Aubo/Logo.jpeg"))

        # List widget instead of ComboBox
        self.tool_list = QListWidget()
        self.tool_list.addItems(fetch_all_tool_names())
        self.tool_list.currentItemChanged.connect(self.on_item_changed)

        self.info_label = QLabel("Tool info here...")

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tool Name:"))
        layout.addWidget(self.tool_list)
        layout.addWidget(self.info_label)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

        # Initialize with first item if available
        if self.tool_list.count() > 0:
            self.tool_list.setCurrentRow(0)
            self.update_display(self.tool_list.currentItem().text())

    def on_item_changed(self, current, previous):
        if current:
            self.update_display(current.text())

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
        current_item = self.tool_list.currentItem()
        if current_item:
            self.selected_tool = current_item.text()
        else:
            self.selected_tool = None
        self.selected_ip = "127.0.0.1"
        self.accept()

