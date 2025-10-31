import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logging(filename="sftp_transfer.log", interval=7):
    # Rotate daily at midnight, keep 7 days of logs
    handler = TimedRotatingFileHandler(
        filename=filename,
        when="midnight",  # 'S'=Seconds, 'M'=Minutes, 'H'=Hours, 'D'=Days, 'W0'=Monday, etc.
        interval=interval,  # Every 1 day
        backupCount=4,  # Keep 7 backup files
        encoding="utf-8",
    )

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s: %(message)s")
    handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
    )
    return logging.getLogger(__name__)
