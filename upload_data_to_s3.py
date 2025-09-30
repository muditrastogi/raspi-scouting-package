import os
import boto3
import configparser
from botocore.exceptions import NoCredentialsError
from urllib.parse import urlparse

def parse_s3_uri(s3_uri):
    # Parse the S3 URI into components
    parsed_uri = urlparse(s3_uri)
    bucket_name = parsed_uri.netloc
    key_prefix = parsed_uri.path.lstrip('/')
    return bucket_name, key_prefix



def check_file_exists(bucket_name, file_key):
    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # HeadObject will throw an exception if the file doesn't exist
        s3.head_object(Bucket=bucket_name, Key=file_key)
        return True
    except Exception as e:
        # If the file doesn't exist, catch the exception and return False
        if e.response['Error']['Code'] == '404':
            return False
        else:
            # Handle other exceptions if needed
            print(f"Error: {e}")
            return False




def load_s3_config():
    """Load S3 configuration from config.txt"""
    config = configparser.ConfigParser()
    try:
        config.read('config.txt', encoding='utf-8')
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def test_s3_connection():
    """Test S3 connection using config credentials"""
    config = load_s3_config()
    if not config or not config.has_section('S3'):
        print("S3 configuration not found in config.txt")
        return False
    
    try:
        aws_access_key = config.get('S3', 'aws_access_key_id')
        aws_secret_key = config.get('S3', 'aws_secret_access_key')
        aws_region = config.get('S3', 'aws_region', fallback='ap-south-1')
        
        s3 = boto3.client('s3', 
                         aws_access_key_id=aws_access_key, 
                         aws_secret_access_key=aws_secret_key,
                         region_name=aws_region)
        
        # Test connection by listing buckets
        s3.list_buckets()
        return True
    except Exception as e:
        print(f"S3 connection test failed: {e}")
        return False

def upload_to_s3(local_folder, s3_uri):
    """Upload files to S3 using configuration from config.txt"""
    
    # Load configuration
    config = load_s3_config()
    if not config or not config.has_section('S3'):
        raise Exception("S3 configuration not found in config.txt")
    
    # Get AWS credentials from config
    aws_access_key = config.get('S3', 'aws_access_key_id')
    aws_secret_key = config.get('S3', 'aws_secret_access_key')
    aws_region_name = config.get('S3', 'aws_region', fallback='ap-south-1')

    # Create an S3 client
    s3 = boto3.client('s3', 
                     aws_access_key_id=aws_access_key, 
                     aws_secret_access_key=aws_secret_key,
                     region_name=aws_region_name)
    s3_bucket_name, s3_key_prefix = parse_s3_uri(s3_uri)

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            s3_key = os.path.join(s3_key_prefix, os.path.relpath(local_path, local_folder)).replace("\\", "/")
            ## first json dir

            ## then images
            print (s3_key)

            try:
                print(f"Uploading {local_path} to {s3_bucket_name}/{s3_key}")
                s3.upload_file(local_path, s3_bucket_name, s3_key)
            except FileNotFoundError:
                print(f"The file {local_path} was not found.")
            except NoCredentialsError:
                print("Credentials not available")

if __name__ == "__main__":
    # Example usage - this will be called from the UI
    # For testing purposes, you can uncomment and modify these lines:
    
    # CYCLE = "cycle116"
    # local_folder_to_sync = "/Users/grairobotics/Desktop/batch2/grai-image/nutrifresh/farm1/unit4_parta_s1/{}/".format(CYCLE)
    # s3_bucket_name = "s3://grai-image/nutrifresh/farm1/unit4_parta_s1/{}/".format(CYCLE)
    # upload_to_s3(local_folder_to_sync, s3_bucket_name)
    
    print("S3 Upload module loaded. Use the UI to upload files.")
