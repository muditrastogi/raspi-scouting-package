import psutil
import csv
import time
import subprocess
from datetime import datetime
import os
import getpass

USERNAME = getpass.getuser()

def get_voltage_info():
    try:
        # Get voltage information using vcgencmd
        voltage = subprocess.check_output(['vcgencmd', 'measure_volts']).decode('utf-8')
        voltage = float(voltage.split('=')[1].strip('V\n'))
        
        # Get throttling status
        throttled = subprocess.check_output(['vcgencmd', 'get_throttled']).decode('utf-8')
        throttled = int(throttled.split('=')[1].strip(), 16)
        
        # Decode throttling flags
        under_voltage = bool(throttled & 0x1)
        arm_freq_capped = bool(throttled & 0x2)
        currently_throttled = bool(throttled & 0x4)
        soft_temp_limit = bool(throttled & 0x8)
        
        return {
            'voltage': voltage,
            'under_voltage': under_voltage,
            'arm_freq_capped': arm_freq_capped,
            'currently_throttled': currently_throttled,
            'soft_temp_limit': soft_temp_limit
        }
    except Exception as e:
        print(f"Error getting voltage info: {e}")
        return {
            'voltage': None,
            'under_voltage': None,
            'arm_freq_capped': None,
            'currently_throttled': None,
            'soft_temp_limit': None
        }

def get_system_metrics():
    # CPU metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_freq = psutil.cpu_freq()
    
    # Memory metrics
    memory = psutil.virtual_memory()
    
    # Disk metrics
    disk = psutil.disk_usage('/')
    
    # Temperature (Raspberry Pi specific)
    try:
        temp = psutil.sensors_temperatures()
        cpu_temp = temp['cpu_thermal'][0].current if 'cpu_thermal' in temp else None
    except:
        cpu_temp = None
    
    # Get voltage and throttling information
    voltage_info = get_voltage_info()
    
    return {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'cpu_percent': cpu_percent,
        'cpu_freq_current': cpu_freq.current if cpu_freq else None,
        'cpu_freq_min': cpu_freq.min if cpu_freq else None,
        'cpu_freq_max': cpu_freq.max if cpu_freq else None,
        'memory_total': memory.total,
        'memory_available': memory.available,
        'memory_percent': memory.percent,
        'disk_total': disk.total,
        'disk_used': disk.used,
        'disk_percent': disk.percent,
        'cpu_temperature': cpu_temp,
        'voltage': voltage_info['voltage'],
        'under_voltage': voltage_info['under_voltage'],
        'arm_freq_capped': voltage_info['arm_freq_capped'],
        'currently_throttled': voltage_info['currently_throttled'],
        'soft_temp_limit': voltage_info['soft_temp_limit']
    }

def save_to_csv(metrics, filename='system_metrics.csv'):
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics.keys())
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(metrics)
        
        # Print warning if under voltage is detected
        if metrics['under_voltage']:
            print(f"WARNING: Under voltage detected at {metrics['timestamp']}!")
        if metrics['currently_throttled']:
            print(f"WARNING: System is currently throttled at {metrics['timestamp']}!")

def main():
    print("Starting system monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            metrics = get_system_metrics()
            os.makedirs(f"/home/{USERNAME}/Desktop/systemlogs/", exist_ok=True)
            filename = f"/home/{USERNAME}/Desktop/systemlogs/system_metrics_{datetime.now().strftime('%Y-%m-%d')}.csv"
            save_to_csv(metrics, filename)
            print(f"Metrics recorded at {metrics['timestamp']}")
            time.sleep(10)  # Wait for 1 minute
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")

if __name__ == "__main__":
    main() 
