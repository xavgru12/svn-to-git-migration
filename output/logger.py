import logging


class LoggerFactory:
    @staticmethod
    def create(name: str, log_file: str = "migration.log") -> logging.Logger:
        # Create a custom logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Check if the logger already has handlers to avoid adding multiple handlers to the same logger
        if not logger.hasHandlers():
            # Create handlers
            file_handler = logging.FileHandler(log_file, mode="w")
            stdout_handler = logging.StreamHandler()

            # Create formatters and add them to the handlers
            formatter = logging.Formatter("%(message)s")
            file_handler.setFormatter(formatter)
            stdout_handler.setFormatter(formatter)

            # Add handlers to the logger
            logger.addHandler(file_handler)
            logger.addHandler(stdout_handler)

        return logger
