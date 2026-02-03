import sys
from datetime import datetime

class StdoutToFile:
    def __init__(self, filepath):
        self.filepath = filepath

    def write(self, message):
        if not message.strip():
            return

        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(f"[STDOUT] {message}")

    def flush(self):
        pass


class StderrToFile:
    def __init__(self, filepath):
        self.filepath = filepath

    def write(self, message):
        if not message.strip():
            return

        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(f"[STDERR] {message}")

    def flush(self):
        pass


def redirect_console_to_file():
    sys.stdout = StdoutToFile("logs/console.log")
    sys.stderr = StderrToFile("logs/console.log")
