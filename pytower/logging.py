import logging
import logging.config
import os

from colorama import Fore, Style, init
from threading import Lock
import yaml

from .__config__ import root_directory

# Initialize colorama for Windows support
init(autoreset=True)

DEBUG_LEVEL_NUM = logging.DEBUG
INFO_LEVEL_NUM = logging.INFO

# Define a custom log level
SUCCESS_LEVEL_NUM = 25  # A level between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL_NUM, "\nSuccess")

WARNING_LEVEL_NUM = logging.WARNING
ERROR_LEVEL_NUM = logging.ERROR
CRITICAL_LEVEL_NUM = logging.CRITICAL

PRINT_LOCK = Lock()


# Create a logger method for the new "SUCCESS" level
def success(self, message, *args, **kws):
    # If the logger is enabled for the SUCCESS level
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        # Log with the SUCCESS level
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)


# Add the success method to the logger
logging.Logger.success = success


class ColorFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Define color schemes for different log levels
    LOG_COLORS = {
        DEBUG_LEVEL_NUM: Fore.WHITE,
        INFO_LEVEL_NUM: Fore.LIGHTWHITE_EX,
        SUCCESS_LEVEL_NUM: Fore.GREEN,
        WARNING_LEVEL_NUM: Fore.YELLOW,
        ERROR_LEVEL_NUM: Fore.RED,
        CRITICAL_LEVEL_NUM: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        # Modify format only if the log level is INFO or DEBUG
        if record.levelno in [logging.DEBUG, logging.INFO]:
            self._style._fmt = '%(message)s'
        else:
            # Default format with levelname for other levels
            self._style._fmt = '%(levelname)s: %(message)s'

        # Get the original log message
        log_msg = super().format(record)

        # Apply the color based on the log level
        color = self.LOG_COLORS.get(record.levelno, '')
        return f'{color}{log_msg}{Style.RESET_ALL}'


initialized = False


def logging_init():
    global initialized
    if not initialized:
        with open(os.path.join(os.path.join(root_directory, 'pytower'), 'logging.yaml')) as fd:
            yaml_config = yaml.safe_load(fd)
            logging.config.dictConfig(yaml_config)

        logger = logging.getLogger()

        # Setup FileHandler and set log directory to root_directory
        log_path = os.path.join(root_directory, 'output.log')
        file_handler = logging.FileHandler(log_path, mode='a')
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    initialized = True


def log(level: int, msg: str):
    logger = logging.getLogger()
    with PRINT_LOCK:
        logging_init()
        logger.log(level, msg)


def debug(msg: str):
    log(DEBUG_LEVEL_NUM, msg)


def info(msg: str):
    log(INFO_LEVEL_NUM, msg)


def success(msg: str):
    log(SUCCESS_LEVEL_NUM, msg)


def warning(msg: str):
    log(WARNING_LEVEL_NUM, msg)


def error(msg: str):
    log(ERROR_LEVEL_NUM, msg)


def critical(msg: str):
    log(CRITICAL_LEVEL_NUM, msg)
