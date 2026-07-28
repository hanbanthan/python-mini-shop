from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("DATABASE PATH", "database/store.db")