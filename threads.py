import threading
import main as mn
import time
import math
from robotcontrol import RobotIOType
from robotcontrol import RobotUserIoName
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

class JointUpdater(QObject):
    joints_updated = pyqtSignal(list)
    request_confirmation = pyqtSignal(list, int, str)  # Signal pour demander confirmation (position, numéro, message)
    add_move_circle_with_positions = pyqtSignal(list, list, list)  # Signal pour ajouter Move Circle
    add_move_line_with_position = pyqtSignal(list)  # Signal pour ajouter Move Line
    add_move_joint_with_position = pyqtSignal(list)  # Signal pour ajouter Move Joint
    add_arc_start = pyqtSignal()  # Nouveau signal pour Arc Start
    add_arc_end = pyqtSignal()
    execute_all_movements = pyqtSignal()
    delete_last_tree_item = pyqtSignal()  # Nouveau signal pour supprimer le dernier élément de l'arborescence

joint_updater = JointUpdater()

# Variables pour suivre l'état des clics et stocker les positions
click_state = 0  # 0: initial, 1: 1ère pos capturée, 2: 2e pos capturée
first_joints = None
second_joints = None
third_joints = None
move_line_joints = None
move_joint_joints = None
confirmation_result = None  # Variable pour stocker le résultat de la confirmation
awaiting_confirmation = False  # Indiquer si on attend une confirmation
# Define analog output variables

def confirm_position(robot, position, position_number):
    """Demander une confirmation pour la position capturée via di_03 (Yes) ou di_04 (No)."""
    global confirmation_result, awaiting_confirmation
    confirmation_result = None
    # awaiting_confirmation = True
    message = f"Position {position_number} capturée : {', '.join(map(lambda x: f'{x:.2f}', position))}\nConfirmer (di_03) ou Annuler (di_04) ?"
    # joint_updater.request_confirmation.emit(position, position_number, message)
    
    # Attendre que confirmation_result soit défini par di_03 ou di_04
    st = robot.get_board_io_status(RobotIOType.User_DI, RobotUserIoName.user_di_03)
    stn = robot.get_board_io_status(RobotIOType.User_DI, RobotUserIoName.user_di_04)
    while st == 0 and stn == 0:
        st = robot.get_board_io_status(RobotIOType.User_DI, RobotUserIoName.user_di_03)
        stn = robot.get_board_io_status(RobotIOType.User_DI, RobotUserIoName.user_di_04)
        time.sleep(0.1)  # Attendre 100ms avant la prochaine vérification
    if st:
        confirmation_result = True
    if stn:
        confirmation_result = False

    return confirmation_result

def set_confirmation_result(result):
    """Définir le résultat de la confirmation."""
    global confirmation_result
    confirmation_result = result

