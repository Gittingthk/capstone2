import logging
import psutil
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        """Initialize system monitor"""
        self.start_time = datetime.now()
        
    def get_system_status(self):
        """Get current system status"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'uptime': str(datetime.now() - self.start_time),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return None
            
    def log_system_status(self):
        """Log current system status"""
        status = self.get_system_status()
        if status:
            logger.info(f"System Status - CPU: {status['cpu_percent']}%, "
                       f"Memory: {status['memory_percent']}%, "
                       f"Uptime: {status['uptime']}") 