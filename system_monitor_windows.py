#!/usr/bin/env python3
"""
Windows System Monitor
A Windows-compatible version of system_monitor.py for the Raspberry Pi Scouting Package
"""

import psutil
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import threading
import logging

class WindowsSystemMonitor:
    def __init__(self):
        # Setup logging
        self.setup_logging()
        
        # Monitoring directories
        self.logs_dir = Path.home() / "Desktop" / "systemlogs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Monitoring interval (seconds)
        self.monitor_interval = 30
        
        # Stop flag for graceful shutdown
        self.stop_monitoring = False
        
        # Performance thresholds
        self.cpu_threshold = 80.0  # CPU usage percentage
        self.memory_threshold = 80.0  # Memory usage percentage
        self.disk_threshold = 90.0  # Disk usage percentage
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('system_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_system_info(self):
        """Get basic system information"""
        try:
            # CPU information
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Network information
            network = psutil.net_io_counters()
            
            # System uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'count': cpu_count,
                    'frequency_mhz': cpu_freq.current if cpu_freq else None,
                    'usage_percent': psutil.cpu_percent(interval=1)
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 2)
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'system': {
                    'boot_time': boot_time.isoformat(),
                    'uptime_hours': round(uptime.total_seconds() / 3600, 2),
                    'platform': psutil.sys.platform,
                    'python_version': psutil.sys.version
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return None
    
    def check_thresholds(self, system_info):
        """Check if any system metrics exceed thresholds"""
        warnings = []
        
        try:
            # Check CPU usage
            if system_info['cpu']['usage_percent'] > self.cpu_threshold:
                warnings.append(f"High CPU usage: {system_info['cpu']['usage_percent']}%")
            
            # Check memory usage
            if system_info['memory']['usage_percent'] > self.memory_threshold:
                warnings.append(f"High memory usage: {system_info['memory']['usage_percent']}%")
            
            # Check disk usage
            if system_info['disk']['usage_percent'] > self.disk_threshold:
                warnings.append(f"High disk usage: {system_info['disk']['usage_percent']}%")
            
            return warnings
            
        except Exception as e:
            self.logger.error(f"Error checking thresholds: {e}")
            return []
    
    def save_metrics(self, system_info):
        """Save system metrics to file"""
        try:
            # Save to daily log file
            date_str = datetime.now().strftime('%Y%m%d')
            metrics_file = self.logs_dir / f"system_metrics_{date_str}.json"
            
            # Load existing metrics if file exists
            existing_metrics = []
            if metrics_file.exists():
                try:
                    with open(metrics_file, 'r') as f:
                        existing_metrics = json.load(f)
                except json.JSONDecodeError:
                    existing_metrics = []
            
            # Add new metrics
            existing_metrics.append(system_info)
            
            # Keep only last 1000 entries to prevent file from growing too large
            if len(existing_metrics) > 1000:
                existing_metrics = existing_metrics[-1000:]
            
            # Save updated metrics
            with open(metrics_file, 'w') as f:
                json.dump(existing_metrics, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
    
    def log_system_status(self, system_info, warnings):
        """Log system status with warnings if any"""
        try:
            # Format status message
            status_msg = f"System Status - CPU: {system_info['cpu']['usage_percent']}%, " \
                        f"Memory: {system_info['memory']['usage_percent']}%, " \
                        f"Disk: {system_info['disk']['usage_percent']}%"
            
            if warnings:
                status_msg += f" | WARNINGS: {'; '.join(warnings)}"
                self.logger.warning(status_msg)
            else:
                self.logger.info(status_msg)
                
        except Exception as e:
            self.logger.error(f"Error logging system status: {e}")
    
    def monitor_system(self):
        """Main monitoring loop"""
        self.logger.info("Starting Windows System Monitor...")
        
        while not self.stop_monitoring:
            try:
                # Get system information
                system_info = self.get_system_info()
                
                if system_info:
                    # Check for threshold violations
                    warnings = self.check_thresholds(system_info)
                    
                    # Log system status
                    self.log_system_status(system_info, warnings)
                    
                    # Save metrics
                    self.save_metrics(system_info)
                    
                    # Log warnings if any
                    for warning in warnings:
                        self.logger.warning(warning)
                
                # Wait for next monitoring cycle
                time.sleep(self.monitor_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, stopping monitor...")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitor_interval)
        
        self.logger.info("System monitor stopped")
    
    def start_monitoring(self):
        """Start the system monitoring in a separate thread"""
        self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitor_thread.start()
        self.logger.info("System monitoring started in background thread")
    
    def stop_monitoring_service(self):
        """Stop the system monitoring service"""
        self.logger.info("Stopping system monitoring service...")
        self.stop_monitoring = True
        
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=10)
            if self.monitor_thread.is_alive():
                self.logger.warning("Monitor thread did not stop gracefully")
        
        self.logger.info("System monitoring service stopped")
    
    def get_recent_metrics(self, hours=24):
        """Get recent system metrics for the specified number of hours"""
        try:
            metrics = []
            current_time = datetime.now()
            
            # Get metrics from today and yesterday if needed
            for i in range(2):
                date_str = (current_time - timedelta(days=i)).strftime('%Y%m%d')
                metrics_file = self.logs_dir / f"system_metrics_{date_str}.json"
                
                if metrics_file.exists():
                    try:
                        with open(metrics_file, 'r') as f:
                            daily_metrics = json.load(f)
                            
                        # Filter metrics within the specified time range
                        cutoff_time = current_time - timedelta(hours=hours)
                        for metric in daily_metrics:
                            metric_time = datetime.fromisoformat(metric['timestamp'])
                            if metric_time >= cutoff_time:
                                metrics.append(metric)
                                
                    except json.JSONDecodeError:
                        continue
            
            # Sort by timestamp
            metrics.sort(key=lambda x: x['timestamp'])
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting recent metrics: {e}")
            return []

def main():
    """Main entry point for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Windows System Monitor')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon service')
    parser.add_argument('--interval', type=int, default=30, help='Monitoring interval in seconds')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
    # Create and start monitor
    monitor = WindowsSystemMonitor()
    monitor.monitor_interval = args.interval
    
    if args.daemon:
        # Run as daemon (background service)
        monitor.start_monitoring()
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring_service()
    else:
        # Run in foreground
        monitor.monitor_system()

if __name__ == "__main__":
    main()
