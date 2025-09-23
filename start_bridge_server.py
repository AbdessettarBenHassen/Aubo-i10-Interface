#!/usr/bin/env python3
# coding=utf-8
"""
Python 3 script to start the Python 2 bridge server
"""
import subprocess
import sys
import os
import time

def start_bridge_server():
    """Start the Python 2 bridge server"""
    try:
        print("Starting Robot Bridge Server (Python 2)...")
        print("Make sure you have Python 2 installed and libpyauboi5 available")
        print("Robot IP: 192.168.23.129 (change this in robot_bridge_server.py if needed)")
        print("Bridge Port: 5000")
        print("Press Ctrl+C to stop the server")
        print()
        
        # Check if Python 2 is available
        try:
            subprocess.run(["python2", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: Python 2 not found!")
            print("Please install Python 2 and make sure 'python2' command is available")
            return False
        
        # Check if the bridge server file exists
        if not os.path.exists("robot_bridge_server.py"):
            print("Error: robot_bridge_server.py not found!")
            return False
        
        # Start the bridge server
        process = subprocess.Popen(["python2", "robot_bridge_server.py"])
        
        print(f"Bridge server started with PID: {process.pid}")
        print("Server is running...")
        
        try:
            # Wait for the process to complete
            process.wait()
        except KeyboardInterrupt:
            print("\nStopping bridge server...")
            process.terminate()
            process.wait()
            print("Bridge server stopped.")
        
        return True
        
    except Exception as e:
        print(f"Error starting bridge server: {e}")
        return False

if __name__ == "__main__":
    start_bridge_server()
