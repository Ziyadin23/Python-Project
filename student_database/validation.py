"""Input validation helpers for student records."""

from __future__ import annotations

import re
from datetime import date

from student_database.constants import (
    ALLOWED_PARENT_RELATIONSHIPS,
    ALLOWED_STATUSES,
    YEAR_LEVELS,
)

STUDENT_ID_RE = re.compile(r"^\d+$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9][0-9\s().-]{6,18}$")


def validate_student_id(student_id: str) -> str:
    """Validate and normalize a numeric student ID."""
    value = str(student_id).strip()
    if not STUDENT_ID_RE.fullmatch(value):
        raise ValueError("Student ID must contain numbers only.")
    return value


def validate_name(name: str) -> str:
    """Validate a person's name."""
    value = str(name).strip()
    if not value:
        raise ValueError("Name cannot be empty.")
    if any(char.isdigit() for char in value):
        raise ValueError("Name cannot contain numbers.")
    return value


def validate_age(age: int | str) -> int:
    """Validate a realistic student age."""
    try:
        value = int(age)
    except (TypeError, ValueError) as exc:
        raise ValueError("Age must be a number.") from exc
    if value < 15 or value > 100:
        raise ValueError("Age must be between 15 and 100.")
    return value


def validate_email(email: str) -> str:
    """Validate an email address with the re module."""
    value = str(email).strip()
    if not EMAIL_RE.fullmatch(value):
        raise ValueError("Email address is not valid.")
    return value


def validate_phone(phone: str) -> str:
    """Validate a phone number with the re module."""
    value = str(phone).strip()
    if not PHONE_RE.fullmatch(value):
        raise ValueError("Phone number is not valid.")
    return value


def validate_major(major: str) -> str:
    """Validate a student's major."""
    value = str(major).strip()
    if not value:
        raise ValueError("Major cannot be empty.")
    return value


def validate_year_level(year_level: int | str) -> int:
    """Validate a student year level."""
    try:
        value = int(year_level)
    except (TypeError, ValueError) as exc:
        raise ValueError("Year level must be a number.") from exc
    if value not in YEAR_LEVELS:
        allowed = ", ".join(map(str, YEAR_LEVELS))
        raise ValueError(f"Year level must be one of: {allowed}.")
    return value


def validate_status(status: str) -> str:
    """Validate and normalize a student status."""
    value = str(status).strip().lower()
    for allowed_status in ALLOWED_STATUSES:
        if value == allowed_status.lower():
            return allowed_status
    allowed = ", ".join(ALLOWED_STATUSES)
    raise ValueError(f"Status must be one of: {allowed}.")


def validate_relationship(relationship: str) -> str:
    """Validate and normalize a parent relationship."""
    value = str(relationship).strip().lower()
    for allowed_relation in ALLOWED_PARENT_RELATIONSHIPS:
        if value == allowed_relation.lower():
            return allowed_relation
    allowed = ", ".join(ALLOWED_PARENT_RELATIONSHIPS)
    raise ValueError(f"Relationship must be one of: {allowed}.")


def validate_grade(score: float | int | str) -> float:
    """Validate a grade score from 0 to 100."""
    try:
        value = float(score)
    except (TypeError, ValueError) as exc:
        raise ValueError("Grade must be a number.") from exc
    if value < 0 or value > 100:
        raise ValueError("Grade must be between 0 and 100.")
    return value


def validate_attendance(value: bool | str) -> bool:
    """Validate attendance input and convert it to a boolean."""
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"present", "p", "yes", "y", "true", "1"}:
        return True
    if normalized in {"absent", "a", "no", "n", "false", "0"}:
        return False
    raise ValueError("Attendance must be present or absent.")


def validate_iso_date(value: str | None) -> str:
    """Validate an ISO date string or return today's date."""
    if value is None or str(value).strip() == "":
        return date.today().isoformat()
    text = str(value).strip()
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError("Date must use YYYY-MM-DD format.") from exc
    return text
