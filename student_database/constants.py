"""Shared constants for the student database system."""

ALLOWED_STATUSES = ("Active", "Inactive", "Graduated", "Suspended")
YEAR_LEVELS = (1, 2, 3)
ALLOWED_PARENT_RELATIONSHIPS = ("Mother", "Father", "Guardian", "Other")

DEFAULT_DATA_PATH = "data/students.json"
DEFAULT_EXPORT_PATH = "data/student_export.csv"
DEFAULT_LOG_PATH = "data/action_log.txt"

ATTENDANCE_PRESENT = "Present"
ATTENDANCE_ABSENT = "Absent"
