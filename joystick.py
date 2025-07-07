import pygame
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional
from typing import Dict, Tuple

@dataclass
class JoystickState:
    buttons: Dict[int, bool]    # {button_id: bool}
    axes: Dict[int, int]        # {axis_id: int} (-1, 0, or 1)
    hats: Dict[int, Tuple[int, int]]  # {hat_id: tuple} ((-1,-1) to (1,1))

class JoystickManager(threading.Thread):
    def __init__(
        self,
        axis_threshold: float = 1000,
        update_interval: float = 0.01,
        button_callback: Optional[Callable[[int, bool], None]] = None,
        axis_callback: Optional[Callable[[int, int], None]] = None,
        hat_callback: Optional[Callable[[int, tuple], None]] = None
    ):
        threading.Thread.__init__(self, daemon=True)
        self.running = False
        self.joystick = None
        self.state = JoystickState(buttons={}, axes={}, hats={})
        self.connected = False
        self.update_interval = update_interval
        self.axis_threshold = axis_threshold
        self.lock = threading.Lock()
        
        # Callbacks
        self.button_callback = button_callback
        self.axis_callback = axis_callback
        self.hat_callback = hat_callback
        
        # Initialize pygame
        pygame.init()
        pygame.joystick.init()
        self._connect_joystick()
    
    def _connect_joystick(self):
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.connected = True
            print(f"Joystick connected: {self.joystick.get_name()}")
        else:
            self.connected = False
            print("No joystick detected")
    
    def run(self):
        self.running = True
        last_state = JoystickState(buttons={}, axes={}, hats={})
        
        while self.running:
            if not self.connected:
                time.sleep(1)
                self._connect_joystick()
                continue
                
            try:
                pygame.event.pump()
                
                # Create new state
                new_state = JoystickState(buttons={}, axes={}, hats={})
                
                # Read buttons
                for i in range(self.joystick.get_numbuttons()):
                    new_state.buttons[i] = self.joystick.get_button(i) == 1
                
                # Read axes
                for i in range(self.joystick.get_numaxes()):
                    axis_value = self.joystick.get_axis(i)
                    if axis_value < -self.axis_threshold:
                        new_state.axes[i] = -1
                    elif axis_value > self.axis_threshold:
                        new_state.axes[i] = 1
                    else:
                        new_state.axes[i] = 0
                
                # Read hats
                for i in range(self.joystick.get_numhats()):
                    new_state.hats[i] = self.joystick.get_hat(i)
                
                # Update state
                with self.lock:
                    self.state = new_state
                
                # Check for changes and trigger callbacks
                self._check_changes(last_state, new_state)
                last_state = new_state
                
            except pygame.error:
                self.connected = False
                print("Joystick disconnected")
                
            time.sleep(self.update_interval)
    
    def _check_changes(self, last_state: JoystickState, new_state: JoystickState):
        # Check button changes
        for btn in set(last_state.buttons) | set(new_state.buttons):
            if new_state.buttons.get(btn, False) != last_state.buttons.get(btn, False):
                if self.button_callback:
                    self.button_callback(btn, new_state.buttons.get(btn, False))
        
        # Check axis changes
        for axis in set(last_state.axes) | set(new_state.axes):
            if new_state.axes.get(axis, 0) != last_state.axes.get(axis, 0):
                if self.axis_callback:
                    self.axis_callback(axis, new_state.axes.get(axis, 0))
        
        # Check hat changes
        for hat in set(last_state.hats) | set(new_state.hats):
            if new_state.hats.get(hat, (0, 0)) != last_state.hats.get(hat, (0, 0)):
                if self.hat_callback:
                    self.hat_callback(hat, new_state.hats.get(hat, (0, 0)))
    
    def stop(self):
        self.running = False
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
    
    def get_state(self) -> JoystickState:
        with self.lock:
            return JoystickState(
                buttons=self.state.buttons.copy(),
                axes=self.state.axes.copy(),
                hats=self.state.hats.copy()
            )