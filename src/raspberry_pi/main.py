#!/usr/bin/env python3
"""
Cell Culture Automation System - Main Controller
This is the main program running on Raspberry Pi 5 that coordinates all subsystems
"""

import os
import sys
import time
import logging
from datetime import datetime
import threading
import queue

# Local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.arduino_communication import ArduinoCommunication
from utils.system_monitor import SystemMonitor
from ai_model.cell_analyzer import CellAnalyzer
from web_interface.app import start_web_server
from raspberry_pi.utils.notification_manager import NotificationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CellCultureSystem:
    def __init__(self):
        """Initialize the cell culture automation system"""
        self.arduino = ArduinoCommunication()
        self.analyzer = CellAnalyzer()
        self.monitor = SystemMonitor()
        self.notification_manager = NotificationManager()
        
        # Command queue for handling operations
        self.command_queue = queue.Queue()
        
        # System state
        self.is_running = False
        self.is_sterilizing = False
        self.current_operation = "대기 중"
        
    def start(self):
        """시스템 시작"""
        try:
            self.is_running = True
            logger.info("세포 배양 자동화 시스템 시작")
            
            # 웹 서버 시작
            web_thread = threading.Thread(target=start_web_server, args=(self,))
            web_thread.daemon = True
            web_thread.start()
            
            # 메인 루프
            while self.is_running:
                if self.is_sterilizing:
                    logger.info("살균 진행 중...")
                self.monitor.log_system_status()
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"시스템 실행 중 오류 발생: {str(e)}")
            self.emergency_stop()
            
    def _main_loop(self):
        """Main control loop of the system"""
        while self.is_running:
            try:
                # Check system status
                if not self.monitor.check_status():
                    raise Exception("System status check failed")
                
                # Process commands from queue
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    self._process_command(command)
                
                # Regular cell analysis
                if self._should_analyze_cells():
                    self._perform_cell_analysis()
                
                # Check if sterilization is needed
                if self._should_sterilize():
                    self._perform_sterilization()
                
                time.sleep(1)  # Prevent CPU overuse
                
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                self.notification_manager.send_alert(
                    "System Error",
                    f"Error in main control loop: {str(e)}"
                )
                
    def _process_command(self, command):
        """Process a command from the queue"""
        try:
            command_type = command.get('type')
            params = command.get('params', {})
            
            if command_type == 'dispense_liquid':
                self._dispense_liquid(params)
            elif command_type == 'move_robot':
                self._control_robot_arm(params)
            elif command_type == 'sterilize':
                self._perform_sterilization()
            else:
                logger.warning(f"Unknown command type: {command_type}")
                
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            
    def _should_analyze_cells(self):
        """Determine if cell analysis should be performed"""
        # Implement logic for when to analyze cells
        # For example, every 6 hours or based on schedule
        return False
        
    def _perform_cell_analysis(self):
        """Perform cell analysis using the AI model"""
        try:
            image = self.analyzer.capture_image()
            results = self.analyzer.analyze_image(image)
            
            if results['contamination_detected']:
                self.notification_manager.send_alert(
                    "Contamination Alert",
                    "Possible contamination detected in cell culture"
                )
                
            if results['confluence'] > 80:
                self.notification_manager.send_alert(
                    "Confluence Alert",
                    f"Cell confluence at {results['confluence']}%"
                )
                
        except Exception as e:
            logger.error(f"Error in cell analysis: {str(e)}")
            
    def _should_sterilize(self):
        """Determine if sterilization should be performed"""
        # Implement sterilization scheduling logic
        return False
        
    def _perform_sterilization(self):
        """Perform UV sterilization and cleaning routine"""
        try:
            self.is_sterilizing = True
            logger.info("Starting sterilization routine")
            
            # Send sterilization command to Arduino
            self.arduino.send_command('sterilize', {'duration': 300})  # 5 minutes
            
            # Wait for completion
            time.sleep(300)
            
            self.is_sterilizing = False
            logger.info("Sterilization completed")
            
        except Exception as e:
            logger.error(f"Error during sterilization: {str(e)}")
            self.is_sterilizing = False
            
    def emergency_stop(self):
        """비상 정지"""
        try:
            self.is_running = False
            self.arduino.emergency_stop()
            logger.warning("비상 정지 실행됨")
        except Exception as e:
            logger.error(f"비상 정지 중 오류 발생: {str(e)}")

    def close(self):
        """시스템 종료"""
        try:
            self.is_running = False
            self.arduino.close()
            self.analyzer.close()
            logger.info("시스템 정상 종료")
        except Exception as e:
            logger.error(f"시스템 종료 중 오류 발생: {str(e)}")

if __name__ == '__main__':
    try:
        system = CellCultureSystem()
        system.start()
    except KeyboardInterrupt:
        logger.info("사용자에 의한 프로그램 종료")
        system.close()
    except Exception as e:
        logger.error(f"예기치 않은 오류 발생: {str(e)}")
        if 'system' in locals():
            system.emergency_stop()
            system.close() 