#!/usr/bin/env python3
"""
Test script for S3 Upload functionality
This script tests the core S3 upload functions without the GUI
"""

import os
import sys
from upload_data_to_s3 import load_s3_config, test_s3_connection, upload_to_s3

def test_config_loading():
    """Test if config file can be loaded properly"""
    print("Testing config file loading...")
    config = load_s3_config()
    
    if config is None:
        print("❌ Failed to load config file")
        return False
    
    if not config.has_section('S3'):
        print("❌ S3 section not found in config")
        return False
    
    required_keys = ['aws_access_key_id', 'aws_secret_access_key', 's3_bucket']
    for key in required_keys:
        if not config.has_option('S3', key):
            print(f"❌ Missing required config key: {key}")
            return False
    
    print("✅ Config file loaded successfully")
    return True

def test_s3_connection_test():
    """Test S3 connection"""
    print("\nTesting S3 connection...")
    try:
        result = test_s3_connection()
        if result:
            print("✅ S3 connection test successful")
            return True
        else:
            print("❌ S3 connection test failed")
            return False
    except Exception as e:
        print(f"❌ S3 connection test error: {e}")
        return False

def test_directory_structure():
    """Test if the expected directory structure exists"""
    print("\nTesting directory structure...")
    
    config = load_s3_config()
    if not config:
        return False
    
    local_dir = config.get('S3', 'local_dir', fallback='')
    if not local_dir:
        print("❌ No local directory configured")
        return False
    
    # Expand environment variables
    local_dir = os.path.expandvars(local_dir)
    
    if not os.path.exists(local_dir):
        print(f"❌ Local directory does not exist: {local_dir}")
        return False
    
    print(f"✅ Local directory exists: {local_dir}")
    
    # Check for subfolders
    try:
        subfolders = [d for d in os.listdir(local_dir) if os.path.isdir(os.path.join(local_dir, d))]
        if subfolders:
            print(f"✅ Found {len(subfolders)} subfolders: {', '.join(subfolders[:5])}")
            if len(subfolders) > 5:
                print(f"   ... and {len(subfolders) - 5} more")
        else:
            print("⚠️  No subfolders found in local directory")
    except Exception as e:
        print(f"❌ Error reading directory: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("S3 Upload System Test")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_s3_connection_test,
        test_directory_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The S3 upload system is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the configuration and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
