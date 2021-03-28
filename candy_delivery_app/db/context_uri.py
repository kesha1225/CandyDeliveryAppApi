import os

from contextvars import ContextVar
from dotenv import load_dotenv

load_dotenv()

DB_URI = ContextVar("DB_URI", default=os.getenv("DB_URI"))
