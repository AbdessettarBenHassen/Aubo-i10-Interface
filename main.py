from ui import *
import utils as utl 
import robotcontrol as mim
from joystick import JoystickManager
from threads import *
import sys
from PyQt5.QtCore import QTimer

ip = '192.168.95.158'

# Global state
rt = False  # Toggle between position/orientation control
robot = None
window = None
movement_active = False  # Track if we're currently moving
step=False
speed = 1

def button_handler(button_id: int, pressed: bool):
    global rt
    global step
    global speed
    action = "PRESSED" if pressed else "RELEASED"
    if button_id == 9 and pressed:  # Only toggle on press, not release
        rt = not rt
        print(f"Control mode switched to {'orientation' if rt else 'position'}")
    if button_id == 10 and pressed:  # Only toggle on press, not release
        step = not step
        print(f"Control mode switched to {'orientation' if rt else 'position'}")
    if button_id == 11 and pressed:  # Only toggle on press, not release
        speed = speed +1
        print(f"Control mode switched to {'orientation' if rt else 'position'}")
    if button_id == 12 and pressed:  # Only toggle on press, not release
        speed = speed -1
        print(f"Control mode switched to {'orientation' if rt else 'position'}")
    print(f"Button {button_id} {action}")

def axis_handler(axis_id: int, value: int):
    global step
    global speed
    if(axis_id<3):
        global movement_active
        if(axis_id==0):
            axis_id=1
        elif(axis_id ==1):
            axis_id=0
        if not robot:
            print("Robot not connected!")
            return
        
        # Determine which axis to control based on rt mode
        control_axis = axis_id + 4 if rt else axis_id + 1
        
        # Only act on significant joystick movements
        if abs(value) > 0.8:  # Deadzone threshold
            direction = "-" if value < 0 else "+"
            
            try:
                # For continuous movement, we need to call this repeatedly while joystick is deflected
                utl.move_cartesian(robot, control_axis, direction, step, str(speed), str(speed))
                movement_active = True
                print(f"Continuous {'orientation' if rt else 'position'} movement on axis {control_axis} {direction}")
            except Exception as e:
                print(f"Movement error: {e}")
        elif movement_active:
            # Joystick returned to center - stop movement
            try:
                # You may need to implement a stop command in your utils
                utl.stop_movement(robot)  # You'll need to implement this function
                movement_active = False
                print("Movement stopped")
            except Exception as e:
                print(f"Stop error: {e}")

def hat_handler(hat_id: int, value: tuple):
    print(f"Hat {hat_id} moved to {value}")
def main():
    # Initialize connection
    robot, queue = utl.robot_connect(ip)
    #  if robot:
    #     robot.robot_startup()
    #     robot.set_base_coord()
    
    # Setup UI
    app = QApplication(sys.argv)
    window = MainWindow(robot)
    
    # Create joystick manager
    joystick = JoystickManager(
        axis_threshold=0.1,  # Lower threshold for continuous control
        button_callback=button_handler,
        axis_callback=axis_handler,
        hat_callback=hat_handler
    )
    joystick.start()
    
    # Position updater
    timer = QTimer(window)
    timer.timeout.connect(lambda: get_robot_current_position(robot, window))
    timer.start(100)  # Update every 100ms
    
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()