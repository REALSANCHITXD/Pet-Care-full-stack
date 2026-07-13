from dotenv import load_dotenv
import os 

# Get the absolute path to secret.env which is in the same directory as this file
env_path = os.path.join(os.path.dirname(__file__), "secret.env")
load_dotenv(dotenv_path=env_path)

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')

JWT_SECRET = os.getenv('SECRET_KEY')
JWT_ALGORITHM = os.getenv('ALGORITHM')
JWT_EXPIRE_MINUTES = int(os.getenv('EXPIRE_MINUTES'))
