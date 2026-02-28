import functools
import logging

logger = logging.getLogger(__name__)


def handle_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError:
            raise
        except Exception as e:
            logger.exception("Unexpected error in %s", func.__name__)
            raise RuntimeError(f"Internal error in {func.__name__}") from e
    return wrapper
