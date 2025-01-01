import os
import time
from logging.handlers import RotatingFileHandler
from datetime import datetime


class TimedRotatingFileHandlerWithPrefix(RotatingFileHandler):
    """
    Custom log handler that includes timestamps in filenames and handles rotation
    """

    def __init__(
        self,
        filename,
        mode="a",
        maxBytes=50 * 1024 * 1024,
        backupCount=7,
        encoding=None,
        delay=False,
        errors=None,
    ):
        self.baseFilename = filename
        self.currentTimestamp = int(time.time())
        filename = self._get_filename_with_timestamp()
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay, errors)

    def _get_filename_with_timestamp(self):
        """Generate filename with timestamp"""
        dirname = os.path.dirname(self.baseFilename)
        basename = os.path.basename(self.baseFilename)
        name, ext = os.path.splitext(basename)
        timestamp = datetime.fromtimestamp(self.currentTimestamp)
        return os.path.join(
            dirname, f"{name}_{timestamp.strftime('%Y%m%d_%H%M%S')}{ext}"
        )

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        # Update timestamp for new file
        self.currentTimestamp = int(time.time())
        self.baseFilename = self._get_filename_with_timestamp()

        if self.backupCount > 0:
            # Find and remove old log files if exceeding backupCount
            log_dir = os.path.dirname(self.baseFilename)
            base_name = os.path.basename(self.baseFilename)
            name, ext = os.path.splitext(base_name)
            name = name.split("_")[0]  # Get base name without timestamp

            # List all matching log files
            files = [
                f for f in os.listdir(log_dir) if f.startswith(name) and f.endswith(ext)
            ]
            files.sort(reverse=True)

            # Remove the oldest files if exceeding backupCount
            for old_log in files[self.backupCount :]:
                os.remove(os.path.join(log_dir, old_log))

        if not self.delay:
            self.stream = self._open()
