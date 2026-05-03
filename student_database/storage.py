"""JSON and CSV persistence helpers."""

from __future__ import annotations

import csv
import json
import os
from typing import Iterable

from student_database.models import Student, student_from_dict


def _ensure_parent_folder(file_path: str) -> None:
    folder = os.path.dirname(os.path.abspath(file_path))
    os.makedirs(folder, exist_ok=True)


def save_students_json(students: Iterable[Student], file_path: str) -> None:
    """Save student records to a JSON file."""
    _ensure_parent_folder(file_path)
    payload = [student.to_dict() for student in students]
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, indent=4)


def load_students_json(file_path: str) -> list[Student]:
    """Load student records from a JSON file."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    if not isinstance(data, list):
        raise ValueError("Student JSON file must contain a list.")
    return [student_from_dict(item) for item in data]


def export_students_csv(students: Iterable[Student], file_path: str) -> None:
    """Export student summary rows to CSV."""
    _ensure_parent_folder(file_path)
    headers = [
        "student_id",
        "name",
        "major",
        "year_level",
        "gpa",
        "average_grade",
        "attendance_percentage",
        "status",
        "category",
    ]
    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for student in students:
            writer.writerow(
                {
                    "student_id": student.student_id,
                    "name": student.name,
                    "major": student.major,
                    "year_level": student.year_level,
                    "gpa": f"{student.gpa():.2f}",
                    "average_grade": f"{student.average_grade():.2f}",
                    "attendance_percentage": (
                        f"{student.attendance_percentage():.2f}"
                    ),
                    "status": student.status,
                    "category": student.student_category(),
                }
            )
