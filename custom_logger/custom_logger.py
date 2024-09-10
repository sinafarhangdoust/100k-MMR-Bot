from threading import Lock
import logging


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class ChatDota2Logger(metaclass=SingletonMeta):
    """
    A Logger class implemented as a singleton.
    """

    def __init__(self, log_file: str = "app.log") -> None:
        """
        Initialize the logger with a file handler.
        """
        self.logger = logging.getLogger("ChatDota2Logger")
        self.logger.setLevel(logging.DEBUG)

        # Prevent adding multiple handlers if the logger already has handlers
        if not self.logger.handlers:
            # Create file handler which logs messages to a file
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)

            # Create console handler with a higher log level
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # Create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Add the handlers to the logger
            # self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def debug(self, message: str, *args) -> None:
        """
        Log a debug message with % formatting support.
        """
        self.logger.debug(message, *args)

    def info(self, message: str, *args) -> None:
        """
        Log an informational message with % formatting support.
        """
        self.logger.info(message, *args)

    def warning(self, message: str, *args) -> None:
        """
        Log a warning message with % formatting support.
        """
        self.logger.warning(message, *args)

    def error(self, message: str, *args) -> None:
        """
        Log an error message with % formatting support.
        """
        self.logger.error(message, *args)

    def critical(self, message: str, *args) -> None:
        """
        Log a critical message with % formatting support.
        """
        self.logger.critical(message, *args)
