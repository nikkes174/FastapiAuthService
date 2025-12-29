import os

from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.environ["DB_URL"]
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

LIFETIME_TOKEN = 20
