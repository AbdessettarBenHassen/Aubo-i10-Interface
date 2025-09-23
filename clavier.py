from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class VirtualKeyboard(QWidget):
    def __init__(self, target_input):
        super().__init__()
        self.target_input = target_input
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Clavier Numérique")
        self.setFixedSize(300, 300)  # Taille adaptée pour un clavier numérique

        self.setStyleSheet("""
            QWidget {
                font-family: 'Arial';
                font-size: 12px;
                background-color: #F5F6F5;
            }
            QPushButton {
                background-color: #666666; /* Gris foncé pour les chiffres */
                color: white;
                border: 1px solid #4C4C4C;
                padding: 5px;
                border-radius: 3px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #4C4C4C; /* Gris encore plus foncé au survol */
            }
            QPushButton:pressed {
                background-color: #404040; /* Gris très foncé au clic */
            }
            QPushButton#special {
                background-color: #3498DB; /* Bleu clair pour C */
                color: white;
            }
            QPushButton#special:hover {
                background-color: #2980B9;
            }
            QPushButton#special:pressed {
                background-color: #2471A3;
            }
            QPushButton#ok {
                background-color: #32CD32; /* Vert pour OK */
                color: white;
            }
            QPushButton#ok:hover {
                background-color: #2E8B57;
            }
            QPushButton#ok:pressed {
                background-color: #228B22;
            }
            QPushButton#cancel {
                background-color: #FF4500; /* Rouge pour Cancel */
                color: white;
            }
            QPushButton#cancel:hover {
                background-color: #FF6347;
            }
            QPushButton#cancel:pressed {
                background-color: #FF0000;
            }
        """)

        main_layout = QVBoxLayout()

        # Layout pour les touches numériques
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)

        # Définition des touches (disposition numérique avec C en dessous de 3)
        self.keys = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', '.', 'C']  # C déplacé en dessous de 3
        ]

        self.buttons = {}  # Dictionnaire pour stocker les boutons

        # Ajouter les touches au layout
        for row, key_row in enumerate(self.keys):
            for col, key in enumerate(key_row):
                button = QPushButton(key)
                button.setFixedSize(50, 40)  # Boutons plus fins
                if key == 'C':
                    button.setObjectName("special")  # Style bleu pour C
                button.setFont(QFont("Arial", 10, QFont.Normal))  # Police plus fine
                button.clicked.connect(lambda _, k=key: self.key_pressed(k))
                self.buttons[key] = button
                grid_layout.addWidget(button, row, col)

        main_layout.addLayout(grid_layout)

        # Ajouter les boutons OK et Cancel
        control_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(90, 35)
        ok_button.setObjectName("ok")  # Style spécifique pour OK
        ok_button.clicked.connect(self.close)
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(90, 35)
        cancel_button.setObjectName("cancel")  # Style spécifique pour Cancel
        cancel_button.clicked.connect(self.close)
        control_layout.addWidget(ok_button)
        control_layout.addWidget(cancel_button)
        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def key_pressed(self, key):
        current_text = self.target_input.text()

        if key == "C":  # Réinitialiser le texte
            self.target_input.setText("")
        elif key == "." and "." in current_text:  # Limiter à un seul point décimal
            pass
        else:  # Ajouter une touche numérique ou point
            self.target_input.setText(current_text + key)