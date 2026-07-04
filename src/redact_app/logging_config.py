import logging
from datetime import datetime
from pathlib import Path


def configure_logging() -> None:
    """Configure console and file logging for audit-friendly app activity."""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    log_path = logs_dir / f"redact-{datetime.now():%Y%m%d-%H%M%S}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )

    logging.getLogger(__name__).info("Logging initialized path=%s", log_path)

