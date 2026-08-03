"""Entry point của chương trình — Hệ thống quản lý cửa hàng mini.
 
Chạy: python main.py
 
Tự động khởi tạo database (tạo bảng) nếu file DB chưa tồn tại, cấu hình
logging, rồi chạy vòng lặp menu CLI chính đến khi người dùng chọn thoát.
"""


from pathlib import Path

from src.cli.app import run
from src.config.logging_config import configure_logging
from src.config.settings import settings
from src.database.init_db import init_db

def main() -> None:
    configure_logging()

    if not Path(settings.database_path).exists():
        init_db()

    run()

if __name__ == "__main__":
    main()
