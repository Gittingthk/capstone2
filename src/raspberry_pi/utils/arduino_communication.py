"""
Arduino Communication Module
Handles communication between Raspberry Pi and Arduino using Serial/I2C
"""

import serial
import json
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ArduinoCommunication:
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 115200):
        """Initialize Arduino communication"""
        try:
            self.serial = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            logger.info(f"Connected to Arduino on {port}")
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {str(e)}")
            raise
            
        self.command_handlers = {
            'dispense': self._handle_dispense,
            'move': self._handle_move,
            'sterilize': self._handle_sterilize,
            'emergency': self._handle_emergency
        }
        
    def send_command(self, command_type: str, params: Dict[str, Any]) -> bool:
        """Send a command to Arduino"""
        try:
            if command_type not in self.command_handlers:
                raise ValueError(f"Unknown command type: {command_type}")
                
            handler = self.command_handlers[command_type]
            return handler(params)
            
        except Exception as e:
            logger.error(f"Error sending command to Arduino: {str(e)}")
            return False
            
    def _handle_dispense(self, params: Dict[str, Any]) -> bool:
        """Handle liquid dispensing command"""
        try:
            command = {
                'cmd': 'DISPENSE',
                'volume': params.get('volume', 0),
                'speed': params.get('speed', 100),
                'pump': params.get('pump_id', 1)
            }
            
            self._send_and_wait(command)
            return True
            
        except Exception as e:
            logger.error(f"Error in dispense command: {str(e)}")
            return False
            
    def _handle_move(self, params: Dict[str, Any]) -> bool:
        """Handle robot arm movement command"""
        try:
            command = {
                'cmd': 'MOVE',
                'x': params.get('x', 0),
                'y': params.get('y', 0),
                'z': params.get('z', 0),
                'speed': params.get('speed', 50)
            }
            
            self._send_and_wait(command)
            return True
            
        except Exception as e:
            logger.error(f"Error in move command: {str(e)}")
            return False
            
    def _handle_sterilize(self, params: Dict[str, Any]) -> bool:
        """Handle sterilization command"""
        try:
            command = {
                'cmd': 'STERILIZE',
                'duration': params.get('duration', 300),
                'uv_intensity': params.get('intensity', 100)
            }
            
            self._send_and_wait(command)
            return True
            
        except Exception as e:
            logger.error(f"Error in sterilize command: {str(e)}")
            return False
            
    def _handle_emergency(self, params: Dict[str, Any]) -> bool:
        """Handle emergency stop command"""
        try:
            command = {
                'cmd': 'EMERGENCY_STOP'
            }
            
            self._send_and_wait(command)
            return True
            
        except Exception as e:
            logger.error(f"Error in emergency stop command: {str(e)}")
            return False
            
    def _send_and_wait(self, command: Dict[str, Any]) -> None:
        """Send command and wait for acknowledgment"""
        try:
            # Convert command to JSON string
            command_str = json.dumps(command) + '\n'
            
            # Send command
            self.serial.write(command_str.encode())
            
            # Wait for acknowledgment
            response = self.serial.readline().decode().strip()
            
            if not response or 'ERROR' in response:
                raise Exception(f"Arduino error: {response}")
                
        except Exception as e:
            logger.error(f"Communication error: {str(e)}")
            raise
            
    def emergency_stop(self) -> None:
        """Immediate emergency stop"""
        try:
            self.send_command('emergency', {})
        except Exception as e:
            logger.critical(f"Failed to send emergency stop: {str(e)}")
            
    def close(self) -> None:
        """Close the serial connection"""
        try:
            if self.serial.is_open:
                self.serial.close()
                logger.info("Arduino connection closed")
        except Exception as e:
            logger.error(f"Error closing Arduino connection: {str(e)}")
            
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close() 