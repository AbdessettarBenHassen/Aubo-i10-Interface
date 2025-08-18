from ui import *
import utils as utl 
from multiprocessing import Process, Queue
import robotcontrol as mim
from joystick import JoystickManager
from threads import *
from config_dialog import ConfigDialog
import sys
from PyQt5.QtWidgets import QApplication,QProgressDialog
from PyQt5.QtCore import QTimer,Qt, QThread, pyqtSignal

#ip = '192.168.0.23'
ip = ''
tooltest = ""
robot = None
window = None
movement_active = False
rt = False
step = False
speed = 1

def button_handler(button_id: int, pressed: bool):
    global rt, step, speed
    if button_id == 9 and pressed:
        rt = not rt
    elif button_id == 10 and pressed:
        step = not step
    elif button_id == 11 and pressed:
        speed += 1
    elif button_id == 12 and pressed:
        speed -= 1

def axis_handler(axis_id: int, value: int):
    global step, speed, movement_active
    if axis_id < 3:
        if axis_id == 0:
            axis_id = 1
        elif axis_id == 1:
            axis_id = 0
        if not robot:
            return
        control_axis = axis_id + 4 if rt else axis_id + 1
        if abs(value) > 0.8:
            direction = "-" if value < 0 else "+"
            try:
                utl.move_cartesian(robot, control_axis, direction, step, str(speed), str(speed))
                movement_active = True
            except Exception as e:
                print(f"Movement error: {e}")
        elif movement_active:
            try:
                utl.stop_movement(robot)
                movement_active = False
            except Exception as e:
                print(f"Stop error: {e}")

def hat_handler(hat_id: int, value: tuple):
    pass
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
            self.start_connection()
        else:
            sys.exit()

    def start_connection(self):
        self.tooltest = self.config.selected_tool
        self.ip = self.config.selected_ip

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

            joystick = JoystickManager(
                axis_threshold=0.1,
                button_callback=button_handler,
                axis_callback=axis_handler,
                hat_callback=hat_handler
            )
            joystick.start()

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
                robot, tool_dynamics = utl.setup_robot(self.ip, self.tooltest)
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

            joystick = JoystickManager(
                axis_threshold=0.1,
                button_callback=button_handler,
                axis_callback=axis_handler,
                hat_callback=hat_handler
            )
            joystick.start()

            # Restart position timer with new window
            self.start_position_timer(window)
            window.show()

if __name__ == "__main__":
    controller = AppController()
    controller.start()

