import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    """ Logger Name: 
            Uses the basename of the provided name (default is the current file) for the logger’s identity.
        
        File Handler:
            Logs messages to a file (self.log_file_path) in the logs directory.
            Sets log level to INFO.
            Uses a simple message format.
        
        Console Handler:
            Logs messages to the console.
            Also set to INFO level and simple format.
            
        Basic Logging Configuration:
            Sets up logging to use both handlers and a simple format.
            
        Structlog Configuration:
            Adds processors for timestamp, log level, event renaming, and JSON rendering.
            Uses structlog’s logger factory for compatibility with Python’s logging.
        
        Return Logger:
            Returns a structlog logger instance with the configured name.
        
        Result
            You get a logger that outputs structured JSON logs to both the console and a file, with timestamps and log levels included.
    """

    def __init__(self, log_dir="logs"):
        # Ensure logs directory exists
        self.logs_dir = os.path.join(os.getcwd(), log_dir)

        # making log directory
        os.makedirs(self.logs_dir, exist_ok=True)

        # Timestamped log file (for persistence)
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

        # Full path for the log file
        self.log_file_path = os.path.join(self.logs_dir, log_file)

    def get_logger(self, name=__file__):
        # Create a logger with the specified name
        logger_name = os.path.basename(name)

        # Configure logging for console + file (both JSON)
        # Filehandler opens a specified file and use it to log messages
        file_handler = logging.FileHandler(self.log_file_path)

        # set the log level
        file_handler.setLevel(logging.INFO)
        # set the log format
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",  # Structlog will handle JSON rendering
            handlers=[console_handler, file_handler]
        )

        # Configure structlog for JSON structured logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger(logger_name)


# --- Usage Example ---
if __name__ == "__main__":
    logger = CustomLogger().get_logger(__file__)
    logger.info("User uploaded a file", user_id=123, filename="report.pdf")
    logger.error("Failed to process PDF", error="File not found", user_id=123)