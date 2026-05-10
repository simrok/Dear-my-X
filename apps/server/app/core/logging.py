"""로깅 설정.

표준 로깅 + loguru 를 같이 사용. uvicorn / sqlalchemy 로거를 loguru 로 통일한다.
"""

from __future__ import annotations

import logging
import sys

from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """표준 logging → loguru 로 라우팅하는 핸들러."""

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logging() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.APP_LOG_LEVEL,
        backtrace=settings.APP_DEBUG,
        diagnose=settings.APP_DEBUG,
        enqueue=True,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for noisy in ("uvicorn", "uvicorn.access", "uvicorn.error", "sqlalchemy.engine"):
        logging.getLogger(noisy).handlers = [InterceptHandler()]
        logging.getLogger(noisy).propagate = False
