from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.environ.get("db_host")
db_name = os.environ.get("db_name")
db_user = os.environ.get("db_user")
db_password = os.environ.get("db_password")
api_key = os.environ.get("api_key")
token = os.environ.get("token")