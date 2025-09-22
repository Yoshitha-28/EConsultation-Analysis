import os
from dotenv import load_dotenv
import time

print("--- STARTING DEBUG SCRIPT ---")

# Check if the .env file exists in the current directory
env_path = '.env'
if os.path.exists(env_path):
    print(f"✅ Found .env file at: {os.path.abspath(env_path)}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"❌ Could not find .env file at path: {os.path.abspath(env_path)}")

# List of variables we absolutely need
required_vars = [
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
    'S3_ENDPOINT',
    'S3_ACCESS_KEY',
    'S3_SECRET_KEY',
    'S3_BUCKET',
    'CELERY_BROKER_URL'
]

print("\n--- CHECKING ENVIRONMENT VARIABLES ---")
all_found = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Print only a part of secrets for security
        if 'KEY' in var or 'PASSWORD' in var:
            print(f"✅ Found {var}: {value[:4]}...")
        else:
            print(f"✅ Found {var}: {value}")
    else:
        print(f"❌ NOT FOUND: {var}")
        all_found = False

print("\n--- DEBUG CONCLUSION ---")
if all_found:
    print("✅ SUCCESS: All required environment variables were found!")
else:
    print("❌ FAILURE: One or more required environment variables are MISSING.")

print("\nScript will now hang for 5 minutes to keep the container alive...")
time.sleep(300)