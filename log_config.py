import logging
import logging.config
import os


def setup_logging():
    # Создание папки + файлов
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Конфиг
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            },
        },
        'handlers': {
            # Файл для WARN и INFO
            'file_warn_info': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'{log_dir}/app_warn_info.log',
                'maxBytes': 10485760,
                'backupCount': 5,
                'formatter': 'standard',
                'encoding': 'utf-8'
            },
            # Файл для DEBUG
            'file_debug': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'{log_dir}/app_debug.log',
                'maxBytes': 10485760,
                'backupCount': 5,
                'formatter': 'detailed',
                'encoding': 'utf-8'
            },
            'console': {
                   'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                }
        },
        'loggers': {
            '': {
                'handlers': ['file_warn_info', 'file_debug', 'console'],
                'level': 'DEBUG',
                'propagate': True
            },
            'hotel': {
                'handlers': ['file_warn_info', 'file_debug'],
                'level': 'DEBUG',
                'propagate': False
            },
            'person': {
                'handlers': ['file_warn_info', 'file_debug'],
                'level': 'DEBUG',
                'propagate': False
            },
            'room': {
                'handlers': ['file_warn_info', 'file_debug'],
                'level': 'DEBUG',
                'propagate': False
            },
            'booking': {
                'handlers': ['file_warn_info', 'file_debug'],
                'level': 'DEBUG',
                'propagate': False
            }
        }
    }

    logging.config.dictConfig(logging_config)

    logger = logging.getLogger('app')
    logger.info("=" * 50)
    logger.info("Приложение запущено")
    logger.info("=" * 50)


def get_logger(name):
    return logging.getLogger(name)