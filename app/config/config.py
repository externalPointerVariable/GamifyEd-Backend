import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
drfSecretKey = os.getenv('SECRET_KEY')
print(drfSecretKey)