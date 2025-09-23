import utils as utl  # Remplace ça par ton module qui contient `self.robo
from robot_bridge_client import *
from PyQt5.QtWidgets import QApplication
import time
def run_move_track_process(waypoints_data,vel,acc,ip):   
        print("⚙️ Processus mouvement lancé...")
        robot = Auboi5Robot()
        handle_move = robot.create_context()
        robot.connect(ip,port = 8899)
        speed_tuple = (vel,) * 6
        speed_tuple2 = (acc,) * 6
        robot.set_end_max_line_velc(vel)
        robot.set_end_max_line_acc(acc)
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
import time


        
