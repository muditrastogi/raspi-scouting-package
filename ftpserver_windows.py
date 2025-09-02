#!/usr/bin/env python3
"""
Windows FTP Server
A Windows-compatible version of ftpserver.py for the Raspberry Pi Scouting Package
"""

import os
import sys
import time
import threading
from pathlib import Path
import logging
from datetime import datetime
import argparse

try:
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.handlers import FTPHandler
    from pyftpdlib.servers import FTPServer
    PYFTPDLIB_AVAILABLE = True
except ImportError:
    PYFTPDLIB_AVAILABLE = False
    print("Warning: pyftpdlib not available. Install with: pip install pyftpdlib")

class WindowsFTPServer:
    def __init__(self, username="pirecorder", password="recorderpi", port=21, 
                 root_dir=None, max_connections=10):
        self.username = username
        self.password = password
        self.port = port
        self.root_dir = root_dir or (Path.home() / "Desktop" / "scout-videos")
        self.max_connections = max_connections
        
        # Ensure root directory exists
        self.root_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Server instance
        self.server = None
        self.is_running = False
        
        # Keep-alive settings
        self.keep_alive_enabled = True
        self.keep_alive_interval = 60  # seconds
        
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory
        logs_dir = Path.home() / "Desktop" / "systemlogs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / 'ftp_server.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_authorizer(self):
        """Create FTP authorizer with user permissions"""
        try:
            authorizer = DummyAuthorizer()
            
            # Add user with read/write permissions to root directory
            authorizer.add_user(
                self.username, 
                self.password, 
                str(self.root_dir), 
                perm="elradfmwMT"
            )
            
            # Add anonymous user with read-only access
            authorizer.add_anonymous(str(self.root_dir), perm="elr")
            
            self.logger.info(f"Created FTP authorizer for user: {self.username}")
            return authorizer
            
        except Exception as e:
            self.logger.error(f"Error creating authorizer: {e}")
            return None
    
    def create_handler(self, authorizer):
        """Create FTP handler with custom settings"""
        try:
            handler = FTPHandler
            handler.authorizer = authorizer
            
            # Custom banner
            handler.banner = "Windows FTP Server - Raspberry Pi Scouting Package"
            
            # Connection limits
            handler.max_login_attempts = 3
            handler.timeout = 300  # 5 minutes
            
            # Logging
            handler.log_prefix = '%(remote_ip)s:%(remote_port)s-[%(username)s]'
            
            self.logger.info("Created FTP handler with custom settings")
            return handler
            
        except Exception as e:
            self.logger.error(f"Error creating handler: {e}")
            return None
    
    def start_server(self):
        """Start the FTP server"""
        if not PYFTPDLIB_AVAILABLE:
            self.logger.error("pyftpdlib not available. Cannot start FTP server.")
            return False
        
        try:
            # Create authorizer
            authorizer = self.create_authorizer()
            if not authorizer:
                return False
            
            # Create handler
            handler = self.create_handler(authorizer)
            if not handler:
                return False
            
            # Create server
            self.server = FTPServer(
                ('0.0.0.0', self.port),
                handler,
                max_cons=self.max_connections,
                max_cons_per_ip=5
            )
            
            # Start server
            self.server.serve_forever()
            
        except Exception as e:
            self.logger.error(f"Error starting FTP server: {e}")
            return False
        
        return True
    
    def start_server_async(self):
        """Start FTP server in a separate thread"""
        if self.is_running:
            self.logger.warning("FTP server is already running")
            return False
        
        self.is_running = True
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()
        
        self.logger.info(f"FTP server started on port {self.port}")
        self.logger.info(f"Root directory: {self.root_dir}")
        self.logger.info(f"Username: {self.username}")
        self.logger.info(f"Max connections: {self.max_connections}")
        
        return True
    
    def stop_server(self):
        """Stop the FTP server"""
        if not self.is_running:
            self.logger.warning("FTP server is not running")
            return False
        
        try:
            self.is_running = False
            
            if self.server:
                self.server.close_all()
                self.logger.info("FTP server stopped")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping FTP server: {e}")
            return False
    
    def get_server_status(self):
        """Get current server status"""
        if not self.server:
            return {
                'status': 'stopped',
                'port': self.port,
                'root_dir': str(self.root_dir),
                'username': self.username,
                'max_connections': self.max_connections,
                'current_connections': 0
            }
        
        try:
            return {
                'status': 'running' if self.is_running else 'stopped',
                'port': self.port,
                'root_dir': str(self.root_dir),
                'username': self.username,
                'max_connections': self.max_connections,
                'current_connections': len(self.server.connections) if hasattr(self.server, 'connections') else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting server status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def list_files(self, directory=None):
        """List files in the FTP root directory"""
        try:
            target_dir = Path(directory) if directory else self.root_dir
            
            if not target_dir.exists():
                return []
            
            files = []
            for item in target_dir.iterdir():
                if item.is_file():
                    stat = item.stat()
                    files.append({
                        'name': item.name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': 'file'
                    })
                elif item.is_dir():
                    stat = item.stat()
                    files.append({
                        'name': item.name,
                        'size': 0,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': 'directory'
                    })
            
            return sorted(files, key=lambda x: (x['type'], x['name']))
            
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return []
    
    def get_directory_size(self, directory=None):
        """Get total size of directory in bytes"""
        try:
            target_dir = Path(directory) if directory else self.root_dir
            
            if not target_dir.exists():
                return 0
            
            total_size = 0
            for item in target_dir.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
            
            return total_size
            
        except Exception as e:
            self.logger.error(f"Error calculating directory size: {e}")
            return 0
    
    def cleanup_old_files(self, days_to_keep=30):
        """Clean up files older than specified days"""
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 3600)
            deleted_count = 0
            deleted_size = 0
            
            for item in self.root_dir.rglob('*'):
                if item.is_file():
                    if item.stat().st_mtime < cutoff_time:
                        try:
                            file_size = item.stat().st_size
                            item.unlink()
                            deleted_count += 1
                            deleted_size += file_size
                            self.logger.info(f"Deleted old file: {item}")
                        except Exception as e:
                            self.logger.error(f"Error deleting file {item}: {e}")
            
            if deleted_count > 0:
                self.logger.info(f"Cleanup completed: {deleted_count} files deleted, "
                               f"{deleted_size / (1024*1024):.2f} MB freed")
            
            return deleted_count, deleted_size
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return 0, 0

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Windows FTP Server')
    parser.add_argument('--port', type=int, default=21, help='FTP server port')
    parser.add_argument('--username', type=str, default='pirecorder', help='FTP username')
    parser.add_argument('--password', type=str, default='recorderpi', help='FTP password')
    parser.add_argument('--root-dir', type=str, help='FTP root directory')
    parser.add_argument('--max-connections', type=int, default=10, help='Maximum connections')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon service')
    
    args = parser.parse_args()
    
    # Create FTP server
    ftp_server = WindowsFTPServer(
        username=args.username,
        password=args.password,
        port=args.port,
        root_dir=args.root_dir,
        max_connections=args.max_connections
    )
    
    if args.daemon:
        # Run as daemon (background service)
        print(f"Starting FTP server on port {args.port}...")
        ftp_server.start_server_async()
        
        try:
            # Keep main thread alive
            while ftp_server.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping FTP server...")
            ftp_server.stop_server()
    else:
        # Run in foreground
        print(f"Starting FTP server on port {args.port}...")
        print("Press Ctrl+C to stop")
        ftp_server.start_server()

if __name__ == "__main__":
    main()
