from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QVBoxLayout,QLabel
from PyQt5.QtCore import Qt
class CurveWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 220)  # Taille fixe du widget
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)  # Centre le contenu verticalement/horizontalement
        self.setLayout(self.layout)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(300, 200)  # Taille fixe pour le label (ajustable)
        self.layout.addWidget(self.image_label)

    def set_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Redimensionnement proportionnel mais contenu dans les limites du label
            pixmap = pixmap.scaled(
                self.image_label.size(),  # Utilise la taille du label comme référence
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
        else:
            print(f"Erreur: Impossible de charger l'image {image_path}")