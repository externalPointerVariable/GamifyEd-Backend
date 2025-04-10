import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()
drfSecretKey = os.getenv('SECRET_KEY')
tmpPostgres = urlparse(os.getenv("DATABASE_URL"))