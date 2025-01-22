import os
import tarfile
import boto3
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get AWS S3 configuration from environment or settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = 'splikami'
AWS_REGION_NAME = 'us-east-1'

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / 'database' / 'db.sqlite3'
BACKUP_DIR = BASE_DIR / 'backups'

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup():
    """Create a timestamped backup of the SQLite database."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_filename = f'backup/db_backup_{timestamp}.tar.gz'
    backup_filepath = BACKUP_DIR / backup_filename

    with tarfile.open(backup_filepath, 'w:gz') as tar:
        tar.add(DATABASE_PATH, arcname=DATABASE_PATH.name)

    return backup_filepath, backup_filename

def upload_to_s3(file_path, file_name):
    """Upload a file to AWS S3."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION_NAME,
    )

    s3_client.upload_file(str(file_path), AWS_BUCKET_NAME, file_name)
    print(f'Uploaded {file_name} to S3 bucket {AWS_BUCKET_NAME}.')

def clean_local_backup(file_path):
    """Remove the local backup file after upload."""
    os.remove(file_path)
    print(f'Removed local backup file: {file_path}')

def main():
    """Main function to handle backup creation and upload."""
    try:
        backup_filepath, backup_filename = create_backup()
        upload_to_s3(backup_filepath, backup_filename)
        clean_local_backup(backup_filepath)
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    main()
