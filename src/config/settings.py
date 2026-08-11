import os
from dataclasses import dataclass
from typing import Any

dotenv_load_dotenv: Any
try:
    from dotenv import load_dotenv as dotenv_load_dotenv
except ModuleNotFoundError:
    dotenv_load_dotenv = None


def _load_dotenv() -> bool:
    if dotenv_load_dotenv is None:
        return False
    return dotenv_load_dotenv()


_load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("DATABASE PATH", "database/store.db")
    max_discount_percent: float = float(os.getenv("MAX DISCOUNT PERCENT", 15.0))
    vip_discount_percent: float = float(os.getenv("VIP DISCOUNT PERCENT", 10.0))
    large_order_threshold: float = float(os.getenv("LARGE_ORDER_THRESHOLD", 5_000_000))
    large_order_extra_discount: float = float(os.getenv("LARGE_ORDER_EXTRA_DISCOUNT", 5.0))


settings = Settings()
