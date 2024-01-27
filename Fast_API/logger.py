import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logger(logger_name, log_file_base):
    log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
    )

    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    loggers = {}

    for level in log_levels:
        log_file = f"Logs/{level}/{level.lower()}_{log_file_base}.log"
        logHandler = TimedRotatingFileHandler(
            log_file, when="midnight", interval=1, backupCount=30, delay=True
        )
        logHandler.setFormatter(log_formatter)

        logger_name = f"{logger_name}_{level.lower()}"
        logger = logging.getLogger(logger_name)

        if not logger.handlers:
            logger.addHandler(logHandler)
            logger.setLevel(logging.getLevelName(level))

        loggers[level.lower()] = logger

    return loggers


loggers = setup_logger("app", "logger")
