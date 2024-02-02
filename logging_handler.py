import logging
import logging.config

# Define your custom logging configuration
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)-8s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        # 'detailed': {
        #     'format': '%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s',
        #     'datefmt': '%Y-%m-%d %H:%M:%S'
        # }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard'
        },
        # 'file': {
        #     'class': 'logging.FileHandler',
        #     'filename': 'app.log',
        #     'level': 'DEBUG',
        #     'formatter': 'detailed'
        # }
    },
    'root': {
        'handlers': ['console', 
                    #  'file'
                     ],
        'level': 'DEBUG'
    }
}

# # Configure logging using the custom configuration
# logging.config.dictConfig(logging_config)

# # Use the logger
# logger = logging.getLogger(__name__)