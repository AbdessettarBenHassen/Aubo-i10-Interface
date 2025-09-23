#!/usr/bin/env python2
# coding: utf-8
import libpyauboi5
import socket
import json
import time
import threading
import logging
import ctypes, os
import json
import os
import Queue as queue  # at top with other imports
robot_lib = ctypes.CDLL("/root/桌面/Aubo/Aubo-i10-Interface/libteachwrapper.so")
robot_lib.robot_login.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
robot_lib.robot_login.restype = ctypes.c_int
robot_lib.joint_move.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_bool]
robot_lib.joint_move.restype = ctypes.c_int
robot_lib.move_line.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_bool]
robot_lib.move_line.restype = ctypes.c_int
robot_lib.robot_startup.argtypes = []
robot_lib.robot_startup.restype = ctypes.c_int
CONFIG_FILE = os.path.expanduser("~/.robot_config.json")
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"ip": "127.0.0.1", "tool": ""}
# Example usage
cfg = load_config()
robot_ip = cfg.get("ip", "192.168.23.129")  # fallback if not set
robot_port = 8899
username = b"aubo"
password = b"123456"

# Convert IP to bytes
robot_ip_bytes = robot_ip.encode('utf-8') if isinstance(robot_ip, str) else robot_ip

# Perform login
result = robot_lib.robot_login(robot_ip_bytes, robot_port, username, password)
if result != 0:
    raise RuntimeError("Robot login failed")

# Startup robot
result = robot_lib.robot_startup()
if result != 0:
    raise RuntimeError("Robot startup failed")

robot_lib.init_service.argtypes = []
robot_lib.init_service.restype = None

robot_lib.teach_move_start.argtypes = [ctypes.c_int, ctypes.c_bool]
robot_lib.teach_move_start.restype = ctypes.c_int

robot_lib.teach_move_stop.argtypes = []
robot_lib.teach_move_stop.restype = ctypes.c_int

robot_lib.cleanup_service.argtypes = []
robot_lib.cleanup_service.restype = None

# Add the four new speed control function declarations
robot_lib.set_joint_maxacc.argtypes = [ctypes.POINTER(ctypes.c_double)]
robot_lib.set_joint_maxacc.restype = ctypes.c_int

robot_lib.set_joint_maxvelc.argtypes = [ctypes.POINTER(ctypes.c_double)]
robot_lib.set_joint_maxvelc.restype = ctypes.c_int

robot_lib.set_end_max_line_acc.argtypes = [ctypes.c_double]
robot_lib.set_end_max_line_acc.restype = ctypes.c_int

robot_lib.set_end_max_line_velc.argtypes = [ctypes.c_double]
robot_lib.set_end_max_line_velc.restype = ctypes.c_int
robot_lib.move_continue.argtypes = []
robot_lib.move_continue.restype = ctypes.c_int

robot_lib.move_pause.argtypes = []
robot_lib.move_pause.restype = ctypes.c_int

robot_lib.move_stop.argtypes = []
robot_lib.move_stop.restype = ctypes.c_int
# Initialize service once at the start
robot_lib.init_service()

from math import pi

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# put near the top-level helpers
try:
    unicode  # py2
except NameError:
    unicode = str

def _to_basic(obj):
    if obj is None or isinstance(obj, (bool, int, float, str, unicode)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_to_basic(x) for x in obj]
    if isinstance(obj, dict):
        return {str(_to_basic(k)): _to_basic(v) for k, v in obj.iteritems()}
    return repr(obj)

def _make_event_jsonable(raw):
    # If some SDKs pass (event, user_data), take first
    if isinstance(raw, (list, tuple)) and raw:
        raw = raw[0]
    if isinstance(raw, dict):
        evt_type = raw.get('type')
        evt_code = raw.get('code')
        evt_msg  = raw.get('content') or raw.get('msg') or raw.get('message')
        return {
            "type": int(evt_type) if evt_type is not None else None,
            "code": int(evt_code) if evt_code is not None else None,
            "content": _to_basic(evt_msg)
        }
    # object with attributes
    evt_type = getattr(raw, 'event_type', None)
    evt_code = getattr(raw, 'event_code', None)
    evt_msg  = getattr(raw, 'event_content', None) or getattr(raw, 'event_msg', None) or getattr(raw, 'msg', None)
    return {
        "type": int(evt_type) if evt_type is not None else None,
        "code": int(evt_code) if evt_code is not None else None,
        "content": _to_basic(evt_msg)
    }

