from dataclasses import dataclass
import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> None:
        return None

load_dotenv()

@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("DATABASE PATH", "database/store.db")
    max_discount_percent: float = float(os.getenv("MAX DISCOUNT PERCENT", 15.0))
    vip_discount_percent: float = float(os.getenv("VIP DISCOUNT PERCENT", 10.0))
    large_order_threshold: float = float(os.getenv("LARGE_ORDER_THRESHOLD", 5_000_000))
    large_order_extra_discount: float = float(os.getenv("LARGE_ORDER_EXTRA_DISCOUNT", 5.0))

settings = Settings()