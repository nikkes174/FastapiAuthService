from dotenv import load_dotenv

load_dotenv()

ADMIN_EMAIL = "admin@mail.com"

DATABASE_URL = "sqlite+aiosqlite:///./data/app.db"

JWT_SECRET_KEY = "test-secret-key"
JWT_ALGORITHM = "HS256"
LIFETIME_TOKEN = 20
