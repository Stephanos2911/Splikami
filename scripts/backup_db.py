import os
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

def upload_to_s3():
    """Upload the SQLite database directly to S3."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database file not found at {DATABASE_PATH}")

    # Generate a timestamped filename for the backup
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    s3_filename = f"backups/db_backup_{timestamp}.sqlite3"

    # Initialize the S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION_NAME,
    )

    # Upload the database file directly to S3
    with open(DATABASE_PATH, 'rb') as db_file:
        s3_client.upload_fileobj(db_file, AWS_BUCKET_NAME, s3_filename)

    print(f"Uploaded {s3_filename} to S3 bucket {AWS_BUCKET_NAME}.")

def main():
    """Main function to handle the upload."""
    try:
        upload_to_s3()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
