"""
logging_config.py — sets up structured (JSON) logging for the whole
app. Call setup_logging() once, when the app starts.

Everywhere else in the app, you just do:
    import logging
    logger = logging.getLogger(__name__)
    logger.info("something happened", extra={"owner": owner, "file_name": file_name})

...and it automatically comes out as one JSON line, tagged with
whatever request it belongs to.
"""

import logging
import json
import sys
import contextvars
from datetime import datetime, timezone

# Holds the CURRENT request's ID. Set once per request (in main.py's
# middleware, below), then readable from ANYWHERE during that
# request — even deep inside rag_chain.py — without passing it as a
# function argument everywhere. This is what makes correlation work.
request_id_var = contextvars.ContextVar("request_id", default="-")

# Fields logging.LogRecord already carries internally. We use this to
# tell apart "stuff Python's logging module always adds" from "extra
# fields the developer passed in" (like owner= or duration_ms=), so
# only the meaningful custom fields get folded into the JSON output.
_STANDARD_FIELDS = {
    "args", "asctime", "created", "exc_info", "exc_text", "filename",
    "funcName", "levelname", "levelno", "lineno", "module", "msecs",
    "message", "msg", "name", "pathname", "process", "processName",
    "relativeCreated", "stack_info", "thread", "threadName", "taskName",
} 


class JSONFormatter(logging.Formatter):
    """
    Turns each log record into one line of JSON. A JSON line is still
    readable by a human in a pinch, but — unlike a free-text sentence
    — it can also be parsed, filtered, and aggregated by a script or
    a log-management tool. That's the actual point of "structured"
    logging: logs a MACHINE can query, not just a human can read.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "request_id": request_id_var.get(),
        }

        # Fold in anything passed via extra={...} — e.g. owner,
        # file_name, duration_ms, status_code.
        for key, value in record.__dict__.items():
            if key not in payload and key not in _STANDARD_FIELDS:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def setup_logging(level: int = logging.INFO) -> None:
    """
    Call this ONCE, when the app starts. Every logger.info/warning/
    error call anywhere in the app after this point automatically
    goes through the JSON formatter and out to stdout.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.handlers = [handler]  # replace any default handlers Python set up
    root.setLevel(level)