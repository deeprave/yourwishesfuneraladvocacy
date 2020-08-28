__all__ = (
    'LOGGING'
)


def _logging_path(filename):
    import os
    return os.path.expanduser(
        os.path.join(
            os.environ.get('DJANGO_LOGDIR', f'${os.getcwd()}/logs'),
            filename
        )
    )


def _mb(val: int):
    return 1024 * 1024 * val


# disabled formatters, handlers and loggers
_DISABLED = set()

_FORMATTERS = {
    'standard': {
        'format': "[%(asctime)s.%(msecs)03d] %(levelname)-18s %(message)s [%(name)s:%(lineno)s]",
        'datefmt': "%Y-%m-%d %H:%M:%S"
    },
}

_HANDLERS = {
    'logfile': {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': _logging_path("info.log"),
        'formatter': 'formatter-standard',
        'maxBytes': _mb(50),
        'backupCount': 3,
    },
    'debuglog': {
        'level': 'DEBUG',
        'class': 'logging.handlers.RotatingFileHandler',
        'formatter': 'formatter-standard',
        'filename': _logging_path("debug.log"),
        'maxBytes': _mb(250),
        'backupCount': 5,
    },
    'console': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'formatter-standard'
    },
}

_LOGGERS = {
    'django': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
    '': {
        'handlers': ['console', 'debuglog', 'logfile'],
        'level': 'DEBUG',
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {name: formatter for name, formatter in _FORMATTERS.items() if name not in _DISABLED},
    'handlers': {name: handler for name, handler in _HANDLERS.items() if name not in _DISABLED},
    'loggers': {name: logger for name, logger in _LOGGERS.items() if name not in _DISABLED},
}
