import contextlib
import logging
from collections.abc import Iterator

from albert.exceptions import AlbertHTTPError

logger = logging.Logger("albert-test-helpers")
logger.setLevel(logging.DEBUG)


@contextlib.contextmanager
def suppress_http_errors() -> Iterator[None]:
    try:
        yield
    except AlbertHTTPError as e:
        logger.warning(f"Encounterd Albert HTTP Error: {e}")
