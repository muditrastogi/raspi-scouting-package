#!/usr/bin/env python3
"""
Raspberry Pi Network Keep-Alive and FTP Server Script
Pings macOS device every 10 seconds to prevent network sleep
Runs FTP server on ~/Desktop/scout-videos directory
"""

import subprocess
import threading
import time
import os
import sys
import pwd
from pathlib import Path

# Configuration
MAC_ADDRESS = "14:98:77:7c:8f:08"  # Update this to your macOS device's MAC
FALLBACK_IP = "192.168.1.3"  # IP to use if MAC address lookup fails
PING_INTERVAL = 10  # seconds
FTP_PORT = 21
FTP_USERNAME = "pirecorder"
FTP_PASSWORD = "recorderpi"
# FTP_ROOT_DIR will be determined dynamically based on the actual user

def get_ip_from_mac(mac_address):
    """Get IP address from MAC address using manual ping sweep and ARP table"""
    try:
        print("Performing manual network scan to populate ARP cache...")
        
        # Get local network range using ip route
        result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
        network_base = None
        
        for line in result.stdout.split('\n'):
            # Look for default route or local network
            if 'src' in line and ('192.168' in line or '10.' in line or '172.' in line):
                parts = line.split()
                for part in parts:
                    if ('192.168' in part or '10.' in part or '172.' in part):
                        # Extract base network (e.g., 192.168.1 from 192.168.1.40)
                        if '/' in part:
                            network_base = part.split('/')[0].rsplit('.', 1)[0]
                        else:
                            network_base = part.rsplit('.', 1)[0]
                        break
                if network_base:
                    break
        
        if not network_base:
            # Try to get it from current IP
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                current_ip = result.stdout.strip().split()[0]
                network_base = current_ip.rsplit('.', 1)[0]
                print(f"Using current IP to determine network: {current_ip}")
        
        if not network_base:
            # Final fallback
            network_base = "192.168.1"
            print(f"Could not detect network, using fallback: {network_base}.x")
        else:
            print(f"Detected network base: {network_base}.x")
        
        # Manual ping sweep to populate ARP cache
        print("Pinging all possible IPs to populate ARP cache...")
        
        # Use threading to ping multiple IPs simultaneously
        import threading
        import queue
        
        def ping_worker(ip_queue):
            while True:
                try:
                    ip = ip_queue.get(timeout=1)
                    # Quick ping with 1 second timeout
                    subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                 capture_output=True, text=True)
                    ip_queue.task_done()
                except queue.Empty:
                    break
                except:
                    ip_queue.task_done()
        
        # Create queue and add all IPs to ping
        ip_queue = queue.Queue()
        
        # Add common IP ranges
        for i in range(1, 255):
            ip_queue.put(f"{network_base}.{i}")
        
        # Start worker threads
        threads = []
        for _ in range(20):  # 20 parallel ping threads
            t = threading.Thread(target=ping_worker, args=(ip_queue,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Wait for all pings to complete (max 15 seconds)
        try:
            ip_queue.join()
        except KeyboardInterrupt:
            print("Ping sweep interrupted")
        
        print("Ping sweep completed, checking ARP table...")
        
        # Now check ARP table for our MAC address
        arp_result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        
        if arp_result.returncode == 0:
            print("Searching ARP table for target MAC...")
            for line in arp_result.stdout.split('\n'):
                if mac_address.lower() in line.lower():
                    # Extract IP address from line like: hostname (192.168.1.100) at 14:98:77:7c:8f:08 [ether] on wlan0
                    import re
                    ip_match = re.search(r'\(([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\)', line)
                    if ip_match:
                        found_ip = ip_match.group(1)
                        print(f"✓ Found target MAC {mac_address} at IP {found_ip}")
                        return found_ip
        
        # If still not found, try arp-scan as final attempt
        print("MAC not found in ARP table, trying arp-scan as backup...")
        try:
            arpscan_result = subprocess.run(['sudo', 'arp-scan', '--localnet'], 
                                          capture_output=True, text=True, timeout=20)
            
            if arpscan_result.returncode == 0:
                for line in arpscan_result.stdout.split('\n'):
                    if mac_address.lower() in line.lower():
                        parts = line.split()
                        if len(parts) >= 2:
                            ip_address = parts[0]
                            found_mac = parts[1]
                            print(f"✓ Found device via arp-scan: {ip_address} -> {found_mac}")
                            return ip_address
        except FileNotFoundError:
            print("arp-scan not available, that's ok")
        except Exception as e:
            print(f"arp-scan failed: {e}")
        
        # Show debugging info
        print(f"\n✗ Target MAC address {mac_address} not found")
        print("Devices currently in ARP table:")
        if arp_result.returncode == 0:
            for line in arp_result.stdout.split('\n'):
                if '(' in line and 'at' in line and ':' in line:
                    print(f"  {line.strip()}")
        
        return None
        
    except Exception as e:
        print(f"Error during network scan: {e}")
        return None

def ping_device(ip_address):
    """Ping device to keep connection alive"""
    while True:
        try:
            # Use ping command (works on Linux/Raspberry Pi)
            result = subprocess.run(['ping', '-c', '1', '-W', '2', ip_address], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Ping successful to {ip_address} at {time.strftime('%H:%M:%S')}")
            else:
                print(f"✗ Ping failed to {ip_address} at {time.strftime('%H:%M:%S')}")
                
        except Exception as e:
            print(f"Error pinging {ip_address}: {e}")
        
        time.sleep(PING_INTERVAL)

def setup_ftp_directory():
    """Create FTP directory if it doesn't exist and handle permissions"""
    # Get the original user who called sudo
    original_user = os.environ.get('SUDO_USER', 'pi')  # fallback to 'pi'
    
    # Get user's home directory
    try:
        user_info = pwd.getpwnam(original_user)
        user_home = user_info.pw_dir
        user_uid = user_info.pw_uid
        user_gid = user_info.pw_gid
    except KeyError:
        print(f"Warning: Could not find user '{original_user}', using /home/pi")
        user_home = "/home/pi"
        user_uid = 1000
        user_gid = 1000
    
    # Use the actual user's home directory
    ftp_root = os.path.join(user_home, "Desktop", "scout-videos")
    
    # Create directory if it doesn't exist
    ftp_path = Path(ftp_root)
    ftp_path.mkdir(parents=True, exist_ok=True)
    
    # Change ownership back to the original user if running as root
    if os.geteuid() == 0:  # Running as root
        try:
            # Change ownership of the directory and all contents
            for root, dirs, files in os.walk(ftp_root):
                os.chown(root, user_uid, user_gid)
                for dir_name in dirs:
                    os.chown(os.path.join(root, dir_name), user_uid, user_gid)
                for file_name in files:
                    os.chown(os.path.join(root, file_name), user_uid, user_gid)
        except OSError as e:
            print(f"Warning: Could not change ownership: {e}")
    
    print(f"FTP directory ready: {ftp_root}")
    print(f"Directory owner: {original_user}")
    return ftp_root

def start_ftp_server(ftp_root_dir):
    """Start FTP server using pyftpdlib"""
    try:
        from pyftpdlib.authorizers import DummyAuthorizer
        from pyftpdlib.handlers import FTPHandler
        from pyftpdlib.servers import FTPServer
        
        # Create authorizer and add user
        authorizer = DummyAuthorizer()
        authorizer.add_user(FTP_USERNAME, FTP_PASSWORD, ftp_root_dir, perm='elradfmwMT')
        
        # Create handler and server
        handler = FTPHandler
        handler.authorizer = authorizer
        handler.banner = "Raspberry Pi Scout Videos FTP Server"
        
        # Create server
        server = FTPServer(('0.0.0.0', FTP_PORT), handler)
        server.max_cons = 256
        server.max_cons_per_ip = 5
        
        print(f"Starting FTP server on port {FTP_PORT}")
        print(f"Username: {FTP_USERNAME}")
        print(f"Password: {FTP_PASSWORD}")
        print(f"Root directory: {ftp_root_dir}")
        print("FTP server is running...")
        
        server.serve_forever()
        
    except ImportError:
        print("Error: pyftpdlib not installed. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyftpdlib'])
        print("Please run the script again after installation.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied to bind to port {FTP_PORT}")
        print("Try running with sudo or use a port above 1024")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting FTP server: {e}")
        sys.exit(1)

def main():
    print("Raspberry Pi Network Keep-Alive and FTP Server")
    print("=" * 50)
    
    # Setup FTP directory with proper permissions
    ftp_root_dir = setup_ftp_directory()
    
    # Get IP address from MAC address
    print(f"Looking up IP address for MAC: {MAC_ADDRESS}")
    target_ip = get_ip_from_mac(MAC_ADDRESS)
    
    if not target_ip:
        print(f"Could not find IP address for MAC: {MAC_ADDRESS}")
        print(f"Using fallback IP address: {FALLBACK_IP}")
        target_ip = FALLBACK_IP
    
    print(f"Target IP: {target_ip}")
    print(f"Will ping every {PING_INTERVAL} seconds")
    
    # Start ping thread
    ping_thread = threading.Thread(target=ping_device, args=(target_ip,), daemon=True)
    ping_thread.start()
    print("Network keep-alive pinging started")
    
    # Start FTP server (this will block)
    try:
        start_ftp_server(ftp_root_dir)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()
