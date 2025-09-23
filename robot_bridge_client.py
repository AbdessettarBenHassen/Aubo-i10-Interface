#!/usr/bin/env python3
# coding=utf-8
import socket
import json
import time
import logging
from math import pi
import threading
import ctypes
import os


# Robot error types (matching the original robotcontrol.py)
# Note: Main RobotErrorType class is defined later in the file

# Robot coordinate types
class RobotCoordType:
    Robot_Base_Coordinate = 0
    Robot_End_Coordinate = 1
    Robot_World_Coordinate = 2

# Robot coordinate calibration methods
class RobotCoordCalMethod:
    CoordCalMethod_xOy = 0
    CoordCalMethod_yOz = 1
    CoordCalMethod_zOx = 2
    CoordCalMethod_xOxy = 3
    CoordCalMethod_xOxz = 4
    CoordCalMethod_yOyx = 5
    CoordCalMethod_yOyz = 6
    CoordCalMethod_zOzx = 7
    CoordCalMethod_zOzy = 8
class RobotEventType:
    RobotEvent_armCanbusError = 0
    RobotEvent_remoteHalt = 1
    RobotEvent_remoteEmergencyStop = 2
    RobotEvent_jointError = 3
    RobotEvent_forceControl = 4
    RobotEvent_exitForceControl = 5
    RobotEvent_softEmergency = 6
    RobotEvent_exitSoftEmergency = 7
    RobotEvent_collision = 8
    RobotEvent_collisionStatusChanged = 9
    RobotEvent_tcpParametersSucc = 10
    RobotEvent_powerChanged = 11
    RobotEvent_ArmPowerOff = 12
    RobotEvent_mountingPoseChanged = 13
    RobotEvent_encoderError = 14
    RobotEvent_encoderLinesError = 15
    RobotEvent_singularityOverspeed = 16
    RobotEvent_currentAlarm = 17
    RobotEvent_toolioError = 18
    RobotEvent_robotStartupPhase = 19
    RobotEvent_robotStartupDoneResult = 20
    RobotEvent_robotShutdownDone = 21
    RobotEvent_atTrackTargetPos = 22
    RobotEvent_SetPowerOnDone = 23
    RobotEvent_ReleaseBrakeDone = 24
    RobotEvent_robotControllerStateChaned = 25
    RobotEvent_robotControllerError = 26
    RobotEvent_socketDisconnected = 27
    RobotEvent_overSpeed = 28
    RobotEvent_algorithmException = 29
    RobotEvent_boardIoPoweron = 30
    RobotEvent_boardIoRunmode = 31
    RobotEvent_boardIoPause = 32
    RobotEvent_boardIoStop = 33
    RobotEvent_boardIoHalt = 34
    RobotEvent_boardIoEmergency = 35
    RobotEvent_boardIoRelease_alarm = 36
    RobotEvent_boardIoOrigin_pose = 37
    RobotEvent_boardIoAutorun = 38
    RobotEvent_safetyIoExternalEmergencyStope = 39
    RobotEvent_safetyIoExternalSafeguardStope = 40
    RobotEvent_safetyIoReduced_mode = 41
    RobotEvent_safetyIoSafeguard_reset = 42
    RobotEvent_safetyIo3PositionSwitch = 43
    RobotEvent_safetyIoOperationalMode = 44
    RobotEvent_safetyIoManualEmergencyStop = 45
    RobotEvent_safetyIoSystemStop = 46
    RobotEvent_alreadySuspended = 47
    RobotEvent_alreadyStopped = 48
    RobotEvent_alreadyRunning = 49
    RobotEvent_MoveEnterStopState = 1300
    RobotEvent_None = 999999
    NoError = [RobotEvent_None]  # List of non-error events

