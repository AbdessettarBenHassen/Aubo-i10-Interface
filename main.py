
from ui import *
import utils as utl 
from multiprocessing import Process, Queue
from threads import *
from config_dialog import ConfigDialog
import sys
from PyQt5.QtWidgets import QApplication,QProgressDialog,QDesktopWidget
from PyQt5.QtCore import QTimer,Qt, QThread, pyqtSignal
import multiprocessing as mp
import subprocess, time
#ip = '192.168.0.23'
ip = ''
tooltest = ""
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
import sys
robot = None
window = None
# Joystick-related variables removed - pygame functionality disabled

# Joystick handlers removed - pygame functionality disabled
def show_robot_error_popup(message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Robot Error")
        msg_box.setText("A robot error occurred:")
        msg_box.setInformativeText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
import sys
import socket
from multiprocessing import Process, Queue
from PyQt5.QtWidgets import QApplication, QProgressDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer
import json
import os
CONFIG_FILE = os.path.expanduser("~/.robot_config.json")
def save_config(ip, tool):
    data = {"ip": ip, "tool": tool}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)
import os, subprocess, time, sys

bridge_process = None

def start_bridge_once():
    global bridge_process
    # ensure old bridge is closed
    stop_bridge()

    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    bridge_script = os.path.join(base_path, "robot_bridge_server.py")

    bridge_process = subprocess.Popen(["python2", bridge_script])
   
    print(f"[Bridge] Started with PID {bridge_process.pid}")
    
    # Wait for bridge server to be ready
    max_wait = 10  # seconds
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            # Test if bridge server is responding
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(('127.0.0.1', 5000))
            s.send(json.dumps({"action": "get_status"}).encode('utf-8'))
            data = s.recv(1024)
            s.close()
            response = json.loads(data.decode('utf-8'))
            if response.get("status") == "ok":
                print("[Bridge] Server is ready!")
                return True
        except Exception as e:
            print(f"[Bridge] Waiting for server... {e}")
            time.sleep(0.5)
    
    print("[Bridge] Server failed to start within timeout")
    return False

def stop_bridge():
    global bridge_process
    if bridge_process is not None:
        try:
            # Try graceful shutdown first
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            try:
                s.connect(('127.0.0.1', 5000))
                shutdown_cmd = json.dumps({"action": "shutdown"})
                s.send(shutdown_cmd.encode('utf-8'))
                s.close()
                time.sleep(1.5)  # give bridge time to cleanup sockets
            except Exception as e:
                print("[Bridge Stop Warning] Could not request shutdown: {}".format(e))

            # If still alive, kill it
            if bridge_process.poll() is None:
                bridge_process.terminate()
                bridge_process.wait(timeout=3)

        except Exception as e:
            print("[Bridge Stop Error] {}".format(e))
        finally:
            bridge_process = None


# Process function: only check socket reachability
def check_robot_reachable(ip, queue, port=8899, timeout=5000):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            queue.put(True)
    except Exception as e:
        print(f"[Connection Test Error] {e}")
        queue.put(False)
    

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config = ConfigDialog()
        self.loading = None
        self.process = None
        self.queue = None
        self.connection_timer = None  # add this!
        self.position_timer = None

    def start(self):
        self.show_config()
        sys.exit(self.app.exec_())

    def show_config(self):
        if self.config.exec_() == self.config.Accepted:
            self.tooltest = self.config.selected_tool
            self.ip = self.config.selected_ip
            save_config(self.ip, self.tooltest)
            start_bridge_once()
            self.start_connection()
            # Bridge server is already running manually - skip this check
            # if not start_bridge_once():
            #     QMessageBox.critical(None, "Error", "Failed to start bridge server. Please try again.")
            #     self.show_config()
            #     return
        else:
            sys.exit()

    def start_connection(self):
 

        # Show loading dialog
        self.loading = QProgressDialog("Connecting to robot...", None, 0, 0)
        self.loading.setWindowModality(Qt.ApplicationModal)
        self.loading.setCancelButton(None)
        self.loading.setMinimumDuration(0)
        self.loading.setWindowTitle("Please wait")
        self.loading.setMinimumWidth(300)
        self.loading.show()

        # Start process to check if robot is reachable
        self.queue = Queue()
        self.process = Process(target=check_robot_reachable, args=(self.ip, self.queue))
        self.process.start()

        # Poll for process result
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_process_result)
        self.timer.start(100)

    def check_process_result(self):
        if not self.queue.empty():
            reachable = self.queue.get()
            self.timer.stop()
            self.process.join()
            self.loading.close()

            if not reachable:
                QMessageBox.critical(None, "Error", "Connection failed. Please try again.")
                self.show_config()
                return

            try:
                robot, tool_dynamics = utl.setup_robot(self.ip, self.tooltest)
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Robot setup failed: {e}")
                self.show_config()
                return

            update_joint_speed_from_slider(50, robot)

            global window
            window = MainWindow(robot, ip=self.ip, tooltest=self.tooltest)
            window.robot = robot
            robot.ui_ref = window
            robot.enable_robot_event()

            # Use a dict to hold the robot reference so we can update it on reconnect
            self.robot_container = {"robot": robot}

            self.start_position_timer(window)
            window.show()

      
            


    def start_position_timer(self, window):
        self.timer = QTimer(window)

        def safe_get_position():
            try:
                get_robot_current_position(self.robot_container["robot"], window)
            except Exception as e:
                print(f"[Position Error] {e}")
                self.timer.stop()
                self.reconnect_robot(window)

        self.timer.timeout.connect(safe_get_position)
        self.timer.start(100)

    def reconnect_robot(self, window):
        # Show reconnect loading dialog
        self.loading = QProgressDialog("Reconnecting to robot...", None, 0, 0)
        self.loading.setWindowModality(Qt.ApplicationModal)
        self.loading.setCancelButton(None)
        self.loading.setMinimumDuration(0)
        self.loading.setWindowTitle("Please wait")
        self.loading.setMinimumWidth(300)
        self.loading.show()

        self.queue = Queue()
        self.process = Process(target=check_robot_reachable, args=(self.ip, self.queue))
        self.process.start()

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.finish_reconnect(window))
        self.timer.start(100)

    def finish_reconnect(self, old_window):
        if not self.queue.empty():
            reachable = self.queue.get()

            if self.connection_timer is not None:
                self.connection_timer.stop()
                self.connection_timer.deleteLater()
                self.connection_timer = None

            self.process.join()
            self.loading.close()

            if not reachable:
                QMessageBox.critical(None, "Error", "Reconnection failed. Please try again.")
                self.show_config()
                return

            try:
                # Use bridge client for reconnection
                from robot_bridge_client import Auboi5Robot
                robot = Auboi5Robot(bridge_host='127.0.0.1', bridge_port=5000)
                
                if not robot.check_connection():
                    raise RuntimeError("Bridge server not responding")
                
                robot, tool_dynamics = utl.setup_robot(self.ip, self.tooltest)
                if result != 0:
                    raise RuntimeError(f"Robot startup failed with code: {result}")
                
                self.robot_container["robot"] = robot
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Reconnect failed: {e}")
                self.show_config()
                return

            update_joint_speed_from_slider(50, robot)

            # Close old window cleanly
            old_window.close()

            # Create a new main window fresh with the new robot instance
            global window
            window = MainWindow(robot, ip=self.ip, tooltest=self.tooltest)
            window.robot = robot
            robot.ui_ref = window
            robot.enable_robot_event()


            # Restart position timer with new window
            self.start_position_timer(window)
            window.show()
            

if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    controller = AppController()
    controller.start()


