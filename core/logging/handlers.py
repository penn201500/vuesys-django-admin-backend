from django.conf import settings
import os
import time
from logging.handlers import RotatingFileHandler
from django.utils import timezone


class TimedRotatingFileHandlerWithPrefix(RotatingFileHandler):
    """
    Custom log handler that includes timestamps in filenames and handles rotation
    """

    def __init__(
        self,
        filename,
        mode="a",
        maxBytes=settings.LOG_FILE_MAX_SIZE,
        backupCount=settings.LOG_FILE_BACKUP_COUNT,
        encoding=settings.LOG_FILE_ENCODING,
        delay=False,
        errors=None,
    ):
        self.baseFilename = filename
        filename = self._get_filename_with_timestamp()
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay, errors)

    def _get_filename_with_timestamp(self):
        """Generate filename with timestamp"""
        dirname = os.path.dirname(self.baseFilename)
        basename = os.path.basename(self.baseFilename)
        name, ext = os.path.splitext(basename)
        current_date = timezone.localtime().strftime("%Y%m%d")
        return os.path.join(dirname, f"{name}_{current_date}{ext}")

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        if self.backupCount > 0:
            # Find and remove old log files if exceeding backupCount
            log_dir = os.path.dirname(self.baseFilename)
            base_name = os.path.basename(self.baseFilename)
            name, ext = os.path.splitext(base_name)
            name = name.split("_")[0]  # Get base name without date

            # List all matching log files with creation time
            files = []
            for filename in os.listdir(log_dir):
                if filename.startswith(name) and filename.endswith(ext):
                    file_path = os.path.join(log_dir, filename)
                    files.append((os.path.getctime(file_path), file_path))

            # Sort by creation time and remove oldest
            files.sort(reverse=True)

            # Remove the oldest files if exceeding backupCount
            for _, filepath in files[self.backupCount :]:
                try:
                    os.remove(filepath)
                except OSError as e:
                    import sys

                    print(f"Error removing log file {filepath}: {e}", file=sys.stderr)

        if not self.delay:
            self.stream = self._open()
