#! /usr/bin/env python
# coding=utf-8
import time
import libpyauboi5
import logging
from logging.handlers import RotatingFileHandler
from multiprocessing import Process, Queue
import os
from math import pi

# Create a logger
#logger = logging.getLogger()

logger = logging.getLogger('main.robotcontrol')


def logger_init():
    # Log level main switch
    logger.setLevel(logging.INFO)

    # Create log directory
    if not os.path.exists('./logfiles'):
        os.mkdir('./logfiles')

    # Create a handler for writing log files
    logfile = './logfiles/robot-ctl-python.log'

    # Open log file in append mode
    # fh = logging.FileHandler(logfile, mode='a')
    fh = RotatingFileHandler(logfile, mode='a', maxBytes=1024*1024*50, backupCount=30)

    # File log level switch
    fh.setLevel(logging.INFO)

    # Create another handler for console output
    ch = logging.StreamHandler()

    # Console log level switch
    ch.setLevel(logging.INFO)

    # Define handler output format
    # formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    formatter = logging.Formatter("%(asctime)s [%(thread)u] %(levelname)s: %(message)s")

    # Set format for file output
    fh.setFormatter(formatter)

    # Set format for console output
    ch.setFormatter(formatter)

    # Set file output to logger
    logger.addHandler(fh)

    # Set console output to logger
    logger.addHandler(ch)


class RobotEventType:
    RobotEvent_armCanbusError = 0  # Arm CAN bus error
    RobotEvent_remoteHalt = 1  # Arm stop
    RobotEvent_remoteEmergencyStop = 2  # Arm remote emergency stop
    RobotEvent_jointError = 3  # Joint error
    RobotEvent_forceControl = 4  # Force control
    RobotEvent_exitForceControl = 5  # Exit force control
    RobotEvent_softEmergency = 6  # Soft emergency stop
    RobotEvent_exitSoftEmergency = 7  # Exit soft emergency stop
    RobotEvent_collision = 8  # Collision
    RobotEvent_collisionStatusChanged = 9  # Collision status changed
    RobotEvent_tcpParametersSucc = 10  # Tool dynamics parameter set successfully
    RobotEvent_powerChanged = 11  # Arm power switch state changed
    RobotEvent_ArmPowerOff = 12  # Arm power off
    RobotEvent_mountingPoseChanged = 13  # Mounting position changed
    RobotEvent_encoderError = 14  # Encoder error
    RobotEvent_encoderLinesError = 15  # Encoder line count mismatch
    RobotEvent_singularityOverspeed = 16  # Singularity overspeed
    RobotEvent_currentAlarm = 17  # Arm current abnormal
    RobotEvent_toolioError = 18  # Arm tool end error
    RobotEvent_robotStartupPhase = 19  # Arm startup phase
    RobotEvent_robotStartupDoneResult = 20  # Arm startup complete result
    RobotEvent_robotShutdownDone = 21  # Arm shutdown result
    RobotEvent_atTrackTargetPos = 22  # Arm trajectory motion reached target position notification
    RobotEvent_SetPowerOnDone = 23  # Set power state complete
    RobotEvent_ReleaseBrakeDone = 24  # Arm brake release complete
    RobotEvent_robotControllerStateChaned = 25  # Arm control state changed
    RobotEvent_robotControllerError = 26  # Arm control error----usually returned when algorithm planning has problems
    RobotEvent_socketDisconnected = 27  # Socket disconnected
    RobotEvent_overSpeed = 28  # Overspeed
    RobotEvent_algorithmException = 29  # Arm algorithm exception
    RobotEvent_boardIoPoweron = 30  # External power-on signal
    RobotEvent_boardIoRunmode = 31  # Linkage/manual
    RobotEvent_boardIoPause = 32  # External pause signal
    RobotEvent_boardIoStop = 33  # External stop signal
    RobotEvent_boardIoHalt = 34  # External shutdown signal
    RobotEvent_boardIoEmergency = 35  # External emergency stop signal
    RobotEvent_boardIoRelease_alarm = 36  # External alarm release signal
    RobotEvent_boardIoOrigin_pose = 37  # External return to origin signal
    RobotEvent_boardIoAutorun = 38  # External auto-run signal
    RobotEvent_safetyIoExternalEmergencyStope = 39  # External emergency stop input 01
    RobotEvent_safetyIoExternalSafeguardStope = 40  # External safeguard stop input 02
    RobotEvent_safetyIoReduced_mode = 41  # Reduced mode input
    RobotEvent_safetyIoSafeguard_reset = 42  # Safeguard reset
    RobotEvent_safetyIo3PositionSwitch = 43  # Three-position switch 1
    RobotEvent_safetyIoOperationalMode = 44  # Operation mode
    RobotEvent_safetyIoManualEmergencyStop = 45  # Teach pendant emergency stop 01
    RobotEvent_safetyIoSystemStop = 46  # System stop input
    RobotEvent_alreadySuspended = 47  # Arm paused
    RobotEvent_alreadyStopped = 48  # Arm stopped
    RobotEvent_alreadyRunning = 49  # Arm running
    RobotEvent_MoveEnterStopState = 1300 # Motion entered stop phase
    RobotEvent_None = 999999

    # Non-error events
    NoError = (RobotEvent_forceControl,
               RobotEvent_exitForceControl,
               RobotEvent_tcpParametersSucc,
               RobotEvent_powerChanged,
               RobotEvent_mountingPoseChanged,
               RobotEvent_robotStartupPhase,
               RobotEvent_robotStartupDoneResult,
               RobotEvent_robotShutdownDone,
               RobotEvent_SetPowerOnDone,
               RobotEvent_ReleaseBrakeDone,
               RobotEvent_atTrackTargetPos,
               RobotEvent_robotControllerStateChaned,
               RobotEvent_robotControllerError,
               RobotEvent_algorithmException,
               RobotEvent_alreadyStopped,
               RobotEvent_alreadyRunning,
               RobotEvent_boardIoPoweron,
               RobotEvent_boardIoRunmode,
               RobotEvent_boardIoPause,
               RobotEvent_boardIoStop,
               RobotEvent_boardIoHalt,
               RobotEvent_boardIoRelease_alarm,
               RobotEvent_boardIoOrigin_pose,
               RobotEvent_boardIoAutorun,
               RobotEvent_safetyIoExternalEmergencyStope,
               RobotEvent_safetyIoExternalSafeguardStope,
               RobotEvent_safetyIoReduced_mode,
               RobotEvent_safetyIoSafeguard_reset,
               RobotEvent_safetyIo3PositionSwitch,
               RobotEvent_safetyIoOperationalMode,
               RobotEvent_safetyIoManualEmergencyStop,
               RobotEvent_safetyIoSystemStop,
               RobotEvent_alreadySuspended,
               RobotEvent_alreadyStopped,
               RobotEvent_alreadyRunning,
               RobotEvent_MoveEnterStopState
               )
               
    UserPostEvent = (RobotEvent_robotControllerError,
                     RobotEvent_safetyIoExternalSafeguardStope,
                     RobotEvent_safetyIoSystemStop
                     )
    ClearErrorEvent = (RobotEvent_armCanbusError,
                       RobotEvent_remoteEmergencyStop,
                       RobotEvent_jointError,
                       RobotEvent_collision,
                       RobotEvent_collisionStatusChanged,
                       RobotEvent_encoderError,
                       RobotEvent_encoderLinesError,
                       RobotEvent_currentAlarm,
                       RobotEvent_softEmergency,
                       RobotEvent_exitSoftEmergency
                       )

    def __init__(self):
        pass


class RobotErrorType:
    RobotError_SUCC = 0  # No error
    RobotError_Base = 2000
    RobotError_RSHD_INIT_FAILED = RobotError_Base + 1  # Library initialization failed
    RobotError_RSHD_UNINIT = RobotError_Base + 2  # Library not initialized
    RobotError_NoLink = RobotError_Base + 3  # No link
    RobotError_Move = RobotError_Base + 4  # Arm movement error
    RobotError_ControlError = RobotError_Base + RobotEventType.RobotEvent_robotControllerError
    RobotError_LOGIN_FAILED = RobotError_Base + 5  # Arm login failed
    RobotError_NotLogin = RobotError_Base + 6  # Arm not logged in
    RobotError_ERROR_ARGS = RobotError_Base + 7  # Parameter error

    def __init__(self):
        pass


class RobotEvent:
    def __init__(self, event_type=RobotEventType.RobotEvent_None, event_code=0, event_msg=''):
        self.event_type = event_type
        self.event_code = event_code
        self.event_msg = event_msg


# noinspection SpellCheckingInspection
class RobotError(Exception):
    def __init__(self, error_type=RobotErrorType.RobotError_SUCC, error_code=0, error_msg=''):
        self.error_type = error_type
        self.error_cdoe = error_code
        self.error_msg = error_msg

    def __str__(self):
        return "RobotError type{0} code={1} msg={2}".format(self.error_type, self.error_cdoe, self.error_msg)


