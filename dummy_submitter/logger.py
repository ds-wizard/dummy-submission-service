import logging
import sys

from dummy_submitter.consts import LOGGER_NAME, DEFAULT_LOG_FORMAT, DEFAULT_LOG_LEVEL
from dummy_submitter.config import SubmitterConfig

LOG = logging.getLogger(LOGGER_NAME)


def init_default_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=DEFAULT_LOG_LEVEL,
        format=DEFAULT_LOG_FORMAT,
    )


def init_config_logging(config: SubmitterConfig):
    logging.basicConfig(
        stream=sys.stdout,
        level=config.logging.level,
        format=config.logging.format,
    )
