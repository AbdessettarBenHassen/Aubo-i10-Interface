from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class VirtualKeyboard(QWidget):
    def __init__(self, target_input):
        super().__init__()
        self.target_input = target_input
        self.shift_active = False  # Pour gérer les majuscules/minuscules
        self.caps_lock_active = False  # Pour gérer le verrouillage des majuscules
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Clavier Virtuel Professionnel")
        self.setFixedSize(900, 400)  # Taille plus grande pour un clavier complet
        self.setStyleSheet("""
            QWidget {
                font-family: 'Arial';
                font-size: 14px;
                background-color: #EAEDED;
            }
            QPushButton {
                background-color: #2E86C1;
                color: white;
                border: 1px solid #1B4F72;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2472A4;
            }
            QPushButton:pressed {
                background-color: #1B4F72;
            }
            QPushButton#special {
                background-color: #5DADE2;
            }
            QPushButton#special:hover {
                background-color: #4A90C2;
            }
            QPushButton#special:pressed {
                background-color: #3A78A2;
            }
        """)

        main_layout = QVBoxLayout()

        # Layout pour les touches
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)

        # Définition des touches (layout QWERTY complet)
        self.keys = [
            # Ligne 1 : Touches de fonction et chiffres
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            # Ligne 2 : Tab et première ligne de lettres
            ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
            # Ligne 3 : Caps Lock et deuxième ligne de lettres
            ['Caps Lock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'Enter'],
            # Ligne 4 : Shift gauche et troisième ligne de lettres
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
            # Ligne 5 : Ctrl, Alt, Espace, flèches
            ['Ctrl', 'Alt', 'Space', 'Alt', 'Ctrl', '←', '↑', '↓', '→']
        ]

        self.buttons = {}  # Dictionnaire pour stocker les boutons

        # Ajouter les touches au layout
        for row, key_row in enumerate(self.keys):
            for col, key in enumerate(key_row):
                button = QPushButton(key)
                # Ajuster la taille des touches
                if key in ['Backspace', 'Tab', 'Caps Lock', 'Enter', 'Shift', 'Ctrl', 'Alt']:
                    button.setFixedSize(80, 50)
                    button.setObjectName("special")  # Style différent pour les touches spéciales
                elif key == 'Space':
                    button.setFixedSize(200, 50)
                    button.setObjectName("special")
                else:
                    button.setFixedSize(50, 50)
                
                button.setFont(QFont("Arial", 12, QFont.Bold))
                button.clicked.connect(lambda _, k=key: self.key_pressed(k))
                self.buttons[key] = button
                grid_layout.addWidget(button, row, col)

        main_layout.addLayout(grid_layout)

        # Ajouter un layout pour les touches de contrôle supplémentaires (optionnel)
        control_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(100, 40)
        ok_button.setObjectName("special")
        ok_button.clicked.connect(self.close)
        control_layout.addStretch()
        control_layout.addWidget(ok_button)
        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def key_pressed(self, key):
        current_text = self.target_input.text()

        if key == "Backspace":  # Effacer un caractère
            self.target_input.setText(current_text[:-1])
        elif key == "Enter":  # Saut de ligne
            self.target_input.setText(current_text + "\n")
        elif key == "Tab":  # Tabulation
            self.target_input.setText(current_text + "\t")
        elif key == "Space":  # Espace
            self.target_input.setText(current_text + " ")
        elif key == "Caps Lock":  # Activer/désactiver le verrouillage des majuscules
            self.caps_lock_active = not self.caps_lock_active
            self.update_shift_keys()
        elif key == "Shift":  # Activer/désactiver les majuscules temporaires
            self.shift_active = not self.shift_active
            self.update_shift_keys()
        elif key in ["Ctrl", "Alt"]:  # Touches de contrôle (peuvent être étendues)
            pass  # Placeholder pour une fonctionnalité future
        elif key in ["←", "↑", "↓", "→"]:  # Touches de direction
            self.handle_arrow_keys(key)
        else:  # Ajouter une lettre, un chiffre ou un symbole
            if key in ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '[', ']', '\\', ';', '\'', ',', '.', '/']:
                # Symboles et chiffres (peuvent être modifiés avec Shift)
                text_to_add = self.get_shifted_symbol(key)
            else:
                # Lettres (majuscules ou minuscules selon Shift/Caps Lock)
                text_to_add = key.upper() if (self.shift_active or self.caps_lock_active) else key.lower()
            self.target_input.setText(current_text + text_to_add)

        # Réinitialiser Shift après une pression (sauf si Caps Lock est actif)
        if key != "Shift" and key != "Caps Lock" and self.shift_active:
            self.shift_active = False
            self.update_shift_keys()

    def get_shifted_symbol(self, key):
        """Retourne le symbole modifié si Shift est actif."""
        shift_symbols = {
            '`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
            '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '-': '_',
            '=': '+', '[': '{', ']': '}', '\\': '|', ';': ':', '\'': '"',
            ',': '<', '.': '>', '/': '?'
        }
        if self.shift_active:
            return shift_symbols.get(key, key)
        return key

    def handle_arrow_keys(self, key):
        """Gère les touches de direction pour déplacer le curseur."""
        cursor = self.target_input.cursorPosition()
        text = self.target_input.text()
        length = len(text)

        if key == "←" and cursor > 0:
            self.target_input.setCursorPosition(cursor - 1)
        elif key == "→" and cursor < length:
            self.target_input.setCursorPosition(cursor + 1)
        elif key == "↑":
            self.target_input.setCursorPosition(0)  # Aller au début (peut être amélioré)
        elif key == "↓":
            self.target_input.setCursorPosition(length)  # Aller à la fin (peut être amélioré)

    def update_shift_keys(self):
        """Met à jour l'affichage des touches en fonction de Shift et Caps Lock."""
        for row in self.keys:
            for key in row:
                if key.isalpha():  # Si c'est une lettre, on change son état
                    self.buttons[key].setText(key.upper() if (self.shift_active or self.caps_lock_active) else key.lower())
                elif key in ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '[', ']', '\\', ';', '\'', ',', '.', '/']:
                    # Mettre à jour l'affichage des symboles
                    self.buttons[key].setText(self.get_shifted_symbol(key))