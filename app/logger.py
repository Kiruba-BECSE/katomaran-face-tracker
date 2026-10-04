import logging
import os


class EventLogger:

    def __init__(self, log_file):

        folder = os.path.dirname(log_file)

        if folder:
            os.makedirs(
                folder,
                exist_ok=True
            )

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s"
        )

        self.logger = logging.getLogger(
            "KatomaranFaceTracker"
        )

    def info(self, message):

        self.logger.info(message)

    def error(self, message):

        self.logger.error(message)

    def warning(self, message):

        self.logger.warning(message)