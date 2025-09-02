#!/usr/bin/env python3
"""
Windows Cleanup Script
A Windows-compatible version of delete_except_newest.sh for the Raspberry Pi Scouting Package
"""

import os
import sys
import glob
from pathlib import Path
import argparse
from datetime import datetime
import logging

class WindowsCleanupScript:
    def __init__(self, target_dir=None, file_pattern="*.mp4", keep_count=1):
        self.target_dir = Path(target_dir) if target_dir else (Path.home() / "Desktop" / "scout-videos")
        self.file_pattern = file_pattern
        self.keep_count = keep_count
        
        # Setup logging
        self.setup_logging()
        
        # Ensure target directory exists
        self.target_dir.mkdir(parents=True, exist_ok=True)
    
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
                logging.FileHandler(logs_dir / 'cleanup_script.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def find_files(self):
        """Find all files matching the pattern in the target directory"""
        try:
            # Use glob to find files recursively
            pattern = str(self.target_dir / "**" / self.file_pattern)
            files = glob.glob(pattern, recursive=True)
            
            # Convert to Path objects and filter out directories
            file_paths = [Path(f) for f in files if Path(f).is_file()]
            
            self.logger.info(f"Found {len(file_paths)} files matching pattern '{self.file_pattern}'")
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error finding files: {e}")
            return []
    
    def get_file_info(self, file_path):
        """Get file information including modification time and size"""
        try:
            stat = file_path.stat()
            return {
                'path': file_path,
                'modified': stat.st_mtime,
                'size': stat.st_size,
                'modified_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def sort_files_by_date(self, files):
        """Sort files by modification date (newest first)"""
        try:
            file_info_list = []
            
            for file_path in files:
                file_info = self.get_file_info(file_path)
                if file_info:
                    file_info_list.append(file_info)
            
            # Sort by modification time (newest first)
            file_info_list.sort(key=lambda x: x['modified'], reverse=True)
            
            return file_info_list
            
        except Exception as e:
            self.logger.error(f"Error sorting files: {e}")
            return []
    
    def cleanup_files(self, dry_run=False):
        """Clean up files, keeping only the newest ones"""
        try:
            # Find all matching files
            files = self.find_files()
            
            if not files:
                self.logger.info("No files found to clean up")
                return {
                    'total_files': 0,
                    'files_kept': 0,
                    'files_deleted': 0,
                    'space_freed_mb': 0
                }
            
            # Sort files by date
            sorted_files = self.sort_files_by_date(files)
            
            if not sorted_files:
                self.logger.warning("No valid files found after sorting")
                return {
                    'total_files': len(files),
                    'files_kept': 0,
                    'files_deleted': 0,
                    'space_freed_mb': 0
                }
            
            # Determine which files to keep and delete
            files_to_keep = sorted_files[:self.keep_count]
            files_to_delete = sorted_files[self.keep_count:]
            
            self.logger.info(f"Total files: {len(sorted_files)}")
            self.logger.info(f"Files to keep: {len(files_to_keep)}")
            self.logger.info(f"Files to delete: {len(files_to_delete)}")
            
            # Show files to be kept
            if files_to_keep:
                self.logger.info("Files to keep:")
                for file_info in files_to_keep:
                    self.logger.info(f"  ✓ {file_info['path'].name} ({file_info['modified_str']})")
            
            # Show files to be deleted
            if files_to_delete:
                self.logger.info("Files to delete:")
                for file_info in files_to_delete:
                    self.logger.info(f"  ✗ {file_info['path'].name} ({file_info['modified_str']})")
            
            # Perform cleanup
            if dry_run:
                self.logger.info("DRY RUN MODE - No files will be deleted")
                return {
                    'total_files': len(sorted_files),
                    'files_kept': len(files_to_keep),
                    'files_deleted': len(files_to_delete),
                    'space_freed_mb': sum(f['size'] for f in files_to_delete) / (1024 * 1024)
                }
            
            # Delete files
            deleted_count = 0
            space_freed = 0
            
            for file_info in files_to_delete:
                try:
                    file_path = file_info['path']
                    file_size = file_info['size']
                    
                    # Delete the file
                    file_path.unlink()
                    
                    deleted_count += 1
                    space_freed += file_size
                    
                    self.logger.info(f"Deleted: {file_path.name}")
                    
                except Exception as e:
                    self.logger.error(f"Error deleting {file_info['path'].name}: {e}")
            
            # Summary
            space_freed_mb = space_freed / (1024 * 1024)
            
            self.logger.info(f"Cleanup completed:")
            self.logger.info(f"  - Files kept: {len(files_to_keep)}")
            self.logger.info(f"  - Files deleted: {deleted_count}")
            self.logger.info(f"  - Space freed: {space_freed_mb:.2f} MB")
            
            return {
                'total_files': len(sorted_files),
                'files_kept': len(files_to_keep),
                'files_deleted': deleted_count,
                'space_freed_mb': space_freed_mb
            }
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return {
                'total_files': 0,
                'files_kept': 0,
                'files_deleted': 0,
                'space_freed_mb': 0,
                'error': str(e)
            }
    
    def cleanup_by_date(self, days_to_keep, dry_run=False):
        """Clean up files older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            
            # Find all matching files
            files = self.find_files()
            
            if not files:
                self.logger.info("No files found to clean up")
                return {
                    'total_files': 0,
                    'files_kept': 0,
                    'files_deleted': 0,
                    'space_freed_mb': 0
                }
            
            # Get file info and filter by date
            files_to_keep = []
            files_to_delete = []
            
            for file_path in files:
                file_info = self.get_file_info(file_path)
                if file_info:
                    if file_info['modified'] > cutoff_time:
                        files_to_keep.append(file_info)
                    else:
                        files_to_delete.append(file_info)
            
            self.logger.info(f"Total files: {len(files)}")
            self.logger.info(f"Files to keep (newer than {days_to_keep} days): {len(files_to_keep)}")
            self.logger.info(f"Files to delete (older than {days_to_keep} days): {len(files_to_delete)}")
            
            # Show files to be deleted
            if files_to_delete:
                self.logger.info("Files to delete (old files):")
                for file_info in files_to_delete:
                    self.logger.info(f"  ✗ {file_info['path'].name} ({file_info['modified_str']})")
            
            # Perform cleanup
            if dry_run:
                self.logger.info("DRY RUN MODE - No files will be deleted")
                return {
                    'total_files': len(files),
                    'files_kept': len(files_to_keep),
                    'files_deleted': len(files_to_delete),
                    'space_freed_mb': sum(f['size'] for f in files_to_delete) / (1024 * 1024)
                }
            
            # Delete old files
            deleted_count = 0
            space_freed = 0
            
            for file_info in files_to_delete:
                try:
                    file_path = file_info['path']
                    file_size = file_info['size']
                    
                    # Delete the file
                    file_path.unlink()
                    
                    deleted_count += 1
                    space_freed += file_size
                    
                    self.logger.info(f"Deleted old file: {file_path.name}")
                    
                except Exception as e:
                    self.logger.error(f"Error deleting {file_info['path'].name}: {e}")
            
            # Summary
            space_freed_mb = space_freed / (1024 * 1024)
            
            self.logger.info(f"Date-based cleanup completed:")
            self.logger.info(f"  - Files kept: {len(files_to_keep)}")
            self.logger.info(f"  - Files deleted: {deleted_count}")
            self.logger.info(f"  - Space freed: {space_freed_mb:.2f} MB")
            
            return {
                'total_files': len(files),
                'files_kept': len(files_to_keep),
                'files_deleted': deleted_count,
                'space_freed_mb': space_freed_mb
            }
            
        except Exception as e:
            self.logger.error(f"Error during date-based cleanup: {e}")
            return {
                'total_files': 0,
                'files_kept': 0,
                'files_deleted': 0,
                'space_freed_mb': 0,
                'error': str(e)
            }

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Windows Cleanup Script')
    parser.add_argument('--target-dir', type=str, help='Target directory to clean up')
    parser.add_argument('--pattern', type=str, default='*.mp4', help='File pattern to match')
    parser.add_argument('--keep-count', type=int, default=1, help='Number of newest files to keep')
    parser.add_argument('--days', type=int, help='Keep files newer than specified days')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    # Create cleanup script
    cleanup = WindowsCleanupScript(
        target_dir=args.target_dir,
        file_pattern=args.pattern,
        keep_count=args.keep_count
    )
    
    # Perform cleanup
    if args.days:
        # Date-based cleanup
        result = cleanup.cleanup_by_date(args.days, dry_run=args.dry_run)
    else:
        # Count-based cleanup
        result = cleanup.cleanup_files(dry_run=args.dry_run)
    
    # Exit with appropriate code
    if result.get('error'):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
