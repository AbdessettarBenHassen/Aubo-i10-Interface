from robotcontrol import*
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
import main as mn
import threads as th  # Importez le module threads pour accéder à th.joints
import math
import logging

logger = logging.getLogger('main.robotcontrol')
timers = {}
cartesian_timers = {}

def radian_to_degree(radians):
        """
        Convert radians to degrees.
        :param radians: Angle in radians.
        :return: Angle in degrees.
        """
        degrees =radians * (180 / math.pi) 
        return round(degrees, 2)
def radian_to_degree2(rpy_radians):
    """
    Convertit les angles RPY de radians en degrés.
    :param rpy_radians: Liste [rx, ry, rz] en radians.
    :return: Liste [rx, ry, rz] en degrés.
    """
    return [math.degrees(angle) for angle in rpy_radians]


def logger_init():
    """Initialize the logging configuration."""
    if logger.hasHandlers():
        return  # Prevent duplicate handlers

    logger.setLevel(logging.INFO)

    if not os.path.exists('./logfiles'):
        os.mkdir('./logfiles')

    logfile = './logfiles/robot-ctl-python.log'
    fh = RotatingFileHandler(logfile, mode='a', maxBytes=1024 * 1024 * 50, backupCount=30)
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(thread)d] %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)


def robot_connect(ip):
    """
    Connect to the robot at the specified IP address.
    """
    logger_init()
    logger.info(f"{Auboi5Robot.get_local_time()} test beginning...")

    Auboi5Robot.initialize()
    
    robot = Auboi5Robot()

    handle = robot.create_context()
    logger.info(f"robot.rshd={handle}")

    try:
        
        queue = Queue()

        p = Process(target=runWaypoint, args=(queue,))
        p.start()
        time.sleep(5)
        logger.info("Process started.")

        port = 8899
        result = robot.connect(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.error(f"Failed to connect to server {ip}:{port}.")
        return robot,queue
    except Exception as e:
        logger.error(f"Error during robot connection: {e}")
        robot.move_stop()
  


logger = logging.getLogger('main.robotcontrol')



# Dictionnaire pour stocker les timers
timers = {}

def start_move_joint(robot, joint, direction, self, joint_step_value):
    """
    Démarre le mouvement d'un joint dans une direction spécifique.
    :param robot: Référence au robot.
    :param joint: Numéro du joint (1 à 6).
    :param direction: "+" pour augmenter, "-" pour diminuer.
    :param step_mode_checkbox: Référence à la checkbox du mode Step.
    :param joint_step_value: Référence au QLabel affichant la valeur du Joint Step.
    """
    if(not(self.st)):
        if (joint, direction) not in timers:
            timer = QTimer()
            print(2)
            timer.timeout.connect(
                lambda: move_joint(robot, joint, direction, self.st, joint_step_value)
            )
            timer.start(100)  # Déclenche move_joint toutes les 100 ms
            timers[(joint, direction)] = timer
            
            print(f"Début du mouvement continu du joint {joint} dans la direction {direction}")
    else:
        move_joint(robot, joint, direction, self.st, joint_step_value)

def stop_move_joint():
    """
    Arrête tous les mouvements des joints ou des coordonnées cartésiennes.
    """
    for timer in timers.values():
        timer.stop()
    timers.clear()
    print("Stopped all joint/cartesian movements")  # Log


def move_joint(robot, joint, direction, st, joint_step_value):
    """
    Modifie la valeur d'un joint et met à jour le robot.
    
    :param robot: Référence au robot.
    :param joint: Numéro du joint (1 à 6).
    :param direction: "+" pour augmenter, "-" pour diminuer.
    :param step_mode_active: Booléen indiquant si le Step Mode est activé.
    :param joint_step_value: Référence au QLabel affichant la valeur du Joint Step.
    """
    global joints
   
    try:
        
        
        # Vérifier si joint_step_value contient du texte valide
        joint_step_text = joint_step_value.text().strip()
        if not joint_step_text:
            raise ValueError("La valeur du Joint Step est vide.")

        # Extraire la valeur numérique de joint_step
        joint_step = float(joint_step_text.split()[0])
        joint_step_rad = math.radians(joint_step)  # Conversion en radians
        print(f"Valeur extraite : {joint_step}° -> {joint_step_rad} rad")
        

         # Force en booléen
        if (st):
            step = math.radians(joint_step)
           
        else:
            step = 0.01

        # Modifier la valeur du joint en fonction de la direction
        if direction == "+":
            th.joints[joint - 1] += step
        elif direction == "-":
            th.joints[joint - 1] -= step
        else:
            raise ValueError("Direction invalide : utilisez '+' ou '-'.")
        

        robot.move_joint(th.joints)
        
        # Afficher le mouvement dans la console
        print(f"Joint {joint} déplacé de {step} dans la direction '{direction}'.")
        

    except ValueError as ve:
        print(f"Erreur de valeur : {ve}")
    except Exception as ex:
        print(f"Erreur inattendue : {ex}")




def move_cartesian(robot, axis, direction, st, position_step_value, orientation_step_value):
    """
    Déplace un axe cartésien en fonction de la direction et du pas de déplacement.
    
    :param robot: Référence au robot.
    :param axis: Numéro de l'axe (1: X, 2: Y, 3: Z, 4: RX, 5: RY, 6: RZ).
    :param direction: "+" pour augmenter, "-" pour diminuer.
    :param st: Booléen indiquant si le mode Step est activé.
    :param translation_step_value: Référence au QLabel affichant la valeur du pas de translation.
    :param rotation_step_value: Référence au QLabel affichant la valeur du pas de rotation.
    """
    try:
        # Récupérer la position cartésienne actuelle
        current_position = robot.get_current_waypoint()
        if current_position is None:
            logger.error("Failed to retrieve current position. Check robot connection.")
            return

        cartesian = current_position.get('pos')  # [x, y, z] en mètres
        ori = current_position.get('ori')  # Orientation en quaternion

        if cartesian is None or ori is None:
            logger.error("Invalid current position: Missing cartesian or orientation data.")
            return

        # Convertir l'orientation en angles RPY (rx, ry, rz) en radians
        rpy_radians = robot.quaternion_to_rpy(ori)
        if rpy_radians is None:
            logger.error("Failed to convert orientation to RPY.")
            return


        # Définir le pas de déplacement pour les translations et les rotations
        if  st:
            # Mode Step : utiliser les pas spécifiques
            position_step_text = position_step_value.split()[0]  # Récupérer uniquement la valeur numérique
            position_step = float(position_step_text)/1000 # Garder la valeur directement sans conversion


            orientation_step_deg = float(orientation_step_value.split()[0])  # "0.5 deg" -> 0.5
            orientation_step = math.radians(orientation_step_deg)   # Conversion en radians
        else:
            # Mode continu : utiliser des pas par défaut
            position_step = 0.01  # 1 cm par défaut
            orientation_step = 0.01  # 0.1 radian (~5.7 degrés) par défaut

        # Modifier les coordonnées cartésiennes ou les angles RPY
        if axis <= 3:  # X, Y, Z
            cartesian[axis - 1] += position_step if direction == "+" else -position_step
        else:  # RX, RY, RZ
            rpy_index = axis - 4  # RX -> 0, RY -> 1, RZ -> 2
            rpy_radians[rpy_index] += orientation_step if direction == "+" else -orientation_step

        # Convertir les angles RPY en degrés
        rpy_degrees = [math.degrees(angle) for angle in rpy_radians]

        # Envoyer la nouvelle position au robot
        robot.move_to_target_in_cartesian(cartesian, rpy_degrees)
        logger.info(f"Moved cartesian axis {axis} in direction {direction}")
    except Exception as e:
        logger.error(f"Error during cartesian movement: {e}")
def start_move_cartesian(robot, axis, direction, self):
    """
    Démarre le mouvement cartésien dans une direction spécifique.
    
    :param robot: Référence au robot.
    :param axis: Numéro de l'axe (1: X, 2: Y, 3: Z, 4: RX, 5: RY, 6: RZ).
    :param direction: "+" pour augmenter, "-" pour diminuer.
    :param st: Booléen indiquant si le mode Step est activé.
    :param translation_step_value: Référence au QLabel affichant la valeur du pas de translation.
    :param rotation_step_value: Référence au QLabel affichant la valeur du pas de rotation.
    """
    if(not(self.st)):
        # Mode continu : utiliser un QTimer pour un mouvement continu
        if (axis, direction) not in cartesian_timers:
            timer = QTimer()
            timer.timeout.connect(
                lambda: move_cartesian(robot, axis, direction,self.st, self.position_step_value.text(),self. orientation_step_value.text())
            )
            timer.start(100)  # Déclenche move_cartesian toutes les 100 ms
            cartesian_timers[(axis, direction)] = timer
            print(f"Début du mouvement continu de l'axe {axis} dans la direction {direction}")
    else:
        # Mode Step : déplacer d'un seul pas
        move_cartesian(robot, axis, direction, self.st, self.position_step_value.text(),self. orientation_step_value.text())

def stop_move_cartesian(axis=None, direction=None):
    """
    Arrête le mouvement cartésien dans une direction spécifique.
    Si axis et direction ne sont pas fournis, arrête tous les mouvements cartésiens.
    :param axis: Numéro de l'axe (1: X, 2: Y, 3: Z, 4: RX, 5: RY, 6: RZ).
    :param direction: "+" pour augmenter, "-" pour diminuer.
    """
    if axis is not None and direction is not None:
        # Arrêter un mouvement spécifique
        if (axis, direction) in cartesian_timers:
            timer = cartesian_timers[(axis, direction)]
            timer.stop()
            del cartesian_timers[(axis, direction)]
            print(f"Stopped moving cartesian axis {axis} in direction {direction}")
    else:
        # Arrêter tous les mouvements cartésiens
        for (ax, dir), timer in list(cartesian_timers.items()):
            timer.stop()
            del cartesian_timers[(ax, dir)]
            print(f"Stopped moving cartesian axis {ax} in direction {dir}")


def start_move_to_zero_pose(robot):
    """
    Démarre le mouvement vers la position zéro lorsque le bouton est appuyé.
    """
    if 'zero_pose_timer' not in timers:
        timers['zero_pose_timer'] = QTimer()
        timers['zero_pose_timer'].timeout.connect(lambda: move_to_zero_pose(robot))  # Déplacer vers la position zéro
        timers['zero_pose_timer'].start(100)  # Démarrer le timer (100 ms)

def stop_move_to_zero_pose():
    """
    Arrête le mouvement lorsque le bouton est relâché.
    """
    if 'zero_pose_timer' in timers:
        timers['zero_pose_timer'].stop()  # Arrêter le timer
        del timers['zero_pose_timer']  # Supprimer le timer du dictionnaire
def move_to_zero_pose(robot):
    """
    Déplace progressivement le robot vers la position zéro.
    """
    try:
        # Définir la position cible (tous les joints à 0 radian)
        target_joints = [0.0] * 6

        # Récupérer la position actuelle des joints
        current_joints = robot.get_current_waypoint()['joint']

        # Vérifier si le robot a atteint la position cible
        if all(abs(current_joints[i] - target_joints[i]) < 0.01 for i in range(6)):
            stop_move_to_zero_pose()  # Arrêter le mouvement
            return

        # Calculer un pas de mouvement proportionnel
        step = 0.1  # Pas de mouvement maximal (en radians)
        new_joints = [
            current_joints[i] + min(step, abs(target_joints[i] - current_joints[i])) * (1 if target_joints[i] > current_joints[i] else -1)
            for i in range(6)
        ]

        # Envoyer la nouvelle position au robot
        robot.move_joint(new_joints)
    except Exception as e:
        logger.error(f"Error moving toward zero pose: {e}")

def start_move_to_init_pose(robot):
    """
    Démarre le mouvement vers la position initiale lorsque le bouton est appuyé.
    """
    if 'init_pose_timer' not in timers:
        timers['init_pose_timer'] = QTimer()
        timers['init_pose_timer'].timeout.connect(lambda: move_to_init_pose(robot))  # Déplacer vers la position initiale
        timers['init_pose_timer'].start(100)  # Démarrer le timer (100 ms)

def stop_move_to_init_pose():
    """
    Arrête le mouvement lorsque le bouton est relâché.
    """
    if 'init_pose_timer' in timers:
        timers['init_pose_timer'].stop()  # Arrêter le timer
        del timers['init_pose_timer']  # Supprimer le timer du dictionnaire


def move_to_init_pose(robot):
    """
    Déplace progressivement le robot vers la position initiale.
    """
    try:
        # Définir la position cible (position initiale en radians)
        target_joints = [math.radians(j) for j in [-0.000172, -7.291862, -75.694718, 21.596727, -89.999982, -0.000458]]

        # Récupérer la position actuelle des joints
        current_joints = robot.get_current_waypoint()['joint']

        # Vérifier si le robot a atteint la position cible
        if all(abs(current_joints[i] - target_joints[i]) < 0.01 for i in range(6)):
            stop_move_to_init_pose()  # Arrêter le mouvement
            return

        # Calculer un pas de mouvement proportionnel
        step = 0.1  # Pas de mouvement maximal (en radians)
        new_joints = [
            current_joints[i] + min(step, abs(target_joints[i] - current_joints[i])) * (1 if target_joints[i] > current_joints[i] else -1)
            for i in range(6)
        ]

        # Envoyer la nouvelle position au robot
        robot.move_joint(new_joints)
    except Exception as e:
        logger.error(f"Error moving toward init pose: {e}")

def stop_movement(robot):
    """Stop all robot movement"""
    # Implementation depends on your robot API
    # Example:
    robot.stop()  # Or equivalent command