class RobotDefaultParameters:
    # Default dynamics parameters
    tool_dynamics = {"position": (0.0, 0.0, 0.0), "payload": 1.0, "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)}

    # Default collision grade
    collision_grade = 6

    def __init__(self):
        pass

    def __str__(self):
        return "Robot Default parameters, tool_dynamics:{0}, collision_grade:{1}".format(self.tool_dynamics,
                                                                                         self.collision_grade)


class RobotMoveTrackType:
    # Arc
    ARC_CIR = 2
    # Track
    CARTESIAN_MOVEP = 3
   # The following four third-order spline interpolation curves have discontinuous accelerations of start and end points, and are not suitable for new joint-driven versions
# cubic spline interpolation (over control point), automatically optimize trajectory running time, currently does not support pose changes
    CARTESIAN_CUBICSPLINE = 4
    # Need to set the time interval for cubic uniform B-spline interpolation (over control point), currently does not support pose changes
    CARTESIAN_UBSPLINEINTP = 5
    # Third-order spline interpolation curve
    JIONT_CUBICSPLINE = 6
    # Can be used for trajectory playback
    JOINT_UBSPLINEINTP = 7

    def __init__(self):
        pass


class RobotIOType:
    # Control cabinet IO
    ControlBox_DI = 0
    ControlBox_DO = 1
    ControlBox_AI = 2
    ControlBox_AO = 3
    # User IO
    User_DI = 4
    User_DO = 5
    User_AI = 6
    User_AO = 7

    def __init__(self):
        pass


class RobotToolIoName:
    tool_io_0 = "T_DI/O_00"
    tool_io_1 = "T_DI/O_01"
    tool_io_2 = "T_DI/O_02"
    tool_io_3 = "T_DI/O_03"

    tool_ai_0 = "T_AI_00"
    tool_ai_1 = "T_AI_01"

    def __init__(self):
        pass


class RobotUserIoName:
    # Control cabinet user DI
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

    # Control cabinet user DO
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

    # Control cabinet analog IO
    user_ai_00 = "VI0"
    user_ai_01 = "VI1"
    user_ai_02 = "VI2"
    user_ai_03 = "VI3"

    user_ao_00 = "VO0"
    user_ao_01 = "VO1"
    user_ao_02 = "VO2"
    user_ao_03 = "VO3"

    def __init__(self):
        pass


class RobotStatus:
    # Current arm stop
    Stopped = 0
    # Current arm running
    Running = 1
    # Current arm paused
    Paused = 2
    # Current arm resumed
    Resumed = 3

    def __init__(self):
        pass


class RobotRunningMode:
    # Arm simulator mode
    RobotModeSimulator = 0
    # Arm real mode
    RobotModeReal = 1

    def __init__(self):
        pass


class RobotToolPowerType:
    OUT_0V = 0
    OUT_12V = 1
    OUT_24V = 2

    def __init__(self):
        pass


class RobotToolIoAddr:
    TOOL_DIGITAL_IO_0 = 0
    TOOL_DIGITAL_IO_1 = 1
    TOOL_DIGITAL_IO_2 = 2
    TOOL_DIGITAL_IO_3 = 3

    def __init__(self):
        pass


class RobotCoordType:
    # Base coordinate system
    Robot_Base_Coordinate = 0
    # End coordinate system
    Robot_End_Coordinate = 1
    # User coordinate system
    Robot_World_Coordinate = 2

    def __init__(self):
        pass


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

    def __init__(self):
        pass


class RobotToolDigitalIoDir:
    # Input
    IO_IN = 0
    # Output
    IO_OUT = 1

    def __init__(self):
        pass


class Auboi5Robot:
    # Number of clients
    __client_count = 0

    def __init__(self):
        self.rshd = -1
        self.connected = False
        self.last_error = RobotError()
        self.last_event = RobotEvent()
        self.atTrackTargetPos = False
        Auboi5Robot.__client_count += 1

    def __del__(self):
        Auboi5Robot.__client_count -= 1
        self.uninitialize()
        logger.info("client_count={0}".format(Auboi5Robot.__client_count))

    def __str__(self):
        return "RSHD={0}, connected={1}".format(self.rshd, self.connected)

    @staticmethod
    def get_local_time():
        """"
        * FUNCTION:    get_local_time
        * DESCRIPTION: Get system current time
        * INPUTS:      无输入
        * OUTPUTS:
        * RETURNS:     输出系统当前时间字符串
        * NOTES:
        """
        return time.strftime("%b %d %Y %H:%M:%S", time.localtime(time.time()))

    def robot_event_callback(self, event):
        """"
        * FUNCTION:    robot_event_callback
        * DESCRIPTION: Arm event
        * INPUTS:      无输入
        * OUTPUTS:
        * RETURNS:     系统事件回调函数
        * NOTES:
        """
        print("event={0}".format(event))
        if event['type'] not in RobotEventType.NoError:
            self.last_error = RobotError(event['type'], event['code'], event['content'])
        else:
            self.last_event = RobotEvent(event['type'], event['code'], event['content'])

    @staticmethod
    def raise_error(error_type, error_code, error_msg):
        """"
        * FUNCTION:    raise_error
        * DESCRIPTION: Throw exception event
        * INPUTS:      无输入
        * OUTPUTS:
        * RETURNS:     无
        * NOTES:
        """
        raise RobotError(error_type, error_code, error_msg)

    def check_event(self):
        """"
        * FUNCTION:    check_event
        * DESCRIPTION: Check if arm has abnormal events
        * INPUTS:      input
        * OUTPUTS:     output
        * RETURNS:     void
        * NOTES:       如果接收到的是异常事件，则函数抛出异常事件
        """
        if self.last_error.error_type != RobotErrorType.RobotError_SUCC:
            raise self.last_error
        if self.rshd == -1 or not self.connected:
            self.raise_error(RobotErrorType.RobotError_NoLink, 0, "no socket link")

    @staticmethod
    def initialize():
        """"
        * FUNCTION:    initialize
        * DESCRIPTION: Initialize arm control library
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        result = libpyauboi5.initialize()
        if result == RobotErrorType.RobotError_SUCC:
            return RobotErrorType.RobotError_SUCC
        else:
            return RobotErrorType.RobotError_RSHD_INIT_FAILED

    @staticmethod
    def uninitialize():
        """"
        * FUNCTION:    uninitialize
        * DESCRIPTION: Reverse initialize arm control library
        * INPUTS:      input
        * OUTPUTS:     output
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        return libpyauboi5.uninitialize()

    def create_context(self):
        """"
        * FUNCTION:    create_context
        * DESCRIPTION: Create arm control context handle
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RSHD
        * NOTES:
        """
        self.rshd = libpyauboi5.create_context()
        return self.rshd

    def get_context(self):
        """"
        * FUNCTION:    get_context
        * DESCRIPTION: Get current arm control context
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     上下文句柄RSHD
        * NOTES:
        """
        return self.rshd

    def connect(self, ip='localhost', port=8899):
        """"
        * FUNCTION:    connect
        * DESCRIPTION: Link to arm server
        * INPUTS:      ip Arm server address
        *              port Port number
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        *
        * NOTES:
        """
        logger.info("ip={0}, port={1}".format(ip, port))
        if self.rshd >= 0:
            if not self.connected:
                if libpyauboi5.login(self.rshd, ip, port) == 0:
                    self.connected = True
                    time.sleep(0.5)
                    return RobotErrorType.RobotError_SUCC
                else:
                    logger.error("login failed!")
                    return RobotErrorType.RobotError_LOGIN_FAILED
            else:
                logger.info("already connected.")
                return RobotErrorType.RobotError_SUCC
        else:
            logger.error("RSHD uninitialized!!!")
            return RobotErrorType.RobotError_RSHD_UNINIT

    def disconnect(self):
        """"
         * FUNCTION:    disconnect
         * DESCRIPTION: Disconnect from arm server link
         * INPUTS:
         * OUTPUTS:
         * RETURNS:     成功返回: RobotError.RobotError_SUCC
         *              失败返回: 其他
         * NOTES:
         """
        if self.rshd >= 0 and self.connected:
            libpyauboi5.logout(self.rshd)
            self.connected = False
            time.sleep(0.5)
            return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def robot_startup(self, collision=RobotDefaultParameters.collision_grade,
                      tool_dynamics=RobotDefaultParameters.tool_dynamics):
        """
        * FUNCTION:    robot_startup
        * DESCRIPTION: Start arm
        * INPUTS:      collision: collision grade range (0~10) Default: 6
        *              tool_dynamics: kinematics parameters
        *              tool_dynamics = position, unit (m): {"position": (0.0, 0.0, 0.0),
        *                              负载，单位(kg)： "payload": 1.0,
        *                              惯量：          "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)}
        *
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.robot_startup(self.rshd, collision, tool_dynamics)
            time.sleep(0.5)
            return result
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def robot_shutdown(self):
        """
        * FUNCTION:    robot_shutdown
        * DESCRIPTION: Close arm
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.robot_shutdown(self.rshd)
            time.sleep(0.5)
            return result
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def enable_robot_event(self):
        self.check_event()
        if self.rshd >= 0 and self.connected:
            self.set_robot_event_callback(self.robot_event_callback)
            return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def init_profile(self):
        """"
        * FUNCTION:    init_profile
        * DESCRIPTION: Initialize global attributes of arm control
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        *
        * NOTES:       调用成功后，系统会自动清理掉之前设置的用户坐标系，
        *              速度，加速度等等属性
        """
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.init_global_move_profile(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_joint_maxacc(self, joint_maxacc=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)):
        """
        * FUNCTION:    set_joint_maxacc
        * DESCRIPTION: Set maximum acceleration of six joints
        * INPUTS:      joint_maxacc: maximum acceleration of six joints, unit (rad/s)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_joint_maxacc(self.rshd, joint_maxacc)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_joint_maxacc(self):
        """U_DO_00
        * FUNCTION:    get_joint_maxacc
        * DESCRIPTION: Get maximum acceleration of six joints
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 六个关节的最大加速度单位(rad/s^2)
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_joint_maxacc(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_joint_maxvelc(self, joint_maxvelc=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)):
        """
        * FUNCTION:    set_joint_maxvelc
        * DESCRIPTION: Set maximum speed of six joints
        * INPUTS:      joint_maxvelc: maximum speed of six joints, unit (rad/s)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_joint_maxvelc(self.rshd, joint_maxvelc)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_joint_maxvelc(self):
        """
        * FUNCTION:    get_joint_maxvelc
        * DESCRIPTION: Get maximum speed of six joints
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 六个关节的最大速度(rad/s)
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_joint_maxvelc(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_end_max_line_acc(self, end_maxacc=0.1):
        """
        * FUNCTION:    set_end_max_line_acc
        * DESCRIPTION: Set maximum linear acceleration of arm end
        * INPUTS:      end_maxacc: maximum linear speed of end, unit (m/s^2)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_end_max_line_acc(self.rshd, end_maxacc)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_end_max_line_acc(self):
        """
        * FUNCTION:    get_end_max_line_acc
        * DESCRIPTION: Get maximum linear acceleration of arm end
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 机械臂末端最大加速度，单位(m/s^2)
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_end_max_line_acc(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_end_max_line_velc(self, end_maxvelc=0.1):
        """
        * FUNCTION:    set_end_max_line_velc
        * DESCRIPTION: Set maximum linear speed of arm end
        * INPUTS:      end_maxacc: maximum linear speed of end, unit (m/s)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_end_max_line_velc(self.rshd, end_maxvelc)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_end_max_line_velc(self):
        """
        * FUNCTION:    get_end_max_line_velc
        * DESCRIPTION: Get maximum linear speed of arm end
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 机械臂末端最大速度，单位(m/s)
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_end_max_line_velc(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_end_max_angle_acc(self, end_maxacc=0.1):
        """
        * FUNCTION:    set_end_max_angle_acc
        * DESCRIPTION: Set maximum angular acceleration of arm end
        * INPUTS:      end_maxacc: maximum acceleration of end, unit (rad/s^2)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_end_max_angle_acc(self.rshd, end_maxacc)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_end_max_angle_acc(self):
        """
        * FUNCTION:    get_end_max_angle_acc
        * DESCRIPTION: Get maximum angular acceleration of arm end
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 机械臂末端最大角加速度，单位(m/s^2)
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_end_max_angle_acc(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_end_max_angle_velc(self, end_maxvelc=0.1):
        """
        * FUNCTION:    set_end_max_angle_velc
        * DESCRIPTION: Set maximum angular speed of arm end
        * INPUTS:      end_maxacc: maximum speed of end, unit (rad/s)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_end_max_line_velc(self.rshd, end_maxvelc)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_end_max_angle_velc(self):
        """
        * FUNCTION:    get_end_max_angle_velc
        * DESCRIPTION: Get maximum angular speed of arm end
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 机械臂末端最大速度，单位(rad/s)
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_end_max_line_velc(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def move_to_target_in_cartesian(self, pos, rpy_xyz):
        """
        * FUNCTION:    move_to_target_in_cartesian
        * DESCRIPTION: Given Cartesian coordinates and Euler angles, the arm axes move to the target position and attitude
        * INPUTS:      pos: position coordinates (x, y, z), unit (m)
        *              rpy: Euler angles (rx, ry, rz), unit (degrees)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            # degrees -> arc degrees
            rpy_xyz = [i / 180.0 * pi for i in rpy_xyz]
            # Euler angle to quaternion
            ori = libpyauboi5.rpy_to_quaternion(self.rshd, rpy_xyz)

            # Inverse calculation to get joint angles
            joint_radian = libpyauboi5.get_current_waypoint(self.rshd)

            ik_result = libpyauboi5.inverse_kin(self.rshd, joint_radian['joint'], pos, ori)

            logging.info("ik_result====>{0}".format(ik_result))
            
            # Arm moves to target position
            result = libpyauboi5.move_joint(self.rshd, ik_result["joint"])
            if result != RobotErrorType.RobotError_SUCC:
                self.raise_error(RobotErrorType.RobotError_Move, result, "move error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def move_joint(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000), issync=False):
        """
        * FUNCTION:    move_joint
        * DESCRIPTION: Arm axes move
        * INPUTS:      joint_radian: joint angles of six joints, unit (rad)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.move_joint(self.rshd, joint_radian, issync)
            if result != RobotErrorType.RobotError_SUCC:
                self.raise_error(RobotErrorType.RobotError_Move, result, "move error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def move_line(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)):
        """
        * FUNCTION:    move_line
        * DESCRIPTION: Arm moves in a straight line while maintaining the current attitude
        * INPUTS:      joint_radian: joint angles of six joints, unit (rad)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.move_line(self.rshd, joint_radian)
            if result != RobotErrorType.RobotError_SUCC:
                self.raise_error(RobotErrorType.RobotError_Move, result, "move error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def move_rotate(self, user_coord, rotate_axis, rotate_angle):
        """
        * FUNCTION:    move_rotate
        * DESCRIPTION: Maintain current position and perform rotational motion
        * INPUTS:      user_coord: user coordinate system
        *              user_coord = {'coord_type': 2,
        *               'calibrate_method': 0,
        *               'calibrate_points':
        *                   {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 
        
        *                    "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *               'tool_desc':
        *                   {"pos": (0.0, 0.0, 0.0),
        *                    "ori": (1.0, 0.0, 0.0, 0.0)}
        *               }
        *              rotate_axis: rotation axis (x,y,z) For example: (1,0,0) means rotating around the Y axis
        *              rotate_angle: rotation angle Unit (rad)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.move_rotate(self.rshd, user_coord, rotate_axis, rotate_angle)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def clear_offline_track(self):
        """
        * FUNCTION:    clear_offline_track
        * DESCRIPTION: Clear non-online trajectory motion data on server
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.clear_offline_track(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def append_offline_track_waypoint(self, waypoints):
        """
        * FUNCTION:    append_offline_track_waypoint
        * DESCRIPTION: Add non-online trajectory motion waypoints to server
        * INPUTS:      waypoints Tuple of non-online trajectory motion waypoints (can contain less than 3000 waypoints), unit: radians
        *               For example: ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    (0.0,-0.000001,-0.000001,0.000001,-0.000001, 0.0))
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.append_offline_track_waypoint(self.rshd, waypoints)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def append_offline_track_file(self, track_file):
        """
        * FUNCTION:    append_offline_track_file
        * DESCRIPTION: Add non-online trajectory motion waypoints file to server
        * INPUTS:       Full path to waypoints file, each line in the waypoints file contains joint angles of six joints (in radians), separated by commas
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.append_offline_track_file(self.rshd, track_file)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def startup_offline_track(self):
        """
        * FUNCTION:    startup_offline_track
        * DESCRIPTION: Notify server to start non-online trajectory motion
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.startup_offline_track(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def stop_offline_track(self):
        """
        * FUNCTION:    stop_offline_track
        * DESCRIPTION: Notify server to stop non-online trajectory motion
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.stop_offline_track(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def enter_tcp2canbus_mode(self):
        """
        * FUNCTION:    enter_tcp2canbus_mode
        * DESCRIPTION: Notify server to enter TCP2CANBUS transparent transmission mode
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.enter_tcp2canbus_mode(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def leave_tcp2canbus_mode(self):
        """
        * FUNCTION:    leave_tcp2canbus_mode
        * DESCRIPTION: Notify server to exit TCP2CANBUS transparent transmission mode
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.leave_tcp2canbus_mode(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_waypoint_to_canbus(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)):
        """
        * FUNCTION:    set_waypoint_to_canbus
        * DESCRIPTION: Transmit motion waypoints to CANBUS
        * INPUTS:      joint_radian: joint angles of six joints, unit (rad)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_waypoint_to_canbus(self.rshd, joint_radian)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def remove_all_waypoint(self):
        """
        * FUNCTION:    remove_all_waypoint
        * DESCRIPTION: Clear all global waypoints already set
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.remove_all_waypoint(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def add_waypoint(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)):
        """
        * FUNCTION:    add_waypoint
        * DESCRIPTION: Add global waypoints for trajectory motion
        * INPUTS:      joint_radian: joint angles of six joints, unit (rad)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.add_waypoint(self.rshd, joint_radian)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_blend_radius(self, blend_radius=0.01):
        """
        * FUNCTION:    set_blend_radius
        * DESCRIPTION: Set blending radius
        * INPUTS:      blend_radius: blending radius, unit (m)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            if 0.01 >= blend_radius <= 0.05:
                return libpyauboi5.set_blend_radius(self.rshd, blend_radius)
            else:
                logger.warn("blend radius value range must be 0.01~0.05")
                return RobotErrorType.RobotError_ERROR_ARGS
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_circular_loop_times(self, circular_count=1):
        """
        * FUNCTION:    set_circular_loop_times
        * DESCRIPTION: Set number of circular motions
        * INPUTS:      circular_count: number of circular motions
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        *
        * NOTES:       当circular_count大于0时，机械臂进行圆运动circular_count次
        *              当circular_count等于0时，机械臂进行圆弧轨迹运动
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_circular_loop_times(self.rshd, circular_count)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_user_coord(self, user_coord):
        """
        * FUNCTION:    set_user_coord
        * DESCRIPTION: Set user coordinate system
        * INPUTS:      user_coord: user coordinate system
        *              user_coord = {'coord_type': RobotCoordType.Robot_World_Coordinate,
        *               'calibrate_method': RobotCoordCalMethod.CoordCalMethod_xOy,
        *               'calibrate_points':
        *                   {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *               'tool_desc':
        *                   {"pos": (0.0, 0.0, 0.0),
        *                    "ori": (1.0, 0.0, 0.0, 0.0)}
        *               }
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_user_coord(self.rshd, user_coord)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_base_coord(self):
        """
        * FUNCTION:    set_base_coord
        * DESCRIPTION: Set base coordinate system
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_base_coord(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def check_user_coord(self, user_coord):
        """
        * FUNCTION:    check_user_coord
        * DESCRIPTION: Check if user coordinate system parameters are reasonable
        * INPUTS:      user_coord: user coordinate system
        *              user_coord = {'coord_type': 2,
        *               'calibrate_method': 0,
        *               'calibrate_points':
        *                   {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *               'tool_desc':
        *                   {"pos": (0.0, 0.0, 0.0),
        *                    "ori": (1.0, 0.0, 0.0, 0.0)}
        *               }
        * OUTPUTS:
        * RETURNS:     合理返回: RobotError.RobotError_SUCC
        *              不合理返回: 其他
        * NOTES:
        """
        return libpyauboi5.check_user_coord(self.rshd, user_coord)

    def set_relative_offset_on_base(self, relative_pos, relative_ori):
        """
        * FUNCTION:    set_relative_offset_on_base
        * DESCRIPTION: Set motion offset based on base coordinate system
        * INPUTS:      relative_pos=(x, y, z) relative displacement, unit (m)
        *              relative_ori=(w,x,y,z) relative attitude
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:            
            return libpyauboi5.set_relative_offset_on_base(self.rshd, relative_pos, relative_ori)
            
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_relative_offset_on_user(self, relative_pos, relative_ori, user_coord):
        """
        * FUNCTION:    set_relative_offset_on_user
        * DESCRIPTION: Set motion offset based on user coordinate system
        * INPUTS:      relative_pos=(x, y, z) relative displacement, unit (m)
        *              relative_ori=(w,x,y,z) target attitude
        *              user_coord: user coordinate system
        *              user_coord = {'coord_type': 2,
        *               'calibrate_method': 0,
        *               'calibrate_points':
        *                   {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *               'tool_desc':
        *                   {"pos": (0.0, 0.0, 0.0),
        *                    "ori": (1.0, 0.0, 0.0, 0.0)}
        *               }
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_relative_offset_on_user(self.rshd, relative_pos, relative_ori, user_coord)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_no_arrival_ahead(self):
        """
        * FUNCTION:    set_no_arrival_ahead
        * DESCRIPTION: Cancel pre-arrival setup
        * INPUTS:
        *
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.set_no_arrival_ahead(self.rshd)
            if result != 0:
                self.raise_error(RobotErrorType.RobotError_Move, result, "set no arrival ahead error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_arrival_ahead_distance(self, distance=0.0):
        """
        * FUNCTION:    set_arrival_ahead_distance
        * DESCRIPTION: Set pre-arrival distance in distance mode
        * INPUTS:      distance Pre-arrival distance in distance mode, unit (meters)
        *
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.set_arrival_ahead_distance(self.rshd, distance)
            if result != 0:
                self.raise_error(RobotErrorType.RobotError_Move, result, "set arrival ahead distance error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_arrival_ahead_time(self, sec=0.0):
        """
        * FUNCTION:    set_arrival_ahead_time
        * DESCRIPTION: Set pre-arrival time in time mode
        * INPUTS:      sec Pre-arrival time in time mode, unit (seconds)
        *
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.set_arrival_ahead_time(self.rshd, sec)
            if result != 0:
                self.raise_error(RobotErrorType.RobotError_Move, result, "set arrival ahead time error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def set_arrival_ahead_blend(self, distance=0.0):
        """
        * FUNCTION:    set_arrival_ahead_blend
        * DESCRIPTION: Set blending radius in distance mode
        * INPUTS:      blend Blending radius in distance mode, unit (meters)
        *
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.set_arrival_ahead_blend(self.rshd, distance)
            if result != 0:
                self.raise_error(RobotErrorType.RobotError_Move, result, "set arrival ahead blend error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def move_track(self, track):
        """
  * FUNCTION: move_track
* DESCRIPTION: Track motion
* INPUTS: track track types, including the following:
* Arc motion RobotMoveTrackType.ARC_CIR
* Track MoveRobotMoveTrackType.CARTESIAN_MOVEP
*
* OUTPUTS:
* RETURNS: Successfully returned: RobotError.RobotError_SUCC
* Failed to return: Others
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            result = libpyauboi5.move_track(self.rshd, track)
            if result != 0:
                self.raise_error(RobotErrorType.RobotError_Move, result, "move error")
            else:
                return RobotErrorType.RobotError_SUCC
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def forward_kin(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)):
        """
        * FUNCTION:    forward_kin
        * DESCRIPTION: Forward solution
        * INPUTS:      joint_radian: joint angles of six joints, unit (rad)
        * OUTPUTS:
        * RETURNS:     成功返回: Joint forward solution, result as per NOTES
        *              失败返回: None
        *
        * NOTES:       六个关节角 {'joint': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        *              位置 'pos': [-0.06403157614989634, -0.4185973810159096, 0.816883228463401],
        *              姿态 'ori': [-0.11863209307193756, 0.3820514380931854, 0.0, 0.9164950251579285]}
        """
        if self.rshd >= 0:
            return libpyauboi5.forward_kin(self.rshd, joint_radian)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def inverse_kin(self, joint_radian=(0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000),
                    pos=(0.0, 0.0, 0.0), ori=(1.0, 0.0, 0.0, 0.0)):
        """
        * FUNCTION:    forward_kin
        * DESCRIPTION: Inverse solution
        * INPUTS:      joint_radian: joint angles of six joints at starting point, unit (rad)
        *              pos Position (x, y, z) in unit (m)
        *              ori Pose (w, x, y, z)
        * OUTPUTS:
        * RETURNS:     成功返回: Joint forward solution, result as per NOTES
        *              失败返回: None
        *
        * NOTES:       六个关节角 {'joint': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        *              位置 'pos': [-0.06403157614989634, -0.4185973810159096, 0.816883228463401],
        *              姿态 'ori': [-0.11863209307193756, 0.3820514380931854, 0.0, 0.9164950251579285]}
        """
        if self.rshd >= 0:
            return libpyauboi5.inverse_kin(self.rshd, joint_radian, pos, ori)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def base_to_user(self, pos, ori, user_coord, user_tool):
        """
        * FUNCTION:    base_to_user
        * DESCRIPTION: Convert user coordinate system to base coordinate system
        * INPUTS:      pos: position in base coordinate system (x, y, z) in unit (m)
        *              ori: attitude in base coordinate system (w, x, y, z)
        *              user_coord: user coordinate system
        *              user_coord = {'coord_type': 2,
        *               'calibrate_method': 0,
        *               'calibrate_points':
        *                   {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *               'tool_desc':
        *                   {"pos": (0.0, 0.0, 0.0),
        *                    "ori": (1.0, 0.0, 0.0, 0.0)}
        *               }
        *               user_tool User tool description
        *               user_tool={"pos": (x, y, z), "ori": (w, x, y, z)}
        * OUTPUTS:
        * RETURNS:     成功返回: 返回位置和姿态{"pos": (x, y, z), "ori": (w, x, y, z)}
        *              失败返回: None
        *
        * NOTES:
        """
        return libpyauboi5.base_to_user(self.rshd, pos, ori, user_coord, user_tool)

    def user_to_base(self, pos, ori, user_coord, user_tool):
        """
        * FUNCTION:    user_to_base
        * DESCRIPTION: Convert user coordinate system to base coordinate system
        * INPUTS:      pos: position in user coordinate system (x, y, z) in unit (m)
        *              ori: attitude in user coordinate system (w, x, y, z)
        *              user_coord: user coordinate system
        *              user_coord = {'coord_type': 2,
        *               'calibrate_method': 0,
        *               'calibrate_points':
        *                   {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        *                    "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
        *               'tool_desc':
        *                   {"pos": (0.0, 0.0, 0.0),
        *                    "ori": (1.0, 0.0, 0.0, 0.0)}
        *               }
        *               user_tool User tool description
        *               user_tool={"pos": (x, y, z), "ori": (w, x, y, z)}
        * OUTPUTS:
        * RETURNS:     成功返回: 返回位置和姿态{"pos": (x, y, z), "ori": (w, x, y, z)}
        *              失败返回: None
        *
        * NOTES:
        """
        return libpyauboi5.user_to_base(self.rshd, pos, ori, user_coord, user_tool)

    def base_to_base_additional_tool(self, flange_pos, flange_ori, user_tool):
        """
        * FUNCTION:    base_to_base_additional_tool
        * DESCRIPTION: Convert base coordinate system to base coordinate system to get position and attitude of tool end
        * INPUTS:      pos: position of flange center in base coordinate system (x, y, z) in unit (m)
        *              ori: attitude information in base coordinate system (w, x, y, z)
        *              user_tool User tool description
        *              user_tool={"pos": (x, y, z), "ori": (w, x, y, z)}
        * OUTPUTS:
        * RETURNS:     成功返回: 返回基于基座标系的工具末端位置位置和姿态信息{"pos": (x, y, z), "ori": (w, x, y, z)}
        *              失败返回: None
        *
        * NOTES:
        """
        return libpyauboi5.base_to_base_additional_tool(self.rshd, flange_pos, flange_ori, user_tool)

    def rpy_to_quaternion(self, rpy):
        """
        * FUNCTION:    rpy_to_quaternion
        * DESCRIPTION: Euler angle to quaternion
        * INPUTS:      rpy: Euler angles (rx, ry, rz), unit (m)
        * OUTPUTS:
        * RETURNS:     成功返回: 四元数结果，结果为详见NOTES
        *              失败返回: None
        *
        * NOTES:       四元素(w, x, y, z)
        """
        if self.rshd >= 0:
            return libpyauboi5.rpy_to_quaternion(self.rshd, rpy)
        else:
            logger.warn("RSHD uninitialized !!!")
            return None

    def quaternion_to_rpy(self, ori):
        """
        * FUNCTION:    quaternion_to_rpy
        * DESCRIPTION: Quaternion to Euler angle
        * INPUTS:      四元数(w, x, y, z)
        * OUTPUTS:
        * RETURNS:     成功返回: 欧拉角结果，结果为详见NOTES
        *              失败返回: None
        *
        * NOTES:       rpy: Euler angles (rx, ry, rz), unit (m)
        """
        if self.rshd >= 0:
            return libpyauboi5.quaternion_to_rpy(self.rshd, ori)
        else:
            logger.warn("RSHD uninitialized !!!")
            return None

    def set_tool_end_param(self, tool_end_param):
        """
        * FUNCTION:    set_tool_end_param
        * DESCRIPTION: Set tool end parameters
        * INPUTS:      末端工具参数： tool_end_param={"pos": (x, y, z), "ori": (w, x, y, z)}
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        *
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_end_param(self.rshd, tool_end_param)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_none_tool_dynamics_param(self):
        """
        * FUNCTION:    set_none_tool_dynamics_param
        * DESCRIPTION: Set dynamics parameters without tool
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        *
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_none_tool_dynamics_param(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_tool_dynamics_param(self, tool_dynamics):
        """
        * FUNCTION:    set_tool_end_param
        * DESCRIPTION: Set dynamics parameters of tool
        * INPUTS:      tool_dynamics: kinematics parameters
        *              tool_dynamics = position, unit (m): {"position": (0.0, 0.0, 0.0),
        *                              负载，单位(kg)： "payload": 1.0,
        *                              惯量：          "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)}
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        *
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_dynamics_param(self.rshd, tool_dynamics)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def get_tool_dynamics_param(self):
        """
        * FUNCTION:    get_tool_dynamics_param
        * DESCRIPTION: Get tool end parameters
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 运动学参数
        *              tool_dynamics = position, unit (m): {"position": (0.0, 0.0, 0.0),
        *                              负载，单位(kg)： "payload": 1.0,
        *                              惯量：          "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)}
        *
        *              失败返回: None
        *
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_tool_dynamics_param(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_none_tool_kinematics_param(self):
        """
        * FUNCTION:    set_none_tool_kinematics_param
        * DESCRIPTION: Set kinematics parameters without tool
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        *
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_none_tool_kinematics_param(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_tool_kinematics_param(self, tool_end_param):
        """
        * FUNCTION:    set_tool_kinematics_param
        * DESCRIPTION: Set kinematics parameters of tool
        * INPUTS:      末端工具参数： tool_end_param={"pos": (x, y, z), "ori": (w, x, y, z)}
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        *
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_kinematics_param(self.rshd, tool_end_param)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def get_tool_kinematics_param(self):
        """
        * FUNCTION:     set_tool_kinematics_param
        * DESCRIPTION: Set kinematics parameters of tool
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 工具的运动学参数
        *               tool_end_param={"pos": (x, y, z), "ori": (w, x, y, z)}
        *
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_tool_kinematics_param(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def move_stop(self):
        """
        * FUNCTION:    move_stop
        * DESCRIPTION: Stop arm motion
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.move_stop(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def move_pause(self):
        """
        * FUNCTION:    move_pause
        * DESCRIPTION: Pause arm motion
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.move_pause(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def move_continue(self):
        """
        * FUNCTION:    move_continue
        * DESCRIPTION: Resume arm motion after pause
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.move_continue(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def collision_recover(self):
        """
        * FUNCTION:    collision_recover
        * DESCRIPTION: Arm collision recovery
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.collision_recover(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_robot_state(self):
        """
        * FUNCTION:    get_robot_state
        * DESCRIPTION: Get current state of arm
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: Current state of arm
        *              机械臂当前停止:RobotStatus.Stopped
        *              机械臂当前运行:RobotStatus.Running
        *              机械臂当前暂停:RobotStatus.Paused
        *              机械臂当前恢复:RobotStatus.Resumed
        *
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_robot_state(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def enter_reduce_mode(self):
        """
        * FUNCTION:    enter_reduce_mode
        * DESCRIPTION: Set arm motion to reduced mode
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.enter_reduce_mode(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin   

    def exit_reduce_mode(self):
        """
        * FUNCTION:    exit_reduce_mode
        * DESCRIPTION: Set arm motion to exit reduced mode
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.exit_reduce_mode(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin   

    def project_startup(self):
        """
        * FUNCTION:    project_startup
        * DESCRIPTION: Notify arm project to start, server also starts to detect safety IO
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.project_startup(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin     

    def rs_project_stop(self):
        """
        * FUNCTION:    rs_project_stop
        * DESCRIPTION: Notify arm project to stop, server stops to detect safety IO
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.rs_project_stop(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin                                   

    def set_work_mode(self, mode=0):
        """
        * FUNCTION:    set_work_mode
        * DESCRIPTION: Set server work mode of arm
        * INPUTS:      mode: server work mode
        *               Arm simulator mode: RobotRunningMode.RobotModeSimulator
        *               Arm real mode: RobotRunningMode.RobotModeReal
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_work_mode(self.rshd, mode)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def get_work_mode(self):
        """
        * FUNCTION:    set_work_mode
        * DESCRIPTION: Get current server work mode of arm
        * INPUTS:      mode: server work mode
        *               Arm simulator mode: RobotRunningMode.RobotModeSimulator
        *               Arm real mode: RobotRunningMode.RobotModeReal
        * OUTPUTS:
        * RETURNS:     成功返回: Server work mode
        *               Arm simulator mode: RobotRunningMode.RobotModeSimulator
        *               Arm real mode: RobotRunningMode.RobotModeReal
        *
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_work_mode(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_collision_class(self, grade=6):
        """
        * FUNCTION:    set_collision_class
        * DESCRIPTION: Set arm collision grade
        * INPUTS:      grade: collision grade, collision grade range (0~10)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_collision_class(self.rshd, grade)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def is_have_real_robot(self):
        """
        * FUNCTION:    is_have_real_robot
        * DESCRIPTION: Get whether real arm has been linked
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 1：存在 0：不存在
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.is_have_real_robot(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def is_online_mode(self):
        """
        * FUNCTION:    is_online_mode
        * DESCRIPTION: Whether arm is running in online mode
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 1：在 0：不在
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.is_online_mode(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def is_online_master_mode(self):
        """
        * FUNCTION:    is_online_master_mode
        * DESCRIPTION: Whether arm is running in online master mode
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 1：主模式 0：从模式
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.is_online_master_mode(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def get_joint_status(self):
        """
        * FUNCTION:    get_joint_status
        * DESCRIPTION: Get current state information of arm
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 返回六个关节状态，包括：电流，电压，温度
        *              {'joint1': {'current': 电流(毫安), 'voltage': 电压(伏特), 'temperature': 温度(摄氏度)},
        *              'joint2': {'current': 0, 'voltage': 0.0, 'temperature': 0},
        *              'joint3': {'current': 0, 'voltage': 0.0, 'temperature': 0},
        *              'joint4': {'current': 0, 'voltage': 0.0, 'temperature': 0},
        *              'joint5': {'current': 0, 'voltage': 0.0, 'temperature': 0},
        *              'joint6': {'current': 0, 'voltage': 0.0, 'temperature': 0}}
        *
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_joint_status(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def get_current_waypoint(self):
        """
        * FUNCTION:    get_current_waypoint
        * DESCRIPTION: Get current position information of arm
        * INPUTS:      grade: collision grade, collision grade range (0~10)
        * OUTPUTS:
        * RETURNS:     成功返回: 关节位置信息，结果为详见NOTES
        *              失败返回: None
        *
        * NOTES:       六个关节角 {'joint': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        *              位置 'pos': [-0.06403157614989634, -0.4185973810159096, 0.816883228463401],
        *              姿态 'ori': [-0.11863209307193756, 0.3820514380931854, 0.0, 0.9164950251579285]}
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_current_waypoint(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def get_board_io_config(self, io_type=RobotIOType.User_DO):
        """
        * FUNCTION:    get_board_io_config
        * DESCRIPTION:
        * INPUTS:      io_type：IO类型：RobotIOType
        * OUTPUTS:
        * RETURNS:     成功返回: IO配置
        *               [{"id": ID
        *                 "name": "IO名字"
        *                 "addr": IO地址
        *                 "type": IO类型
        *                 "value": IO当前值},]
        *
        *              失败返回: None
        * NOTES:       RobotIOType详见class RobotIOType
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_board_io_config(self.rshd, io_type)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def get_board_io_status(self, io_type, io_name):
        """
        * FUNCTION:    get_board_io_status
        * DESCRIPTION: Get IO status
        * INPUTS:      io_type: type
        *              io_name: name RobotUserIoName.user_dx_xx
        * OUTPUTS:
        * RETURNS:     成功返回: IO状态 double数值(数字IO，返回0或1,模拟IO返回浮点数）
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_board_io_status(self.rshd, io_type, io_name)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_board_io_status(self, io_type, io_name, io_value):
        """
        * FUNCTION:    set_board_io_status
        * DESCRIPTION: Set IO status
        * INPUTS:      io_type: type
        *              io_name: name RobotUserIoName.user_dx_xx
        *              io_value: status value (digital IO returns 0 or 1, analog IO returns floating point number)
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        #self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_board_io_status(self.rshd, io_type, io_name, io_value)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def set_tool_power_type(self, power_type=RobotToolPowerType.OUT_0V):
        """
        * FUNCTION:    set_tool_power_type
        * DESCRIPTION: Set power type of tool end
        * INPUTS:      power_type: power type
        *              RobotToolPowerType.OUT_0V
        *              RobotToolPowerType.OUT_12V
        *              RobotToolPowerType.OUT_24V
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_power_type(self.rshd, power_type)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def get_tool_power_type(self):
        """
        * FUNCTION:    get_tool_power_type
        * DESCRIPTION: Get power type of tool end
        * INPUTS:      power_type: power type

        * OUTPUTS:
        * RETURNS:     成功返回: 电源类型，包括如下：
        *                       RobotToolPowerType.OUT_0V
        *                       RobotToolPowerType.OUT_12V
        *                       RobotToolPowerType.OUT_24V
        *
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_tool_power_type(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_tool_io_type(self, io_addr=RobotToolIoAddr.TOOL_DIGITAL_IO_0,
                         io_type=RobotToolDigitalIoDir.IO_OUT):
        """
        * FUNCTION:    set_tool_io_type
        * DESCRIPTION: Set digital IO type of tool end
        * INPUTS:      io_addr: tool end IO address 详见class RobotToolIoAddr
        *              io_type: tool end IO type 详见class RobotToolDigitalIoDir

        * OUTPUTS:
        * RETURNS:     成功返回: IO类型，包括如下：
        *                       RobotToolDigitalIoDir.IO_IN
        *                       RobotToolDigitalIoDir.IO_OUT
        *
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_io_type(self.rshd, io_addr, io_type)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def get_tool_power_voltage(self):
        """
        * FUNCTION:    get_tool_power_voltage
        * DESCRIPTION: Get voltage value of tool end
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: 返回电压数值，单位（伏特）
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_tool_power_voltage(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def get_tool_io_status(self, io_name):
        """
        * FUNCTION:    get_tool_io_status
        * DESCRIPTION: Get status of tool end IO
        * INPUTS:      io_name: IO name

        * OUTPUTS:
        * RETURNS:     成功返回: 返回工具端IO状态
        *
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_tool_io_status(self.rshd, io_name)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_tool_io_status(self, io_name, io_status):
        """
        * FUNCTION:    set_tool_io_status
        * DESCRIPTION: Set status of tool end IO
        * INPUTS:      io_name：工具端IO名称
        *              io_status: tool end IO status: value range (0 or 1)

        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_tool_do_status(self.rshd, io_name, io_status)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED

    def startup_excit_traj_track(self, track_file='', track_type=0, subtype=0):
        """
        * FUNCTION:    startup_excit_traj_track
        * DESCRIPTION: Notify server to start identifying trajectory motion
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.startup_excit_traj_track(self.rshd, track_file, track_type, subtype)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_NotLogin

    def get_dynidentify_results(self):
        """
        * FUNCTION:    get_dynidentify_results
        * DESCRIPTION: Get identification results
        * INPUTS:
        * OUTPUTS:
        * RETURNS:     成功返回: Identification result array
        *              失败返回: None
        * NOTES:
        """
        self.check_event()
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.get_dynidentify_results(self.rshd)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return None

    def set_robot_event_callback(self, callback):
        """
        * FUNCTION:    set_robot_event_callback
        * DESCRIPTION: Set callback function for arm events
        * INPUTS:      callback: name of callback function
        * OUTPUTS:
        * RETURNS:     成功返回: RobotError.RobotError_SUCC
        *              失败返回: 其他
        * NOTES:
        """
        if self.rshd >= 0 and self.connected:
            return libpyauboi5.set_robot_event_callback(self.rshd, callback)
        else:
            logger.warn("RSHD uninitialized or not login!!!")
            return RobotErrorType.RobotError_LOGIN_FAILED


# Test function
def test(test_count):
    # Initialize logger
    logger_init()

    # Start testing
    logger.info("{0} test beginning...".format(Auboi5Robot.get_local_time()))

    # System initialization
    Auboi5Robot.initialize()

    # Create arm control class
    robot = Auboi5Robot()

    # Create context
    handle = robot.create_context()

    # Print context
    logger.info("robot.rshd={0}".format(handle))

    try:

        # Link to server
        # ip = 'localhost'
        ip = '192.168.11.128'

        port = 8899
        result = robot.connect(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("connect server{0}:{1} failed.".format(ip, port))
        else:
            # # Re-power
            #robot.robot_shutdown()
            #
            # # Power on
            robot.robot_startup()
            #
            # # Set collision grade
            robot.set_collision_class(7)

            # Set tool power to 12V
            # robot.set_tool_power_type(RobotToolPowerType.OUT_12V)

            # Set tool IO_0 to output
            #robot.set_tool_io_type(RobotToolIoAddr.TOOL_DIGITAL_IO_0, RobotToolDigitalIoDir.IO_OUT)

            # Get status of tool IO_0
            #tool_io_status = robot.get_tool_io_status(RobotToolIoName.tool_io_0)
            #logger.info("tool_io_0={0}".format(tool_io_status))

            # Set status of tool IO_0
            #robot.set_tool_io_status(RobotToolIoName.tool_io_0, 1)


            # Get control cabinet user DO
            #io_config = robot.get_board_io_config(RobotIOType.User_DO)

            # Output DO configuration
            #logger.info(io_config)

            # Whether arm is running in online mode
            #logger.info("robot online mode is {0}".format(robot.is_online_mode()))

            # Loop testing
            while test_count > 0:
                test_count -= 1

                joint_status = robot.get_joint_status()
                logger.info("joint_status={0}".format(joint_status))

                # Initialize global configuration file
                robot.init_profile()

                # Set maximum joint acceleration
                robot.set_joint_maxacc((0.5, 0.5, 0.5, 0.5, 0.5, 0.5))

                # Set maximum joint speed
                robot.set_joint_maxvelc((0.5, 0.5, 0.5, 0.5, 0.5, 0.5))

                joint_radian = (0.541678, 0.225068, -0.948709, 0.397018, -1.570800, 0.541673)
                logger.info("move joint to {0}".format(joint_radian))

                robot.move_joint(joint_radian)

                # Get maximum joint acceleration
                logger.info(robot.get_joint_maxacc())

                # Forward solution test
                fk_ret = robot.forward_kin((-0.000003, -0.127267, -1.321122, 0.376934, -1.570796, -0.000008))
                logger.info(fk_ret)

                # Inverse solution
                joint_radian = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
                ik_result = robot.inverse_kin(joint_radian, fk_ret['pos'], fk_ret['ori'])
                logger.info(ik_result)

                # Arm axis 1
                joint_radian = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
                logger.info("move joint to {0}".format(joint_radian))
                robot.move_joint(joint_radian)

                # Arm axis 2
                joint_radian = (0.541678, 0.225068, -0.948709, 0.397018, -1.570800, 0.541673)
                logger.info("move joint to {0}".format(joint_radian))
                robot.move_joint(joint_radian)

                # Arm axis 3
                joint_radian = (-0.000003, -0.127267, -1.321122, 0.376934, -1.570796, -0.000008)
                logger.info("move joint to {0}".format(joint_radian))
                robot.move_joint(joint_radian)

                # Set maximum linear acceleration of arm end (m/s)
                robot.set_end_max_line_acc(0.1)

                # Get maximum linear acceleration of arm end (m/s)
                robot.set_end_max_line_velc(0.2)

                # Clear all global waypoints already set
                robot.remove_all_waypoint()

                # Add global waypoint 1, for trajectory motion
                joint_radian = (-0.07618534972551196, 0.5119034115471475, -1.6027922611478171, -0.530740505817827, -1.5436807868161575, -0.08034752365920544)
                robot.move_joint(joint_radian)
                robot.remove_all_waypoint()
                robot.add_waypoint(joint_radian)

                # Add global waypoint 2, for trajectory motion
                joint_radian = (-0.3742805173826728, 0.10436873450049867, -2.1719984972293678, -0.685032254269936, -1.5487447898276492, -0.37847911633785547)
                robot.add_waypoint(joint_radian)

                # Add global waypoint 3, for trajectory motion
                joint_radian = (0.15257591526447342, 0.20142028083176625, -2.0572652820455337, -0.6812332833535826, -1.54140746055885, 0.1484920368010244)
                robot.add_waypoint(joint_radian)

                # Set number of circular motions
                robot.set_circular_loop_times(3)

                # Circular motion
                logger.info("move_track ARC_CIR")
                robot.move_track(RobotMoveTrackType.ARC_CIR)

                # Clear all global waypoints already set
                robot.remove_all_waypoint()

                # Arm axes move back to 0 position
                joint_radian = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
                logger.info("move joint to {0}".format(joint_radian))
                robot.move_joint(joint_radian)

            # Disconnect from server link
            robot.disconnect()

    except RobotError as e:
        logger.error("{0} robot Event:{1}".format(robot.get_local_time(), e))


    finally:
        # Disconnect from server link
        if robot.connected:
            # Shut down arm
            robot.robot_shutdown()
            # Disconnect from arm link
            robot.disconnect()
        # Release library resources
        Auboi5Robot.uninitialize()
        logger.info("{0} test completed.".format(Auboi5Robot.get_local_time()))


def step_test():
    # Initialize logger
    logger_init()

    # Start testing
    logger.info("{0} test beginning...".format(Auboi5Robot.get_local_time()))

    # System initialization
    Auboi5Robot.initialize()

    # Create arm control class
    robot = Auboi5Robot()

    # Create context
    handle = robot.create_context()

    # Print context
    logger.info("robot.rshd={0}".format(handle))

    try:

        # Link to server
        ip = 'localhost'
        port = 8899
        result = robot.connect(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("connect server{0}:{1} failed.".format(ip, port))
        else:
            # Re-power
            robot.robot_shutdown()

            # Power on
            robot.robot_startup()

            # Set collision grade
            robot.set_collision_class(7)

            # # Initialize global configuration file
            # robot.init_profile()
            #
            # # logger.info(robot.get_board_io_config(RobotIOType.User_DI))
            #
            # # Get current position
            # logger.info(robot.get_current_waypoint())
            #
            # joint_radian = (0, 0, 0, 0, 0, 0)
            # # Move to initial position
            # robot.move_joint(joint_radian)
            #
            # # Move 0.1 mm along Z axis
            # current_pos = robot.get_current_waypoint()
            #
            # current_pos['pos'][2] -= 0.001
            #
            # ik_result = robot.inverse_kin(current_pos['joint'], current_pos['pos'], current_pos['ori'])
            # logger.info(ik_result)
            #
            # # joint_radian = (0.541678, 0.225068, -0.948709, 0.397018, -1.570800, 0.541673)
            # # logger.info("move joint to {0}".format(joint_radian))
            # # robot.move_joint(joint_radian)
            #
            # robot.move_line(ik_result['joint'])

            # Disconnect from server link
            robot.disconnect()

    except RobotError as e:
        logger.error("robot Event:{0}".format(e))

    finally:
        # Disconnect from server link
        if robot.connected:
            # Disconnect from arm link
            robot.disconnect()
        # Release library resources
        Auboi5Robot.uninitialize()
        logger.info("{0} test completed.".format(Auboi5Robot.get_local_time()))


# def excit_traj_track_test():
#     # Initialize logger
#     logger_init()

#     # Start testing
#     logger.info("{0} test beginning...".format(Auboi5Robot.get_local_time()))

#     # System initialization
#     Auboi5Robot.initialize()

#     # Create arm control class
#     robot = Auboi5Robot()

#     # Create context
#     handle = robot.create_context()

#     # Print context
#     logger.info("robot.rshd={0}".format(handle))

#     try:

#         # Link to server
#         ip = 'localhost'
#         port = 8899
#         result = robot.connect(ip, port)

#         if result != RobotErrorType.RobotError_SUCC:
#             logger.info("connect server{0}:{1} failed.".format(ip, port))
#         else:

#             # Re-power
#             # robot.robot_shutdown()

#             # Power on
#             # robot.robot_startup()

#             # Set collision grade
#             # robot.set_collision_class(7)

#             joint_radian = (0, 0, 0, 0, 0, 0)
#             # Move to initial position
#             robot.move_joint(joint_radian)

#             logger.info("starup excit traj track....")

#             # Start identifying trajectory
#             #robot.startup_excit_traj_track("dynamics_exciting_trajectories/excitTraj1.offt", 1, 0)

#             # Wait for 2 seconds for identification results
#             #time.sleep(5)

#             # Get identification results
#             dynidentify_ret = robot.get_dynidentify_results()
#             logger.info("dynidentify result={0}".format(dynidentify_ret))
#             for i in range(0,54):
# 	            dynidentify_ret[i] = dynidentify_ret[i]/1024.0
#             logger.info("dynidentify result={0}".format(dynidentify_ret))

#             # Disconnect from server link
#             robot.disconnect()

#     except RobotError as e:
#         logger.error("robot Event:{0}".format(e))


#     finally:
#         # Disconnect from server link
#         if robot.connected:
#             # Disconnect from arm link
#             robot.disconnect()
#         # Release library resources
#         Auboi5Robot.uninitialize()


def move_rotate_test():
    # Initialize logger
    logger_init()

    # Start testing
    logger.info("{0} test beginning...".format(Auboi5Robot.get_local_time()))

    # System initialization
    Auboi5Robot.initialize()

    # Create arm control class
    robot = Auboi5Robot()

    # Create context
    handle = robot.create_context()

    # Print context
    logger.info("robot.rshd={0}".format(handle))

    try:

        # Link to server
        ip = 'localhost'
        port = 8899
        result = robot.connect(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("connect server{0}:{1} failed.".format(ip, port))
        else:

            # Re-power
            # robot.robot_shutdown()

            # Power on
            # robot.robot_startup()

            # Set collision grade
            # robot.set_collision_class(7)

            # joint_radian = (1, 0, 0, 0, 0, 0)
            # # Move to initial position
            # robot.move_joint(joint_radian)

            joint_radian = (0.541678, 0.225068, -0.948709, 0.397018, -1.570800, 0.541673)
            logger.info("move joint to {0}".format(joint_radian))
            robot.move_joint(joint_radian)

            # Get current position
            current_pos = robot.get_current_waypoint()

            # Tool rotation axis vector (relative to flange, so x,y,z need to be measured to get 0.1 meters)
            tool_pos_on_end = (0, 0, 0.10)

            # Tool attitude (w,x,y,z relative to flange, default information if not known)
            tool_ori_on_end = (1, 0, 0, 0)

            tool_desc = {"pos": tool_pos_on_end, "ori": tool_ori_on_end}

            # Get position of tool end relative to base coordinate system
            tool_pos_on_base = robot.base_to_base_additional_tool(current_pos['pos'],
                                                                  current_pos['ori'],
                                                                  tool_desc)

            logger.info("current_pos={0}".format(current_pos['pos'][0]))

            logger.info("tool_pos_on_base={0}".format(tool_pos_on_base['pos'][0]))

            # Translate tool rotation axis vector to base coordinate system (rotation direction follows right-hand rule)
            rotate_axis = map(lambda a, b: a - b, tool_pos_on_base['pos'], current_pos['pos'])

            logger.info("rotate_axis={0}".format(rotate_axis))

            # Default coordinate system uses base coordinate system (default values are fine)
            user_coord = {'coord_type': RobotCoordType.Robot_Base_Coordinate,
                          'calibrate_method': 0,
                          'calibrate_points':
                              {"point1": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                               "point2": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                               "point3": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)},
                          'tool_desc':
                              {"pos": (0.0, 0.0, 0.0),
                               "ori": (1.0, 0.0, 0.0, 0.0)}
                          }

            # Call rotation axis interface, last parameter is rotation angle (radians)
            robot.move_rotate(user_coord, rotate_axis, 1)

            # Disconnect from server link
            robot.disconnect()

    except RobotError as e:
        logger.error("robot Event:{0}".format(e))

    finally:
        # Disconnect from server link
        if robot.connected:
            # Disconnect from arm link
            robot.disconnect()
        # Release library resources
        Auboi5Robot.uninitialize()


def test_rsm():
    # Initialize logger
    logger_init()

    # Start testing
    logger.info("{0} test beginning...".format(Auboi5Robot.get_local_time()))

    # System initialization
    Auboi5Robot.initialize()

    # Create arm control class
    robot = Auboi5Robot()

    # Create context
    handle = robot.create_context()

    # Print context
    logger.info("robot.rshd={0}".format(handle))

    try:

        # Link to server
        #ip = 'localhost'
        ip = '192.168.11.128'
        port = 8899
        result = robot.connect(ip, port)
        
        #robot.enable_robot_event()

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("connect server{0}:{1} failed.".format(ip, port))
        else:

            # robot.move_pause()

            #joint_radian = (0, 0, 0, 0, 0, 0)
            # Move to initial position
            #robot.move_joint(joint_radian)

            while True:
                time.sleep(0.05)

                rel = robot.set_board_io_status(RobotIOType.User_DO, RobotUserIoName.user_do_02, 0)
                print(rel)
                print("++++++++++++++++++++++++")
                #result = robot.get_board_io_status(RobotIOType.User_DO, RobotUserIoName.user_do_02)
                #print(result)
                # print("*********************************")

                time.sleep(2)
                # rel1 = robot.set_board_io_status(RobotIOType.User_DO, RobotUserIoName.user_do_02, 0)
                # print(rel1)
                # print("++++++++++++++++++++++++")

            # Disconnect from server link
            robot.disconnect()

    except RobotError as e:
        logger.error("robot Event:{0}".format(e))


    finally:
        # Disconnect from server link
        if robot.connected:
            # Disconnect from arm link
            robot.disconnect()
        # Release library resources
        Auboi5Robot.uninitialize()


class GetRobotWaypointProcess(Process):
    def __init__(self):
        Process.__init__(self)
        self.isRunWaypoint = False
        self._waypoints = None


    def startMoveList(self, waypoints):
        if self.isRunWaypoint == True:
            return False
        else:
            self._waypoints = waypoints

    def run(self):
        # Initialize logger
        logger_init()

        # Start testing
        logger.info("{0} test beginning...".format(Auboi5Robot.get_local_time()))

        # System initialization
        Auboi5Robot.initialize()

        # Create arm control class
        robot = Auboi5Robot()

        # Create context
        handle = robot.create_context()

        # Print context
        logger.info("robot.rshd={0}".format(handle))

        try:
            # Link to server
            #ip = 'localhost'
            ip = '192.168.11.128'
            port = 8899
            result = robot.connect(ip, port)

            if result != RobotErrorType.RobotError_SUCC:
                logger.info("connect server{0}:{1} failed.".format(ip, port))
            else:
                while True:
                    time.sleep(2)
                    waypoint = robot.get_current_waypoint()
                    print(waypoint)
                    print("----------------------------------------------")


                    # Disconnect from server link
                robot.disconnect()

        except RobotError as e:
            logger.error("robot Event:{0}".format(e))

        except KeyboardInterrupt:
            # Disconnect from server link
            if robot.connected:
                # Disconnect from arm link
                robot.disconnect()
            # Release library resources
            Auboi5Robot.uninitialize()
            print("get  waypoint run end-------------------------")

def runWaypoint(queue):
    while True:
        # while not queue.empty():
        print(queue.get(True))


def test_process_demo():
    # Initialize logger
    logger_init()

    # Start testing
    logger.info("{0} test beginning...".format(Auboi5Robot.get_local_time()))

    # System initialization
    Auboi5Robot.initialize()

    # Create arm control class
    robot = Auboi5Robot()

    # Create context
    handle = robot.create_context()

    # Print context
    logger.info("robot.rshd={0}".format(handle))

    try:

        # time.sleep(0.2)
        # process_get_robot_current_status = GetRobotWaypointProcess()
        # process_get_robot_current_status.daemon = True
        # process_get_robot_current_status.start()
        # time.sleep(0.2)

        queue = Queue()

        p = Process(target=runWaypoint, args=(queue,))
        p.start()
        time.sleep(5)
        print("process started.")

        # Link to server
        #ip = 'localhost'
        ip = '192.168.11.128'
        port = 8899
        result = robot.connect(ip, port)

        if result != RobotErrorType.RobotError_SUCC:
            logger.info("connect server{0}:{1} failed.".format(ip, port))
        else:
            robot.enable_robot_event()
            robot.init_profile()
            joint_maxvelc = (2.596177, 2.596177, 2.596177, 3.110177, 3.110177, 3.110177)
            joint_maxacc = (17.308779/2.5, 17.308779/2.5, 17.308779/2.5, 17.308779/2.5, 17.308779/2.5, 17.308779/2.5)
            robot.set_joint_maxacc(joint_maxacc)
            robot.set_joint_maxvelc(joint_maxvelc)
            robot.set_arrival_ahead_blend(0.05)
            while True:
                time.sleep(1)

                joint_radian = (0.541678, 0.225068, -0.948709, 0.397018, -1.570800, 0.541673)
                robot.move_joint(joint_radian, True)
                
                print("finished0")
                joint_radian = (55.5/180.0*pi, -20.5/180.0*pi, -72.5/180.0*pi, 38.5/180.0*pi, -90.5/180.0*pi, 55.5/180.0*pi)
                robot.move_joint(joint_radian, True)
                time.sleep(3)
                print("finished1")
                joint_radian = (0, 0, 0, 0, 0, 0)
                robot.move_joint(joint_radian, True)
                print("-----------------------------")

                queue.put(joint_radian)

                # time.sleep(5)

                # process_get_robot_current_status.test()

                # print("-----------------------------")

                # Disconnect from server link
            robot.disconnect()

    except KeyboardInterrupt:
        robot.move_stop()

    except RobotError as e:
        logger.error("robot Event:{0}".format(e))



    finally:
        # Disconnect from server link
        if robot.connected:
            # Disconnect from arm link
            robot.disconnect()
        # Release library resources
        Auboi5Robot.uninitialize()
        print("run end-------------------------")

if __name__ == '__main__':
    test_process_demo()
    logger.info("test completed")



















