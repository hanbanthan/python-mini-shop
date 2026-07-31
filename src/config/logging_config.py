"""

- log normal (stock update, notification, ...) -> console
- Logger "audit" (used by AuditLogObserver) -> file logs/audit.log,
seperate file from application

Call configure_logging() only once at the start of the appllication 
(example: in main.py) to configure logging for the entire application.

"""

import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2]/"logs"

def configure_logging(level: int = logging.INFO) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler()
        ],
        force=True,
    )

    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(level)
    audit_logger.propagate = True

    # avoid adding multiple handlers to the audit logger if configure_logging is called multiple times
    if not any (isinstance(h, logging.FileHandler) for h in audit_logger.handlers):
        file_handler = logging.FileHandler(LOG_DIR/"audit.log", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        audit_logger.addHandler(file_handler)