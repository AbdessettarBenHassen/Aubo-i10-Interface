from robotcontrol import*
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
import main as mn
import threads as th  # Importez le module threads pour accéder à th.joints
import math
import logging
from robot_db import get_full_tool_data

logger = logging.getLogger('main.robotcontrol')
timers = {}
cartesian_timers = {}
stopped_joints = set()
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

    
    
    robot = Auboi5Robot()
    robot.initialize()

    handle = robot.create_context()
    logger.info(f"robot.rshd={handle}")

    try:
        
        logger.info("Process started.")

        port = 8899
        result = robot.connect(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.error(f"Failed to connect to server {ip}:{port}.")
        return robot
    except Exception as e:
        logger.error(f"Error during robot connection: {e}")
        robot.move_stop()
  


logger = logging.getLogger('main.robotcontrol')


# utils.py
def setup_robot(ip, tool_name):
    robot = robot_connect(ip)
    print("done")
    if robot is None:
        return None, None

    tool_data = get_full_tool_data(tool_name)
    dynamics = tool_data['dynamics']

    # Build tool_dynamics dict in the expected format
    tool_dynamics = {
        "position": (
            dynamics.get('gravity_center_x', 0.0),
            dynamics.get('gravity_center_y', 0.0),
            dynamics.get('gravity_center_z', 0.0)
        ),
        "payload": dynamics.get('payload', 0.0),
        "inertia": (
            dynamics.get('inertia_xx', 0.0),
            dynamics.get('inertia_yy', 0.0),
            dynamics.get('inertia_zz', 0.0),
            dynamics.get('inertia_xy', 0.0),
            dynamics.get('inertia_xz', 0.0),
            dynamics.get('inertia_yz', 0.0)
        )
    }

    # Use this tool_dynamics for robot startup and setting tool params
    robot.robot_startup(6, tool_dynamics)
    robot.init_profile()

    return robot, tool_dynamics

# Dictionnaire pour stocker les timers
timers = {}



class TeachMoveMode:
    NO_TEACH = 0
    JOINT1 = 1
    JOINT2 = 2
    JOINT3 = 3
    JOINT4 = 4
    JOINT5 = 5
    JOINT6 = 6
    MOV_X = 7
    MOV_Y = 8
    MOV_Z = 9
    ROT_X = 10
    ROT_Y = 11
    ROT_Z = 12
def joint_index_to_enum(joint_index):
    mapping = {
        0: TeachMoveMode.JOINT1,
        1: TeachMoveMode.JOINT2,
        2: TeachMoveMode.JOINT3,
        3: TeachMoveMode.JOINT4,
        4: TeachMoveMode.JOINT5,
        5: TeachMoveMode.JOINT6
    }
    return mapping.get(joint_index, TeachMoveMode.NO_TEACH)
def start_move_joint(robot, joint, direction, self, joint_step_value):
    """
    Démarre le mouvement d'un joint dans une direction spécifique.
    :param robot: Référence au robot.
    :param joint: Numéro du joint (1 à 6).
    :param direction: "+" pour augmenter, "-" pour diminuer.
    :param step_mode_checkbox: Référence à la checkbox du mode Step.
    :param joint_step_value: Référence au QLabel affichant la valeur du Joint Step.
    """
    joint_mapping = {
        1: TeachMoveMode.JOINT1,
        2: TeachMoveMode.JOINT2,
        3: TeachMoveMode.JOINT3,
        4: TeachMoveMode.JOINT4,
        5: TeachMoveMode.JOINT5,
        6: TeachMoveMode.JOINT6
    }

    # Get the correct TeachMoveMode value from joint number
    joint_mode = joint_mapping.get(joint, TeachMoveMode.NO_TEACH)
    if(not(self.st)):
        if(direction == "+"):
            libpyauboi5.teach_move_start(robot.rshd,joint_mode, True)
        else:
            libpyauboi5.teach_move_start(robot.rshd,joint_mode, False)
    else:
        move_joint(robot, joint, direction, self.st, joint_step_value)

def stop_move_joint(robot, joint, direction):
    """
    Stop the movement of a specific joint in a specific direction.
    """

    libpyauboi5.teach_move_stop(robot.rshd)
       

def update_joint_speed_from_slider(value, robot):
    global value_from_slider
    value_from_slider = value

    # Scale slider value from 0–100 → 0.5–1.5
    speed = (value * 1) / 100  # 1.0 = 1.5 - 0.5

    # Set the same speed for all joints
    speed_tuple = (speed,) * 6

    # Apply to robot
    robot.set_end_max_line_acc(1.0)
    robot.set_end_max_line_velc(speed)
    robot.set_joint_maxacc((1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
    robot.set_joint_maxvelc(speed_tuple)

def move_joint(robot, joint, direction, st, joint_step_value):
    global joints
    robot.set_arrival_ahead_distance(0.459999)
    try:
        # Check if movement was stopped
        if (joint, direction) in stopped_joints:
            stopped_joints.remove((joint, direction))
            raise RuntimeError(f"Movement for joint {joint} in direction '{direction}' was stopped manually.")

        # --- existing code continues here ---
        
        joint_step_text = joint_step_value.text().strip()
        if not joint_step_text:
            raise ValueError("La valeur du Joint Step est vide.")

        joint_step = float(joint_step_text.split()[0])
        joint_step_rad = math.radians(joint_step)
        print(f"Valeur extraite : {joint_step}° -> {joint_step_rad} rad")
        
        if st:
            step = math.radians(joint_step)
        else:
            step = ((value_from_slider * 0.05) / 100) * 2

        if direction == "+":
            th.joints[joint - 1] += step
        elif direction == "-":
            th.joints[joint - 1] -= step
        else:
            raise ValueError("Direction invalide : utilisez '+' ou '-'.")

        print(step)
        robot.move_joint(th.joints, True)
        print(f"Joint {joint} déplacé de {step} dans la direction '{direction}'.")

    except ValueError as ve:
        print(f"Erreur de valeur : {ve}")
    except RuntimeError as re:
        print(f"Stop detected: {re}")
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
        axe_mapping = {
        1: TeachMoveMode.MOV_X,
        2: TeachMoveMode.MOV_Y,
        3: TeachMoveMode.MOV_Z,
        4: TeachMoveMode.ROT_X,
        5: TeachMoveMode.ROT_Y,
        6: TeachMoveMode.ROT_Z,
        }

    # Get the correct TeachMoveMode value from joint number
        joint_mode = axe_mapping.get(axis, TeachMoveMode.NO_TEACH)
        if(direction == "+"):
            libpyauboi5.teach_move_start(robot.rshd,joint_mode, True)
        else:
            libpyauboi5.teach_move_start(robot.rshd,joint_mode, False)
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
    libpyauboi5.teach_move_stop(0)



def stop_move_to_zero_pose(robot):
    print(robot.get_tool_dynamics_param())
    """
    Arrête le mouvement lorsque le bouton est relâché.
    """
    robot.move_stop()  # Stop all movements
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
            stop_move_to_zero_pose(robot)  # Arrêter le mouvement
            return
     

        # Envoyer la nouvelle position au robot
        robot.move_joint(target_joints,False)
    except Exception as e:
        logger.error(f"Error moving toward zero pose: {e}")
import sqlite3

def fetch_user_coord_from_db(coord_name):
    db_path = "C:/Users/abdes/OneDrive/Desktop/Aubo/tool_coord_param.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Step 1: Fetch from coord_param
    cursor.execute("SELECT coord_name, tool_name, coord_calibrate_mathod, coord_point1, coord_point2, coord_point3 FROM coord_param WHERE coord_name = ?", (coord_name,))
    row = cursor.fetchone()
    if not row:
        print(f"[ERROR] No user coord found with name: {coord_name}")
        conn.close()
        return None

    coord_name, tool_name, method, point1_str, point2_str, point3_str = row

    def parse_point(p):
        return tuple(float(x) for x in p.split(",")[:6])  # Only first 6 floats

    # Step 2: Fetch tool pose from tool_kinematics_param by tool_name
    cursor.execute("""
        SELECT end_pos_x, end_pos_y, end_pos_z, end_ori_rx, end_ori_ry, end_ori_rz 
        FROM tool_kinematics_param WHERE kinematics_name = ?
    """, (tool_name,))
    tool_row = cursor.fetchone()

    if not tool_row:
        print(f"[WARNING] No tool kinematics found for tool: {tool_name}, using default pose")
        tool_pos = (0.0, 0.0, 0.0)
        tool_ori = (1.0, 0.0, 0.0, 0.0)  # Identity quaternion default
    else:
        # Convert RX,RY,RZ Euler angles to quaternion (assuming angles in radians)
        # If your robot expects quaternion, you'll need to convert Euler to quaternion here.
        # For now, set ori as (1,0,0,0) or implement conversion if you want
        tool_pos = tool_row[:3]  # x,y,z
        # Simple placeholder: convert Euler (rx,ry,rz) to quaternion
        rx, ry, rz = tool_row[3], tool_row[4], tool_row[5]
        tool_ori = euler_to_quaternion(rx, ry, rz)

    conn.close()

    user_coord = {
        'coord_type': RobotCoordType.Robot_World_Coordinate,  # user-defined coord type (update as per your SDK)
        'calibrate_method': method_mapping(method),
        'calibrate_points': {
            "point1": parse_point(point1_str),
            "point2": parse_point(point2_str),
            "point3": parse_point(point3_str),
        },
        'tool_desc': {
            'pos': tool_pos,
            'ori': tool_ori
        }
    }
    return user_coord

def euler_to_quaternion(rx, ry, rz):
    """
    Convert Euler angles (rx, ry, rz in radians) to quaternion (x, y, z, w)
    Note: Robot SDK may expect (w, x, y, z) or (x,y,z,w), adjust accordingly.
    """
    import math
    cy = math.cos(rz * 0.5)
    sy = math.sin(rz * 0.5)
    cp = math.cos(ry * 0.5)
    sp = math.sin(ry * 0.5)
    cr = math.cos(rx * 0.5)
    sr = math.sin(rx * 0.5)

    w = -1
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy

    return (w, x, y, z)



def method_mapping(method_str):
    """Map string to RobotCoordCalMethod enum value."""
    mapping = {
        'xOy': RobotCoordCalMethod.CoordCalMethod_xOy,
        'yOz': RobotCoordCalMethod.CoordCalMethod_yOz,
        'zOx': RobotCoordCalMethod.CoordCalMethod_zOx,
        'xOxy': RobotCoordCalMethod.CoordCalMethod_xOxy,
        'xOxz': RobotCoordCalMethod.CoordCalMethod_xOxz,
        'yOyx': RobotCoordCalMethod.CoordCalMethod_yOyx,
        'yOyz': RobotCoordCalMethod.CoordCalMethod_yOyz,
        'zOzx': RobotCoordCalMethod.CoordCalMethod_zOzx,
        'zOzy': RobotCoordCalMethod.CoordCalMethod_zOzy,
    }
    return mapping.get(method_str, RobotCoordCalMethod.CoordCalMethod_xOy)  # Default to xOy

def coord_type_mapping(type_str):
    """Map string to RobotCoordType enum value."""
    mapping = {
        'base': RobotCoordType.Robot_Base_Coordinate,
        'end': RobotCoordType.Robot_End_Coordinate,
        'user': RobotCoordType.Robot_World_Coordinate,
    }
    return mapping.get(type_str.lower(), RobotCoordType.Robot_Base_Coordinate)  # Default to base

def on_reference_changed(robot, value):
    print(f"Reference coordinate changed to: {value}")
    
    if value == "Base":
        libpyauboi5.set_teach_base_coord(robot.rshd)
    elif value == "flange_center":
        libpyauboi5.set_teach_end_coord(robot.rshd)
    else:
        # Assume it's a user coordinate system
        user_coord = fetch_user_coord_from_db(value)
        print(user_coord)
        print(robot.check_user_coord(user_coord))
        if user_coord:
                result = libpyauboi5.set_teach_user_coord(robot.rshd, user_coord)
                if result == RobotErrorType.RobotError_SUCC:
                    print("User coordinate set successfully.")
                else:
                    print("Failed to set user coordinate.")

       

def start_move_to_init_pose(robot):
    """
    Démarre le mouvement vers la position initiale lorsque le bouton est appuyé.
    """
    move_to_init_pose(robot)

def stop_move_to_init_pose(robot):
    """
    Arrête le mouvement lorsque le bouton est relâché.
    """
    robot.move_stop()  # Stop all movements


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
            stop_move_to_init_pose(robot)  # Arrêter le mouvement
            return
        # Envoyer la nouvelle position au robot
        robot.move_joint(target_joints,False)
    except Exception as e:
        logger.error(f"Error moving toward init pose: {e}")

def stop_movement(robot):
    """Stop all robot movement"""
    # Implementation depends on your robot API
    # Example:
    robot.stop()  # Or equivalent command



