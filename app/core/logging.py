import json
import logging
import sys


class JSONFormater(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%MS%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging(level: int = logging.INFO) -> None:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(JSONFormater())

    logging.basicConfig(level=level, handlers=[stream_handler])
