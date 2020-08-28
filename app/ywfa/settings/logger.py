__all__ = (
    'LOGGING',
)


def _logging_path(filename):
    import os
    path = os.path.expanduser(
        os.path.expandvars(
            os.path.join(os.environ.get('DJANGO_LOGDIR', f'{os.getcwd()}/logs'), filename)
        )
    )
    with open(path, 'w+') as _:
        pass
    return path


def _mb(val: int):
    return 1024 * 1024 * val


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s.%(msecs)03d] %(levelname)-18s %(message)s (%(name)s:%(lineno)s)",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': _logging_path("info.log"),
            'formatter': 'standard',
            'maxBytes': _mb(50),
            'backupCount': 3,
        },
        'debuglog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': _logging_path("debug.log"),
            'maxBytes': _mb(250),
            'backupCount': 5,
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        '': {
            'handlers': ['console', 'debuglog', 'logfile'],
            'level': 'DEBUG',
        },
    },
}