class RobotBridgeServer:
    def __init__(self, robot_ip=None, robot_port=8899, bridge_host='127.0.0.1', bridge_port=5000):
        # Load IP from config if not provided
        config = load_config()
        self.robot_ip = robot_ip
        self.robot_port = robot_port
        self.bridge_host = bridge_host
        self.bridge_port = bridge_port
        self.bridge_host = bridge_host
        self.bridge_port = bridge_port
        self.event_queue = queue.Queue()
        # Robot connection
        self.RSHD = None
        self.connected = False
        
        # Initialize robot
        self.init_robot()
        
        # Start server
        self.start_server()
    
    def init_robot(self):
        """Initialize the robot connection"""
        try:
            logger.info("Initializing robot library...")
            libpyauboi5.initialize()
            
            logger.info("Creating robot context...")
            self.RSHD = libpyauboi5.create_context()
            logger.info("Connecting to robot at {}:{}...".format(self.robot_ip, self.robot_port))
            result = libpyauboi5.login(self.RSHD, self.robot_ip, self.robot_port)
            if result == 0:
                self.connected = True
                logger.info("Successfully connected to robot!")
                try:
                    if hasattr(libpyauboi5, 'enable_robot_event'):
                        libpyauboi5.enable_robot_event(self.RSHD)

                    if hasattr(libpyauboi5, 'set_robot_event_callback'):
                        NO_ERROR_TYPES = {1300,44}  # RobotEvent_None
                        def _event_cb(raw_event):
                            try:
                                evt = _make_event_jsonable(raw_event)
                                evt_type = int(evt.get('type')) if evt and evt.get('type') is not None else None
                                if evt_type in NO_ERROR_TYPES:
                                    return  # same as: if event['type'] in RobotEventType.NoError: ignore
                                self.event_queue.put(evt)
                                print("oqoqoqoqoqo",evt_type)
                            except Exception as e:
                                logger.error("Failed to handle robot event: {}".format(e))
                            self._event_cb_ref = _event_cb
                            libpyauboi5.set_robot_event_callback(self.RSHD, self._event_cb_ref)
                    else:
                        logger.warning("SDK has no set_robot_event_callback; events unavailable.")
                except Exception as e:
                    logger.error("Error registering event callback: {}".format(e))
            else:
                logger.error("Failed to connect to robot!")
                self.connected = False
                
        except Exception as e:
            logger.error("Error initializing robot: {}".format(e))
            self.connected = False
    
    def start_server(self):
        """Start the bridge server"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.bridge_host, self.bridge_port))
            self.server.listen(5)
            logger.info("Robot bridge server running on {}:{}".format(self.bridge_host, self.bridge_port))
            
            # Start listening for connections
            while True:
                conn, addr = self.server.accept()
                logger.info("Client connected from {}".format(addr))
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            logger.error("Server error: {}".format(e))
        finally:
            if hasattr(self, 'server'):
                self.server.close()
    
    def handle_client(self, conn, addr):
        """Handle client connections"""
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                
                try:
                    cmd = json.loads(data.decode('utf-8'))
                    response = self.process_command(cmd)
                    conn.send(json.dumps(response).encode('utf-8'))
                except Exception as e:
                    logger.error("Error processing command: {}".format(e))
                    response = {"status": "error", "message": str(e)}
                    conn.send(json.dumps(response).encode('utf-8'))
                    
        except Exception as e:
            logger.error("Client handling error: {}".format(e))
        finally:
            conn.close()

    
    def process_command(self, cmd):
        """Process robot commands"""
        try:
            action = cmd.get("action")
            params = cmd.get("params", {})
            
            if not self.connected:
                return {"status": "error", "message": "Robot not connected"}
            
            if action == "move_joint":
               joint_values = params.get("joint_values", [0, 0, 0, 0, 0, 0])
               is_sync = params.get("is_sync", True)
               JointArrayType = ctypes.c_double * 6
               joint_array = JointArrayType(*joint_values)
               try:
                 result = robot_lib.joint_move(joint_array, is_sync)
                 return {"status": "ok", "result": result}
               except Exception as e:
                 return {"status": "error", "message": str(e)}
                
            elif action == "move_line":
                joint_values = params.get("joint_values", [0, 0, 0, 0, 0, 0])
                is_sync = params.get("is_sync", True)
                
                try:
                    # Create array for joint values
                    JointArrayType = ctypes.c_double * 6
                    joint_array = JointArrayType(*joint_values)
                    
                    result = robot_lib.move_line(joint_array, is_sync)
                    return {"status": "ok", "result": result}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
                
            elif action == "move_to_target_in_cartesian":
                pos = params.get("pos", [0, 0, 0])
                rpy_xyz = params.get("rpy_xyz", [0, 0, 0])
                # Convert degrees to radians
                rpy_rad = [i / 180.0 * pi for i in rpy_xyz]
                ori = libpyauboi5.rpy_to_quaternion(self.RSHD, rpy_rad)
                joint_radian = libpyauboi5.get_current_waypoint(self.RSHD)
                ik_result = libpyauboi5.inverse_kin(self.RSHD, joint_radian['joint'], pos, ori)
                result = libpyauboi5.move_joint(self.RSHD, ik_result["joint"])
                return {"status": "ok", "result": result}
                
            elif action == "get_current_waypoint":
                result = libpyauboi5.get_current_waypoint(self.RSHD)
                return {"status": "ok", "waypoint": result}
                
            elif action == "get_robot_state":
                result = libpyauboi5.get_robot_state(self.RSHD)
                return {"status": "ok", "state": result}
                
            elif action == "move_stop":
                result = libpyauboi5.move_stop(self.RSHD)
                result = robot_lib.robot_move_stop()
                return {"status": "ok", "result": result}
                
            elif action == "move_pause":
                result = libpyauboi5.move_pause(self.RSHD)
                result = robot_lib.move_pause()
                return {"status": "ok", "result": result}
                
            elif action == "move_continue":
                result = libpyauboi5.move_continue(self.RSHD)
                result = robot_lib.move_continue()
                return {"status": "ok", "result": result}
                
            elif action == "robot_startup":
                collision = params.get("collision", 6)
                tool_dynamics = params.get("tool_dynamics", {"position": (0.0, 0.0, 0.0), "payload": 0.0, "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)})
                result = libpyauboi5.robot_startup(self.RSHD, collision, tool_dynamics)
                return {"status": "ok", "result": result}
                
            elif action == "robot_shutdown":
                result = libpyauboi5.robot_shutdown(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "init_profile":
                result = libpyauboi5.init_global_move_profile(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_joint_maxacc":
                joint_maxacc = params.get("joint_maxacc", (1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
                JointArrayType = ctypes.c_double * 6
                joint_array = JointArrayType(*joint_maxacc)
                try:
                    result = libpyauboi5.set_joint_maxacc(self.RSHD, joint_maxacc)
                    result = robot_lib.set_joint_maxacc(joint_array)
                    return {"status": "ok", "result": result}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
                
            elif action == "get_joint_maxacc":
                result = libpyauboi5.get_joint_maxacc(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_joint_maxvelc":
                joint_maxvelc = params.get("joint_maxvelc", (1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
                JointArrayType = ctypes.c_double * 6
                joint_array = JointArrayType(*joint_maxvelc)
                try:
                    result = libpyauboi5.set_joint_maxvelc(self.RSHD, joint_maxvelc)
                    result = robot_lib.set_joint_maxvelc(joint_array)
                    return {"status": "ok", "result": result}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
                
            elif action == "get_joint_maxvelc":
                result = libpyauboi5.get_joint_maxvelc(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_end_max_line_acc":
                end_maxacc = params.get("end_maxacc", 0.1)
                try:
                    result = libpyauboi5.set_end_max_line_acc(self.RSHD, end_maxacc)
                    result = robot_lib.set_end_max_line_acc(end_maxacc)
                    return {"status": "ok", "result": result}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
                
            elif action == "get_end_max_line_acc":
                result = libpyauboi5.get_end_max_line_acc(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_end_max_line_velc":
                end_maxvelc = params.get("end_maxvelc", 0.1)
                try:
                    result = libpyauboi5.set_end_max_line_velc(self.RSHD, end_maxvelc)
                    result = robot_lib.set_end_max_line_velc(end_maxvelc)
                    return {"status": "ok", "result": result}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
                
            elif action == "get_end_max_line_velc":
                result = libpyauboi5.get_end_max_line_velc(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_arrival_ahead_distance":
                distance = params.get("distance", 0.0)
                result = libpyauboi5.set_arrival_ahead_distance(self.RSHD, distance)
                return {"status": "ok", "result": result}
                
            elif action == "forward_kin":
                joint_radian = params.get("joint_radian", (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
                result = libpyauboi5.forward_kin(self.RSHD, joint_radian)
                return {"status": "ok", "result": result}
                
            elif action == "inverse_kin":
                joint_radian = params.get("joint_radian", (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
                pos = params.get("pos", (0.0, 0.0, 0.0))
                ori = params.get("ori", (1.0, 0.0, 0.0, 0.0))
                result = libpyauboi5.inverse_kin(self.RSHD, joint_radian, pos, ori)
                return {"status": "ok", "result": result}
            elif action == "get_last_event":
                try:
                    evt = self.event_queue.get_nowait()
                    return {"status": "ok", "event": evt}
                except Exception:
                    return {"status": "ok", "event": None}
                
            elif action == "rpy_to_quaternion":
                rpy = params.get("rpy", [0.0, 0.0, 0.0])
                result = libpyauboi5.rpy_to_quaternion(self.RSHD, rpy)
                return {"status": "ok", "result": result}
                
            elif action == "quaternion_to_rpy":
                ori = params.get("ori", (1.0, 0.0, 0.0, 0.0))
                result = libpyauboi5.quaternion_to_rpy(self.RSHD, ori)
                return {"status": "ok", "result": result}
                
            elif action == "set_tool_dynamics_param":
                tool_dynamics = params.get("tool_dynamics", {"position": (0.0, 0.0, 0.0), "payload": 0.0, "inertia": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)})
                result = libpyauboi5.set_tool_dynamics_param(self.RSHD, tool_dynamics)
                return {"status": "ok", "result": result}
                
            elif action == "get_tool_dynamics_param":
                result = libpyauboi5.get_tool_dynamics_param(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_tool_kinematics_param":
                tool_end_param = params.get("tool_end_param", {"pos": (0.0, 0.0, 0.0), "ori": (1.0, 0.0, 0.0, 0.0)})
                result = libpyauboi5.set_tool_kinematics_param(self.RSHD, tool_end_param)
                return {"status": "ok", "result": result}
                
            elif action == "get_tool_kinematics_param":
                result = libpyauboi5.get_tool_kinematics_param(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_user_coord":
                user_coord = params.get("user_coord", {})
                result = libpyauboi5.set_user_coord(self.RSHD, user_coord)
                return {"status": "ok", "result": result}
                
            elif action == "set_base_coord":
                result = libpyauboi5.set_base_coord(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "get_board_io_status":
                io_type = params.get("io_type", 0)
                io_name = params.get("io_name", "")
                result = libpyauboi5.get_board_io_status(self.RSHD, io_type, io_name)
                return {"status": "ok", "result": result}
                
            elif action == "set_board_io_status":
                io_type = params.get("io_type", 0)
                io_name = params.get("io_name", "")
                io_value = params.get("io_value", 0)
                result = libpyauboi5.set_board_io_status(self.RSHD, io_type, io_name, io_value)
                return {"status": "ok", "result": result}
                
            elif action == "get_tool_io_status":
                io_name = params.get("io_name", "")
                result = libpyauboi5.get_tool_io_status(self.RSHD, io_name)
                return {"status": "ok", "result": result}
                
            elif action == "set_tool_io_status":
                io_name = params.get("io_name", "")
                io_status = params.get("io_status", 0)
                result = libpyauboi5.set_tool_do_status(self.RSHD, io_name, io_status)
                return {"status": "ok", "result": result}
                
            elif action == "set_work_mode":
                mode = params.get("mode", 0)
                result = libpyauboi5.set_work_mode(self.RSHD, mode)
                return {"status": "ok", "result": result}
                
            elif action == "get_work_mode":
                result = libpyauboi5.get_work_mode(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_collision_class":
                grade = params.get("grade", 6)
                result = libpyauboi5.set_collision_class(self.RSHD, grade)
                return {"status": "ok", "result": result}
                
            elif action == "is_have_real_robot":
                result = libpyauboi5.is_have_real_robot(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "is_online_mode":
                result = libpyauboi5.is_online_mode(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "get_joint_status":
                result = libpyauboi5.get_joint_status(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "get_board_io_config":
                io_type = params.get("io_type", 0)
                result = libpyauboi5.get_board_io_config(self.RSHD, io_type)
                return {"status": "ok", "result": result}
                
            elif action == "set_tool_power_type":
                power_type = params.get("power_type", 0)
                result = libpyauboi5.set_tool_power_type(self.RSHD, power_type)
                return {"status": "ok", "result": result}
                
            elif action == "get_tool_power_type":
                result = libpyauboi5.get_tool_power_type(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "get_tool_power_voltage":
                result = libpyauboi5.get_tool_power_voltage(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "enter_reduce_mode":
                result = libpyauboi5.enter_reduce_mode(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "exit_reduce_mode":
                result = libpyauboi5.exit_reduce_mode(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "project_startup":
                result = libpyauboi5.project_startup(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "rs_project_stop":
                result = libpyauboi5.rs_project_stop(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "teach_move_start":
                joint_mode = params.get("joint_mode", 0)  # assuming 0 is default teach_mode
                direction = params.get("direction", True)
                try:
                  result = robot_lib.teach_move_start(joint_mode, direction) 
                  return {"status": "ok", "result": result}
                except Exception as e:
                  return {"status": "error", "message": str(e)}

            elif action == "teach_move_stop":
                try:
                  result = robot_lib.teach_move_stop()
                  return {"status": "ok", "result": result}
                except Exception as e:
                  return {"status": "error", "message": str(e)}

                
            elif action == "set_teach_base_coord":
                result = libpyauboi5.set_teach_base_coord(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_teach_end_coord":
                result = libpyauboi5.set_teach_end_coord(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_teach_user_coord":
                user_coord = params.get("user_coord", {})
                result = libpyauboi5.set_teach_user_coord(self.RSHD, user_coord)
                return {"status": "ok", "result": result}
                
            elif action == "check_user_coord":
                user_coord = params.get("user_coord", {})
                # For now, just return True - you may need to implement actual validation
                result = True
                return {"status": "ok", "result": result}
                
            elif action == "remove_all_waypoint":
                result = libpyauboi5.remove_all_waypoint(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "add_waypoint":
                joint_radian = params.get("joint_radian", [0.0] * 6)
                result = libpyauboi5.add_waypoint(self.RSHD, tuple(joint_radian))
                return {"status": "ok", "result": result}
                
            elif action == "set_circular_loop_times":
                times = params.get("times", 1)
                result = libpyauboi5.set_circular_loop_times(self.RSHD, times)
                return {"status": "ok", "result": result}
                
            elif action == "move_track":
                track_type = params.get("track_type", 2)  # Default to ARC_CIR
                result = libpyauboi5.move_track(self.RSHD, track_type)
                return {"status": "ok", "result": result}
                
            elif action == "collision_recover":
                result = libpyauboi5.collision_recover(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "connect":
                ip = params.get("ip", "192.168.23.129")
                port = params.get("port", 8899)
                result = libpyauboi5.login(self.RSHD, ip, port)
                if result == 0:
                    self.connected = True
                return {"status": "ok", "result": result}
                
            elif action == "robot_startup":
                axis_num = params.get("axis_num", 6)
                tool_dynamics = params.get("tool_dynamics", {})
                result = libpyauboi5.robot_startup(self.RSHD, axis_num, tool_dynamics)
                return {"status": "ok", "result": result}
                
            elif action == "robot_shutdown":
                result = libpyauboi5.robot_shutdown(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "init_profile":
                result = libpyauboi5.init_profile(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_base_coord":
                result = libpyauboi5.set_base_coord(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "set_joint_maxvelc":
                joint_maxvelc = params.get("joint_maxvelc", (1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
                result = libpyauboi5.set_joint_maxvelc(self.RSHD, joint_maxvelc)
                return {"status": "ok", "result": result}
                
            elif action == "set_joint_maxacc":
                joint_maxacc = params.get("joint_maxacc", (1.0, 1.0, 1.0, 1.0, 1.0, 1.0))
                result = libpyauboi5.set_joint_maxacc(self.RSHD, joint_maxacc)
                return {"status": "ok", "result": result}
                
            elif action == "set_end_max_line_velc":
                velocity = params.get("velocity", 1.0)
                result = libpyauboi5.set_end_max_line_velc(self.RSHD, velocity)
                return {"status": "ok", "result": result}
                
            elif action == "set_end_max_line_acc":
                acceleration = params.get("acceleration", 1.0)
                result = libpyauboi5.set_end_max_line_acc(self.RSHD, acceleration)
                return {"status": "ok", "result": result}
                
            elif action == "forward_kin":
                joint_radian = params.get("joint_radian", [0, 0, 0, 0, 0, 0])
                result = libpyauboi5.forward_kin(self.RSHD, joint_radian)
                return {"status": "ok", "result": result}
                
            elif action == "quaternion_to_rpy":
                ori = params.get("ori", [0, 0, 0, 1])
                result = libpyauboi5.quaternion_to_rpy(self.RSHD, ori)
                return {"status": "ok", "result": result}
                
            elif action == "get_board_io_status":
                io_type = params.get("io_type", 0)
                io_name = params.get("io_name", "")
                result = libpyauboi5.get_board_io_status(self.RSHD, io_type, io_name)
                return {"status": "ok", "result": result}
                
            elif action == "set_board_io_status":
                io_type = params.get("io_type", 0)
                io_name = params.get("io_name", "")
                value = params.get("value", 0)
                result = libpyauboi5.set_board_io_status(self.RSHD, io_type, io_name, value)
                return {"status": "ok", "result": result}
                
            elif action == "get_tool_dynamics_param":
                result = libpyauboi5.get_tool_dynamics_param(self.RSHD)
                return {"status": "ok", "result": result}
                
            elif action == "disconnect":
                if self.connected:
                    libpyauboi5.logout(self.RSHD)
                    self.connected = False
                return {"status": "ok", "message": "Disconnected"}
                
            elif action == "get_status":
                return {"status": "ok", "connected": self.connected, "robot_ip": self.robot_ip}
                
            else:
                return {"status": "error", "message": "Unknown action: {}".format(action)}
                
        except Exception as e:
            logger.error("Error processing command {}: {}".format(cmd.get("action", "unknown"), e))
            return {"status": "error", "message": str(e)}
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.connected:
                libpyauboi5.logout(self.RSHD)
            libpyauboi5.uninitialize()
            logger.info("Robot bridge server cleaned up")
        except Exception as e:
            logger.error("Error during cleanup: {}".format(e))

if __name__ == "__main__":
    import time
    try:
        cfg = load_config()
        while True:
            try:
                server = RobotBridgeServer(
                    robot_ip=cfg.get("ip", "127.0.0.1"),
                    robot_port=8899,
                    bridge_host='127.0.0.1',
                    bridge_port=5000
                )
                print("ipstoura",robot_ip)
                logger.info("Bridge started with robot_ip={} tool={}".format(cfg.get("ip"), cfg.get("tool")))
                break  # started successfully, exit loop
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    logger.warning("Port 5000 already in use, retrying in 2 seconds...")
                    time.sleep(2)  # wait before retry
                else:
                    raise
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        if 'server' in locals():
            server.cleanup()
    except Exception as e:
        logger.error("Server error: {}".format(e))




