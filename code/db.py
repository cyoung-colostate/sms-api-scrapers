import os
from sqlalchemy import create_engine
import config

DB_HOST = os.getenv('DB_HOST', config.DB_HOST)
DB_USER = os.getenv('DB_USER', config.DB_USER)
DB_PASS = os.getenv('DB_PASS', config.DB_PASS)
DB_NAME = os.getenv('DB_NAME', config.DB_NAME)
DB_PORT = os.getenv('DB_PORT', config.DB_PORT)
DB_URL = os.getenv("DATABASE_URL", f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)