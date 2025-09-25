"""
System Performance Logger
Logs system performance metrics (RAM, CPU, temperature, etc.) to CSV files every 30 seconds
Saves logs to Desktop/logs directory organized by date
"""

import psutil
import os
import csv
import threading
import time
from datetime import datetime
import platform
import getpass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemPerformanceLogger:
    def __init__(self, log_interval=30):
        """
        Initialize the performance logger
        
        Args:
            log_interval (int): Logging interval in seconds (default: 30)
        """
        self.log_interval = log_interval
        self.is_logging = False
        self.logging_thread = None
        self.stop_event = threading.Event()
        
        # Setup log directory
        self.setup_log_directory()
        
        # CSV headers
        self.csv_headers = [
            'timestamp',
            'cpu_percent',
            'memory_percent',
            'memory_used_gb',
            'memory_total_gb',
            'disk_usage_percent',
            'disk_free_gb',
            'disk_total_gb',
            'network_bytes_sent',
            'network_bytes_recv',
            'boot_time',
            'uptime_hours',
            'process_count',
            'cpu_temperature',
            'gpu_temperature',
            'system_load_1min',
            'system_load_5min',
            'system_load_15min'
        ]
        
        # Silent initialization - only log errors
        # logger.info(f"Performance logger initialized with {log_interval}s interval")
    
    def setup_log_directory(self):
        """Create logs directory on Desktop if it doesn't exist"""
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            self.logs_dir = os.path.join(desktop_path, "logs")
            os.makedirs(self.logs_dir, exist_ok=True)
            # Silent directory creation
            pass
        except Exception as e:
            logger.error(f"Error creating log directory: {e}")
            # Fallback to current directory
            self.logs_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(self.logs_dir, exist_ok=True)
    
    def get_log_filename(self):
        """Get CSV filename based on current date"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.logs_dir, f"system_performance_{date_str}.csv")
    
    def get_cpu_temperature(self):
        """Get CPU temperature (Windows specific)"""
        try:
            # For Windows, try to get temperature using psutil
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            return round(entries[0].current, 2)
            
            # Alternative method for Windows using WMI
            try:
                import wmi
                w = wmi.WMI(namespace="root\\wmi")
                temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
                temp_celsius = float(temperature_info.CurrentTemperature) / 10.0 - 273.15
                return round(temp_celsius, 2)
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Could not get CPU temperature: {e}")
        
        return None
    
    def get_gpu_temperature(self):
        """Get GPU temperature (if available)"""
        try:
            # Try nvidia-ml-py for NVIDIA GPUs
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                return temp
            except:
                pass
            
            # Alternative: try to get GPU temp through psutil
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                for name, entries in temps.items():
                    if 'gpu' in name.lower() or 'video' in name.lower():
                        if entries:
                            return round(entries[0].current, 2)
        except Exception as e:
            logger.debug(f"Could not get GPU temperature: {e}")
        
        return None
    
    def get_system_load(self):
        """Get system load averages (Linux/Mac style, approximated for Windows)"""
        try:
            if platform.system() != "Windows":
                return os.getloadavg()
            else:
                # For Windows, approximate load average using CPU percentage
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                load_avg = cpu_percent / 100.0 * cpu_count
                return [load_avg, load_avg, load_avg]  # Approximate 1, 5, 15 min averages
        except:
            return [None, None, None]
    
    def collect_metrics(self):
        """Collect all system performance metrics"""
        try:
            # Basic system info
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = round(memory.used / (1024**3), 2)
            memory_total_gb = round(memory.total / (1024**3), 2)
            
            # Disk metrics (for main drive)
            disk = psutil.disk_usage('/')
            if platform.system() == "Windows":
                disk = psutil.disk_usage('C:\\')
            disk_usage_percent = round((disk.used / disk.total) * 100, 2)
            disk_free_gb = round(disk.free / (1024**3), 2)
            disk_total_gb = round(disk.total / (1024**3), 2)
            
            # Network metrics
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            # System uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_hours = round(uptime_seconds / 3600, 2)
            
            # Process count
            process_count = len(psutil.pids())
            
            # Temperature metrics
            cpu_temperature = self.get_cpu_temperature()
            gpu_temperature = self.get_gpu_temperature()
            
            # System load
            load_1min, load_5min, load_15min = self.get_system_load()
            
            metrics = {
                'timestamp': timestamp,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used_gb': memory_used_gb,
                'memory_total_gb': memory_total_gb,
                'disk_usage_percent': disk_usage_percent,
                'disk_free_gb': disk_free_gb,
                'disk_total_gb': disk_total_gb,
                'network_bytes_sent': network_bytes_sent,
                'network_bytes_recv': network_bytes_recv,
                'boot_time': boot_time,
                'uptime_hours': uptime_hours,
                'process_count': process_count,
                'cpu_temperature': cpu_temperature,
                'gpu_temperature': gpu_temperature,
                'system_load_1min': load_1min,
                'system_load_5min': load_5min,
                'system_load_15min': load_15min
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return None
    
    def write_metrics_to_csv(self, metrics):
        """Write metrics to CSV file"""
        try:
            filename = self.get_log_filename()
            file_exists = os.path.exists(filename)
            
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.csv_headers)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                    # Silent file creation
                
                # Write metrics
                writer.writerow(metrics)
                
                # Flush to ensure data is written immediately
                csvfile.flush()
                os.fsync(csvfile.fileno())
                
        except Exception as e:
            logger.error(f"Error writing metrics to CSV: {e}")
    
    def logging_worker(self):
        """Background worker thread for continuous logging"""
        # Silent background worker - no startup message
        
        while not self.stop_event.is_set():
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                
                if metrics:
                    # Write to CSV
                    self.write_metrics_to_csv(metrics)
                    
                    # Silent background logging - no console output during normal operation
                    # Uncomment the line below for debugging:
                    # logger.debug(f"Logged: CPU: {metrics['cpu_percent']:.1f}%, RAM: {metrics['memory_percent']:.1f}%, Disk: {metrics['disk_usage_percent']:.1f}%")
                
                # Wait for next interval or stop event
                self.stop_event.wait(self.log_interval)
                
            except Exception as e:
                logger.error(f"Error in logging worker: {e}")
                # Continue logging even if there's an error
                time.sleep(self.log_interval)
    
    def start_logging(self):
        """Start performance logging in background thread"""
        if self.is_logging:
            logger.warning("Performance logging is already running")
            return
        
        self.is_logging = True
        self.stop_event.clear()
        
        # Start logging thread
        self.logging_thread = threading.Thread(target=self.logging_worker, daemon=True)
        self.logging_thread.start()
        
        # Silent start - no console message
    
    def stop_logging(self):
        """Stop performance logging"""
        if not self.is_logging:
            return
        
        # Silent stop - no console messages
        self.is_logging = False
        self.stop_event.set()
        
        # Wait for thread to finish
        if self.logging_thread and self.logging_thread.is_alive():
            self.logging_thread.join(timeout=5)
    
    def is_running(self):
        """Check if logging is currently running"""
        return self.is_logging
    
    def get_log_file_info(self):
        """Get information about current log file"""
        filename = self.get_log_filename()
        try:
            if os.path.exists(filename):
                stat_info = os.stat(filename)
                size_mb = round(stat_info.st_size / (1024*1024), 2)
                modified = datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                # Count lines (approximate record count)
                with open(filename, 'r') as f:
                    line_count = sum(1 for line in f) - 1  # Subtract header
                
                return {
                    'filename': filename,
                    'size_mb': size_mb,
                    'last_modified': modified,
                    'record_count': line_count
                }
            else:
                return {
                    'filename': filename,
                    'size_mb': 0,
                    'last_modified': 'Not created yet',
                    'record_count': 0
                }
        except Exception as e:
            logger.error(f"Error getting log file info: {e}")
            return None


# For testing the logger independently
if __name__ == "__main__":
    print("System Performance Logger Test")
    print("=" * 40)
    
    # Create logger with 5-second interval for testing
    logger_instance = SystemPerformanceLogger(log_interval=5)
    
    try:
        # Start logging
        logger_instance.start_logging()
        
        # Run for 30 seconds
        print("Logging for 30 seconds... Press Ctrl+C to stop early")
        for i in range(6):
            time.sleep(5)
            info = logger_instance.get_log_file_info()
            if info:
                print(f"Log file: {info['record_count']} records, {info['size_mb']} MB")
        
    except KeyboardInterrupt:
        print("\nStopping logger...")
    finally:
        logger_instance.stop_logging()
        
        # Show final log file info
        info = logger_instance.get_log_file_info()
        if info:
            print(f"\nFinal log file: {info['filename']}")
            print(f"Records: {info['record_count']}")
            print(f"Size: {info['size_mb']} MB")
            print("Log file saved to Desktop/logs directory")
