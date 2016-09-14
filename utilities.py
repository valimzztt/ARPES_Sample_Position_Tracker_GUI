from enum import Enum, unique

@unique
class ErrorPriority(Enum):
    """
    Notice - prints on std err
    Warning - prints on std err and is logged
    Critical - prints on std err and shows a dialog, is logged
    Crash - logs a crash report, adds a dialog and exits
    """
    Notice = 0
    Warning = 1
    Critical = 2
    Crash = 3