import utils as utl  # Remplace ça par ton module qui contient `self.robo
from robotcontrol import *
from PyQt5.QtWidgets import QApplication
import time
def run_move_track_process(waypoints_data,vel,acc):
        
        print("⚙️ Processus mouvement lancé...")
        Auboi5Robot.initialize()
        robot = Auboi5Robot()
        handle_move = robot.create_context()
        robot.connect('192.168.11.129',port = 8899)
        speed_tuple = (vel/10,) * 6
        speed_tuple2 = (acc/10,) * 6
        robot.set_end_max_line_velc(vel/10)
        robot.set_end_max_line_acc(acc/10)
        robot.set_joint_maxvelc(speed_tuple)
        robot.set_joint_maxacc(speed_tuple2)
        first, second, third = waypoints_data
        robot.move_joint(first)
        robot.remove_all_waypoint()
        robot.add_waypoint(joint_radian=first)   
        robot.add_waypoint(joint_radian=second)
        robot.add_waypoint(joint_radian=third)
        robot.set_circular_loop_times(1)       
        print("✅ Points ajoutés :", first, second, third)
        robot.move_track(RobotMoveTrackType.ARC_CIR)
        print("done")
