"""Manager layer for student database operations."""

from __future__ import annotations

from typing import Iterable

from student_database.constants import DEFAULT_LOG_PATH
from student_database.decorators import log_action
from student_database.models import Student
from student_database.storage import (
    export_students_csv,
    load_students_json,
    save_students_json,
)
from student_database.validation import validate_status, validate_student_id


class StudentManager:
    """Associate and manage many Student objects."""

    def __init__(
        self,
        students: Iterable[Student] | None = None,
        log_path: str | None = DEFAULT_LOG_PATH,
        data_path: str | None = None,
    ) -> None:
        self._students: dict[str, Student] = {}
        self.log_path = log_path
        self.data_path = data_path
        for student in students or []:
            self.add_student(student)

    def _auto_save(self) -> None:
        """Save to JSON if a data path is configured."""
        if self.data_path:
            self.save_json(self.data_path)

    def __len__(self) -> int:
        return len(self._students)

    def __iter__(self):
        return iter(self.all_students())

    @property
    def students(self) -> dict[str, Student]:
        """Return a shallow copy of managed students."""
        return self._students.copy()

    @log_action("Added student")
    def add_student(self, student: Student) -> Student:
        """Add a new student if the ID is unique."""
        if student.student_id in self._students:
            raise ValueError(f"Student ID {student.student_id} already exists.")
        self._students[student.student_id] = student
        self._auto_save()
        return student

    @log_action("Updated student")
    def update_student(self, student_id: str, **fields: object) -> Student:
        """Update editable fields for a student."""
        student = self.get_student(student_id)
        editable_fields = {
            "name",
            "age",
            "email",
            "phone",
            "major",
            "year_level",
            "status",
        }
        unknown_fields = set(fields) - editable_fields
        if unknown_fields:
            names = ", ".join(sorted(unknown_fields))
            raise ValueError(f"Cannot update field(s): {names}.")
        for field_name, value in fields.items():
            if value is not None and value != "":
                setattr(student, field_name, value)
        self._auto_save()
        return student

    @log_action("Deleted student")
    def delete_student(self, student_id: str) -> Student:
        """Delete and return a student."""
        normalized_id = validate_student_id(student_id)
        if normalized_id not in self._students:
            raise KeyError(f"No student found with ID {normalized_id}.")
        student = self._students.pop(normalized_id)
        self._auto_save()
        return student

    @log_action("Added grade")
    def add_grade(self, student_id: str, score: float | int | str) -> float:
        """Add a grade to a student."""
        result = self.get_student(student_id).add_grade(score)
        self._auto_save()
        return result

    @log_action("Recorded attendance")
    def add_attendance(
        self,
        student_id: str,
        present: bool | str,
        record_date: str | None = None,
    ) -> dict[str, object]:
        """Add an attendance record to a student."""
        result = self.get_student(student_id).add_attendance(present, record_date)
        self._auto_save()
        return result

    def get_student(self, student_id: str) -> Student:
        """Return one student by ID."""
        normalized_id = validate_student_id(student_id)
        try:
            return self._students[normalized_id]
        except KeyError as exc:
            raise KeyError(f"No student found with ID {normalized_id}.") from exc

    def all_students(self) -> list[Student]:
        """Return all students sorted by student ID."""
        return sorted(self._students.values(), key=lambda student: student.student_id)

    def search(self, query: str) -> list[Student]:
        """Search students by ID, name, or major."""
        text = str(query).strip().lower()
        if not text:
            return []
        return list(
            filter(
                lambda student: (
                    text in student.student_id.lower()
                    or text in student.name.lower()
                    or text in student.major.lower()
                ),
                self._students.values(),
            )
        )

    def unique_majors(self) -> set[str]:
        """Return all unique majors."""
        return {student.major for student in self._students.values()}

    def filter_by_major(self, major: str) -> list[Student]:
        """Filter students by major."""
        text = str(major).strip().lower()
        return list(
            filter(
                lambda student: student.major.lower() == text,
                self._students.values(),
            )
        )

    def filter_by_year_level(self, year_level: int) -> list[Student]:
        """Filter students by year level."""
        return list(
            filter(
                lambda student: student.year_level == int(year_level),
                self._students.values(),
            )
        )

    def filter_by_status(self, status: str) -> list[Student]:
        """Filter students by status."""
        normalized_status = validate_status(status)
        return list(self.iter_students_by_status(normalized_status))

    def filter_by_gpa(
        self,
        minimum: float = 0.0,
        maximum: float = 4.0,
    ) -> list[Student]:
        """Filter students by GPA range."""
        return list(
            filter(
                lambda student: minimum <= student.gpa() <= maximum,
                self._students.values(),
            )
        )

    def iter_students_by_status(self, status: str):
        """Generate students with a matching status."""
        normalized_status = validate_status(status)
        for student in self.all_students():
            if student.status == normalized_status:
                yield student

    def students_at_risk(self, minimum_attendance: float = 75.0):
        """Generate students with attendance below the target."""
        for student in self.all_students():
            if student.attendance and student.attendance_percentage() < minimum_attendance:
                yield student

    def student_gpa_map(self) -> dict[str, float]:
        """Return student IDs mapped to GPA values using map."""
        pairs = map(
            lambda student: (student.student_id, student.gpa()),
            self._students.values(),
        )
        return dict(pairs)

    def average_class_gpa(self) -> float:
        """Return the average GPA across all students."""
        gpas = list(map(lambda student: student.gpa(), self._students.values()))
        if not gpas:
            return 0.0
        return round(sum(gpas) / len(gpas), 2)

    def save_json(self, file_path: str) -> None:
        """Save students to JSON."""
        save_students_json(self.all_students(), file_path)

    def load_json(self, file_path: str) -> int:
        """Load students from JSON and replace current records."""
        loaded_students = load_students_json(file_path)
        self._students = {student.student_id: student for student in loaded_students}
        return len(self._students)

    def export_csv(self, file_path: str) -> None:
        """Export students to CSV."""
        export_students_csv(self.all_students(), file_path)
