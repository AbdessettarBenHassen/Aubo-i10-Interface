from PyQt5.QtWidgets import QApplication,QMainWindow,QSpinBox,QDoubleSpinBox,QTreeWidgetItem,QListWidget, QTreeWidget, QDialog,QPushButton,QMessageBox, QStackedWidget, QWidget, QVBoxLayout, QLabel, QGridLayout, QHBoxLayout, QSlider, QLineEdit, QRadioButton, QGroupBox, QComboBox, QCheckBox, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont, QIcon
import sys
from threads import joint_updater
from functools import partial
import utils as utl 
from utils import *
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QGridLayout
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
import json
import os
from PyQt5.QtGui import QPixmap,QDoubleValidator
from clavier import *
from PyQt5.QtCore import QStandardPaths
from courbe import *
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox 
# import threading

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
class EditSpeedDialog(QDialog):
    def __init__(self, parent=None, current_speed=0.0):
        super().__init__(parent)
        self.setWindowTitle("Edit Speed")
        self.setFixedSize(300, 120)

        layout = QVBoxLayout()

        # Champ pour la vitesse
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed (mm/s):")
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(0.1, 2000)
        self.speed_spinbox.setValue(current_speed)
        self.speed_spinbox.setDecimals(2)
        speed_layout.addWidget(speed_label)
        self.speed_spinbox.setStyleSheet("""
            QDoubleSpinBox {
                padding: 5px;
                border: 1px solid #A9A9A9;
                border-radius: 3px;
                background-color: white;
                font-size: 11pt;
            }
        """)
        speed_layout.addWidget(self.speed_spinbox)
        layout.addLayout(speed_layout)

        # Boutons OK et Annuler
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4682B4;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: white;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #87CEEB;
            }
            QPushButton:pressed {
                background-color: #4169E1;
            }
        """)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: black;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #B0C4DE;
            }
            QPushButton:pressed {
                background-color: #4682B4;
                color: white;
            }
        """)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_speed(self):
        return self.speed_spinbox.value()
class SpeedAccDialog(QDialog):
    def __init__(self, parent=None, speed_data=None):
        super().__init__(parent)
        self.setWindowTitle("Set Speed and Acceleration")
        self.setFixedSize(300, 150)

        # Layout principal
        layout = QVBoxLayout()

        # End Linear Speed
        speed_layout = QHBoxLayout()
        speed_label = QLabel("End Linear Speed (mm/s):")
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(1, 2000)
        self.speed_spinbox.setValue(2000)  # Valeur par défaut : 2000 mm/s
        self.speed_spinbox.setDecimals(2)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_spinbox)
        layout.addLayout(speed_layout)

        # End Linear Acceleration
        acc_layout = QHBoxLayout()
        acc_label = QLabel("End Linear Acc (mm/s²):")
        self.acc_spinbox = QDoubleSpinBox()
        self.acc_spinbox.setRange(1, 2000)
        self.acc_spinbox.setValue(2000)  # Valeur par défaut : 2000 mm/s²
        self.acc_spinbox.setDecimals(2)
        acc_layout.addWidget(acc_label)
        acc_layout.addWidget(self.acc_spinbox)
        layout.addLayout(acc_layout)

        # Charger les valeurs existantes si elles sont fournies
        if speed_data:
            speed = float(speed_data.get("speed", 2000))
            acceleration = float(speed_data.get("acceleration", 2000))
            self.speed_spinbox.setValue(speed)
            self.acc_spinbox.setValue(acceleration)
            print(f"SpeedAccDialog - Valeurs chargées : Speed={speed} mm/s, Acceleration={acceleration} mm/s²")
        else:
            self.speed_spinbox.setValue(2000)
            self.acc_spinbox.setValue(2000)
            print("SpeedAccDialog - Aucune speed_data fournie, valeurs par défaut utilisées")

        # Boutons OK et Annuler
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_data(self):
        """
        Retourne un dictionnaire contenant les valeurs de vitesse et d'accélération saisies.
        """
        speed = self.speed_spinbox.value()
        acceleration = self.acc_spinbox.value()
        return {"speed": speed, "acceleration": acceleration}

    def get_values(self):
        # Retourner les valeurs directement en mm/s et mm/s²
        speed = self.speed_spinbox.value()
        acc = self.acc_spinbox.value()
        return speed, acc

class JointSpeedAccDialog(QDialog):
    def __init__(self, parent=None, speed_data=None):
        super().__init__(parent)
        self.setWindowTitle("Set Joint Speeds and Accelerations")
        self.setFixedSize(400, 450)

        layout = QVBoxLayout()

        parameters_label = QLabel("Parameters")
        parameters_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(parameters_label)

        # Initialiser les valeurs par défaut en mm/s
        self.speed_values = [2000.0] * 6  # mm/s (au lieu de rad/s)
        self.acc_values = [2000.0] * 6    # mm/s²

        # Affichage des vitesses en mm/s
        self.speed_display_label = QLabel("Speed(mm/s): 2000.0,2000.0,2000.0,2000.0,2000.0,2000.0")
        layout.addWidget(self.speed_display_label)

        # Affichage des accélérations en mm/s²
        self.acc_display_label = QLabel("Acc(mm/s²): 2000.0,2000.0,2000.0,2000.0,2000.0,2000.0")
        layout.addWidget(self.acc_display_label)

        layout.addSpacing(10)

        joint_select_layout = QHBoxLayout()
        joint_select_label = QLabel("Select Joint:")
        self.joint_combo = QComboBox()
        self.joint_combo.addItems(["Joint1 Speed", "Joint2 Speed", "Joint3 Speed", "Joint4 Speed", "Joint5 Speed", "Joint6 Speed"])
        self.joint_combo.currentIndexChanged.connect(self.update_labels)
        joint_select_layout.addWidget(joint_select_label)
        joint_select_layout.addWidget(self.joint_combo)
        layout.addLayout(joint_select_layout)

        # Ajuster la plage pour mm/s
        speed_layout = QHBoxLayout()
        self.speed_label = QLabel(f"{self.joint_combo.currentText()}:")
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(0.1, 2000.0)  # Plage en mm/s
        self.speed_spinbox.setValue(2000.0)       # Valeur par défaut 2000 mm/s
        self.speed_spinbox.setDecimals(2)
        self.speed_spinbox.valueChanged.connect(self.update_speed)
        speed_range_label = QLabel("(0.1–2000.0) mm/s")
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_spinbox)
        speed_layout.addWidget(speed_range_label)
        layout.addLayout(speed_layout)

        acc_layout = QHBoxLayout()
        self.acc_label = QLabel(f"{self.joint_combo.currentText().replace('Speed', 'Acc')}:")
        self.acc_spinbox = QDoubleSpinBox()
        self.acc_spinbox.setRange(0.1, 2000.0)  # Plage en mm/s²
        self.acc_spinbox.setValue(2000.0)       # Valeur par défaut 2000 mm/s²
        self.acc_spinbox.setDecimals(2)
        self.acc_spinbox.valueChanged.connect(self.update_acc)
        acc_range_label = QLabel("(0.1–2000.0) mm/s²")
        acc_layout.addWidget(self.acc_label)
        acc_layout.addWidget(self.acc_spinbox)
        acc_layout.addWidget(acc_range_label)
        layout.addLayout(acc_layout)

        share_buttons_layout = QHBoxLayout()
        self.share_speed_button = QPushButton("Share Speed")
        self.share_speed_button.clicked.connect(self.apply_share_speed)
        self.share_acc_button = QPushButton("Share Acc")
        self.share_acc_button.clicked.connect(self.apply_share_acc)
        share_buttons_layout.addWidget(self.share_speed_button)
        share_buttons_layout.addWidget(self.share_acc_button)
        layout.addLayout(share_buttons_layout)

        if speed_data:
            speed = float(speed_data.get("speed", 2000.0))
            acceleration = float(speed_data.get("acceleration", 2000.0))
            self.speed_spinbox.setValue(speed)
            self.acc_spinbox.setValue(acceleration)
            self.speed_values = [speed] * 6
            self.acc_values = [acceleration] * 6
            self.update_parameters_display()

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def update_labels(self):
        current_index = self.joint_combo.currentIndex()
        self.speed_label.setText(f"{self.joint_combo.currentText()}:")
        self.acc_label.setText(f"{self.joint_combo.currentText().replace('Speed', 'Acc')}:")
        self.speed_spinbox.setValue(self.speed_values[current_index])
        self.acc_spinbox.setValue(self.acc_values[current_index])

    def update_speed(self):
        current_index = self.joint_combo.currentIndex()
        self.speed_values[current_index] = self.speed_spinbox.value()
        self.update_parameters_display()

    def update_acc(self):
        current_index = self.joint_combo.currentIndex()
        self.acc_values[current_index] = self.acc_spinbox.value()
        self.update_parameters_display()

    def apply_share_speed(self):
        current_speed = self.speed_spinbox.value()
        self.speed_values = [current_speed] * 6
        self.speed_spinbox.setValue(current_speed)
        self.update_parameters_display()

    def apply_share_acc(self):
        current_acc = self.acc_spinbox.value()
        self.acc_values = [current_acc] * 6
        self.acc_spinbox.setValue(current_acc)
        self.update_parameters_display()

    def update_parameters_display(self):
        speed_text = ", ".join(f"{value:.2f}" for value in self.speed_values)
        acc_text = ", ".join(f"{value:.2f}" for value in self.acc_values)
        self.speed_display_label.setText(f"Speed(mm/s): {speed_text}")
        self.acc_display_label.setText(f"Acc(mm/s²): {acc_text}")

    def get_values(self):
        # Convertir les vitesses et accélérations de mm/s en rad/s
        # Hypothèse : longueur moyenne du bras = 500 mm (à ajuster selon votre robot)
        radius = 500.0  # Longueur du bras en mm (à ajuster)
        speed_mm_s = self.speed_values  # Vitesse en mm/s
        acc_mm_s2 = self.acc_values     # Accélération en mm/s²
        speed_rad_s = [s / radius for s in speed_mm_s]  # Conversion en rad/s
        acc_rad_s2 = [a / radius for a in acc_mm_s2]    # Conversion en rad/s²
        return speed_rad_s, acc_rad_s2

    def get_data(self):
        speed = self.speed_spinbox.value()
        acceleration = self.acc_spinbox.value()
        return {"speed": speed, "acceleration": acceleration}

class MoveCircleDialog(QDialog):
    def __init__(self, robot, joint_updater, parent=None):
        super().__init__(parent)
        self.robot = robot
        self.joint_updater = joint_updater
        self.setWindowTitle("Capture Move Circle Waypoints")
        self.first_joints = None
        self.second_joints = None
        self.third_joints = None
        self.current_joints = None
        
        # Connecter le signal joints_updated pour mettre à jour les joints en temps réel
        self.joint_updater.joints_updated.connect(self.update_current_joints)
        
        # Layout
        layout = QVBoxLayout()
        
        # Labels pour afficher la position actuelle
        self.current_position_label = QLabel("Position actuelle : Non lue")
        layout.addWidget(self.current_position_label)
        
        # Boutons pour capturer les positions
        self.capture_first_btn = QPushButton("Capturer 1ère position")
        self.capture_first_btn.clicked.connect(self.capture_first)
        layout.addWidget(self.capture_first_btn)
        
        self.capture_second_btn = QPushButton("Capturer 2ème position")
        self.capture_second_btn.clicked.connect(self.capture_second)
        self.capture_second_btn.setEnabled(False)
        layout.addWidget(self.capture_second_btn)
        
        self.capture_third_btn = QPushButton("Capturer 3ème position")
        self.capture_third_btn.clicked.connect(self.capture_third)
        self.capture_third_btn.setEnabled(False)
        layout.addWidget(self.capture_third_btn)
        
        # Bouton pour confirmer
        self.confirm_btn = QPushButton("Confirmer")
        self.confirm_btn.clicked.connect(self.accept)
        self.confirm_btn.setEnabled(False)
        layout.addWidget(self.confirm_btn)
        
        # Bouton pour annuler
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        self.setLayout(layout)
        
        # Capturer la position initiale immédiatement
        self.update_current_joints_from_robot()
    
    def update_current_joints_from_robot(self):
        """Mettre à jour les joints actuels directement à partir du robot."""
        current_coordinate = self.robot.get_current_waypoint()
        joints = current_coordinate["joint"]
        self.current_joints = [math.degrees(j) for j in joints]
        self.current_position_label.setText(f"Position actuelle : {', '.join(map(lambda x: f'{x:.2f}', self.current_joints))}")
    
    def update_current_joints(self, joints):
        """Mettre à jour les joints actuels à partir du signal joints_updated."""
        self.current_joints = [math.degrees(j) for j in joints]
        self.current_position_label.setText(f"Position actuelle : {', '.join(map(lambda x: f'{x:.2f}', self.current_joints))}")
    
    def capture_first(self):
        """Capturer la première position."""
        self.update_current_joints_from_robot()
        if self.current_joints is None:
            QMessageBox.warning(self, "Erreur", "Aucune position actuelle détectée. Déplacez le robot et réessayez.")
            return
        self.first_joints = self.current_joints[:]
        self.capture_first_btn.setEnabled(False)
        self.capture_second_btn.setEnabled(True)
        QMessageBox.information(self, "Succès", f"1ère position capturée : {', '.join(map(lambda x: f'{x:.2f}', self.first_joints))}")
    
    def capture_second(self):
        """Capturer la deuxième position."""
        self.update_current_joints_from_robot()
        if self.current_joints is None:
            QMessageBox.warning(self, "Erreur", "Aucune position actuelle détectée. Déplacez le robot et réessayez.")
            return
        if self.current_joints == self.first_joints:
            QMessageBox.warning(self, "Erreur", "La 2ème position doit être différente de la 1ère position.")
            return
        self.second_joints = self.current_joints[:]
        self.capture_second_btn.setEnabled(False)
        self.capture_third_btn.setEnabled(True)
        QMessageBox.information(self, "Succès", f"2ème position capturée : {', '.join(map(lambda x: f'{x:.2f}', self.second_joints))}")
    
    def capture_third(self):
        """Capturer la troisième position."""
        self.update_current_joints_from_robot()
        if self.current_joints is None:
            QMessageBox.warning(self, "Erreur", "Aucune position actuelle détectée. Déplacez le robot et réessayez.")
            return
        if self.current_joints == self.first_joints or self.current_joints == self.second_joints:
            QMessageBox.warning(self, "Erreur", "La 3ème position doit être différente des positions précédentes.")
            return
        self.third_joints = self.current_joints[:]
        self.capture_third_btn.setEnabled(False)
        self.confirm_btn.setEnabled(True)
        QMessageBox.information(self, "Succès", f"3ème position capturée : {', '.join(map(lambda x: f'{x:.2f}', self.third_joints))}")
    
    def get_waypoints(self):
        """Retourner les trois points de passage capturés."""
        return self.first_joints, self.second_joints, self.third_joints

class SaveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Project")
        self.setFixedSize(300, 100)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self.program_name_input = QLineEdit()
        self.program_name_input.setPlaceholderText("Please input program name")
        self.program_name_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #A9A9A9;
                border-radius: 3px;
                background-color: #F5F5F5;  /* Correction de la couleur */
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.program_name_input)

        save_button = QPushButton("Save")
        save_button.setFixedSize(60, 30)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: black;
                font-weight: bold;
                font-size: 11pt;
                box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            QPushButton:pressed {
                background-color: #4682B4;
                color: white;
                box-shadow: inset 1px 1px 2px rgba(0, 0, 0, 0.2);
            }
        """)
        save_button.clicked.connect(self.accept)
        layout.addWidget(save_button)

        self.setLayout(layout)
class WeldingMachineController:
    def __init__(self):
        self.connected = False
        self.current_settings = {
            'current': 0,
            'voltage': 0,
            'gas_flow': False,  # État du gaz
            'gas_preflow_time': 1.0,  # Temps en secondes
            'gas_postflow_time': 2.0   # Temps en secondes
        }
    
    def set_gas(self,robot, state: bool, flow_time: float = None):
        """Contrôle l'écoulement du gaz de protection"""
        # self.connected = True
        # if not self.connected:
        #     raise ConnectionError("Machine non connectée")
        
        # self.current_settings['gas_flow'] = state
        
        # if flow_time is not None:
        #     if state:  # Pre-flow
        #         self.current_settings['gas_preflow_time'] = flow_time
        #     else:      # Post-flow
        #         self.current_settings['gas_postflow_time'] = flow_time
        robot.set_board_io_status(RobotIOType.User_DO, RobotUserIoName.user_do_01, state)
        # time.sleep(flow_time)
        print(f"Gaz {'activé' if state else 'désactivé'} "
              f"(Temps: {flow_time}s)" if flow_time else "")
        
        return True
    
    def get_current(self):
            """Récupérer le courant actuel."""
            return self.current
    
    # def start_gas_preflow(self, time: float = None):
    #     """Démarre le pré-écoulement du gaz"""
    #     flow_time = time or self.current_settings['gas_preflow_time']
    #     return self.set_gas(True, flow_time)
    
    # def stop_gas_postflow(self, time: float = None):
    #     """Démarre le post-écoulement du gaz"""
    #     flow_time = time or self.current_settings['gas_postflow_time']
    #     return self.set_gas(False, flow_time)
    def set_arc_signal(self, robot,state):
        # Code pour activer/désactiver le signal d'arc
        robot.set_board_io_status(RobotIOType.User_DO, RobotUserIoName.user_do_00, state)

        
    def set_current(self,robot, current):
            """Définir le* courant de soudage."""
            self.current = float(current)
            robot.set_board_io_status(RobotIOType.User_AO, RobotUserIoName.user_ao_00, current)
            print(f"Courant défini à {self.current:.1f} A")


    def set_voltage(self, robot,voltage):
        """Définir la tension de soudage."""
        self.voltage = float(voltage)
        robot.set_board_io_status(RobotIOType.User_AO, RobotUserIoName.user_ao_01, voltage)

        print(f"Tension définie à {self.voltage:.1f} V")

    def detect_arc(self,robot, timeout):
            start_time = time.time()
            while time.time() - start_time < timeout:
                current = self.get_current()
                robot.set_board_io_status(RobotIOType.User_DI, RobotUserIoName.user_di_00, timeout)

                if current > 5.0:  # Adjust threshold based on your machine
                    return True
                time.sleep(0.1)
            return False