class RobotErrorType:
    RobotError_SUCC = 0
    RobotError_Base = 2000
    RobotError_RSHD_INIT_FAILED = RobotError_Base + 1
    RobotError_RSHD_UNINIT = RobotError_Base + 2
    RobotError_NoLink = RobotError_Base + 3
    RobotError_Move = RobotError_Base + 4
    RobotError_ControlError = RobotError_Base + RobotEventType.RobotEvent_robotControllerError
    RobotError_LOGIN_FAILED = RobotError_Base + 5
    RobotError_NotLogin = RobotError_Base + 6
    RobotError_ERROR_ARGS = RobotError_Base + 7

class RobotEvent:
    def __init__(self, event_type=RobotEventType.RobotEvent_None, event_code=0, event_msg=''):
        self.event_type = event_type
        self.event_code = event_code
        self.event_msg = event_msg

class RobotError(Exception):
    def __init__(self, error_type=RobotErrorType.RobotError_SUCC, error_code=0, error_msg=''):
        self.error_type = error_type
        self.error_cdoe = error_code
        self.error_msg = error_msg

    def __str__(self):
        return "RobotError type{0} code={1} msg={2}".format(self.error_type, self.error_cdoe, self.error_msg)

class RobotDefaultParameters:
    tool_dynamics = {"position": (0.0, 0.0, 0.0), "payload": 0.0, "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)}
    collision_grade = 6

class RobotMoveTrackType:
    ARC_CIR = 2
    CARTESIAN_MOVEP = 3
    CARTESIAN_CUBICSPLINE = 4
    CARTESIAN_UBSPLINEINTP = 5
    JIONT_CUBICSPLINE = 6
    JOINT_UBSPLINEINTP = 7

class RobotIOType:
    ControlBox_DI = 0
    ControlBox_DO = 1
    ControlBox_AI = 2
    ControlBox_AO = 3
    User_DI = 4
    User_DO = 5
    User_AI = 6
    User_AO = 7

class RobotStatus:
    Stopped = 0
    Running = 1
    Paused = 2
    Resumed = 3

class RobotRunningMode:
    RobotModeSimulator = 0
    RobotModeReal = 1

class RobotToolPowerType:
    OUT_0V = 0
    OUT_12V = 1
    OUT_24V = 2

class RobotCoordType:
    Robot_Base_Coordinate = 0
    Robot_End_Coordinate = 1
    Robot_World_Coordinate = 2

class RobotCoordCalMethod:
    CoordCalMethod_xOy = 0
    CoordCalMethod_yOz = 1
    CoordCalMethod_zOx = 2
    CoordCalMethod_xOxy = 3
    CoordCalMethod_xOxz = 4
    CoordCalMethod_yOyx = 5
    CoordCalMethod_yOyz = 6
    CoordCalMethod_zOzx = 7
    CoordCalMethod_zOzy = 8

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

class RobotToolDigitalIoDir:
    IO_IN = 0
    IO_OUT = 1

class RobotToolIoAddr:
    TOOL_DIGITAL_IO_0 = 0
    TOOL_DIGITAL_IO_1 = 1
    TOOL_DIGITAL_IO_2 = 2
    TOOL_DIGITAL_IO_3 = 3

class RobotToolIoName:
    tool_io_0 = "T_DI/O_00"
    tool_io_1 = "T_DI/O_01"
    tool_io_2 = "T_DI/O_02"
    tool_io_3 = "T_DI/O_03"
    tool_ai_0 = "T_AI_00"
    tool_ai_1 = "T_AI_01"

class RobotUserIoName:
    # User DI
    user_di_00 = "U_DI_00"
    user_di_01 = "U_DI_01"
    user_di_02 = "U_DI_02"
    user_di_03 = "U_DI_03"
    user_di_04 = "U_DI_04"
    user_di_05 = "U_DI_05"
    user_di_06 = "U_DI_06"
    user_di_07 = "U_DI_07"
    user_di_10 = "U_DI_10"
    user_di_11 = "U_DI_11"
    user_di_12 = "U_DI_12"
    user_di_13 = "U_DI_13"
    user_di_14 = "U_DI_14"
    user_di_15 = "U_DI_15"
    user_di_16 = "U_DI_16"
    user_di_17 = "U_DI_17"

    # User DO
    user_do_00 = "U_DO_00"
    user_do_01 = "U_DO_01"
    user_do_02 = "U_DO_02"
    user_do_03 = "U_DO_03"
    user_do_04 = "U_DO_04"
    user_do_05 = "U_DO_05"
    user_do_06 = "U_DO_06"
    user_do_07 = "U_DO_07"
    user_do_10 = "U_DO_10"
    user_do_11 = "U_DO_11"
    user_do_12 = "U_DO_12"
    user_do_13 = "U_DO_13"
    user_do_14 = "U_DO_14"
    user_do_15 = "U_DO_15"
    user_do_16 = "U_DO_16"
    user_do_17 = "U_DO_17"

    # User AI
    user_ai_00 = "VI0"
    user_ai_01 = "VI1"
    user_ai_02 = "VI2"
    user_ai_03 = "VI3"

    # User AO
    user_ao_00 = "VO0"
    user_ao_01 = "VO1"
    user_ao_02 = "VO2"
    user_ao_03 = "VO3"
# Configure logging
logging.basicConfig(
    level=logging.WARNING, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)



class RobotBridgeClient:
    """Python 3 client for communicating with Python 2 robot bridge server"""
    
    def __init__(self, bridge_host='127.0.0.1', bridge_port=5000):
        self.bridge_host = bridge_host
        self.bridge_port = bridge_port
        self.connected = False
        self.last_error = None
        self.last_event = None
        self.atTrackTargetPos = False
        self.step_mode_checkbox = None  # For compatibility with UI
        self.rshd = 0  # Dummy RSHD value for compatibility with UI
        
        # Test connection
        self.test_connection()
    
    def test_connection(self):
        """Test if bridge server is available"""
        try:
            response = self.send_command({"action": "get_status"})
            if response.get("status") == "ok":
                self.connected = True
                logger.info("Bridge server connection successful")
            else:
                self.connected = False
                logger.error("Bridge server connection failed")
        except Exception as e:
            self.connected = False
            logger.error(f"Bridge server connection error: {e}")

    
    def send_command(self, cmd, timeout=10):
        """Send command to bridge server and get response"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((self.bridge_host, self.bridge_port))
            s.send(json.dumps(cmd).encode('utf-8'))
            data = s.recv(8192)
            s.close()
            
            response = json.loads(data.decode('utf-8'))
            if response.get("status") == "error":
                raise RuntimeError(response.get("message", "Unknown error"))
            return response
            
        except Exception as e:
            logger.error(f"Bridge communication failed: {e}")
            raise RuntimeError(f"Bridge communication failed: {e}")
    
    def check_connection(self):
        """Check if bridge server is still connected"""
        if not self.connected:
            self.test_connection()
        return self.connected

    @staticmethod
    def initialize():
        """Initialize robot library (static method for compatibility)"""
        return RobotErrorType.RobotError_SUCC

    @staticmethod
    def uninitialize():
        """Uninitialize robot library (static method for compatibility)"""
        return RobotErrorType.RobotError_SUCC

    @staticmethod
    def get_local_time():
        """Get current local time as string"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def create_context(self):
        """Create robot context (compatibility method)"""
        return 0  # Return a dummy handle

    def connect(self, ip, port=8899):
        """Connect to robot"""
        try:
            response = self.send_command({
                "action": "connect",
                "params": {"ip": ip, "port": port}
            })
            if response.get("status") == "ok":
                self.connected = True
                return RobotErrorType.RobotError_SUCC
            return RobotErrorType.RobotError_NotLogin
        except Exception as e:
            logger.error(f"Connect error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def robot_startup(self, collision=RobotDefaultParameters.collision_grade,
                      tool_dynamics=RobotDefaultParameters.tool_dynamics):
        self.check_event()
        try:
            response = self.send_command({
                "action": "robot_startup",
                "params": {"collision": collision, "tool_dynamics": tool_dynamics}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Robot startup error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def robot_shutdown(self):
        """Robot shutdown"""
        try:
            response = self.send_command({"action": "robot_shutdown"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Robot shutdown error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def init_profile(self):
        """Initialize robot profile"""
        try:
            response = self.send_command({"action": "init_profile"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Init profile error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def set_base_coord(self):
        """Set base coordinate system"""
        try:
            response = self.send_command({"action": "set_base_coord"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set base coord error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def set_joint_maxvelc(self, joint_maxvelc):
        """Set joint maximum velocity"""
        try:
            response = self.send_command({
                "action": "set_joint_maxvelc",
                "params": {"joint_maxvelc": joint_maxvelc}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set joint maxvelc error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def set_joint_maxacc(self, joint_maxacc):
        """Set joint maximum acceleration"""
        try:
            response = self.send_command({
                "action": "set_joint_maxacc",
                "params": {"joint_maxacc": joint_maxacc}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set joint maxacc error: {e}")
            return RobotErrorType.RobotError_NotLogin
    def teach_move_stop(self):
        """Stop teach move"""
        try:
            response = self.send_command({"action": "teach_move_stop"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Teach move stop error: {e}")
            return RobotErrorType.RobotError_NotLogin
    def set_end_max_line_velc(self, velocity):
        """Set end effector maximum linear velocity"""
        try:
            response = self.send_command({
                "action": "set_end_max_line_velc",
                "params": {"velocity": velocity}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set end max line velc error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def set_end_max_line_acc(self, acceleration):
        """Set end effector maximum linear acceleration"""
        try:
            response = self.send_command({
                "action": "set_end_max_line_acc",
                "params": {"acceleration": acceleration}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set end max line acc error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def forward_kin(self, joint_radian):
        """Forward kinematics - convert joint angles to cartesian position"""
        try:
            response = self.send_command({
                "action": "forward_kin",
                "params": {"joint_radian": joint_radian}
            })
            return response.get("result", {})
        except Exception as e:
            logger.error(f"Forward kinematics error: {e}")
            return {}

    def quaternion_to_rpy(self, ori):
        """Convert quaternion to roll-pitch-yaw angles"""
        try:
            response = self.send_command({
                "action": "quaternion_to_rpy",
                "params": {"ori": ori}
            })
            return response.get("result", [0, 0, 0])
        except Exception as e:
            logger.error(f"Quaternion to RPY error: {e}")
            return [0, 0, 0]

    def get_board_io_status(self, io_type, io_name):
        """Get board IO status"""
        try:
            response = self.send_command({
                "action": "get_board_io_status",
                "params": {"io_type": io_type, "io_name": io_name}
            })
            return response.get("result", 0)
        except Exception as e:
            logger.error(f"Get board IO status error: {e}")
            return 0
    
    def set_board_io_status(self, io_type, io_name, value):
        """Set board IO status"""
        try:
            response = self.send_command({
                "action": "set_board_io_status",
                "params": {"io_type": io_type, "io_name": io_name, "value": value}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set board IO status error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def get_tool_dynamics_param(self):
        """Get tool dynamics parameters"""
        try:
            response = self.send_command({"action": "get_tool_dynamics_param"})
            return response.get("result", {})
        except Exception as e:
            logger.error(f"Get tool dynamics param error: {e}")
            return {}
    

# Robot Event Types (copied from original robotcontrol.py)


# Main robot control class that replaces Auboi5Robot
class Auboi5Robot(RobotBridgeClient):
    __client_count = 0

    def __init__(self, bridge_host='127.0.0.1', bridge_port=5000):
        super().__init__(bridge_host, bridge_port)
        Auboi5Robot.__client_count += 1
        self.rshd = 0  # Dummy value for compatibility
        self.last_error = RobotError()
        self.last_event = RobotEvent()
        self.atTrackTargetPos = False
        self._event_thread_stop = False
        self._event_thread = threading.Thread(target=self._event_poller, name="robot_event_poller")
        self._event_thread.daemon = True
        self._event_thread.start()
        self.ui_ref = None
        self.on_robot_error = None

    def __del__(self):
        try:
            self._event_thread_stop = True
        except Exception:
            pass
        Auboi5Robot.__client_count -= 1
        self.uninitialize()

    def __str__(self):
        return "RSHD={0}, connected={1}".format(self.rshd, self.connected)

    @staticmethod
    def get_local_time():
        return time.strftime("%b %d %Y %H:%M:%S", time.localtime(time.time())) 
    def _event_poller(self):
        print("🔄 Event polling thread started")
        while not getattr(self, "_event_thread_stop", False):
            try:
                resp = self.send_command({"action": "get_last_event"}, timeout=3)
                evt = resp.get("event")
                if evt:
                    print(f"📬 Event received in poller: {evt}")
                    try:
                        self.robot_event_callback(evt)
                    except Exception as cb_e:
                        logger.error(f"robot_event_callback error: {cb_e}")
            except Exception as e:
                # bridge might be down; ignore to avoid log spam
                print(f"Event polling error (ignored): {e}")
            time.sleep(0.2)
        print("🛑 Event polling thread stopped")
    def set_ui_ref(self, ui):
        self.ui_ref = ui
    def set_error_callback(self, fn):
        self.on_robot_error = fn
    def robot_event_callback(self, event):
        from PyQt5.QtCore import QTimer
        print(f"🎯 robot_event_callback called with event: {event}")
        if event['type'] not in RobotEventType.NoError:
            self.last_error = RobotError(event['type'], event['code'], event['content'])
            print(f"❌ Robot error occurred: {self.last_error}")
            
            if hasattr(self, 'ui_ref'):
                print(f"ui_ref: {self.ui_ref}")
                if self.ui_ref:
                    print("📬 Triggering popup from UI...")
                    self.ui_ref.robot_error_signal.emit(str(self.last_error))
                else:
                    print("❗ No UI reference available")
            else:
                print("❗ self has no ui_ref attribute.")
        else:
            print(f"ℹ️ Non-error event received: {event['type']}")

    @staticmethod
    def raise_error(error_type, error_code, error_msg):
        raise RobotError(error_type, error_code, error_msg)

    def check_event(self):
        if self.last_error.error_type != RobotErrorType.RobotError_SUCC:
            return self.last_error
        if not self.connected:
            self.raise_error(RobotErrorType.RobotError_NoLink, 0, "no socket link")

    @staticmethod
    def initialize():
        return RobotErrorType.RobotError_SUCC

    @staticmethod
    def uninitialize():
        return RobotErrorType.RobotError_SUCC

    def create_context(self):
        self.rshd = 0  # Dummy value for compatibility
        return self.rshd

    def get_context(self):
        return self.rshd

    def connect(self, ip='localhost', port=8899):
        # Connection is handled by bridge server
        return RobotErrorType.RobotError_SUCC

    def disconnect(self):
        try:
            self.send_command({"action": "disconnect"})
            return RobotErrorType.RobotError_SUCC
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def robot_startup(self, collision=RobotDefaultParameters.collision_grade,
                      tool_dynamics=RobotDefaultParameters.tool_dynamics):
        self.check_event()
        try:
            response = self.send_command({
                "action": "robot_startup",
                "params": {"collision": collision, "tool_dynamics": tool_dynamics}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Robot startup error: {e}")
            return RobotErrorType.RobotError_NotLogin
    def teach_move_start(self, joint_mode, direction):
        """Start teach move for a specific joint mode and direction"""
        try:
            response = self.send_command({
                "action": "teach_move_start",
                "params": {"joint_mode": joint_mode, "direction": direction}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Teach move start error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def robot_shutdown(self):
        try:
            response = self.send_command({"action": "robot_shutdown"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Robot shutdown error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def enable_robot_event(self):
        self.check_event()
        # Event handling is done through bridge
        return RobotErrorType.RobotError_SUCC
    
    # Event checking is handled by the _event_poller thread

    def init_profile(self):
        try:
            response = self.send_command({"action": "init_profile"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Init profile error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def set_joint_maxacc(self, joint_maxacc=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_joint_maxacc",
                "params": {"joint_maxacc": joint_maxacc}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set joint maxacc error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def get_joint_maxacc(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_joint_maxacc"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Get joint maxacc error: {e}")
            return None

    def set_joint_maxvelc(self, joint_maxvelc=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_joint_maxvelc",
                "params": {"joint_maxvelc": joint_maxvelc}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set joint maxvelc error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def get_joint_maxvelc(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_joint_maxvelc"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Get joint maxvelc error: {e}")
            return None

    def set_end_max_line_acc(self, end_maxacc=0.1):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_end_max_line_acc",
                "params": {"end_maxacc": end_maxacc}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set end max line acc error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def get_end_max_line_acc(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_end_max_line_acc"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Get end max line acc error: {e}")
            return None

    def set_end_max_line_velc(self, end_maxvelc=0.1):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_end_max_line_velc",
                "params": {"end_maxvelc": end_maxvelc}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set end max line velc error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def get_end_max_line_velc(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_end_max_line_velc"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Get end max line velc error: {e}")
            return None

    def set_arrival_ahead_distance(self, distance):
        """Set arrival ahead distance"""
        try:
            response = self.send_command({
                "action": "set_arrival_ahead_distance",
                "params": {"distance": distance}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set arrival ahead distance error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def move_to_target_in_cartesian(self, pos, rpy_xyz):
        self.check_event()
        try:
            response = self.send_command({
                "action": "move_to_target_in_cartesian",
                "params": {"pos": pos, "rpy_xyz": rpy_xyz}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Move to target in cartesian error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def move_joint(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000), issync=True):
        self.check_event()
        try:
            response = self.send_command({
                "action": "move_joint",
                "params": {"joint_values": joint_radian, "is_sync": issync}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Move joint error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def move_line(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000), issync=True):
        self.check_event()
        try:
            response = self.send_command({
                "action": "move_line",
                "params": {"joint_values": joint_radian, "is_sync": issync}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Move line error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def move_stop(self):
        self.check_event()
        try:
            response = self.send_command({"action": "move_stop"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Move stop error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def move_pause(self):
        self.check_event()
        try:
            response = self.send_command({"action": "move_pause"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Move pause error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def move_continue(self):
        self.check_event()
        try:
            response = self.send_command({"action": "move_continue"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Move continue error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def get_robot_state(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_robot_state"})
            return response.get("state")
        except Exception as e:
            logger.error(f"Get robot state error: {e}")
            return None

    def get_current_waypoint(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_current_waypoint"})
            return response.get("waypoint")
        except Exception as e:
            logger.error(f"Get current waypoint error: {e}")
            return None

    def forward_kin(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)):
        try:
            response = self.send_command({
                "action": "forward_kin",
                "params": {"joint_radian": joint_radian}
            })
            return response.get("result")
        except Exception as e:
            logger.error(f"Forward kinematics error: {e}")
            return None

    def inverse_kin(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000),
                    pos=(0.0, 0.0, 0.0), ori=(1.0, 0.0, 0.0, 0.0)):
        try:
            response = self.send_command({
                "action": "inverse_kin",
                "params": {"joint_radian": joint_radian, "pos": pos, "ori": ori}
            })
            return response.get("result")
        except Exception as e:
            logger.error(f"Inverse kinematics error: {e}")
            return None

    def rpy_to_quaternion(self, rpy):
        try:
            response = self.send_command({
                "action": "rpy_to_quaternion",
                "params": {"rpy": rpy}
            })
            return response.get("result")
        except Exception as e:
            logger.error(f"RPY to quaternion error: {e}")
            return None

    def quaternion_to_rpy(self, ori):
        try:
            response = self.send_command({
                "action": "quaternion_to_rpy",
                "params": {"ori": ori}
            })
            return response.get("result")
        except Exception as e:
            logger.error(f"Quaternion to RPY error: {e}")
            return None

    def set_tool_dynamics_param(self, tool_dynamics):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_tool_dynamics_param",
                "params": {"tool_dynamics": tool_dynamics}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set tool dynamics param error: {e}")
            return None

    def get_tool_dynamics_param(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_tool_dynamics_param"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Get tool dynamics param error: {e}")
            return None

    def set_tool_kinematics_param(self, tool_end_param):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_tool_kinematics_param",
                "params": {"tool_end_param": tool_end_param}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set tool kinematics param error: {e}")
            return None

    def get_tool_kinematics_param(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_tool_kinematics_param"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Get tool kinematics param error: {e}")
            return None

    def set_user_coord(self, user_coord):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_user_coord",
                "params": {"user_coord": user_coord}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set user coord error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def set_base_coord(self):
        self.check_event()
        try:
            response = self.send_command({"action": "set_base_coord"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set base coord error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def get_board_io_status(self, io_type, io_name):
        self.check_event()
        try:
            response = self.send_command({
                "action": "get_board_io_status",
                "params": {"io_type": io_type, "io_name": io_name}
            })
            return response.get("result")
        except Exception as e:
            logger.error(f"Get board IO status error: {e}")
            return None

    def set_board_io_status(self, io_type, io_name, io_value):
        try:
            response = self.send_command({
                "action": "set_board_io_status",
                "params": {"io_type": io_type, "io_name": io_name, "io_value": io_value}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set board IO status error: {e}")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def get_tool_io_status(self, io_name):
        self.check_event()
        try:
            response = self.send_command({
                "action": "get_tool_io_status",
                "params": {"io_name": io_name}
            })
            return response.get("result")
        except Exception as e:
            logger.error(f"Get tool IO status error: {e}")
            return None

    def set_tool_io_status(self, io_name, io_status):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_tool_io_status",
                "params": {"io_name": io_name, "io_status": io_status}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set tool IO status error: {e}")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def set_work_mode(self, mode=0):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_work_mode",
                "params": {"mode": mode}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set work mode error: {e}")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def get_work_mode(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_work_mode"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Get work mode error: {e}")
            return None

    def set_collision_class(self, grade=6):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_collision_class",
                "params": {"grade": grade}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set collision class error: {e}")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def is_have_real_robot(self):
        self.check_event()
        try:
            response = self.send_command({"action": "is_have_real_robot"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Is have real robot error: {e}")
            return None

    def is_online_mode(self):
        self.check_event()
        try:
            response = self.send_command({"action": "is_online_mode"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Is online mode error: {e}")
            return None

    def get_joint_status(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_joint_status"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Get joint status error: {e}")
            return None

    def get_board_io_config(self, io_type=RobotIOType.User_DO):
        self.check_event()
        try:
            response = self.send_command({
                "action": "get_board_io_config",
                "params": {"io_type": io_type}
            })
            return response.get("result")
        except Exception as e:
            logger.error(f"Get board IO config error: {e}")
            return None

    def set_tool_power_type(self, power_type=RobotToolPowerType.OUT_0V):
        self.check_event()
        try:
            response = self.send_command({
                "action": "set_tool_power_type",
                "params": {"power_type": power_type}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set tool power type error: {e}")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def get_tool_power_type(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_tool_power_type"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Get tool power type error: {e}")
            return None

    def get_tool_power_voltage(self):
        self.check_event()
        try:
            response = self.send_command({"action": "get_tool_power_voltage"})
            return response.get("result")
        except Exception as e:
            logger.error(f"Get tool power voltage error: {e}")
            return None

    def enter_reduce_mode(self):
        self.check_event()
        try:
            response = self.send_command({"action": "enter_reduce_mode"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Enter reduce mode error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def exit_reduce_mode(self):
        self.check_event()
        try:
            response = self.send_command({"action": "exit_reduce_mode"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Exit reduce mode error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def project_startup(self):
        self.check_event()
        try:
            response = self.send_command({"action": "project_startup"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Project startup error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def rs_project_stop(self):
        self.check_event()
        try:
            response = self.send_command({"action": "rs_project_stop"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Project stop error: {e}")
            return RobotErrorType.RobotError_NotLogin

    @staticmethod
    def get_local_time():
        """Get current local time as string"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def teach_move_start(self, joint_mode, direction):
        """Start teach move for a specific joint mode and direction"""
        try:
            response = self.send_command({
                "action": "teach_move_start",
                "params": {"joint_mode": joint_mode, "direction": direction}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Teach move start error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def teach_move_stop(self):
        """Stop teach move"""
        try:
            response = self.send_command({"action": "teach_move_stop"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Teach move stop error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def set_teach_base_coord(self):
        """Set teach base coordinate system"""
        try:
            response = self.send_command({"action": "set_teach_base_coord"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set teach base coord error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def set_teach_end_coord(self):
        """Set teach end coordinate system"""
        try:
            response = self.send_command({"action": "set_teach_end_coord"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set teach end coord error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def set_teach_user_coord(self, user_coord):
        """Set teach user coordinate system"""
        try:
            response = self.send_command({
                "action": "set_teach_user_coord",
                "params": {"user_coord": user_coord}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set teach user coord error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def check_user_coord(self, user_coord):
        """Check if user coordinate is valid"""
        try:
            response = self.send_command({
                "action": "check_user_coord",
                "params": {"user_coord": user_coord}
            })
            return response.get("result", True)
        except Exception as e:
            logger.error(f"Check user coord error: {e}")
            return False

    def remove_all_waypoint(self):
        """Remove all waypoints"""
        try:
            response = self.send_command({"action": "remove_all_waypoint"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Remove all waypoint error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def add_waypoint(self, joint_radian):
        """Add a waypoint"""
        try:
            response = self.send_command({
                "action": "add_waypoint",
                "params": {"joint_radian": joint_radian}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Add waypoint error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def set_circular_loop_times(self, times):
        """Set circular loop times"""
        try:
            response = self.send_command({
                "action": "set_circular_loop_times",
                "params": {"times": times}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Set circular loop times error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def move_track(self, track_type):
        """Move track"""
        try:
            response = self.send_command({
                "action": "move_track",
                "params": {"track_type": track_type}
            })
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Move track error: {e}")
            return RobotErrorType.RobotError_NotLogin

    def collision_recover(self):
        """Recover from collision"""
        try:
            response = self.send_command({"action": "collision_recover"})
            return response.get("result", RobotErrorType.RobotError_SUCC)
        except Exception as e:
            logger.error(f"Collision recover error: {e}")
            return RobotErrorType.RobotError_NotLogin

# Alias for compatibility with original robotcontrol.py
# Note: Auboi5Robot class is defined above, no need for alias

# Test function
def test_bridge():
    """Test the bridge connection"""
    try:
        robot = Auboi5Robot()
        print("Bridge connection test successful!")
        
        # Test getting robot state
        state = robot.get_robot_state()
        print(f"Robot state: {state}")
        
        # Test getting current waypoint
        waypoint = robot.get_current_waypoint()
        print(f"Current waypoint: {waypoint}")
        
    except Exception as e:
        print(f"Bridge test failed: {e}")

if __name__ == "__main__":
    test_bridge()