def get_robot_current_position(robot, window, coords=None):
    global joints, pos, ori, click_state, first_joints, second_joints, third_joints, confirmation_result, awaiting_confirmation
    current_coordinate = robot.get_current_waypoint()
    joints = current_coordinate["joint"]
    ori = current_coordinate["ori"]
    pos = current_coordinate["pos"]
    
    joint_updater.joints_updated.emit(joints)  # Émettre les nouvelles valeurs des joints
    
    user_di_list = [
        RobotUserIoName.user_di_00, RobotUserIoName.user_di_01, RobotUserIoName.user_di_02,
        RobotUserIoName.user_di_03, RobotUserIoName.user_di_04, RobotUserIoName.user_di_05,
        RobotUserIoName.user_di_06, RobotUserIoName.user_di_07, RobotUserIoName.user_di_10,
    ]
    user_di_states = []
    for user_di in user_di_list:
        state = robot.get_board_io_status(RobotIOType.User_DI, user_di)
        if state in (0, 1):
            user_di_states.append(state)
        else:
            print(f"Échec de la lecture de l'état de {user_di}")
            user_di_states.append(None)
    
    target_joints_tuple = None
    if coords is not None and len(coords) == 6:
        target_joints = []
        for coord in coords:
            try:
                coord_float = float(coord)
                target_joints.append(math.radians(coord_float))
            except (ValueError, TypeError):
                print(f"Valeur de coordonnée invalide : {coord}. Doit être un nombre.")
                target_joints = []
                break
        if target_joints:
            target_joints_tuple = tuple(target_joints)
            print(f"Joints cibles (radians) : {target_joints_tuple}")

    # Gérer user_di_02 pour capturer les positions directement
    if len(user_di_states) > 2 and user_di_states[2] == 1:  # user_di_02
        # Convertir les joints en degrés pour stockage
        current_joints_deg = [math.degrees(j) for j in joints]
        
        if click_state == 0:
            # 1er clic : capturer la 1ère position
            print(f"Tentative de capture de la 1ère position : {current_joints_deg}")
            confirmed = confirm_position(robot, current_joints_deg, 1)
            if confirmed:
                first_joints = current_joints_deg
                print(f"1ère position confirmée : {first_joints}")
                click_state = 1
            else:
                print("1ère position annulée.")
        
        elif click_state == 1:
            # 2e clic : capturer la 2e position
            if current_joints_deg == first_joints:
                print("Erreur : La 2ème position doit être différente de la 1ère position.")
            else:
                print(f"Tentative de capture de la 2ème position : {current_joints_deg}")
                confirmed = confirm_position(robot, current_joints_deg, 2)
                if confirmed:
                    second_joints = current_joints_deg
                    print(f"2ème position confirmée : {second_joints}")
                    click_state = 2
                else:
                    print("2ème position annulée.")
        
        elif click_state == 2:
            # 3e clic : capturer la 3e position et ajouter à l'arborescence
            if current_joints_deg == first_joints or current_joints_deg == second_joints:
                print("Erreur : La 3ème position doit être différente des positions précédentes.")
            else:
                print(f"Tentative de capture de la 3ème position : {current_joints_deg}")
                confirmed = confirm_position(robot, current_joints_deg, 3)
                if confirmed:
                    third_joints = current_joints_deg
                    print(f"3ème position confirmée : {third_joints}")
                    # Émettre le signal pour ajouter la commande Move Circle
                    joint_updater.add_move_circle_with_positions.emit(first_joints, second_joints, third_joints)
                    # Réinitialiser l'état
                    click_state = 0
                    first_joints = None
                    second_joints = None
                    third_joints = None
                else:
                    print("3ème position annulée.")
        
        user_di_states[2] = 0

    # Gérer user_di_03 et user_di_04 pour la confirmation
    if len(user_di_states) > 3 and user_di_states[3] == 1 and awaiting_confirmation:  # user_di_03 (Yes)
        set_confirmation_result(True)
        user_di_states[3] = 0
        print("Confirmation : Position acceptée via di_03")
    
    if len(user_di_states) > 4 and user_di_states[4] == 1:  # user_di_04 (No)
        if awaiting_confirmation:
            set_confirmation_result(False)
            print("Confirmation : Position annulée via di_04")
        # Émettre le signal pour supprimer le dernier élément de l'arborescence
        joint_updater.delete_last_tree_item.emit()
        user_di_states[4] = 0

    # Convertir les joints en degrés pour stockage
    current_joints_deg = [math.degrees(j) for j in joints]

    # Gérer user_di_00 pour Move Joint
    if len(user_di_states) > 0 and user_di_states[0] == 1 and not awaiting_confirmation:  # user_di_00
        print(f"Tentative de capture de la position pour Move Joint : {current_joints_deg}")
        confirmed = confirm_position(robot, current_joints_deg, 1)
        if confirmed:
            move_joint_joints = current_joints_deg
            print(f"Position pour Move Joint confirmée : {move_joint_joints}")
            joint_updater.add_move_joint_with_position.emit(move_joint_joints)
        else:
            print("Position pour Move Joint annulée.")
        user_di_states[0] = 0

    # Gérer user_di_01 pour Move Line
    if len(user_di_states) > 1 and user_di_states[1] == 1 and not awaiting_confirmation:  # user_di_01
        print(f"Tentative de capture de la position pour Move Line : {current_joints_deg}")
        confirmed = confirm_position(robot, current_joints_deg, 1)
        if confirmed:
            move_line_joints = current_joints_deg
            print(f"Position pour Move Line confirmée : {move_line_joints}")
            joint_updater.add_move_line_with_position.emit(move_line_joints)
        else:
            print("Position pour Move Line annulée.")
        user_di_states[1] = 0

    # Gérer user_di_05 pour Arc Start
    if len(user_di_states) > 5 and user_di_states[5] == 1 and not awaiting_confirmation:  # user_di_05
        print("Tentative d'ajout d'Arc Start via user_di_05")
        confirmed = confirm_position(robot, [], 0)  # Pas de position, juste confirmation
        if confirmed:
            print("Arc Start confirmé")
            joint_updater.add_arc_start.emit()
        else:
            print("Ajout d'Arc Start annulé.")
        user_di_states[5] = 0

    # Gérer user_di_06 pour Arc End
    if len(user_di_states) > 6 and user_di_states[6] == 1 and not awaiting_confirmation:  # user_di_06
        print("Tentative d'ajout d'Arc End via user_di_06")
        confirmed = confirm_position(robot, [], 0)  # Pas de position, juste confirmation
        if confirmed:
            print("Arc End confirmé")
            joint_updater.add_arc_end.emit()
        else:
            print("Ajout d'Arc End annulé.")
        user_di_states[6] = 0
    if len(user_di_states) > 7 and user_di_states[7] == 1 and not awaiting_confirmation:  # user_di_07
        print("Détection de user_di_08 : Exécution de tous les mouvements")
        confirmed = confirm_position(robot, [], 0)  # Pas de position, juste confirmation
        if confirmed:
           joint_updater.execute_all_movements.emit()  # Appeler la méthode execute_all_movements de MainWindow
        user_di_states[7] = 0