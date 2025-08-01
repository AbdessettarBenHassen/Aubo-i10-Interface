from ui import *
import utils as utl 
import robotcontrol as mim
from joystick import JoystickManager
from threads import *
from config_dialog import ConfigDialog
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

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
def main():
    app = QApplication(sys.argv)

    config = ConfigDialog()
    if config.exec_() == config.Accepted:
        tooltest = config.selected_tool
        ip = config.selected_ip
        print("Selected tool:", tooltest)
        print("Selected IP:", ip)

    global robot
    robot, tool_dynamics = utl.setup_robot(ip, tooltest)
     # Make sure `window` is your main window object
    if robot is None:
        print("Connection failed.")
        sys.exit()
    update_joint_speed_from_slider(50, robot) 
    global window
    window = MainWindow(robot, ip=ip, tooltest=tooltest)
    window.robot = robot
    robot.ui_ref = window  # ✅ Assign UI reference BEFORE enabling event
    robot.enable_robot_event()  # ✅ Now it's safe
    joystick = JoystickManager(
        axis_threshold=0.1,
        button_callback=button_handler,
        axis_callback=axis_handler,
        hat_callback=hat_handler
    )
    joystick.start()

    timer = QTimer(window)
    timer.timeout.connect(lambda: get_robot_current_position(robot, window))
    timer.start(100)
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