class MainWindow(QMainWindow):
    def __init__(self,robot):
        super().__init__()

        
        self.robot = robot
        self.setWindowTitle("Aubo i10 Interface")
        self.setGeometry(100, 100, 1024, 768)
        self.joint_value_displays = []  # Liste pour stocker les QLineEdit des joints
        self.joint_value_labels = [] 
        self.step_mode_checkbox = QCheckBox("Step Mode")
        self.st = False
        self.config_file = self.get_config_path()
        self.load_parameters_file() 
        self.curve_image_path = "courbe.jpg"
        self.save_dir = os.path.join(os.getcwd(), "programs")
        self.save_file = os.path.join(self.save_dir, "saved_programs.txt")
        self.saved_programs = {}
        self.is_modified = False  # Indicateur de modification
        self.current_program_name = None  # Initialize current_program_name
        self.load_saved_programs()
        self.robot.step_mode_checkbox = self.step_mode_checkbox
        self.current_file = "0"
        self.welding_machine = WeldingMachineController()

        joint_updater.add_move_circle_with_positions.connect(self.handle_add_move_circle_with_positions)
        joint_updater.add_move_line_with_position.connect(self.handle_add_move_line_with_position)
        joint_updater.add_move_joint_with_position.connect(self.handle_add_move_joint_with_position)
        joint_updater.add_arc_start.connect(self.handle_add_arc_start)
        joint_updater.add_arc_end.connect(self.handle_add_arc_end)
        joint_updater.execute_all_movements.connect(self.handle_execute_all_movements)
        joint_updater.request_confirmation.connect(self.handle_request_confirmation)
        
       
        joint_updater.delete_last_tree_item.connect(self.handle_delete_last_tree_item)

                # Appliquer un style CSS moderne
        self.setStyleSheet("""
            QWidget {
                font-family: 'Arial';
                font-size: 14px;
                background-color: #F4F6F7;  /* Fond clair et neutre */
            }
            QPushButton {
                background-color: #2E86C1;  /* Bleu professionnel et technologique */
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2472A4;  /* Bleu légèrement plus foncé au survol */
            }
            QPushButton:pressed {
                background-color: #1B4F72;  /* Bleu plus sombre lors du clic */
            }
            QGroupBox {
                border: 2px solid #D1D3D4;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #AAB7B8;
                border-radius: 3px;
                background-color: white;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QSlider::groove:horizontal {
                background-color: #D6DBDF;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background-color: #2E86C1;  /* Bleu professionnel pour le curseur */
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)

        # Main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Barre de navigation
        self.nav_buttons = QHBoxLayout()
        self.main_layout.addLayout(self.nav_buttons)

        self.pages = QStackedWidget()
        self.main_layout.addWidget(self.pages)

        # Création des pages
        self.robot_teaching_page = self.create_robot_teaching_page()
        self.programming_page = self.create_programming_page() # Page vide pour Programming
        self.settings_page = self.create_settings_page()  # Page Settings avec le contenu de Programming
        self.extensions_page = self.create_extensions_page()
        self.system_info_page = self.create_page("System Info")
        self.about_page = self.create_page("About")
        
        self.pages.addWidget(self.robot_teaching_page)
        self.pages.addWidget(self.programming_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.extensions_page)
        self.pages.addWidget(self.system_info_page)
        self.pages.addWidget(self.about_page)


        # Ajouter les boutons de navigation
        self.add_nav_button("Robot Teaching", self.robot_teaching_page)
        self.add_nav_button("Programming", self.programming_page)
        self.add_nav_button("Settings", self.settings_page)
        self.add_nav_button("Extensions", self.extensions_page)
        self.add_nav_button("System Info", self.system_info_page)
        self.add_nav_button("About", self.about_page)

        joint_updater.joints_updated.connect(self.update_joint_values)
        joint_updater.joints_updated.connect(self.update_manipulator_pose)
    def handle_request_confirmation(self, position, position_number, message):
        """Afficher une fenêtre de confirmation et définir le résultat."""
        from threads import set_confirmation_result
        reply = QMessageBox.question(self, f"Confirmer Position {position_number}", message,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        result = (reply == QMessageBox.Yes)
        set_confirmation_result(result)
    
    def handle_request_confirmation(self, position, position_number, message):
        """Afficher une fenêtre de confirmation et définir le résultat."""
        from threads import set_confirmation_result
        reply = QMessageBox.question(self, f"Confirmer Position {position_number}", message,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        result = (reply == QMessageBox.Yes)
        set_confirmation_result(result)
    
    def handle_add_move_circle_with_positions(self, first_joints, second_joints, third_joints):
        """Ajouter une commande Move Circle avec les positions capturées via user_di_02."""
        self.add_move_circle_to_tree(first_joints, second_joints, third_joints)
    def handle_execute_all_movements(self):
        """Ajouter une commande Move Circle avec les positions capturées via user_di_02."""
        self.execute_all_movements()
    
    def handle_add_move_line_with_position(self, joints):
        """Ajouter une commande Move Line avec la position capturée via user_di_01."""
        self.add_move_line_to_tree(joints)
    def handle_add_move_joint_with_position(self, joints):
        """Ajouter une commande Move Line avec la position capturée via user_di_01."""
        self.add_move_joint_to_tree(joints)
    def handle_add_arc_start(self):
        """Ajouter une commande Move Line avec la position capturée via user_di_01."""
        self.add_arc_start_to_tree()
    
    def handle_add_arc_end(self):
        """Ajouter une commande Move Joint avec la position capturée via user_di_00."""
        self.add_arc_end_to_tree()
    def handle_delete_last_tree_item(self):
        """Supprime le dernier élément de l'arborescence du projet."""
        root = self.project_tree.topLevelItem(0)
        if not root:
            print("Aucune arborescence de projet trouvée.")
            return

        child_count = root.childCount()
        if child_count == 0:
            print("L'arborescence est vide, rien à supprimer.")
            return

        # Supprimer le dernier enfant
        last_item = root.child(child_count - 1)
        root.removeChild(last_item)
        print(f"Élément supprimé : {last_item.text(0)}")

        # Si l'arborescence est vide après suppression, ajouter un élément "Empty"
        if root.childCount() == 0:
            empty_item = QTreeWidgetItem(["Empty"])
            root.addChild(empty_item)
            root.setExpanded(True)

        self.is_modified = True  # Marquer comme modifié

    def get_config_path(self):
        """Retourne le chemin du fichier de configuration"""
        config_dir = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return os.path.join(config_dir, "welding_parameters.json")

    def load_parameters_file(self):
        """Charge les paramètres depuis le fichier JSON"""
        try:
            config_path = self.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    # Handle both formats (wrapped and direct)
                    self.file_parameters = data.get("welding_parameters", data)
                
                # Ensure global_values exists
                if "global_values" not in self.file_parameters:
                    self.file_parameters["global_values"] = self.get_default_parameters()["global_values"]
            else:
                self.file_parameters = self.get_default_parameters()
                self.save_parameters_file()
        except Exception as e:
            print(f"Error loading parameters: {e}")
            self.file_parameters = self.get_default_parameters()
            self.calculate_ponte()
    def save_parameters_file(self):
        """Sauvegarde tous les paramètres dans un fichier JSON"""
        try:
            # Ensure global_values exists before saving
            if "global_values" not in self.file_parameters:
                self.file_parameters["global_values"] = {}
            config_path = self.get_config_path()  # Utilisez une seule variable
            with open(config_path, "w") as f:
                json.dump(self.file_parameters, f, indent=4)
            print(f"Paramètres sauvegardés dans {config_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres : {e}")

    def get_default_parameters(self):
        """Retourne les paramètres par défaut"""
        return {
        "global_values": {  # Nouvelle section pour les valeurs partagées
            "y_value1": "10.000",
            "y_value2": "0.000",
            "x_value1": "5.000",
            "x_value2": "315.000",
            "y_value3": "12.000",
            "y_value4": "2.000",
            "x_value3": "10.000",
            "x_value4": "320.000",
        },
            "0": {
                "weld_current": "222.000",
                "weld_voltage": "1.500",
                "arc_ending_a": "40.000",
                "arc_ending_v": "1.000",
                "remove_stick_a": "50.000",
                "remove_stick_v": "0.000",
                "arc_ending_s": "0.400",
                "proof_stick": "0.600",
                "starting_a": "140.000",
                "starting_v": "0.600",
                "starting_s": "1.500",
                "reserve": "0.800",
                "wire_fb": "0.100",
                "speed": "0.000",
                "comment": ""
            },
            "1": {
                "weld_current": "120.000",
                "weld_voltage": "1.200",
                "arc_ending_a": "30.000",
                "arc_ending_v": "0.800",
                "remove_stick_a": "40.000",
                "remove_stick_v": "0.000",
                "arc_ending_s": "0.300",
                "proof_stick": "0.500",
                "starting_a": "130.000",
                "starting_v": "0.500",
                "starting_s": "1.200",
                "reserve": "0.700",
                "wire_fb": "0.080",
                "speed": "0.000",
                "comment": ""
            },
            "2": {
                "weld_current": "150.000",
                "weld_voltage": "1.300",
                "arc_ending_a": "35.000",
                "arc_ending_v": "0.900",
                "remove_stick_a": "45.000",
                "remove_stick_v": "0.000",
                "arc_ending_s": "0.350",
                "proof_stick": "0.550",
                "starting_a": "135.000",
                "starting_v": "0.550",
                "starting_s": "1.300",
                "reserve": "0.750",
                "wire_fb": "0.090",
                "speed": "0.000",
                "comment": ""
            },
            "3": {
                "weld_current": "180.000",
                "weld_voltage": "1.400",
                "arc_ending_a": "38.000",
                "arc_ending_v": "0.950",
                "remove_stick_a": "48.000",
                "remove_stick_v": "0.000",
                "arc_ending_s": "0.380",
                "proof_stick": "0.580",
                "starting_a": "138.000",
                "starting_v": "0.580",
                "starting_s": "1.400",
                "reserve": "0.780",
                "wire_fb": "0.095",
                "speed": "0.000",
                "comment": ""
            },
            "4": {
                "weld_current": "200.000",
                "weld_voltage": "1.450",
                "arc_ending_a": "39.000",
                "arc_ending_v": "0.980",
                "remove_stick_a": "49.000",
                "remove_stick_v": "0.000",
                "arc_ending_s": "0.390",
                "proof_stick": "0.590",
                "starting_a": "139.000",
                "starting_v": "0.590",
                "starting_s": "1.450",
                "reserve": "0.790",
                "wire_fb": "0.098",
                "speed": "0.000",
                "comment": ""
            },
            "5": {
                "weld_current": "210.000",
                "weld_voltage": "1.480",
                "arc_ending_a": "39.500",
                "arc_ending_v": "0.990",
                "remove_stick_a": "49.500",
                "remove_stick_v": "0.000",
                "arc_ending_s": "0.395",
                "proof_stick": "0.595",
                "starting_a": "139.500",
                "starting_v": "0.595",
                "starting_s": "1.480",
                "reserve": "0.795",
                "wire_fb": "0.099",
                "speed": "0.000",
                "comment": ""
            },
            "6": {
                "weld_current": "215.000",
                "weld_voltage": "1.490",
                "arc_ending_a": "39.800",
                "arc_ending_v": "0.995",
                "remove_stick_a": "49.800",
                "remove_stick_v": "0.000",
                "arc_ending_s": "0.398",
                "proof_stick": "0.598",
                "starting_a": "139.800",
                "starting_v": "0.598",
                "starting_s": "1.490",
                "reserve": "0.798",
                "wire_fb": "0.0995",
                "speed": "0.000",
                "comment": ""
            },
            "7": {
                "weld_current": "218.000",
                "weld_voltage": "1.495",
                "arc_ending_a": "39.900",
                "arc_ending_v": "0.998",
                "remove_stick_a": "49.900",
                "remove_stick_v": "0.000",
                "arc_ending_s": "0.399",
                "proof_stick": "0.599",
                "starting_a": "139.900",
                "starting_v": "0.599",
                "starting_s": "1.495",
                "reserve": "0.799",
                "wire_fb": "0.0998",
                "speed": "0.000",
                "comment": ""
            },
            "8": {
                "weld_current": "220.000",
                "weld_voltage": "1.498",
                "arc_ending_a": "39.950",
                "arc_ending_v": "0.999",
                "remove_stick_a": "49.950",
                "remove_stick_v": "0.000",
                "arc_ending_s": "0.3995",
                "proof_stick": "0.5995",
                "starting_a": "139.950",
                "starting_v": "0.5995",
                "starting_s": "1.498",
                "reserve": "0.7995",
                "wire_fb": "0.0999",
                "speed": "0.000",
                "comment": ""
            },
            "9": {
                "weld_current": "221.000",
                "weld_voltage": "1.499",
                "arc_ending_a": "39.980",
                "arc_ending_v": "0.9995",
                "remove_stick_a": "49.980",
                "remove_stick_v": "0.000",
                "arc_ending_s": "0.3998",
                "proof_stick": "0.5998",
                "starting_a": "139.980",
                "starting_v": "0.5998",
                "starting_s": "1.499",
                "reserve": "0.7998",
                "wire_fb": "0.09995",
                "speed": "0.000",
                "comment": ""
            }
        }

    def create_page(self, text):
        page = QWidget()
        layout = QVBoxLayout()
        label = QLabel(text)
        label.setFont(QFont("Arial", 20))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        page.setLayout(layout)
        return page
    
    def add_nav_button(self, name, page):
        button = QPushButton(name)
        button.clicked.connect(lambda: self.pages.setCurrentWidget(page))
        self.nav_buttons.addWidget(button)

    def create_robot_teaching_page(self):
        page = QWidget()
        layout = QGridLayout()

        # Realtime Data (déplacé à gauche)
        realtime_data_group = QGroupBox("Realtime Data")
        realtime_data_layout = QVBoxLayout()

        # Joints
        self.joint_labels = []
        self.joint_value_labels = []  # Liste pour stocker les QLabel des valeurs des joints
        for i in range(6):  # 6 joints
            label = QLabel(f"Joint {i+1}:")  # Label pour le joint
            value_label = QLabel()  # QLabel pour afficher la valeur (initialisé à 0)
            self.joint_value_labels.append(value_label)  # Ajouter le QLabel à la liste

            # Ajouter le label et le QLabel au layout
            joint_layout = QHBoxLayout()
            joint_layout.addWidget(label)
            joint_layout.addWidget(value_label)
            realtime_data_layout.addLayout(joint_layout)

        realtime_data_group.setLayout(realtime_data_layout)
        layout.addWidget(realtime_data_group, 0, 0, 2, 1)

        # Work Mode (déplacé à droite)
        work_mode_group = QGroupBox("Work Mode")
        work_mode_layout = QVBoxLayout()
        real_robot = QRadioButton("Real Robot")
        simulation_robot = QRadioButton("Simulation Robot")
        simulation_robot.setChecked(True)
        work_mode_layout.addWidget(real_robot)
        work_mode_layout.addWidget(simulation_robot)
        work_mode_group.setLayout(work_mode_layout)
        layout.addWidget(work_mode_group, 0, 1)  # Déplacé à la colonne 1
        self.position_step = 1.0  # en mm
        self.position_step_value = QLabel(f"{self.position_step:.1f} mm")
        self.orientation_step = 0.5  # en degrés
        self.orientation_step_value = QLabel(f"{self.orientation_step:.1f} deg")
        # Position Control (déplacé à droite)

        position_control_group = QGroupBox("Position Control")
        position_control_layout = QGridLayout()
        directions = ["X+", "X-", "Y+", "Y-", "Z+", "Z-"]
        for i, direction in enumerate(directions):
            btn = QPushButton(direction)
            axis = (i // 2) + 1  # 1: X, 2: Y, 3: Z
            xx=self.position_step_value
            btn.pressed.connect(
                partial(utl.start_move_cartesian, self.robot, axis, "+" if i % 2 == 0 else "-",self)
            )
            btn.released.connect(utl.stop_move_cartesian)
            position_control_layout.addWidget(btn, i // 2, i % 2)
        position_control_group.setLayout(position_control_layout)
        layout.addWidget(position_control_group, 0, 2)  # Déplacé à la colonne 2

        # Step Mode Control
        step_mode_group = QGroupBox()
        step_mode_layout = QVBoxLayout()
        

        # Checkbox for Step Mode
        self.step_mode_checkbox = QCheckBox("Step Mode")
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.step_mode_checkbox)
        title_layout.addStretch()
        step_mode_group.setLayout(step_mode_layout)
        step_mode_group.setTitle("")
        step_mode_layout.addLayout(title_layout)
        step_mode_layout.addWidget(self.step_mode_checkbox)

        # Valeurs initiales
        self.position_step = 1 
        self.orientation_step = 0.5 # en degrés
        self.joint_step = 0.5 # en degrés
       

        # Limites
        self.position_step_min = 0.1  # en mm
        self.position_step_max = 10.0  # en mm

        self.orientation_step_min = 0.1  # en degrés
        self.orientation_step_max = 10.0  # en degrés

        self.joint_step_min = 0.1  # en degrés
        self.joint_step_max = 10.0  # en degrés

        # Position Step
        position_step_label = QLabel("Position Step:")
        self.position_step_value = QLabel(f"{self.position_step:.1f} mm")
        position_step_controls = QHBoxLayout()
        self.position_step_minus = QPushButton("-")
        self.position_step_plus = QPushButton("+")
        position_step_controls.addWidget(self.position_step_minus)
        position_step_controls.addWidget(self.position_step_value)
        position_step_controls.addWidget(self.position_step_plus)
        step_mode_layout.addWidget(position_step_label)
        step_mode_layout.addLayout(position_step_controls)

        # Orientation Step
        orientation_step_label = QLabel("Orientation Step:")
        self.orientation_step_value = QLabel(f"{self.orientation_step:.1f} deg")
        orientation_step_controls = QHBoxLayout()
        self.orientation_step_minus = QPushButton("-")
        self.orientation_step_plus = QPushButton("+")
        orientation_step_controls.addWidget(self.orientation_step_minus)
        orientation_step_controls.addWidget(self.orientation_step_value)
        orientation_step_controls.addWidget(self.orientation_step_plus)
        step_mode_layout.addWidget(orientation_step_label)
        step_mode_layout.addLayout(orientation_step_controls)

        # Joint Step
        joint_step_label = QLabel("Joint Step:")
        self.joint_step_value = QLabel(f"{self.joint_step:.1f} deg")
        joint_step_controls = QHBoxLayout()
        self.joint_step_minus = QPushButton("-")
        self.joint_step_plus = QPushButton("+")
        joint_step_controls.addWidget(self.joint_step_minus)
        joint_step_controls.addWidget(self.joint_step_value)
        joint_step_controls.addWidget(self.joint_step_plus)
        step_mode_layout.addWidget(joint_step_label)
        step_mode_layout.addLayout(joint_step_controls)

        # Connecter les boutons aux fonctions
        self.position_step_plus.clicked.connect(lambda: self.update_position_step(True))  # Bouton +
        self.position_step_minus.clicked.connect(lambda: self.update_position_step(False))  # Bouton -

        self.orientation_step_plus.clicked.connect(lambda: self.update_orientation_step(True))  # Bouton +
        self.orientation_step_minus.clicked.connect(lambda: self.update_orientation_step(False))  # Bouton -

        self.joint_step_plus.clicked.connect(lambda: self.update_joint_step(True))  # Bouton +
        self.joint_step_minus.clicked.connect(lambda: self.update_joint_step(False))  # Bouton -
        # Afficher les valeurs initiales dans les champs
        self.position_step_value.setText(f"{self.position_step:.1f} mm")
        self.orientation_step_value.setText(f"{self.orientation_step:.1f} deg")
        self.joint_step_value.setText(f"{self.joint_step:.1f} deg")

        # Connecter la checkbox à une fonction
        self.step_mode_checkbox.stateChanged.connect(self.toggle_step_mode)

        step_mode_group.setLayout(step_mode_layout)
        layout.addWidget(step_mode_group, 1, 1)


        # Joint Control (déplacé à droite)
        joint_control_group = QGroupBox("Joint Control (deg)")
        joint_control_layout = QGridLayout()
        for i in range(6):
            label = QLabel(f"Joint {i+1}:")
            decrease_btn = QPushButton("-")
            increase_btn = QPushButton("+")

            
            # En mode continu, utiliser le signal "pressed" pour un mouvement continu
            increase_btn.pressed.connect(
                partial(utl.start_move_joint, self.robot, i + 1, "+", self, self.joint_step_value)
            )
        
            increase_btn.released.connect(utl.stop_move_joint)

            decrease_btn.pressed.connect(
                partial(utl.start_move_joint, self.robot, i + 1, "-",  self, self.joint_step_value)
            )
            decrease_btn.released.connect(utl.stop_move_joint)

 
            value_display = QLineEdit()
            value_display.setReadOnly(True)
            self.joint_value_displays.append(value_display)
            joint_control_layout.addWidget(label, i, 0)
            joint_control_layout.addWidget(decrease_btn, i, 1)
            joint_control_layout.addWidget(value_display, i, 2)
            joint_control_layout.addWidget(increase_btn, i, 3)
        joint_control_group.setLayout(joint_control_layout)
        layout.addWidget(joint_control_group, 1, 2)  # Déplacé à la colonne 2
        

        # Manipulator Pose
        manipulator_pose_group = QGroupBox("Manipulator Pose")
        manipulator_pose_layout = QGridLayout()

        # Titres des colonnes
        manipulator_pose_layout.addWidget(QLabel("Pos(m)"), 0, 1)
        manipulator_pose_layout.addWidget(QLabel("Ori(deg)"), 0, 3)

        # Lignes pour les valeurs
        self.pos_labels = []  # Liste pour stocker les labels de position (X, Y, Z)
        self.ori_labels = []  # Liste pour stocker les labels d'orientation (RX, RY, RZ)

        labels = ["X:", "Y:", "Z:", "RX:", "RY:", "RZ:"]
        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            value_display = QLabel("0.000000")  # Valeur par défaut
            if i < 3:  # Position (X, Y, Z)
                self.pos_labels.append(value_display)
                manipulator_pose_layout.addWidget(label, i + 1, 0)
                manipulator_pose_layout.addWidget(value_display, i + 1, 1)
            else:  # Orientation (RX, RY, RZ)
                self.ori_labels.append(value_display)
                manipulator_pose_layout.addWidget(label, i + 1, 2)
                manipulator_pose_layout.addWidget(value_display, i + 1, 3)

        manipulator_pose_group.setLayout(manipulator_pose_layout)
        layout.addWidget(manipulator_pose_group, 2, 0, 1, 2)
        self.orientation_step_value.setText(f"{self.orientation_step:.1f} deg")
        orientation_control_group = QGroupBox("Orientation Control")
        orientation_control_layout = QGridLayout()
        orientation_directions = ["RX+", "RX-", "RY+", "RY-", "RZ+", "RZ-"]
        for i, direction in enumerate(orientation_directions):
            btn = QPushButton(direction)
            axis = (i // 2) + 4  # 4: RX, 5: RY, 6: RZ
            yy=self.orientation_step_value

            btn.pressed.connect(
                partial(utl.start_move_cartesian, self.robot, axis, "+" if i % 2 == 0 else "-", self)
            )
            btn.released.connect(utl.stop_move_cartesian)
            orientation_control_layout.addWidget(btn, i // 2, i % 2)
        orientation_control_group.setLayout(orientation_control_layout)
        layout.addWidget(orientation_control_group, 2, 2)

        # Reference Coord System
        reference_coord_group = QGroupBox("Reference Coord System")
        reference_coord_layout = QVBoxLayout()
        reference_dropdown = QComboBox()
        reference_dropdown.addItems(["Base", "flange_center", "TCP3", "TCP_1", "TCP_2", "p1"])
        reference_coord_layout.addWidget(reference_dropdown)
        reference_coord_group.setLayout(reference_coord_layout)
        layout.addWidget(reference_coord_group, 3, 0, 1, 1)

        # Nouveau groupe pour les boutons et le contrôle de vitesse
        buttons_speed_group = QGroupBox()
        buttons_speed_layout = QVBoxLayout()

        # Boutons Init Pose et Zero Pose
        init_pose_button = QPushButton("Init Pose")
        init_pose_button.pressed.connect(partial(utl.start_move_to_init_pose, self.robot))
        init_pose_button.released.connect(utl.stop_move_to_init_pose)
        zero_pose_button = QPushButton("Zero Pose")
        zero_pose_button.pressed.connect(partial(utl.start_move_to_zero_pose, self.robot))  # Début du mouvement
        zero_pose_button.released.connect(utl.stop_move_to_zero_pose)
        buttons_speed_layout.addWidget(init_pose_button)
        buttons_speed_layout.addWidget(zero_pose_button)

        # Contrôle de vitesse (Speed)
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        speed_slider = QSlider(Qt.Horizontal)
        speed_slider.setMinimum(0)
        speed_slider.setMaximum(100)
        speed_slider.setValue(50)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(speed_slider)
        buttons_speed_layout.addLayout(speed_layout)

        buttons_speed_group.setLayout(buttons_speed_layout)
        layout.addWidget(buttons_speed_group, 3, 1, 1, 1)

        # Nouveau groupe similaire à Reference Coord System
        new_reference_coord_group = QGroupBox("flange_center")
        new_reference_coord_layout = QVBoxLayout()
        new_reference_dropdown = QComboBox()
        new_reference_dropdown.addItems(["flange_center", "TCP3", "TCP_1", "TCP_2"])
        new_reference_coord_layout.addWidget(new_reference_dropdown)
        new_reference_coord_group.setLayout(new_reference_coord_layout)
        layout.addWidget(new_reference_coord_group, 3, 2, 1, 1)
        page.setLayout(layout)


        return page

    def update_joint_values(self, joints_radians):
        """
        Met à jour les champs de texte avec les valeurs actuelles des joints en degrés.
        """
        try:
            # Convertir les joints de radians en degrés
            joints_degrees = [round(math.degrees(joint), 6) for joint in joints_radians]

            # Mettre à jour les champs de texte des joints dans "Joint Control"
            for i, value_display in enumerate(self.joint_value_displays):
                value_display.setText(f"{joints_degrees[i]:.6f}")

            # Mettre à jour les labels dans "Realtime Data"
            for i, value_label in enumerate(self.joint_value_labels):
                value_label.setText(f"{joints_degrees[i]:.6f}")  # Afficher avec 6 décimales

        except Exception as e:
            print(f"Erreur lors de la mise à jour des valeurs des joints : {e}")


    def update_manipulator_pose(self):
        """
        Met à jour les valeurs de position et d'orientation dans "Manipulator Pose".
        """
        try:
            # Récupérer la position et l'orientation actuelles du robot
            current_waypoint = self.robot.get_current_waypoint()
            if current_waypoint is None:
                return

            # Extraire la position (X, Y, Z) en mètres
            pos = current_waypoint.get('pos', [0.0, 0.0, 0.0])  # [x, y, z] en mètres

            # Extraire l'orientation (quaternion) et la convertir en angles RPY (rx, ry, rz) en radians
            ori = current_waypoint.get('ori', [1.0, 0.0, 0.0, 0.0])  # Quaternion [w, x, y, z]
            rpy_radians = self.robot.quaternion_to_rpy(ori)  # Convertir en angles RPY en radians

            # Convertir les angles RPY en degrés
            rpy_degrees = [math.degrees(angle) for angle in rpy_radians]  # Conversion en degrés

            # Mettre à jour les labels de position (X, Y, Z)
            for i, label in enumerate(self.pos_labels):
                label.setText(f"{pos[i]:.6f}")

            # Mettre à jour les labels d'orientation (RX, RY, RZ) en degrés
            for i, label in enumerate(self.ori_labels):
                label.setText(f"{rpy_degrees[i]:.6f}")  # Afficher en degrés avec le symbole °

        except Exception as e:
            print(f"Erreur lors de la mise à jour de la pose du manipulateur : {e}")


    def update_position_step(self, increment):
        """
        Met à jour la valeur de l'étape de position.
        :param increment: True pour augmenter, False pour diminuer.
        """
        try:
            # Récupérer la valeur actuelle du Position Step depuis l'interface
            current_step = float(self.position_step_value.text().split()[0])  # Extraire la valeur numérique

            # Modifier la valeur du Position Step
            if increment:
                new_step = min(current_step + 0.1, self.position_step_max)  # Limite maximale
            else:
                new_step = max(current_step - 0.1, self.position_step_min)  # Limite minimale
            self.position_step=new_step
            # Mettre à jour l'affichage de la valeur du Position Step
            self.position_step_value.setText(f"{new_step:.1f} mm")
          
        except Exception as e:
            print(f"Erreur lors de la mise à jour du Position Step : {e}")

    def update_orientation_step(self, increment):
        """
        Met à jour la valeur de l'étape d'orientation.
        :param increment: True pour augmenter, False pour diminuer.
        """
        try:
            # Récupérer la valeur actuelle de l'Orientation Step depuis l'interface
            current_step = float(self.orientation_step_value.text().split()[0])  # Extraire la valeur numérique

            # Modifier la valeur de l'Orientation Step
            if increment:
                new_step = min(current_step + 0.1, self.orientation_step_max)  # Limite maximale
            else:
                new_step = max(current_step - 0.1, self.orientation_step_min)  # Limite minimale

            # Mettre à jour l'affichage de la valeur de l'Orientation Step
            self.orientation_step_value.setText(f"{new_step:.1f} deg")
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'Orientation Step : {e}")


    def update_joint_step(self, increment):
        """
        Met à jour la valeur de l'étape des joints.
        :param increment: True pour augmenter, False pour diminuer.
        """
        try:
            # Récupérer la valeur actuelle du Joint Step depuis l'interface
            current_step = float(self.joint_step_value.text().split()[0])  # Extraire la valeur numérique

            # Modifier la valeur du Joint Step
            if increment:
                new_step = min(current_step + 0.1, 10.0)  # Limite maximale de 10.0 deg
            else:
                new_step = max(current_step - 0.1, 0.1)  # Limite minimale de 0.1 deg

            # Mettre à jour l'affichage de la valeur du Joint Step
            self.joint_step_value.setText(f"{new_step:.1f} deg")
        except Exception as e:
            print(f"Erreur lors de la mise à jour du Joint Step : {e}")
    def toggle_step_mode(self):
        """
        Active ou désactive les pas de déplacement en fonction de l'état de la checkbox.
        """
        self.st=self.step_mode_checkbox.isChecked()
        if self.step_mode_checkbox.isChecked():
            # Activer les pas de déplacement
            self.position_step = float(self.position_step_value.text().split()[0])* 1000   # Récupérer la valeur du champ
            self.orientation_step = math.degrees(float(self.orientation_step_value.text().split()[0]))  # Récupérer la valeur du champ
            self.joint_step = math.degrees(float(self.joint_step_value.text().split()[0]))

            # Afficher les valeurs récupérées
            print(f"Step Mode activé. Pas de déplacement : "
                f"Position = {self.position_step} mm, "
                f"Orientation = {self.orientation_step} deg, "
                f"Joint = {self.joint_step} deg")

            logger.info("Step Mode activé. Pas de déplacement : "
                        f"Position = {self.position_step} mm, "
                        f"Orientation = {self.orientation_step} deg, "
                        f"Joint = {self.joint_step} deg")
        else:
            # Désactiver les pas de déplacement (utiliser des valeurs par défaut ou désactiver les mouvements)
            self.position_step = 0.0 # Pas de déplacement pour la position
            self.orientation_step = 0.0  # Pas de déplacement pour l'orientation
            self.joint_step= 0.0  # Pas de déplacement pour les joints

            # Afficher les valeurs par défaut
            print("Step Mode désactivé. Pas de déplacement désactivés.")

            logger.info("Step Mode désactivé. Pas de déplacement désactivés.")


 
    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        # Top section with file number and comment
        top_layout = QHBoxLayout()
        self.file_number = QComboBox()
        self.file_number.addItems([str(i) for i in range(10)])
        self.file_number.currentTextChanged.connect(self.on_file_changed)
        self.comment = QLineEdit()
        self.comment.mousePressEvent = lambda event: self.show_virtual_keyboard(self.comment)
        self.comment.textChanged.connect(self.on_comment_changed)
        top_layout.addWidget(QLabel("File number"))
        top_layout.addWidget(self.file_number)
        top_layout.addWidget(QLabel("Comment"))
        top_layout.addWidget(self.comment)
        layout.addLayout(top_layout)

        # Group box for welding parameters
        params_group = QGroupBox("Welding Parameters")
        params_layout = QHBoxLayout()

        # Left column
        left_params = QVBoxLayout()
        self.weld_current_input = self.add_param(left_params, "Weld current", "120.000", "A")
        self.weld_voltage_input = self.add_param(left_params, "Weld voltage", "1.500", "V")
        self.arc_ending_a_input = self.add_param(left_params, "Arc Ending", "40.000", "A")
        self.arc_ending_v_input = self.add_param(left_params, "Arc Ending", "1.000", "V")
        self.remove_stick_a_input = self.add_param(left_params, "Remove stick", "50.000", "A")
        self.remove_stick_v_input = self.add_param(left_params, "Remove stick", "0.000", "V")
        self.arc_ending_s_input = self.add_param(left_params, "Arc Ending", "0.400", "s")
        self.proof_stick_input = self.add_param(left_params, "Proof stick", "0.600", "s")
        params_layout.addLayout(left_params)

        # Right column
        right_params = QVBoxLayout()
        self.starting_a_input = self.add_param(right_params, "Starting (A)", "140.000", "A")
        self.starting_v_input = self.add_param(right_params, "Starting (V)", "0.600", "V")
        self.starting_s_input = self.add_param(right_params, "Starting (S)", "1.500", "s")
        self.reserve_input = self.add_param(right_params, "Reserve", "0.800", "      ")
        self.wire_fb_input = self.add_param(right_params, "Wire FB(ms)", "0.100", "ms")
        self.speed_input = self.add_param(right_params, "speed", "0.000","           ")
        self.wire_feedback = QCheckBox("Wire auto feedback")
        self.arc_start = QCheckBox("Arcstart in advance")
        right_params.addWidget(self.wire_feedback)
        right_params.addWidget(self.arc_start)
        params_layout.addLayout(right_params)
        self.starting_a_input.textChanged.connect(lambda text: self.auto_save_parameter("starting_a", text))
        self.starting_v_input.textChanged.connect(lambda text: self.auto_save_parameter("starting_v", text))
        self.starting_s_input.textChanged.connect(lambda text: self.auto_save_parameter("starting_s", text))
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        


        # Curves layout
        curves_layout = QHBoxLayout()

        # Left curve section
        left_curve_section = QVBoxLayout()
        left_curve_row = QHBoxLayout()

        # Analog values (left of the curve)
        analog_values_left = QVBoxLayout()
        analog_values_left.addWidget(QLabel("Analog"))
        self.y_value1 = QLineEdit()
        self.y_value1.mousePressEvent = lambda event: self.show_virtual_keyboard(self.y_value1)
        self.y_value2 = QLineEdit()
        self.y_value2.mousePressEvent = lambda event: self.show_virtual_keyboard(self.y_value2)
        self.y_value2.setFixedWidth(60)
        self.y_value1.setFixedWidth(60)
        analog_values_left.addWidget(self.y_value1)
        analog_values_left.addSpacing(100)
        analog_values_left.addWidget(self.y_value2)
        left_curve_row.addLayout(analog_values_left)
        a_ponte_right_layout = QHBoxLayout()
        a_ponte_right_layout.addWidget(QLabel())
        self.a_ponte_right_value = QLabel()  # Valeur par défaut
        a_ponte_right_layout.addWidget(self.a_ponte_right_value)
        a_ponte_right_layout.addStretch()  # Pour aligner à gauche
        left_curve_section.addLayout(a_ponte_right_layout)



        # Curve widget
        self.curve_widget_left = CurveWidget()
        self.curve_widget_left.set_image("courbe.jpg")
        left_curve_row.addWidget(self.curve_widget_left)
        left_curve_section.addLayout(left_curve_row)


        # Welder (A) values (below the curve)
        welder_values_left = QHBoxLayout()
        welder_values_left.setSpacing( 105)
        welder_values_left.addWidget(QLabel("Welder (A)"))
        self.x_value1 = QLineEdit()
        self.x_value1.mousePressEvent = lambda event: self.show_virtual_keyboard(self.x_value1)
        self.x_value1.setFixedWidth(60)
        self.x_value2 = QLineEdit()
        self.x_value2.mousePressEvent = lambda event: self.show_virtual_keyboard(self.x_value2)
        self.x_value2.setFixedWidth(60)
        welder_values_left.addWidget(self.x_value1)
        welder_values_left.addWidget(self.x_value2)
        welder_values_left.addStretch()
        left_curve_section.addLayout(welder_values_left)
        curves_layout.addLayout(left_curve_section)



        # Right curve section
        right_curve_section = QVBoxLayout()
        right_curve_row = QHBoxLayout()

        # Analog values (left of the curve)
        analog_values_right = QVBoxLayout()
        analog_values_right.addWidget(QLabel("Analog"))
        self.y_value3 = QLineEdit()
        self.y_value3.mousePressEvent = lambda event: self.show_virtual_keyboard(self.y_value3)
        self.y_value4 = QLineEdit()
        self.y_value4.mousePressEvent = lambda event: self.show_virtual_keyboard(self.y_value4)
        self.y_value4.setFixedWidth(60)
        self.y_value3.setFixedWidth(60)
        analog_values_right.addWidget(self.y_value3)
        analog_values_right.addSpacing(100)
        analog_values_right.addWidget(self.y_value4)
        right_curve_row.addLayout(analog_values_right)
        a_ponte_left_layout = QHBoxLayout()
        a_ponte_left_layout.addWidget(QLabel())
        self.a_ponte_left_value = QLabel()  # Valeur par défaut
        a_ponte_left_layout.addWidget(self.a_ponte_left_value)
        a_ponte_left_layout.addStretch(0)  # Pour aligner à gauche
        right_curve_section.addLayout(a_ponte_left_layout)

        # Curve widget
        self.curve_widget_right = CurveWidget()
        self.curve_widget_right.set_image("courbe.jpg")
        right_curve_row.addWidget(self.curve_widget_right)
        right_curve_section.addLayout(right_curve_row)

        # Welder (A) values (below the curve)
        welder_values_right = QHBoxLayout()
        welder_values_right.setSpacing(105)
        welder_values_right.addWidget(QLabel("Welder (A)"))
        self.x_value3 = QLineEdit()
        self.x_value3.mousePressEvent = lambda event: self.show_virtual_keyboard(self.x_value3)
        self.x_value3.setFixedWidth(60)
        self.x_value4 = QLineEdit()
        self.x_value4.mousePressEvent = lambda event: self.show_virtual_keyboard(self.x_value4)
        self.x_value4.setFixedWidth(60)
        welder_values_right.addWidget(self.x_value3)
        welder_values_right.addWidget(self.x_value4)
        welder_values_right.addStretch(0)
        right_curve_section.addLayout(welder_values_right)
        curves_layout.addLayout(right_curve_section)
        layout.addLayout(curves_layout)


        # Test section
        test_main_layout = QHBoxLayout()
        test_left_layout = QVBoxLayout()
        self.test_input_left = QLineEdit()
        self.test_input_left.mousePressEvent = lambda event: self.show_virtual_keyboard(self.test_input_left)
        self.test_input_left.setPlaceholderText("Enter test value")  
        self.test_button_left = QPushButton("Test ")
        test_left_layout.addWidget(self.test_input_left)
        test_left_layout.addWidget(self.test_button_left)
        self.test_button_left.clicked.connect(self.calculate_test_value_left)

        test_right_layout = QVBoxLayout()
        self.test_input_right = QLineEdit()
        self.test_input_right.mousePressEvent = lambda event: self.show_virtual_keyboard(self.test_input_right)
        self.test_input_right.setPlaceholderText("Enter test value")  
        self.test_button_right = QPushButton("Test ")
        test_right_layout.addWidget(self.test_input_right)
        test_right_layout.addWidget(self.test_button_right)

        self.test_button_right.clicked.connect(self.calculate_test_value_right)

        test_main_layout.addLayout(test_left_layout)
        test_main_layout.addLayout(test_right_layout)
        layout.addLayout(test_main_layout)

        # Dans create_settings_page()

        # Charger les paramètres du fichier par défaut
        self.load_file_parameters(self.current_file)
        self.y_value1.textChanged.connect(self.calculate_curve_slope)
        self.y_value2.textChanged.connect(self.calculate_curve_slope)
        self.x_value1.textChanged.connect(self.calculate_curve_slope)
        self.x_value2.textChanged.connect(self.calculate_curve_slope)
        self.x_value3.textChanged.connect(self.calculate_curve2_slope)
        self.x_value4.textChanged.connect(self.calculate_curve2_slope) 
        self.y_value3.textChanged.connect(self.calculate_curve2_slope)
        self.y_value4.textChanged.connect(self.calculate_curve2_slope)

        # Calcul initial des coefficients des courbes
        self.calculate_curve_slope()  # Calcul initial des coefficients de la courbe 1
        self.calculate_curve2_slope()  # Calcul initial des coefficients de la courbe 2

        # Connexion des signaux textChanged pour tous les champs
        self.weld_current_input.textChanged.connect(self.calculate_voltage_from_current)
        self.remove_stick_a_input.textChanged.connect(self.calculate_voltage_from_current)
        self.starting_a_input.textChanged.connect(self.calculate_voltage_from_current)
        self.arc_ending_a_input.textChanged.connect(self.calculate_voltage_from_current)
        self.weld_voltage_input.textChanged.connect(self.calculate_voltage_from_current)
        self.arc_ending_v_input.textChanged.connect(self.calculate_voltage_from_current)
        self.remove_stick_v_input.textChanged.connect(self.calculate_voltage_from_current)
        self.starting_v_input.textChanged.connect(self.calculate_voltage_from_current)

        # Appel initial pour sauvegarder les résultats
        self.calculate_voltage_from_current()
        page.setLayout(layout)
        return page

    def on_file_changed(self, new_file_num):
        """Changement de fichier avec sauvegarde automatique"""
        # Sauvegarde le commentaire actuel avant de changer de fichier
        if self.current_file in self.file_parameters:
            self.file_parameters[self.current_file]["comment"] = self.comment.text()
        
        self.save_parameters_file()  # Sauvegarde tous les paramètres
        self.current_file = new_file_num
        self.load_file_parameters(new_file_num)

    def on_comment_changed(self, text):
        # Sauvegarde automatique du commentaire
        if self.current_file in self.file_parameters:
            self.file_parameters[self.current_file]["comment"] = text

    def save_current_parameters(self):
        """Sauvegarde les paramètres actuels dans le dictionnaire et dans le fichier"""
        if self.current_file not in self.file_parameters:
            self.file_parameters[self.current_file] = {}
        
        # Sauvegarde des paramètres de soudage
        self.file_parameters[self.current_file].update({
            "weld_current_a": self.weld_current_input.text(),
            "weld_voltage_v": self.weld_voltage_input.text(),
            "arc_ending_a": self.arc_ending_a_input.text(),
            "arc_ending_v": self.arc_ending_v_input.text(),
            "remove_stick_a": self.remove_stick_a_input.text(),
            "remove_stick_v": self.remove_stick_v_input.text(),
            "arc_ending_s": self.arc_ending_s_input.text(),
            "proof_stick_s": self.proof_stick_input.text(),
            "starting_a": self.starting_a_input.text(),
            "starting_v": self.starting_v_input.text(),
            "starting_s": self.starting_s_input.text(),
            "reserve": self.reserve_input.text(),
            "wire_fb_ms": self.wire_fb_input.text(),
            "speed": self.speed_input.text(),
            "wire_feedback": self.wire_feedback.isChecked(),  # Sauvegarde de l'état de la case à cocher
            "arc_start": self.arc_start.isChecked(),  # Sauvegarde de l'état de la case à cocher
            "comment": self.comment.text()
        })
        

        
        # Sauvegarde des valeurs globales (courbes)
        self.save_global_values()
        
        self.save_parameters_file()
    def save_global_values(self):
        """Sauvegarde les valeurs partagées dans global_values"""
        # Initialize global_values if it doesn't exist
        if "global_values" not in self.file_parameters:
            self.file_parameters["global_values"] = {}
        
        # Update all values
        self.file_parameters["global_values"].update({
            "y_value1": self.y_value1.text(),
            "y_value2": self.y_value2.text(),
            "x_value1": self.x_value1.text(),
            "x_value2": self.x_value2.text(),
            "y_value3": self.y_value3.text(),
            "y_value4": self.y_value4.text(),
            "x_value3": self.x_value3.text(),
            "x_value4": self.x_value4.text(),
        })
        
        # Debug print to verify saving (remove in production)
        print("Saved global values:", self.file_parameters["global_values"])
        
        self.save_parameters_file()
    def load_file_parameters(self, file_num):
        params = self.file_parameters.get(file_num, {})
        global_values = self.file_parameters.get("global_values", {})
        
        # Chargement de tous les paramètres
        self.weld_current_input.setText(str(params.get("weld_current_a", "120.000")))
        self.weld_voltage_input.setText(str(params.get("weld_voltage_v", "1.500")))
        self.arc_ending_a_input.setText(str(params.get("arc_ending_a", "40.000")))
        self.arc_ending_v_input.setText(str(params.get("arc_ending_v", "1.000")))
        self.remove_stick_a_input.setText(str(params.get("remove_stick_a", "50.000")))
        self.remove_stick_v_input.setText(str(params.get("remove_stick_v", "0.000")))
        self.arc_ending_s_input.setText(str(params.get("arc_ending_s", "0.400")))
        self.proof_stick_input.setText(str(params.get("proof_stick_s", "0.600")))
        self.starting_a_input.setText(str(params.get("starting_a", "140.000")))
        self.starting_v_input.setText(str(params.get("starting_v", "0.600")))
        self.starting_s_input.setText(str(params.get("starting_s", "1.500")))
        self.reserve_input.setText(str(params.get("reserve", "0.800")))
        self.wire_fb_input.setText(str(params.get("wire_fb_ms", "0.100")))
        self.speed_input.setText(str(params.get("speed", "0.000")))
        self.wire_feedback.setChecked(params.get("wire_feedback", False))  # Chargement de l'état de la case à cocher
        self.arc_start.setChecked(params.get("arc_start", False))  # Chargement de l'état de la case à cocher
        self.comment.setText(str(params.get("comment", "")))
        self.y_value1.setText(str(global_values.get("y_value1", "10.000")))
        self.y_value2.setText(str(global_values.get("y_value2", "0.000")))
        self.x_value1.setText(str(global_values.get("x_value1", "5.000")))
        self.x_value2.setText(str(global_values.get("x_value2", "315.000")))
        self.y_value3.setText(str(global_values.get("y_value3", "12.000")))
        self.y_value4.setText(str(global_values.get("y_value4", "2.000")))
        self.x_value3.setText(str(global_values.get("x_value3", "10.000")))
        self.x_value4.setText(str(global_values.get("x_value4", "320.000")))
        

    def add_param(self, layout, label, default_value, unit):
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        
        param_input = QLineEdit(default_value)
        param_input.setFixedWidth(80)
        
        # Connecter le clic pour ouvrir le clavier virtuel
        param_input.mousePressEvent = lambda event, le=param_input: self.show_virtual_keyboard(le)
        
        # Générer une clé unique en incluant l'unité
        param_name = label.lower().replace(" ", "_").replace("(", "").replace(")", "")
        if unit and unit.strip():  # Si une unité est fournie, l'ajouter à la clé
            param_name += f"_{unit.lower().replace(' ', '')}"
        
        # Connecter la modification pour sauvegarde automatique
        param_input.textChanged.connect(lambda text, pn=param_name: self.auto_save_parameter(pn, text))
        
        row.addWidget(param_input)
        if unit:
            row.addWidget(QLabel(unit))
        layout.addLayout(row)
        
        return param_input
        
        return param_input
    def auto_save_parameter(self, param_name, value):
        """Sauvegarde automatique d'un paramètre modifié"""
        if self.current_file in self.file_parameters:
            self.file_parameters[self.current_file][param_name] = value
            self.save_parameters_file() 

    def closeEvent(self, event):
        """Sauvegarde lors de la fermeture de l'application"""
        self.save_current_parameters()
        event.accept()

    def show_virtual_keyboard(self, target_input):
        # Fermer le clavier existant s'il est ouvert
        if hasattr(self, 'virtual_keyboard'):
            self.virtual_keyboard.close()
        
        # Créer et afficher le nouveau clavier
        self.virtual_keyboard = VirtualKeyboard(target_input)
        
        # Positionner le clavier près du champ de saisie
        keyboard_position = target_input.mapToGlobal(QPoint(0, target_input.height()))
        self.virtual_keyboard.move(keyboard_position)
        
        self.virtual_keyboard.show()


    def open_virtual_keyboard(self):
        self.keyboard = VirtualKeyboard(self.test_input_left)
        self.keyboard.show()

    def calculate_curve_slope(self):
        try:
            x1 = float(self.x_value1.text())
            x2 = float(self.x_value2.text())
            y1 = float(self.y_value2.text())
            y2 = float(self.y_value1.text())
            
            if  x2<=x1 or y2<=y1:
                self.a_ponte_right_value.setText("Pente: Indéfinie")
                self.curve_slope = None
                self.curve_intercept = None
            else:
                self.curve_slope = (y2 - y1) / (x2 - x1)
                self.curve_intercept = y1 - self.curve_slope * x1
                # self.a_ponte_right_value.setText(f"A: {self.curve_slope:.10g}, b: {self.curve_intercept:.10g}") 

            self.save_global_values()    
            
            # Après la mise à jour des coefficients, appeler calculate_voltage_from_current
            self.calculate_voltage_from_current()

            
        except ValueError:
            self.a_ponte_right_value.setText("Valeurs invalides")
            self.curve_slope = None
            self.curve_intercept = None
            self.save_global_values()
            # Appeler calculate_voltage_from_current même en cas d'erreur pour mettre à jour l'affichage
            self.calculate_voltage_from_current()

    def calculate_test_value_left(self):
        try:
            test_value = float(self.test_input_left.text())
            if self.curve_slope is not None and self.curve_intercept is not None:
                result = self.curve_slope * test_value + self.curve_intercept
                self.test_button_left.setText(f"Résultat: {result:.2f} V")
            else:
                self.test_button_left.setText("Pente non définie")
        except ValueError:
            self.test_button_left.setText("Valeur de test invalide")

    def calculate_curve2_slope(self):
        try:
            x3 = float(self.x_value3.text())
            x4 = float(self.x_value4.text())
            y3 = float(self.y_value4.text())
            y4 = float(self.y_value3.text())
            
            if x4<=x3 or y4<=y3:
                self.curve2_slope = None
                self.curve2_intercept = None
                self.a_ponte_left_value.setText("Courbe 2: Pente indéfinie")
            else:
                self.curve2_slope = (y4 - y3) / (x4 - x3)
                self.curve2_intercept = y3 - self.curve2_slope * x3
                # self.a_ponte_left_value.setText(
                #     # f"Courbe 2: A={self.curve2_slope:.10g} b={self.curve2_intercept:.10g}\n"
                #     # f"Équation: y = {self.curve2_slope:.10g}x + {self.curve2_intercept:.10g}"
                # )
            self.save_global_values()
            self.calculate_voltage_from_current()
            
        except ValueError:
            self.a_ponte_left_value.setText("Courbe 2: Valeurs invalides")
            self.curve2_slope = None
            self.curve2_intercept = None
            self.save_global_values()
            self.calculate_voltage_from_current()

    def calculate_test_value_right(self):
        try:
            test_value = float(self.test_input_right.text())
            if self.curve2_slope is not None and self.curve2_intercept is not None:
                result = self.curve2_slope * test_value + self.curve2_intercept
                self.test_button_right.setText(f"Résultat: {result:.2f} V")
            else:
                self.test_button_right.setText("Pente non définie")
        except ValueError:
            self.test_button_right.setText("Valeur de test invalide")




    def calculate_voltage_from_current(self):
        try:
            # Récupérer les valeurs actuelles
            weld_current = float(self.weld_current_input.text())
            remove_stick_a = float(self.remove_stick_a_input.text())
            starting_a = float(self.starting_a_input.text())
            arc_ending_a = float(self.arc_ending_a_input.text())
            
            # Nouvelles valeurs pour la courbe 1
            weld_voltage = float(self.weld_voltage_input.text())
            arc_ending_v = float(self.arc_ending_v_input.text())
            remove_stick_v = float(self.remove_stick_v_input.text())
            starting_v = float(self.starting_v_input.text())
            
            # Vérifier si les coefficients des deux courbes sont disponibles et non None
            curve1_available = (hasattr(self, 'curve_slope') and hasattr(self, 'curve_intercept') and
                            self.curve_slope is not None and self.curve_intercept is not None)
            curve2_available = (hasattr(self, 'curve2_slope') and hasattr(self, 'curve2_intercept') and
                            self.curve2_slope is not None and self.curve2_intercept is not None)
            
            # Initialiser le dictionnaire pour stocker les résultats
            results = {}
            
            if curve2_available:
                A2 = self.curve2_slope
                b2 = self.curve2_intercept
                
                # Calculer les tensions pour la courbe 2
                calculated_weld_voltage_curve2 = A2 * weld_current + b2
                calculated_remove_stick_a = A2 * remove_stick_a + b2
                calculated_starting_a = A2 * starting_a + b2
                calculated_arc_ending_a = A2 * arc_ending_a + b2
                
                # Stocker les valeurs pour la courbe 2
                self.last_calculated_weld_voltage_curve2 = calculated_weld_voltage_curve2
                self.last_calculated_remove_stick_a = calculated_remove_stick_a
                self.last_calculated_starting_a = calculated_starting_a
                self.last_calculated_arc_ending_a = calculated_arc_ending_a
                
                # Ajouter les résultats de la courbe 2 au dictionnaire
                results["curve2"] = {
                    "weld_A": calculated_weld_voltage_curve2,
                    "remove_stick_A": calculated_remove_stick_a,
                    "starting_A": calculated_starting_a,
                    "arc_ending_A": calculated_arc_ending_a,
                    "equation": f"y = {A2:.3f}x + {b2:.3f}"
                }
            else:
                results["curve2"] = {"error": "Veuillez d'abord calculer la courbe 2 ou vérifier les valeurs"}
            
            if curve1_available:
                A1 = self.curve_slope
                b1 = self.curve_intercept
                
                # Calculer les tensions pour la courbe 1
                calculated_weld_voltage_curve1 = A1 * weld_voltage + b1
                calculated_arc_ending_v = A1 * arc_ending_v + b1
                calculated_remove_stick_v = A1 * remove_stick_v + b1
                calculated_starting_v = A1 * starting_v + b1
                
                # Stocker les valeurs pour la courbe 1
                self.last_calculated_weld_voltage_curve1 = calculated_weld_voltage_curve1
                self.last_calculated_arc_ending_v = calculated_arc_ending_v
                self.last_calculated_remove_stick_v = calculated_remove_stick_v
                self.last_calculated_starting_v = calculated_starting_v
                
                # Ajouter les résultats de la courbe 1 au dictionnaire
                results["curve1"] = {
                    "weld_V": calculated_weld_voltage_curve1,
                    "arc_ending_V": calculated_arc_ending_v,
                    "remove_stick_V": calculated_remove_stick_v,
                    "starting_V": calculated_starting_v,
                    "equation": f"y = {A1:.3f}x + {b1:.3f}"
                }
            else:
                results["curve1"] = {"error": "Veuillez d'abord calculer la courbe 1 ou vérifier les valeurs"}
            
            # Sauvegarder les résultats dans un fichier JSON
            file_path = "calculation_results.json"
            print("Sauvegarde dans :", os.path.abspath(file_path))
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(results, file, indent=4, ensure_ascii=False)
                
        except ValueError:
            # En cas d'erreur, sauvegarder le message d'erreur dans le fichier JSON
            results = {"error": "Valeur invalide dans les entrées"}
            file_path = "calculation_results.json"
            print("Sauvegarde dans :", os.path.abspath(file_path))
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(results, file, indent=4, ensure_ascii=False)


    def create_extensions_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Programming")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Arc Control Group
        arc_control_group = QGroupBox("Arc Control")
        arc_control_layout = QVBoxLayout()

        
        # Arc Start/End Controls
        arc_btn_group = QGroupBox("Arc Process")
        arc_btn_layout = QHBoxLayout()
        
        self.arc_start_button = QPushButton("ARC START")
        self.arc_start_button.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #2ECC71; }
            QPushButton:pressed { background-color: #219653; }
        """)
        
        self.arc_end_button = QPushButton("ARC END")
        self.arc_end_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #EC7063; }
            QPushButton:pressed { background-color: #CB4335; }
        """)
        
        arc_btn_layout.addWidget(self.arc_start_button)
        arc_btn_layout.addWidget(self.arc_end_button)
        arc_btn_group.setLayout(arc_btn_layout)
        
        # Arc Parameters Display
        param_group = QGroupBox("Current Arc Parameters")
        param_layout = QGridLayout()
        
        # Add parameter labels and value displays
        self.param_displays = {}
        params = [
            ("Gas Detect Signal", "Yxx"),
            ("Gas Preflow Time", ""),
            ("Arc Starting Signal", "Yxx"),
            ("Arc Start Error Time Delay", ""),
            ("Arc Defect Time", ""),
            ("Arc Starting Time", ""),
            ("Gas Postflow Time", ""),
            ("Prevent Stick Time", ""),
            ("Arc Ending Time", ""),
            ("Arc Loss Error Time", ""),
            ("Arc Detect Signal", "Xxx"),
            ("Arc Starting Current", ""),
            ("Welding Current", ""),
            ("Arc Ending Current", ""),
            ("Prevent Stick Current", ""),
            ("Arc Starting Voltage", ""),
            ("Welding Voltage", ""),
            ("Arc Ending Voltage", ""),
            ("Prevent Stick Voltage", "")
        ]
        
        for i, (name, default) in enumerate(params):
            row = i // 2
            col = (i % 2) * 2
            param_layout.addWidget(QLabel(name), row, col)
            display = QLabel(default)
            display.setStyleSheet("background-color: white; border: 1px solid gray;")
            param_layout.addWidget(display, row, col+1)
            self.param_displays[name] = display
        
        param_group.setLayout(param_layout)
        
        # Add all groups to main layout
        arc_control_layout.addWidget(arc_btn_group)
        arc_control_layout.addWidget(param_group)
        arc_control_group.setLayout(arc_control_layout)
        
        layout.addWidget(arc_control_group)
        layout.addStretch()
        
        # Connect signals
        self.arc_start_button.clicked.connect(self.start_arc_process)
        self.arc_end_button.clicked.connect(self.end_arc_process)


        page.setLayout(layout)
        return page


    def load_json_parameters(self):
        """Charge les paramètres depuis le fichier calculation_results.json"""
        file_path = "calculation_results.json"
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                print(f"Le fichier {file_path} n'existe pas encore.")
                return {"curve1": {}, "curve2": {}}
        except Exception as e:
            print(f"Erreur lors du chargement du fichier JSON: {e}")
            return {"error": str(e)}

    def start_arc_process(self):
        """Handle the full arc start sequence using saved parameters from JSON and interface."""
        try:
            # Load parameters from the JSON file for current and voltage
            file_path = "calculation_results.json"
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    params = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading JSON file: {e}")
                QMessageBox.critical(self, "Error", "Failed to load calculation_results.json")
                return

            # Extract current values from the JSON file
            starting_current = 50.0  # Default value if not found in JSON
            if "curve2" in params and "starting_A" in params["curve2"]:
                try:
                    starting_current = float(params["curve2"]["starting_A"])
                    # if starting_current < 10.0:  # Validate current (ensure it's sufficient)
                    #     starting_current = 50.0
                    #     QMessageBox.warning(self, "Warning", "Starting current too low in JSON, using default (50.0 A)")
                except (ValueError, TypeError) as e:
                    print(f"Error parsing starting_A from JSON: {e}")
                    QMessageBox.warning(self, "Warning", "Invalid starting_A value in JSON, using default (50.0 A)")

            weld_current = 100.0  # Default value if not found in JSON
            if "curve2" in params and "weld_A" in params["curve2"]:
                try:
                    weld_current = float(params["curve2"]["weld_A"])
                    # if weld_current < 20.0:  # Validate current
                    #     weld_current = 100.0
                    #     QMessageBox.warning(self, "Warning", "Weld current too low in JSON, using default (100.0 A)")
                except (ValueError, TypeError) as e:
                    print(f"Error parsing weld_A from JSON: {e}")
                    QMessageBox.warning(self, "Warning", "Invalid weld_A value in JSON, using default (100.0 A)")

            # Calculate voltage values dynamically (using existing class attributes)
            starting_voltage = getattr(self, 'last_calculated_starting_v', 20.0)  # Default to 20V if not set
            weld_voltage = getattr(self, 'last_calculated_weld_voltage_curve1', 25.0)  # Default to 25V if not set

            # Validate voltage values
            # if starting_voltage < 15.0:
            #     starting_voltage = 20.0
            #     QMessageBox.warning(self, "Warning", "Starting voltage too low, using default (20.0 V)")
            # if weld_voltage < 15.0:
            #     weld_voltage = 25.0
            #     QMessageBox.warning(self, "Warning", "Weld voltage too low, using default (25.0 V)")

            # Get timing parameters from the interface
            try:
                gas_preflow_time = float(self.reserve_input.text())  # Gas Preflow Time (Reserve)
                # if gas_preflow_time < 0.5:
                #     gas_preflow_time = 2.0
                #     QMessageBox.warning(self, "Warning", "Gas preflow time too short, using default (2.0 s)")
            except (ValueError, AttributeError) as e:
                print(f"Error retrieving Reserve from interface: {e}")
                gas_preflow_time = 2.0
                QMessageBox.warning(self, "Warning", "Invalid Reserve value in interface, using default (2.0 s)")

            try:
                arc_starting_time = float(self.starting_s_input.text())  # Arc Starting Time (Starting S)
                # if arc_starting_time < 0.5:
                #     arc_starting_time = 1.0
                #     QMessageBox.warning(self, "Warning", "Arc starting time too short, using default (1.0 s)")
            except (ValueError, AttributeError) as e:
                print(f"Error retrieving Starting (S) from interface: {e}")
                arc_starting_time = 1.0
                QMessageBox.warning(self, "Warning", "Invalid Starting (S) value in interface, using default (1.0 s)")

            try:
                arc_detect_time = float(self.arc_ending_s_input.text())  # Arc Detect Time (Arc Ending S)
                # if arc_detect_time < 1.0:
                #     arc_detect_time = 2.0
                #     QMessageBox.warning(self, "Warning", "Arc detect time too short, using default (2.0 s)")
            except (ValueError, AttributeError) as e:
                print(f"Error retrieving Arc Ending (S) from interface: {e}")
                arc_detect_time = 2.0
                QMessageBox.warning(self, "Warning", "Invalid Arc Ending (S) value in interface, using default (2.0 s)")

            arc_start_error_time = 0.5  # Arc Start Error Time Delay (unchanged)

            # Update displays with the loaded values
            self.param_displays["Gas Preflow Time"].setText(f"{gas_preflow_time:.1f} s")
            self.param_displays["Arc Start Error Time Delay"].setText(f"{arc_start_error_time:.1f} s")
            self.param_displays["Arc Defect Time"].setText(f"{arc_detect_time:.1f} s")
            self.param_displays["Arc Starting Time"].setText(f"{arc_starting_time:.1f} s")
            self.param_displays["Arc Starting Current"].setText(f"{starting_current:.1f} A")
            self.param_displays["Welding Current"].setText(f"{weld_current:.1f} A")
            self.param_displays["Arc Starting Voltage"].setText(f"{starting_voltage:.1f} V")
            self.param_displays["Welding Voltage"].setText(f"{weld_voltage:.1f} V")
            self.param_displays["Gas Detect Signal"].setText("Yxx: ON")
            self.param_displays["Arc Starting Signal"].setText("Yxx: ON")
            self.param_displays["Arc Detect Signal"].setText("Xxx: ON")

            # ARCSTART Sequence
            # Step 1: Gas preflow
            print(f"Step 1: Starting gas preflow for {gas_preflow_time} seconds")
            self.welding_machine.set_gas(self.robot,True,gas_preflow_time)
            



            # Step 3: Apply arc starting current and voltage
            print(f"Step 3: Applying arc starting current {starting_current} A and voltage {starting_voltage} V for {arc_starting_time} seconds")
            self.welding_machine.set_current(self.robot,starting_current)
            self.welding_machine.set_voltage(self.robot,starting_voltage)
            self.welding_machine.set_arc_signal(self.robot,True)
            time.sleep(arc_starting_time)
            print(f"Step 5: Transitioning to main welding with current {weld_current} A and voltage {weld_voltage} V")
            self.welding_machine.set_current(self.robot,weld_current)
            
            self.welding_machine.set_voltage(self.robot,weld_voltage)
            time.sleep(0.2)

            # # Step 4: Wait for arc detection with retry mechanism
            # print(f"Step 4: Waiting for arc detection for {arc_detect_time} seconds")
            # max_attempts = 3
            # attempt = 1
            # arc_detected = False
            # while attempt <= max_attempts and not arc_detected:
            #     print(f"Arc detection attempt {attempt}/{max_attempts}")
            #     arc_detected = self.welding_machine.detect_arc(arc_detect_time / max_attempts)  # Split time across attempts
            #     if not arc_detected:
            #         print(f"Arc detection failed on attempt {attempt}")
            #         if attempt < max_attempts:
            #             print("Retrying with slightly increased current and voltage...")
            #             starting_current *= 1.1  # Increase by 10%
            #             starting_voltage *= 1.1  # Increase by 10%
            #             self.welding_machine.set_current(starting_current)
            #             self.welding_machine.set_voltage(starting_voltage)
            #             print(f"Adjusted to current {starting_current:.1f} A and voltage {starting_voltage:.1f} V")
            #             time.sleep(0.5)  # Small delay before retry
            #     attempt += 1

            # if not arc_detected:
            #     raise Exception("Arc detection failed after multiple attempts!")

            # Update displays with possibly adjusted values
            self.param_displays["Arc Starting Current"].setText(f"{starting_current:.1f} A")
            self.param_displays["Arc Starting Voltage"].setText(f"{starting_voltage:.1f} V")

            # Step 5: Transition to welding parameters
            # print(f"Step 5: Transitioning to main welding with current {weld_current} A and voltage {weld_voltage} V")
            # self.welding_machine.set_current(weld_current)
            # self.welding_machine.set_voltage(weld_voltage)

            # QMessageBox.information(self, "Success", "Arc started successfully!")

        except Exception as e:
            print(f"Error during arc start process: {e}")
            # Cleanup in case of error
            self.welding_machine.set_gas(self.robot,False)
            self.welding_machine.set_current(self.robot,0)
            self.welding_machine.set_voltage(self.robot,0)
            self.welding_machine.set_arc_signal(self.robot,False)
            self.param_displays["Gas Detect Signal"].setText("Yxx: OFF")
            self.param_displays["Arc Starting Signal"].setText("Yxx: OFF")
            self.param_displays["Arc Detect Signal"].setText("Xxx: OFF")
            QMessageBox.critical(self, "Error", f"Arc start failed: {str(e)}")

    def end_arc_process(self):
        """Handle the full arc end sequence using saved parameters from JSON and interface."""
        try:
            # Load parameters from the JSON file for current and voltage
            file_path = "calculation_results.json"
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    params = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading JSON file: {e}")
                QMessageBox.critical(self, "Error", "Failed to load calculation_results.json")
                return

            # Extract values from the JSON file
            # Arc Ending Current (arc_ending_A from curve2)
            ending_current = 40.0  # Default value if not found in JSON
            if "curve2" in params and "arc_ending_A" in params["curve2"]:
                try:
                    ending_current = float(params["curve2"]["arc_ending_A"])
                    # if ending_current < 0:  # Check for negative current
                    #     ending_current = 40.0
                    #     QMessageBox.warning(self, "Warning", "Negative arc_ending_A value in JSON, using default (40.0 A)")
                except (ValueError, TypeError) as e:
                    print(f"Error parsing arc_ending_A from JSON: {e}")
                    QMessageBox.warning(self, "Warning", "Invalid arc_ending_A value in JSON, using default (40.0 A)")

            # Arc Ending Voltage (arc_ending_V from curve1)
            ending_voltage = 18.0  # Default value if not found in JSON
            if "curve1" in params and "arc_ending_V" in params["curve1"]:
                try:
                    ending_voltage = float(params["curve1"]["arc_ending_V"])
                except (ValueError, TypeError) as e:
                    print(f"Error parsing arc_ending_V from JSON: {e}")
                    QMessageBox.warning(self, "Warning", "Invalid arc_ending_V value in JSON, using default (18.0 V)")

            # Prevent Stick Current (remove_stick_A from curve2)
            remove_stick_current = 30.0  # Default value if not found in JSON
            if "curve2" in params and "remove_stick_A" in params["curve2"]:
                try:
                    remove_stick_current = float(params["curve2"]["remove_stick_A"])
                except (ValueError, TypeError) as e:
                    print(f"Error parsing remove_stick_A from JSON: {e}")
                    QMessageBox.warning(self, "Warning", "Invalid remove_stick_A value in JSON, using default (30.0 A)")

            # Prevent Stick Voltage (remove_stick_V from curve1)
            remove_stick_voltage = 15.0  # Default value if not found in JSON
            if "curve1" in params and "remove_stick_V" in params["curve1"]:
                try:
                    remove_stick_voltage = float(params["curve1"]["remove_stick_V"])
                except (ValueError, TypeError) as e:
                    print(f"Error parsing remove_stick_V from JSON: {e}")
                    QMessageBox.warning(self, "Warning", "Invalid remove_stick_V value in JSON, using default (15.0 V)")

            # Get timing parameters from the interface
            try:
                proof_stick_time = float(self.proof_stick_input.text())  # Prevent Stick Time (Proof of stick)
            except (ValueError, AttributeError) as e:
                print(f"Error retrieving Proof of stick from interface: {e}")
                proof_stick_time = 1.0  # Default value
                QMessageBox.warning(self, "Warning", "Invalid Proof of stick value in interface, using default (1.0 s)")

            try:
                arc_ending_time = float(self.arc_ending_s_input.text())  # Arc Ending Time (Arc Ending S)
            except (ValueError, AttributeError) as e:
                print(f"Error retrieving Arc Ending (S) from interface: {e}")
                arc_ending_time = 1  # Default value
                QMessageBox.warning(self, "Warning", "Invalid Arc Ending (S) value in interface, using default (0.5 s)")

            gas_postflow_time = 1  # Gas Postflow Time (hardcoded, no direct field in interface)
            arc_ending_error_time = 0.5  # Arc Loss Error Time (hardcoded, no direct field in interface)
            # If you have a field for Arc Loss Error Time, you can add similar logic here.

            # Update displays with the loaded values
            self.param_displays["Arc Ending Current"].setText(f"{ending_current:.1f} A")
            self.param_displays["Arc Ending Voltage"].setText(f"{ending_voltage:.1f} V")
            self.param_displays["Prevent Stick Current"].setText(f"{remove_stick_current:.1f} A")
            self.param_displays["Prevent Stick Voltage"].setText(f"{remove_stick_voltage:.1f} V")
            self.param_displays["Prevent Stick Time"].setText(f"{proof_stick_time:.1f} s")
            self.param_displays["Gas Postflow Time"].setText(f"{gas_postflow_time:.1f} s")
            self.param_displays["Arc Ending Time"].setText(f"{arc_ending_time:.1f} s")
            self.param_displays["Arc Loss Error Time"].setText(f"{arc_ending_error_time:.1f} s")

            # ARCEND Sequence
            # Step 1: Apply arc ending current and voltage
            self.welding_machine.set_current(self.robot,ending_current)
            self.welding_machine.set_voltage(self.robot,ending_voltage)
            print(f"Arc ending with current {ending_current} A and voltage {ending_voltage} V for {arc_ending_time} seconds")
            time.sleep(arc_ending_time)

            # Step 2: Prevent stick phase
            # self.welding_machine.set_current(remove_stick_current)
            # self.welding_machine.set_voltage(remove_stick_voltage)
            # print(f"Preventing stick with current {remove_stick_current} A and voltage {remove_stick_voltage} V for {proof_stick_time} seconds")
            # time.sleep(proof_stick_time)

            # # Step 3: Disable arc signal with error delay
            self.welding_machine.set_arc_signal(self.robot,False)
            # print(f"Arc signal deactivated (Yxx), error delay: {arc_ending_error_time} seconds")
            # time.sleep(arc_ending_error_time)

            # Step 4: Gas postflow
            print(f"Gas postflow for {gas_postflow_time} seconds")
            time.sleep(gas_postflow_time)

            # Step 5: Complete shutdown
            self.welding_machine.set_current(self.robot,0)
            self.welding_machine.set_voltage(self.robot,0)
            self.welding_machine.set_gas(self.robot,False)
            self.param_displays["Gas Detect Signal"].setText("Yxx: OFF")
            self.param_displays["Arc Starting Signal"].setText("Yxx: OFF")
            self.param_displays["Arc Detect Signal"].setText("Xxx: OFF")
            print("Complete arc shutdown")

            # QMessageBox.information(self, "Success", "Arc ended successfully!")

        except Exception as e:
            # Emergency shutdown in case of error
            self.welding_machine.set_gas(self.robot,False)
            self.welding_machine.set_current(self.robot,0)
            self.welding_machine.set_voltage(self.robot,0)
            self.welding_machine.set_arc_signal(self.robot,False)
            self.param_displays["Gas Detect Signal"].setText("Yxx: OFF")
            self.param_displays["Arc Starting Signal"].setText("Yxx: OFF")
            self.param_displays["Arc Detect Signal"].setText("Xxx: OFF")
            print(f"Error during arc end process: {e}")
            QMessageBox.critical(self, "Error", f"Arc end failed: {str(e)}")



    def create_programming_page(self):
        # Création de la page principale
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        # Layout principal pour la partie gauche (boutons + "New Project")
        left_panel = QHBoxLayout()

        # Layout vertical pour les boutons à gauche de "New Project"
        left_buttons_layout = QVBoxLayout()
        left_buttons_layout.setSpacing(5)

        # Liste des boutons à gauche
        new_buttons = [
            ("Project", "Manage projects"),
            ("New", "Create a new project"),
            ("Load", "Load an existing project"),
            ("Save", "Save the current project"),
            # ("Default", "Reset to default settings")
        ]

        for btn_text, tooltip in new_buttons:
            btn = QPushButton(btn_text)
            btn.setFixedSize(100, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4682B4;
                    border: 1px solid #A9A9A9;
                    border-radius: 5px;
                    padding: 5px;
                    color: white;
                    font-weight: bold;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #87CEEB;
                }
                QPushButton:pressed {
                    background-color: #4169E1;
                }
            """)
            btn.setToolTip(tooltip)

            if btn_text == "Save":
                btn.clicked.connect(self.show_save_section)
            elif btn_text == "New":
                btn.clicked.connect(self.clear_project_tree_and_show_basic)
            elif btn_text == "Load":
                btn.clicked.connect(self.show_load_section)

            left_buttons_layout.addWidget(btn)
        
        left_buttons_layout.addStretch()
        left_panel.addLayout(left_buttons_layout)

        # Zone "New Project"
        center_panel = QVBoxLayout()
        center_panel.setSpacing(2)
        center_panel.setContentsMargins(0, 0, 0, 0)
        
        new_project_label = QLabel("New Project")
        new_project_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12pt;
            padding: 2px 6px; 
            color: white; 
            background-color: #4682B4;
            border-radius: 3px;
            border: 1px solid #2F4F4F;
        """)
        new_project_label.setFixedHeight(20)
        new_project_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        new_project_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        center_panel.addWidget(new_project_label)

        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderHidden(True)
        self.project_tree.setStyleSheet("""
            border: 1px solid #4682B4;
            background-color: #F5F5F5;
            color: black;
            border-radius: 3px;
            font-size: 14pt;
        """)
        self.project_tree.setFixedSize(500, 500)
        project_item = QTreeWidgetItem(["Project_Program"])
        QTreeWidgetItem(project_item, ["Empty"])
        project_item.setExpanded(True)
        project_item.setIcon(0, QIcon("tick.png"))
        self.project_tree.addTopLevelItem(project_item)

        # self.project_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.project_tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)

        center_panel.addWidget(self.project_tree)

        # Layout pour les boutons "Start", "Stop", "Step", "Delete"
        control_layout = QHBoxLayout()
        control_layout.setSpacing(5)

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.execute_all_movements)
        
        start_button.setFixedSize(100, 40)
        start_button.setStyleSheet("""
            QPushButton {
            
                background-color: #E0E0E0;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: black;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #B0C4DE;
            }
            QPushButton:pressed {
                background-color: #4682B4;
                color: white;
            }
        """)
        control_layout.addWidget(start_button)

        stop_button = QPushButton("Stop")
        stop_button.setFixedSize(100, 40)
        stop_button.setStyleSheet("""
            QPushButton {
                background-color: #4682B4;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: white;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #4169E1;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
                color: black;
            }
        """)
        # stop_button.clicked.connect(self.stop_loop)  # Connexion du bouton d'arrêt à la méthode stop_loop

        control_layout.addWidget(stop_button)

        step_button = QPushButton("Step")
        step_button.clicked.connect(self.on_step_button_clicked)
        step_button.setFixedSize(100, 40)
        step_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: black;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #B0C4DE;
            }
            QPushButton:pressed {
                background-color: #4682B4;
                color: white;
            }
        """)
        control_layout.addWidget(step_button)

        delete_button = QPushButton("Delete")
        delete_button.setFixedSize(100, 40)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FF4040;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: white;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
            QPushButton:pressed {
                background-color: #CC3333;
            }
        """)
        delete_button.clicked.connect(self.delete_selected_item)
        control_layout.addWidget(delete_button)
        



        center_panel.addLayout(control_layout)

        move_limit_layout = QHBoxLayout()
        move_limit_label = QLabel("Move Limit")
        move_limit_label.setStyleSheet("font-size: 9pt; color: black;")
        move_limit_layout.addWidget(move_limit_label)

        move_limit_slider = QSlider(Qt.Horizontal)
        move_limit_slider.setMinimum(0)
        move_limit_slider.setMaximum(100)
        move_limit_slider.setValue(100)
        move_limit_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #4682B4;
                border: 1px solid #A9A9A9;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #A9A9A9;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        move_limit_layout.addWidget(move_limit_slider)

        move_limit_value = QLabel("100%")
        move_limit_value.setStyleSheet("font-size: 9pt; color: black;")
        move_limit_layout.addWidget(move_limit_value)

        center_panel.addLayout(move_limit_layout)

        left_panel.addLayout(center_panel)
        main_layout.addLayout(left_panel, 2)

        self.right_container = QWidget()
        self.right_container_layout = QVBoxLayout(self.right_container)
        self.right_container_layout.setSpacing(5)
        self.right_container_layout.setContentsMargins(0, 0, 0, 0)

        self.basic_condition_widget = QWidget()
        basic_condition_layout = QVBoxLayout(self.basic_condition_widget)
        basic_condition_layout.setSpacing(5)
        basic_condition_layout.setContentsMargins(0, 0, 0, 0)
        
        basic_condition_label = QLabel("Basic Condition")
        basic_condition_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12pt; 
            padding: 2px 6px; 
            color: white; 
            background-color: #4682B4;
            border-radius: 3px;
            border: 1px solid #2F4F4F;
        """)
        basic_condition_label.setFixedHeight(20)
        basic_condition_layout.addWidget(basic_condition_label)

        basic_condition_buttons = [
            ("Loop", "Create a loop structure"),
            # ("Break", "Break out of a loop"),
            # ("Continue", "Skip to the next iteration"),
            ("arc_start", "Add an if condition"),
            ("arc_end", "Add an else-if condition"),
            # ("Else", "Add an else condition"),
            # ("Switch", "Create a switch statement"),
            # ("Case", "Add a case in a switch"),
            # ("Default", "Add a default case"),
            # ("Set", "Set a variable or value"),
            # ("Wait", "Add a delay"),
            # ("Timer", "Set a timer"),
            # ("Line Comment", "Add a single-line comment"),
            # ("Block Comment", "Add a block comment"),
            # ("Goto", "Jump to a label"),
            # ("Message", "Display a message"),
            # ("Empty", "Add an empty placeholder"),
            # ("Waypoint", "Set a waypoint"),
            ("Move Line", "Move in a straight line"),
            ("Move Joint", "Move using joint angles"),
            ("Move Circle", "Move in a circular path"),
        ]

        button_groups = [basic_condition_buttons[i:i+3] for i in range(0, len(basic_condition_buttons), 3)]

        for group in button_groups:
            group_layout = QHBoxLayout()
            group_layout.setSpacing(5)
            for btn_text, tooltip in group:
                if btn_text:
                    btn = QPushButton(btn_text)
                    btn.setFixedSize(150, 40)
                    btn.setStyleSheet("""
                        QPushButton {
                            padding: 5px;
                            border: 1px solid #A9A9A9;
                            background-color: #4682B4;
                            color: white;
                            border-radius: 5px;
                            font-size: 11pt;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #87CEEB;
                        }
                        QPushButton:pressed {
                            background-color: #4169E1;
                        }
                    """)
                    btn.setToolTip(tooltip)
                    # Special handling for "Move Joint" button
                    if btn_text == "Move Joint":
                        btn.clicked.connect(self.add_move_joint_to_tree)
                    elif btn_text == "Move Line":
                        btn.clicked.connect(self.add_move_line_to_tree)
                    elif btn_text == "Move Circle":
                        btn.clicked.connect(self.add_move_circle_to_tree)
                    elif btn_text == "arc_start":
                        btn.clicked.connect(self.add_arc_start_to_tree)
                    elif btn_text == "arc_end":
                        btn.clicked.connect(self.add_arc_end_to_tree)

                    else:
                        btn.clicked.connect(lambda checked, text=btn_text: self.add_to_project_tree(text))
                    group_layout.addWidget(btn)
                else:
                    group_layout.addStretch()
            basic_condition_layout.addLayout(group_layout)

        basic_condition_layout.addStretch()
        self.right_container_layout.addWidget(self.basic_condition_widget)
        main_layout.addWidget(self.right_container, 3)

        page.setStyleSheet("""
            QWidget {
                background-color: #DCDCDC;
            }
            QPushButton {
                border: 1px solid #A9A9A9;
                background-color: #E0E0E0;
                color: black;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #B0C4DE;
            }
            QPushButton:pressed {
                background-color: #4169E1;
        
                                   color: white;
            }
        """)

        return page
    def load_saved_programs(self):
        """Charge les programmes sauvegardés et la liste globale."""
        if not self.save_dir:
            self.save_dir = os.path.join(os.getcwd(), "programs")
            os.makedirs(self.save_dir, exist_ok=True)

        self.saved_programs = {}

        # Charger la liste des programmes depuis programs_list.json
        programs_list_file = os.path.join(self.save_dir, "programs_list.json")
        if os.path.exists(programs_list_file):
            try:
                with open(programs_list_file, "r") as file:
                    program_names = json.load(file)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement de la liste des programmes : {e}")
                program_names = []
        else:
            program_names = []

        # Charger chaque programme individuel
        for filename in os.listdir(self.save_dir):
            if filename.endswith(".json") and filename != "programs_list.json":
                program_name = filename[:-5]  # Supprimer l'extension ".json"
                if program_name in program_names:  # Vérifier que le programme est dans la liste
                    file_path = os.path.join(self.save_dir, filename)
                    try:
                        with open(file_path, "r") as file:
                            content = json.load(file)
                        self.saved_programs[program_name] = content
                        print(f"Programme chargé : {program_name}")
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Erreur lors du chargement de '{filename}' : {e}")



    def show_save_section(self):
        # Nettoyer le conteneur de droite
        for i in reversed(range(self.right_container_layout.count())):
            widget = self.right_container_layout.itemAt(i).widget()
            if widget:
                self.right_container_layout.removeWidget(widget)
                widget.setParent(None)

        # Créer le widget principal pour la section "Save"
        save_widget = QWidget()
        layout = QVBoxLayout(save_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Titre
        title = QLabel("Save Project")
        title.setStyleSheet("""
            font-weight: bold;
            font-size: 12pt;
            padding: 2px 6px;
            color: white;
            background-color: #4682B4;
            border-radius: 3px;
            border: 1px solid #2F4F4F;
        """)
        title.setFixedHeight(20)
        layout.addWidget(title)

        # Champ de saisie pour le nom du programme
        name_input = QLineEdit()
        name_input.setPlaceholderText("Please input program name")
        name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #A9A9A9;
                border-radius: 3px;
                padding: 5px;
                background-color: #F5F5F5;
                font-size: 12pt;
            }
        """)
        layout.addWidget(name_input)

        # Layout horizontal pour le bouton de sauvegarde
        button_row = QHBoxLayout()
        button_row.setSpacing(5)

        # Bouton "Save"
        save_btn = QPushButton("save")
        save_btn.setFixedSize(80, 30)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: black;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #B0C4DE;
            }
            QPushButton:pressed {
                background-color: #4682B4;
                color: white;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_program(name_input.text(), save_widget))
        button_row.addWidget(save_btn)
        button_row.addStretch()

        layout.addLayout(button_row)
        layout.addStretch()

        self.right_container_layout.addWidget(save_widget)



    def save_program(self, program_name, save_widget):
        # Si aucun nom n'est fourni et qu'un programme est déjà chargé, utiliser le nom actuel
        if not program_name and self.current_program_name:
                program_name = self.current_program_name

        # Vérifier que le nom du programme n'est pas vide
        if not program_name:
            QMessageBox.warning(self.project_tree, "Attention", "Le nom du programme ne peut pas être vide !")
            return

        root = self.project_tree.topLevelItem(0)
        if not root:
            QMessageBox.warning(self.project_tree, "Attention", "Aucun projet à sauvegarder !")
            return

        # Construire le contenu du programme à partir des éléments de l'arborescence
        program_content = []
        for i in range(root.childCount()):
            item = root.child(i)
            item_text = item.text(0)
            movement_data = item.data(0, Qt.UserRole)

            program_content.append({
                "text": item_text,
                "data": movement_data
            })

        # Sauvegarder dans le dictionnaire interne
        self.saved_programs[program_name] = program_content

        # Définir le répertoire de sauvegarde s’il n’existe pas
        if not self.save_dir:
            self.save_dir = os.path.join(os.getcwd(), "programs")
            os.makedirs(self.save_dir, exist_ok=True)

        # Sauvegarder dans un fichier JSON
        program_file = os.path.join(self.save_dir, f"{program_name}.json")
        try:
            with open(program_file, "w") as file:
                json.dump(program_content, file, indent=4)
            print(f"Programme '{program_name}' sauvegardé dans : {program_file}")
            # QMessageBox.information(self.project_tree, "Succès", f"Programme '{program_name}' sauvegardé avec succès !")
            self.is_modified = False  # Réinitialiser l'indicateur après sauvegarde
            self.current_program_name = program_name  # Mettre à jour le nom du programme actuel

            # Sauvegarder la liste des programmes mise à jour
            self.save_programs_list()

        except Exception as e:
            QMessageBox.critical(self.project_tree, "Erreur", f"Échec de la sauvegarde : {e}")
            print(f"Erreur lors de la sauvegarde : {e}")
            return

        # Réinitialiser l’état de base de l’interface
        self.show_basic_condition()


    # Afficher la section "Load"
    def show_load_section(self):
        # Retirer le contenu actuel du conteneur droit
        for i in reversed(range(self.right_container_layout.count())):
            widget = self.right_container_layout.itemAt(i).widget()
            if widget:
                self.right_container_layout.removeWidget(widget)
                widget.setParent(None)

        # Créer un widget pour la section "Load"
        load_widget = QWidget()
        load_layout = QVBoxLayout(load_widget)
        load_layout.setContentsMargins(10, 10, 10, 10)
        load_layout.setSpacing(5)

        # Titre "Load Program"
        load_label = QLabel("Load Program")
        load_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12pt; 
            padding: 2px 6px; 
            color: white; 
            background-color: #4682B4;
            border-radius: 3px;
            border: 1px solid #2F4F4F;
        """)
        load_label.setFixedHeight(20)
        load_layout.addWidget(load_label)

        # Liste des programmes sauvegardés
        self.program_list = QListWidget()
        if not self.saved_programs:
            self.program_list.addItem("No programs saved yet.")
        else:
            for program_name in self.saved_programs.keys():
                self.program_list.addItem(program_name)
        self.program_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #4682B4;
                background-color: #F5F5F5;
                color: black;
                border-radius: 3px;
                font-size: 14pt;  /* Augmentation de la taille de la police */
            }
        """)
        load_layout.addWidget(self.program_list)

        # Layout horizontal pour les boutons "Load", "Remove" et "Back"
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)

        # Bouton "Load"
        load_button = QPushButton("Load")
        load_button.setFixedSize(80, 30)
        load_button.setStyleSheet("""
            QPushButton {
                background-color: #4682B4;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #87CEEB;
            }
            QPushButton:pressed {
                background-color: #4169E1;
            }
        """)
        load_button.clicked.connect(self.load_program_from_list)
        button_layout.addWidget(load_button)

        # Bouton "Remove"
        remove_button = QPushButton("Remove")
        remove_button.setFixedSize(80, 30)
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #FF4040;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
            QPushButton:pressed {
                background-color: #CC3333;
            }
        """)
        remove_button.clicked.connect(self.remove_program_from_list)
        button_layout.addWidget(remove_button)

        # Bouton "Back"
        back_button = QPushButton("Back")
        back_button.setFixedSize(80, 30)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            QPushButton:pressed {
                background-color: #4682B4;
                color: white;
            }
        """)
        back_button.clicked.connect(self.show_basic_condition)
        button_layout.addWidget(back_button)

        load_layout.addLayout(button_layout)
        load_layout.addStretch()  # Pousse le contenu vers le haut
        self.right_container_layout.addWidget(load_widget)

    def load_program_from_list(self):
        selected_item = self.program_list.currentItem()
        if not selected_item or selected_item.text() == "No programs saved yet.":
            QMessageBox.warning(self, "Warning", "Please select a program to load!")
            return

        program_name = selected_item.text()
        program_content = self.saved_programs.get(program_name, [])

        # Réinitialiser l'arborescence du projet
        self.current_program_name = program_name
        self.project_tree.clear()
        root = QTreeWidgetItem(["Project_Program"])
        self.project_tree.addTopLevelItem(root)
        root.setExpanded(True)

        # Charger le contenu du programme
        if program_content:
            for item_data in program_content:
                item_text = item_data.get("text", "Unnamed Step")
                movement_data = item_data.get("data")

                new_item = QTreeWidgetItem([item_text])
                if movement_data is not None:
                    new_item.setData(0, Qt.UserRole, tuple(movement_data))

                root.addChild(new_item)
        else:
            # Si le programme est vide, ajouter un élément vide
            root.addChild(QTreeWidgetItem(["Empty"]))

        # Confirmation de chargement
        QMessageBox.information(self, "Success", f"Program '{program_name}' loaded successfully!")
        self.is_modified = False  # Réinitialiser l'indicateur après chargement
        self.current_program_name = program_name  # Mettre à jour le nom du programme actuel

        # Afficher l'état de base
        self.show_basic_condition()

    def remove_program_from_list(self):
        selected_item = self.program_list.currentItem()
        if not selected_item or selected_item.text() == "No programs saved yet.":
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un programme à supprimer !")
            return

        program_name = selected_item.text()

        # Demander confirmation
        confirm = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer '{program_name}' ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return

        # Supprimer du dictionnaire
        self.saved_programs.pop(program_name, None)

        # Si le programme supprimé est celui actuellement chargé, réinitialiser
        if self.current_program_name == program_name:
            self.current_program_name = None
            self.clear_project_tree()  # Nettoyer l'arborescence
            self.is_modified = False  # Réinitialiser l'état modifié

        # Définir save_dir si nécessaire
        if not self.save_dir:
            self.save_dir = os.path.join(os.getcwd(), "programs")
            print(f"Chemin par défaut défini : {self.save_dir}")

        # Supprimer le fichier
        try:
            program_file = os.path.join(self.save_dir, f"{program_name}.json")  # Correction : .json au lieu de .txt
            if os.path.isfile(program_file):
                os.remove(program_file)
                print(f"Fichier supprimé : {program_file}")

            QMessageBox.information(self, "Succès", f"Programme '{program_name}' supprimé avec succès !")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la suppression : {e}")
            print(f"Erreur lors de la suppression : {e}")
            return

        # Marquer comme modifié pour indiquer un changement dans la liste des programmes
        self.is_modified = True

        # Sauvegarder la liste des programmes mise à jour
        self.save_programs_list()

        # Rafraîchir la liste
        self.program_list.clear()
        if not self.saved_programs:
            self.program_list.addItem("No programs saved yet.")
        else:
            self.program_list.addItems(self.saved_programs.keys())


    def add_to_project_tree(self, text):
        self.is_modified = True  # Marquer comme modifié
        root = self.project_tree.topLevelItem(0)
        if not root:
            root = QTreeWidgetItem(["Project_Program"])
            self.project_tree.addTopLevelItem(root)
            root.setExpanded(True)

        # Supprimer "Empty" si présent
        for i in range(root.childCount()):
            child = root.child(i)
            if child.text(0) == "Empty":
                root.removeChild(child)
                break

        # Ajouter le nouvel élément
        new_item = QTreeWidgetItem([text])
        root.addChild(new_item)
        root.setExpanded(True)

    def on_tree_item_clicked(self, item, column):
        if item.text(column) in ["Project_Program", "Empty"]:
            return

        dialog = QDialog(self.project_tree)
        dialog.setWindowTitle(f"Manage {item.text(column)}")
        dialog.setFixedSize(200, 100)

        dialog_layout = QVBoxLayout(dialog)

        label = QLabel(f"Selected: {item.text(column)}")
        dialog_layout.addWidget(label)

        confirm_button = QPushButton("Confirm")
        confirm_button.setFixedSize(100, 30)
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4682B4;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #87CEEB;
            }
            QPushButton:pressed {
                background-color: #4169E1;
            }
        """)
        confirm_button.clicked.connect(lambda: self.confirm_item(item, dialog))
        dialog_layout.addWidget(confirm_button)

        remove_button = QPushButton("Remove")
        remove_button.setFixedSize(100, 30)
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #FF4040;
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
            QPushButton:pressed {
                background-color: #CC3333;
            }
        """)
        remove_button.clicked.connect(lambda: self.remove_item(item, dialog))
        dialog_layout.addWidget(remove_button)

        dialog.exec_()

    def confirm_item(self, item, dialog):
        current_text = item.text(0)
        new_text = current_text.replace("_Undefined", "")
        item.setText(0, new_text)
        item.setIcon(0, QIcon("tick.png"))
        dialog.accept()

    def remove_item(self, item, dialog):
        parent = item.parent()
        if parent:
            parent.removeChild(item)

        if parent and parent.childCount() == 0:
            empty_item = QTreeWidgetItem(["Empty"])
            parent.addChild(empty_item)
            parent.setExpanded(True)

        dialog.accept()

    # def delete_selected_item(self):
    #     selected_item = self.project_tree.currentItem()
    #     if selected_item and selected_item.text(0) != "Project_Program":
    #         parent = selected_item.parent()
    #         if parent:
    #             parent.removeChild(selected_item)

    #         if parent and parent.childCount() == 0:
    #             empty_item = QTreeWidgetItem(["Empty"])
    #             parent.addChild(empty_item)
    #             parent.setExpanded(True)

    def delete_selected_item(self):
        self.is_modified = True  # Marquer comme modifié
        selected_items = self.project_tree.selectedItems()
        if not selected_items:
            return  # Rien n'est sélectionné

        selected_item = selected_items[0]
        parent = selected_item.parent()

        if parent:  # Si l'élément a un parent (n'est pas la racine)
            parent.removeChild(selected_item)

            # Si le parent n'a plus d'enfants, ajouter "Empty"
            if parent.childCount() == 0:
                parent.addChild(QTreeWidgetItem(["Empty"]))
                parent.setExpanded(True)


    def show_basic_condition(self):
        # Retirer le contenu actuel du conteneur sans le supprimer
        for i in reversed(range(self.right_container_layout.count())):
            widget = self.right_container_layout.itemAt(i).widget()
            if widget is not None:
                self.right_container_layout.removeWidget(widget)  # Retirer sans supprimer
                widget.setParent(None)  # Détacher le widget du parent

        # Remettre "Basic Condition"
        self.right_container_layout.addWidget(self.basic_condition_widget)
    def add_move_circle_to_tree(self, first_joints=None, second_joints=None, third_joints=None, speed=None, acc=None):
        """Ajouter une commande Move Circle à l'arborescence avec vitesse et accélération."""
        if first_joints is None or second_joints is None or third_joints is None:
            dialog = MoveCircleDialog(self.robot, joint_updater, self)
            if not dialog.exec_():
                return -1
            first_joints, second_joints, third_joints = dialog.get_waypoints()
        
        # Set default speed and acceleration if not provided
        speed = float(speed) if speed is not None else 2000.00  # Default speed in mm/s
        acc = float(acc) if acc is not None else 2000.00       # Default acceleration in mm/s²
        
        root = self.project_tree.topLevelItem(0)
        if not root:
            root = QTreeWidgetItem(["Project_Program"])
            self.project_tree.addTopLevelItem(root)
            root.setExpanded(True)
        
        # Supprimer "Empty" si présent
        for i in range(root.childCount()):
            child = root.child(i)
            if child.text(0) == "Empty":
                root.removeChild(child)
                break
        
        # Formater le texte d'affichage
        first_joints_str = ", ".join(map(lambda x: f"{x:.2f}", first_joints))
        second_joints_str = ", ".join(map(lambda x: f"{x:.2f}", second_joints))
        third_joints_str = ", ".join(map(lambda x: f"{x:.2f}", third_joints))
        move_circle_text = f"Move Circle ({first_joints_str}) -> ({second_joints_str}) -> ({third_joints_str}), Speed: {speed:.2f} mm/s, Acc: {acc:.2f} mm/s²"
        
        # Ajouter à l'arborescence avec la structure correcte
        new_item = QTreeWidgetItem([move_circle_text])
        new_item.setData(0, Qt.UserRole, ("Circle", ((first_joints, second_joints, third_joints), speed, acc)))  # Structure ajustée
        root.addChild(new_item)
        root.setExpanded(True)
        self.is_modified = True
        return 0

    def add_move_joint_to_tree(self, joints=None):
        self.is_modified = True
        
        if joints is None or not isinstance(joints, (list, tuple)):
            joint_values = [display.text() for display in self.joint_value_displays]
        else:
            try:
                joint_values = [f"{float(j):.6f}" for j in joints]
            except (TypeError, ValueError) as e:
                print(f"Error formatting joints: {e}. Using current joint values.")
                joint_values = [display.text() for display in self.joint_value_displays]
        
        # Utiliser des valeurs par défaut sans ouvrir la fenêtre de dialogue
        radius = 500.0  # Longueur du bras en mm (à ajuster selon votre robot)
        joint_speeds = [2000.0 / radius] * 6  # Vitesse par défaut 2000 mm/s convertie en rad/s
        joint_accs = [2000.0 / radius] * 6    # Accélération par défaut 2000 mm/s² convertie en rad/s²
        
        # Reconversion pour l'affichage (mm/s)
        display_speeds = [speed * radius for speed in joint_speeds]
        
        joint_values_str = ", ".join(joint_values)
        speeds_str = ", ".join([f"{speed:.2f}" for speed in display_speeds])
        move_joint_text = f"Move Joint ({joint_values_str}, Speeds: {speeds_str} mm/s)"
        
        root = self.project_tree.topLevelItem(0)
        if not root:
            root = QTreeWidgetItem(["Project_Program"])
            self.project_tree.addTopLevelItem(root)
            root.setExpanded(True)
        
        for i in range(root.childCount()):
            child = root.child(i)
            if child.text(0) == "Empty":
                root.removeChild(child)
                break
        
        new_item = QTreeWidgetItem([move_joint_text])
        new_item.setData(0, Qt.UserRole, ("Joint", (joint_values, joint_speeds, joint_accs)))
        root.addChild(new_item)
        root.setExpanded(True)
        
        return 0

    def add_move_line_to_tree(self, joints=None):
        """Ajouter une commande Move Line à l'arborescence sans afficher la fenêtre de vitesse."""
        self.is_modified = True
        
        # Handle the case where joints is None or invalid
        if joints is None or not isinstance(joints, (list, tuple)):
            # Fallback to current joint values from joint_value_displays
            joint_values = [display.text() for display in self.joint_value_displays]
        else:
            try:
                # Ensure joints contains valid numbers
                joint_values = [f"{float(j):.6f}" for j in joints]
            except (TypeError, ValueError) as e:
                print(f"Error formatting joints: {e}. Using current joint values.")
                joint_values = [display.text() for display in self.joint_value_displays]
        
        # Skip the dialog and set default speed and acceleration values
        speed = 2000.00  # Default speed in mm/s (as seen in the dialog screenshot)
        acc = 2000.00    # Default acceleration in mm/s² (as seen in the dialog screenshot)
        
        # Format joint values as a string
        joint_values_str = ", ".join(joint_values)
        # Include speed and acceleration in the displayed text
        move_line_text = f"Move Line ({joint_values_str}, Speed: {speed:.2f} mm/s, Acc: {acc:.2f} mm/s²)"
        
        # Add to the project tree
        root = self.project_tree.topLevelItem(0)
        if not root:
            root = QTreeWidgetItem(["Project_Program"])
            self.project_tree.addTopLevelItem(root)
            root.setExpanded(True)
        
        # Remove "Empty" item if present
        for i in range(root.childCount()):
            child = root.child(i)
            if child.text(0) == "Empty":
                root.removeChild(child)
                break
        
        # Add new "Move Line" item with joint values, speed, and acceleration
        new_item = QTreeWidgetItem([move_line_text])
        new_item.setData(0, Qt.UserRole, ("Line", (joint_values, speed, acc)))
        root.addChild(new_item)
        root.setExpanded(True)
        
        return 0

    def execute_all_movements(self):
        if not self.check_save_before_execution():
            return

        try:
            root = self.project_tree.topLevelItem(0)
            if not root or root.childCount() == 0:
                QMessageBox.warning(self, "Avertissement", "Aucun programme à exécuter dans l'arborescence !")
                return

            print("Début de l'exécution du programme...")

            file_number = str(self.current_file)
            json_speed = float(self.file_parameters[file_number].get("speed", 2000.00))  # Par défaut 2000 mm/s

            in_arc_sequence = False
            for i in range(root.childCount()):
                item = root.child(i)
                item_text = item.text(0)

                if item_text == "Arc Start":
                    self.start_arc_process()
                    in_arc_sequence = True
                    continue
                elif item_text == "Arc End":
                    self.end_arc_process()
                    in_arc_sequence = False
                    continue

                movement_data = item.data(0, Qt.UserRole)
                if not movement_data:
                    continue

                movement_type, coordinates = movement_data
                if movement_type in ["Joint", "Line", "Circle"]:
                    if in_arc_sequence:
                        if movement_type == "Joint":
                            joint_values, joint_speeds, joint_accs = coordinates
                            radius = 500.0  # Même valeur que ci-dessus
                            adjusted_speeds = [(json_speed / radius)] * len(joint_speeds)  # Convertir mm/s en rad/s
                            adjusted_coordinates = (movement_type, (joint_values, adjusted_speeds, joint_accs))
                        elif movement_type == "Circle":
                            (first_values, second_values, third_values), speed, acc = coordinates
                            adjusted_coordinates = (movement_type, ((first_values, second_values, third_values), json_speed, acc))
                        else:  # Line
                            joint_values, speed, acc = coordinates
                            adjusted_coordinates = (movement_type, (joint_values, json_speed, acc))
                    else:
                        adjusted_coordinates = (movement_type, coordinates)

                    self.move_robot_to_coordinates(adjusted_coordinates)
                else:
                    print(f"⚠️ Type de mouvement non reconnu : '{movement_type}'")

            print("✅ Fin de l'exécution du programme.")
            QMessageBox.information(self, "Succès", "Programme exécuté avec succès !")

        except Exception as e:
            print(f"❌ Erreur critique : {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Échec de l'exécution : {str(e)}")
    def are_points_collinear(self, joints1, joints2, joints3):
            """
            Vérifie si trois points définis par des angles de joints sont colinéaires.
            Args:
                joints1 (tuple): Angles des joints pour le premier point (en radians).
                joints2 (tuple): Angles des joints pour le deuxième point (en radians).
                joints3 (tuple): Angles des joints pour le troisième point (en radians).
            Returns:
                bool: True si les points sont colinéaires, False sinon.
            """
            # Convertir les angles de joints en coordonnées cartésiennes
            pos1 = self.robot.forward_kin(joints1)['pos']
            pos2 = self.robot.forward_kin(joints2)['pos']
            pos3 = self.robot.forward_kin(joints3)['pos']

            # Calculer les vecteurs entre les points
            vec1 = [pos2[i] - pos1[i] for i in range(3)]  # Vecteur P1 -> P2
            vec2 = [pos3[i] - pos2[i] for i in range(3)]  # Vecteur P2 -> P3

            # Calculer le produit vectoriel pour vérifier la colinéarité
            cross_product = [
                vec1[1] * vec2[2] - vec1[2] * vec2[1],
                vec1[2] * vec2[0] - vec1[0] * vec2[2],
                vec1[0] * vec2[1] - vec1[1] * vec2[0]
            ]

            # Si le produit vectoriel est proche de zéro, les points sont colinéaires
            tolerance = 1e-6
            return all(abs(x) < tolerance for x in cross_product)
    
    def move_robot_to_coordinates(self, coordinates):
        """
        Déplace le robot vers les coordonnées spécifiées.
        Utilise les paramètres de vitesse et d'accélération préalablement sauvegardés dans les données.
        """
        try:
            # Vérifier l'état du robot
            robot_state = self.robot.get_robot_state()
            if robot_state is None:
                return

            mode, data = coordinates

            # Initialiser les paramètres de mouvement pour tous les modes
            result = self.robot.init_profile()
            if result != RobotErrorType.RobotError_SUCC:
                return

            # Définir le système de coordonnées de base
            result = self.robot.set_base_coord()
            if result != RobotErrorType.RobotError_SUCC:
                return

            # Extraire les valeurs de vitesse et d'accélération des données
            if mode == "Joint":
                joint_values, joint_speeds, joint_accs = data

                # Définir les vitesses et accélérations maximales des joints
                joint_maxvelc = tuple(joint_speeds)  # rad/s
                joint_maxacc = tuple(joint_accs)     # rad/s²

                result = self.robot.set_joint_maxvelc(joint_maxvelc)
                if result != RobotErrorType.RobotError_SUCC:
                    return

                result = self.robot.set_joint_maxacc(joint_maxacc)
                if result != RobotErrorType.RobotError_SUCC:
                    return

            else:
                # Pour "Move Line" et "Move Circle"
                if mode == "Circle":
                    (first_values, second_values, third_values), speed, acc = data
                else:
                    joint_values, speed, acc = data

                # Définir les vitesses et accélérations maximales des joints (valeurs par défaut)
                joint_maxvelc = (1.5, 1.5, 1.5, 1.5, 1.5, 1.5)  # rad/s
                joint_maxacc = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0)    # rad/s²

                result = self.robot.set_joint_maxvelc(joint_maxvelc)
                if result != RobotErrorType.RobotError_SUCC:
                    return

                result = self.robot.set_joint_maxacc(joint_maxacc)
                if result != RobotErrorType.RobotError_SUCC:
                    return

                # Définir la vitesse linéaire maximale (en m/s, donc convertir mm/s en m/s)
                end_max_line_velc = speed / 1000.0  # Convertir mm/s en m/s
                result = self.robot.set_end_max_line_velc(end_max_line_velc)
                if result != RobotErrorType.RobotError_SUCC:
                    return

                # Définir l'accélération linéaire maximale (en m/s², donc convertir mm/s² en m/s²)
                end_max_line_acc = acc / 1000.0  # Convertir mm/s² en m/s²
                result = self.robot.set_end_max_line_acc(end_max_line_acc)
                if result != RobotErrorType.RobotError_SUCC:
                    return

            if mode == "Circle":
                # Extraire les coordonnées
                (first_values, second_values, third_values), _, _ = data

                result = self.robot.remove_all_waypoint()
                if result != RobotErrorType.RobotError_SUCC:
                    return

                # Convertir le premier ensemble en radians
                first_joints = []
                for coord in first_values:
                    try:
                        coord_float = float(coord)
                        first_joints.append(math.radians(coord_float))
                    except (ValueError, TypeError):
                        return

                # Convertir le deuxième ensemble en radians
                second_joints = []
                for coord in second_values:
                    try:
                        coord_float = float(coord)
                        second_joints.append(math.radians(coord_float))
                    except (ValueError, TypeError):
                        return

                # Convertir le troisième ensemble en radians
                third_joints = []
                for coord in third_values:
                    try:
                        coord_float = float(coord)
                        third_joints.append(math.radians(coord_float))
                    except (ValueError, TypeError):
                        QMessageBox.critical(self, "Erreur", f"Valeur de coordonnée invalide dans le troisième point de passage : {coord}. Doit être un nombre.")
                        return

                first_joints_tuple = tuple(first_joints)
                second_joints_tuple = tuple(second_joints)
                third_joints_tuple = tuple(third_joints)

                print(f"Ajout du premier point de passage : {first_joints_tuple}")
                print(f"Ajout du deuxième point de passage : {second_joints_tuple}")
                print(f"Ajout du troisième point de passage : {third_joints_tuple}")

                self.robot.move_joint(first_joints_tuple)
                self.robot.remove_all_waypoint()

                result = self.robot.add_waypoint(joint_radian=first_joints_tuple)
                if result != RobotErrorType.RobotError_SUCC:
                    QMessageBox.critical(self, "Erreur", f"Échec de l'ajout du premier point de passage : {result}")
                    return

                result = self.robot.add_waypoint(joint_radian=second_joints_tuple)
                if result != RobotErrorType.RobotError_SUCC:
                    QMessageBox.critical(self, "Erreur", f"Échec de l'ajout du deuxième point de passage : {result}")
                    return

                result = self.robot.add_waypoint(joint_radian=third_joints_tuple)
                if result != RobotErrorType.RobotError_SUCC:
                    QMessageBox.critical(self, "Erreur", f"Échec de l'ajout du troisième point de passage : {result}")
                    return

                result = self.robot.set_circular_loop_times(1)
                if result != RobotErrorType.RobotError_SUCC:
                    QMessageBox.critical(self, "Erreur", f"Échec de la définition du nombre circulaire : {result}")
                    return

                print("Exécution de move_track avec ARC_CIR...")
                result = self.robot.move_track(RobotMoveTrackType.ARC_CIR)

            else:
                # Pour "Move Joint" et "Move Line"
                joint_values, _, _ = data

                target_joints = []
                for coord in joint_values:
                    try:
                        coord_float = float(coord)
                        target_joints.append(math.radians(coord_float))
                    except (ValueError, TypeError):
                        QMessageBox.critical(self, "Erreur", f"Valeur de coordonnée invalide : {coord}. Doit être un nombre.")
                        return

                target_joints_tuple = tuple(target_joints)

                if mode == "Joint":
                    result = self.robot.move_joint(joint_radian=target_joints_tuple, issync=True)
                elif mode == "Line":
                    result = self.robot.move_line(joint_radian=target_joints_tuple)
                else:
                    QMessageBox.critical(self, "Erreur", f"Mode non supporté : {mode}")
                    return

            if result != RobotErrorType.RobotError_SUCC:
                QMessageBox.critical(self, "Erreur", f"Échec du mouvement : {result}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec du mouvement du robot : {str(e)}")
    def on_step_button_clicked(self):
        if not self.check_save_before_execution():
            return

        selected_items = self.project_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a 'Move Joint', 'Move Line', or 'Move Circle' item in the project tree!")
            return

        selected_item = selected_items[0]
        item_text = selected_item.text(0)

        if item_text.startswith("Move Joint"):
            mode = "Joint"
        elif item_text.startswith("Move Line"):
            mode = "Line"
        elif item_text.startswith("Move Circle"):
            mode = "Circle"
        else:
            QMessageBox.warning(self, "Warning", "Selected item is not a 'Move Joint', 'Move Line', or 'Move Circle' command!")
            return

        try:
            movement_data = selected_item.data(0, Qt.UserRole)
            if not movement_data:
                QMessageBox.critical(self, "Error", "No movement data associated with this item!")
                return

            movement_type, coordinates = movement_data

            if movement_type == "Circle":
                (first_values, second_values, third_values), speed, acc = coordinates
                adjusted_coordinates = (movement_type, ((first_values, second_values, third_values), speed, acc))
            elif movement_type == "Line":
                joint_values, speed, acc = coordinates
                adjusted_coordinates = (movement_type, (joint_values, speed, acc))
            else:  # Move Joint
                joint_values, joint_speeds, joint_accs = coordinates
                adjusted_coordinates = (movement_type, (joint_values, joint_speeds, joint_accs))

            self.move_robot_to_coordinates(adjusted_coordinates)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute movement: {str(e)}")

    def clear_project_tree(self):
        # Nettoyer l'arborescence actuelle
        self.project_tree.clear()
        # Recréer l'arborescence initiale
        root = QTreeWidgetItem(["Project_Program"])
        root.addChild(QTreeWidgetItem(["Empty"]))
        root.setExpanded(True)
        root.setIcon(0, QIcon("tick.png"))
        self.project_tree.addTopLevelItem(root)

    def clear_project_tree_and_show_basic(self):
        # Nettoyer l'arborescence
        self.clear_project_tree()
        self.current_program_name = None  # Réinitialiser le nom du programme
        self.is_modified = False  # Réinitialiser l'indicateur de modification
        # Afficher la section "Basic Condition"
        self.show_basic_condition()
    def check_save_before_execution(self):
        """
        Vérifie si le programme a été modifié et sauvegarde automatiquement avec la date d'aujourd'hui.
        Retourne True pour permettre l'exécution.
        """
        if self.is_modified:
            # Générer un nom de programme avec la date d'aujourd'hui
            program_name = self.generate_program_name_with_date()
            print(f"Le programme a été modifié. Sauvegarde automatique sous : {program_name}")

            # Sauvegarder automatiquement
            self.save_program(program_name, None)

            # Vérifier si la sauvegarde a réussi (is_modified devrait être False après une sauvegarde réussie)
            if self.is_modified:
                print("Échec de la sauvegarde automatique. Annulation de l'exécution.")
                return False  # Annuler l'exécution si la sauvegarde échoue

        return True  # Autoriser l'exécution
    def save_programs_list(self):
        """Sauvegarde la liste des programmes dans un fichier global."""
        if not self.save_dir:
            self.save_dir = os.path.join(os.getcwd(), "programs")
            os.makedirs(self.save_dir, exist_ok=True)

        programs_list_file = os.path.join(self.save_dir, "programs_list.json")
        try:
            with open(programs_list_file, "w") as file:
                json.dump(list(self.saved_programs.keys()), file, indent=4)
            print(f"Liste des programmes sauvegardée dans : {programs_list_file}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la liste des programmes : {e}")

    def add_arc_start_to_tree(self):
        """Add an 'Arc Start' item to the project tree."""
        selected_item = self.project_tree.currentItem()
        if not selected_item:
            selected_item = self.project_tree.topLevelItem(0)  # Default to the root "Project_Program"

        # Remove "Empty" item if present
        for i in range(selected_item.childCount()):
            if selected_item.child(i).text(0) == "Empty":
                selected_item.removeChild(selected_item.child(i))
                break

        # Add new "Arc Start" item
        arc_start_item = QTreeWidgetItem(["Arc Start"])
        arc_start_item.setIcon(0, QIcon("tick.png"))  # Use the same icon as other items
        selected_item.addChild(arc_start_item)
        selected_item.setExpanded(True)

    def add_arc_end_to_tree(self):
        """Add an 'Arc End' item to the project tree."""
        selected_item = self.project_tree.currentItem()
        if not selected_item:
            selected_item = self.project_tree.topLevelItem(0)  # Default to the root "Project_Program"

        # Remove "Empty" item if present
        for i in range(selected_item.childCount()):
            if selected_item.child(i).text(0) == "Empty":
                selected_item.removeChild(selected_item.child(i))
                break

        # Add new "Arc End" item
        arc_end_item = QTreeWidgetItem(["Arc End"])
        arc_end_item.setIcon(0, QIcon("tick.png"))  # Use the same icon as other items
        selected_item.addChild(arc_end_item)
        selected_item.setExpanded(True)
    def on_tree_item_double_clicked(self, item, column):
        item_text = item.text(0)
        movement_data = item.data(0, Qt.UserRole)

        if not movement_data:
            return

        movement_type, coordinates = movement_data

        if movement_type not in ["Line", "Circle", "Joint"]:
            return

        radius = 500.0  # Même valeur que ci-dessus
        if movement_type == "Circle":
            (first_values, second_values, third_values), speed, acc = coordinates
            first_values = [float(val) if isinstance(val, str) else val for val in first_values]
            second_values = [float(val) if isinstance(val, str) else val for val in second_values]
            third_values = [float(val) if isinstance(val, str) else val for val in third_values]
            speed = float(speed) if isinstance(speed, str) else speed
            acc = float(acc) if isinstance(acc, str) else acc
        elif movement_type == "Line":
            joint_values, speed, acc = coordinates
            joint_values = [float(val) if isinstance(val, str) else val for val in joint_values]
            speed = float(speed) if isinstance(speed, str) else speed
            acc = float(acc) if isinstance(acc, str) else acc
        else:  # Move Joint
            joint_values, joint_speeds, joint_accs = coordinates
            joint_values = [float(val) if isinstance(val, str) else val for val in joint_values]
            joint_speeds = [float(val) if isinstance(val, str) else val for val in joint_speeds]
            joint_accs = [float(val) if isinstance(val, str) else val for val in joint_accs]
            speed = joint_speeds[0] * radius  # Convertir rad/s en mm/s pour l'affichage

        dialog = EditSpeedDialog(self, current_speed=speed)
        if dialog.exec_():
            new_speed = dialog.get_speed()

            if movement_type == "Circle":
                new_coordinates = ((first_values, second_values, third_values), new_speed, acc)
            elif movement_type == "Line":
                new_coordinates = (joint_values, new_speed, acc)
            else:  # Move Joint
                new_joint_speeds = [new_speed / radius] * len(joint_speeds)  # Convertir mm/s en rad/s
                new_coordinates = (joint_values, new_joint_speeds, joint_accs)

            item.setData(0, Qt.UserRole, (movement_type, new_coordinates))

            try:
                if movement_type == "Circle":
                    first_joints_str = ", ".join(map(lambda x: f"{x:.2f}", first_values))
                    second_joints_str = ", ".join(map(lambda x: f"{x:.2f}", second_values))
                    third_joints_str = ", ".join(map(lambda x: f"{x:.2f}", third_values))
                    item.setText(0, f"Move Circle ({first_joints_str}) -> ({second_joints_str}) -> ({third_joints_str}), Speed: {new_speed:.2f} mm/s, Acc: {acc:.2f} mm/s²")
                elif movement_type == "Line":
                    joint_values_str = ", ".join(map(lambda x: f"{x:.2f}", joint_values))
                    item.setText(0, f"Move Line ({joint_values_str}, Speed: {new_speed:.2f} mm/s, Acc: {acc:.2f} mm/s²)")
                else:  # Move Joint
                    speeds_str = ", ".join([f"{new_speed:.2f}" for _ in range(len(joint_speeds))])
                    joint_values_str = ", ".join(map(lambda x: f"{x:.2f}", joint_values))
                    item.setText(0, f"Move Joint ({joint_values_str}, Speeds: {speeds_str} mm/s)")
            except Exception as e:
                print(f"Erreur lors de la mise à jour du texte : {e}")
                return

            self.is_modified = True
            print(f"Vitesse modifiée pour '{movement_type}' : {new_speed} mm/s")
    def generate_program_name_with_date(self):
        """Génère un nom de programme basé sur la date et l'heure actuelles (format : Program_YYYYMMDD_HHMMSS)."""
        from datetime import datetime
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format YYYYMMDD_HHMMSS
        return f"Program_{current_date}"
