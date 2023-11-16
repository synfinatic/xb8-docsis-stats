import logging
from enum import Enum


class LogLevel(Enum):
    """Maps our logging levels to something for humans."""
    error = 'error'
    info = 'info'
    warn = 'warn'
    debug = 'debug'

    def __str__(self):
        return self.value

    @property
    def level(self) -> int:
        levels = {
            'debug': logging.DEBUG,
            'warn': logging.WARNING,
            'info': logging.INFO,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }
        return levels[self.value]
