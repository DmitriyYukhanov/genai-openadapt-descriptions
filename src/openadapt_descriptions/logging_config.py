"""Logging configuration for OpenAdapt Descriptions."""

import logging
import json
from typing import Dict, Any
from . import constants

class StructuredLogger(logging.Logger):
    """Logger that adds structured context to log messages."""
    
    def _log_with_context(self, level: int, msg: str, args, context: Dict[str, Any], **kwargs):
        if context:
            msg = f"{msg} | {json.dumps(context)}"
        super().log(level, msg, *args, **kwargs)

    def info(self, msg: str, *args, extra: Dict[str, Any] = None, **kwargs):
        self._log_with_context(logging.INFO, msg, args, extra or {}, **kwargs)

    def warning(self, msg: str, *args, extra: Dict[str, Any] = None, **kwargs):
        self._log_with_context(logging.WARNING, msg, args, extra or {}, **kwargs)

    def error(self, msg: str, *args, extra: Dict[str, Any] = None, **kwargs):
        self._log_with_context(logging.ERROR, msg, args, extra or {}, **kwargs)

    def debug(self, msg: str, *args, extra: Dict[str, Any] = None, **kwargs):
        self._log_with_context(logging.DEBUG, msg, args, extra or {}, **kwargs)

def setup_logging():
    """Configure logging with the StructuredLogger."""
    logging.setLoggerClass(StructuredLogger)
    logging.basicConfig(
        level=constants.DEFAULT_LOG_LEVEL,
        format=constants.LOG_FORMAT,
        datefmt=constants.LOG_DATE_FORMAT
    ) 