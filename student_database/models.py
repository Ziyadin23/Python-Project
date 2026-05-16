"""Domain models for the student database system."""

from __future__ import annotations

from student_database.constants import ATTENDANCE_ABSENT, ATTENDANCE_PRESENT
from student_database.validation import (
    validate_age,
    validate_attendance,
    validate_email,
    validate_grade,
    validate_iso_date,
    validate_major,
    validate_name,
    validate_phone,
    validate_relationship,
    validate_status,
    validate_student_id,
    validate_year_level,
)


class Person:
    """Base class for people in the system."""

    def __init__(self, name: str, age: int, email: str, phone: str) -> None:
        self._name = validate_name(name)
        self._age = validate_age(age)
        self._email = validate_email(email)
        self._phone = validate_phone(phone)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = validate_name(value)

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        self._age = validate_age(value)

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = validate_email(value)

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        self._phone = validate_phone(value)


class Parent:
    """Parent or guardian contact information."""

    def __init__(self, name: str, email: str, phone: str, relationship: str) -> None:
        self._name = validate_name(name)
        self._email = validate_email(email)
        self._phone = validate_phone(phone)
        self._relationship = validate_relationship(relationship)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = validate_name(value)

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = validate_email(value)

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        self._phone = validate_phone(value)

    @property
    def relationship(self) -> str:
        return self._relationship

    @relationship.setter
    def relationship(self, value: str) -> None:
        self._relationship = validate_relationship(value)

    def summary_row(self) -> tuple[str, str, str, str]:
        """Return a tuple suitable for display."""
        return (self.name, self.relationship, self.email, self.phone)

    def to_dict(self) -> dict[str, str]:
        """Convert the parent to a JSON-friendly dictionary."""
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "relationship": self.relationship,
        }


class Student(Person):
    """A student record with grades and attendance data."""

    def __init__(
        self,
        student_id: str,
        name: str,
        age: int,
        email: str,
        phone: str,
        major: str,
        year_level: int,
        status: str = "Active",
        grades: list[float] | None = None,
        attendance: list[dict[str, object]] | None = None,
        parents: list[Parent] | list[dict[str, object]] | None = None,
    ) -> None:
        super().__init__(name=name, age=age, email=email, phone=phone)
        self._student_id = validate_student_id(student_id)
        self._major = validate_major(major)
        self._year_level = validate_year_level(year_level)
        self._status = validate_status(status)
        self._grades: list[float] = []
        self._attendance: list[dict[str, object]] = []
        self._parents: list[Parent] = []

        for grade in grades or []:
            self.add_grade(grade)
        for record in attendance or []:
            self.add_attendance(
                record.get("present", False),
                record.get("date"),
            )
        for parent in parents or []:
            if isinstance(parent, Parent):
                self._parents.append(parent)
            elif isinstance(parent, dict):
                self.add_parent(
                    str(parent.get("name") or ""),
                    str(parent.get("email") or ""),
                    str(parent.get("phone") or ""),
                    str(parent.get("relationship") or ""),
                )
            else:
                raise ValueError("Parent entries must be Parent objects or dicts.")

    @property
    def student_id(self) -> str:
        return self._student_id

    @property
    def major(self) -> str:
        return self._major

    @major.setter
    def major(self, value: str) -> None:
        self._major = validate_major(value)

    @property
    def year_level(self) -> int:
        return self._year_level

    @year_level.setter
    def year_level(self, value: int) -> None:
        self._year_level = validate_year_level(value)

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = validate_status(value)

    @property
    def grades(self) -> list[float]:
        return list(self._grades)

    @property
    def attendance(self) -> list[dict[str, object]]:
        return [record.copy() for record in self._attendance]

    @property
    def parents(self) -> tuple[Parent, ...]:
        return tuple(self._parents)

    def add_grade(self, score: float | int | str) -> float:
        """Add a validated grade and return the stored score."""
        grade = validate_grade(score)
        self._grades.append(grade)
        return grade

    def add_attendance(
        self,
        present: bool | str,
        record_date: str | None = None,
    ) -> dict[str, object]:
        """Add one attendance record."""
        record = {
            "date": validate_iso_date(record_date),
            "present": validate_attendance(present),
        }
        self._attendance.append(record)
        return record.copy()

    def add_parent(
        self,
        name: str,
        email: str,
        phone: str,
        relationship: str,
    ) -> Parent:
        """Add a parent or guardian record."""
        parent = Parent(name=name, email=email, phone=phone, relationship=relationship)
        self._parents.append(parent)
        return parent

    def remove_parent(self, index: int) -> Parent:
        """Remove a parent by index and return it."""
        if index < 0 or index >= len(self._parents):
            raise ValueError("Parent selection is out of range.")
        return self._parents.pop(index)

    def iter_parents(self):
        """Generate parents attached to the student."""
        for parent in self._parents:
            yield parent

    def average_grade(self) -> float:
        """Return the average grade from 0 to 100."""
        if not self._grades:
            return 0.0
        return round(sum(self._grades) / len(self._grades), 2)

    def gpa(self) -> float:
        """Convert the average grade to a 0.0 to 4.0 GPA."""
        return round(min(4.0, self.average_grade() / 25), 2)

    def attendance_percentage(self) -> float:
        """Return the percent of recorded days marked present."""
        if not self._attendance:
            return 0.0
        present_days = sum(1 for record in self._attendance if record["present"])
        return round((present_days / len(self._attendance)) * 100, 2)

    def student_category(self) -> str:
        """Return the category used by reports."""
        return "Regular Student"

    def summary_row(self) -> tuple[str, str, str, int, float, str]:
        """Return a tuple suitable for table display."""
        return (
            self.student_id,
            self.name,
            self.major,
            self.year_level,
            self.gpa(),
            self.status,
        )

    def to_dict(self) -> dict[str, object]:
        """Convert the student to a JSON-friendly dictionary."""
        return {
            "student_type": self.__class__.__name__,
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "phone": self.phone,
            "major": self.major,
            "year_level": self.year_level,
            "status": self.status,
            "grades": self.grades,
            "attendance": self.attendance,
            "parents": [parent.to_dict() for parent in self._parents],
        }


class HonorStudent(Student):
    """Specialized student record for high-achieving students."""

    def __init__(
        self,
        student_id: str,
        name: str,
        age: int,
        email: str,
        phone: str,
        major: str,
        year_level: int,
        status: str = "Active",
        grades: list[float] | None = None,
        attendance: list[dict[str, object]] | None = None,
        scholarship_level: str = "Merit",
        parents: list[Parent] | list[dict[str, object]] | None = None,
    ) -> None:
        super().__init__(
            student_id=student_id,
            name=name,
            age=age,
            email=email,
            phone=phone,
            major=major,
            year_level=year_level,
            status=status,
            grades=grades,
            attendance=attendance,
            parents=parents,
        )
        self.scholarship_level = scholarship_level.strip() or "Merit"

    def student_category(self) -> str:
        """Return the category used by reports."""
        return f"Honor Student ({self.scholarship_level})"

    def honor_status(self) -> str:
        """Return a label based on the student's current GPA."""
        if self.gpa() >= 3.8:
            return "President's List"
        if self.gpa() >= 3.5:
            return "Dean's List"
        return "Honor Watch"

    def to_dict(self) -> dict[str, object]:
        """Convert the honor student to a JSON-friendly dictionary."""
        data = super().to_dict()
        data["scholarship_level"] = self.scholarship_level
        data["honor_status"] = self.honor_status()
        return data


def student_from_dict(data: dict[str, object]) -> Student:
    """Create the right student object from saved JSON data."""
    student_type = str(data.get("student_type", "Student"))
    common_kwargs = {
        "student_id": str(data["student_id"]),
        "name": str(data["name"]),
        "age": int(data["age"]),
        "email": str(data["email"]),
        "phone": str(data["phone"]),
        "major": str(data["major"]),
        "year_level": int(data["year_level"]),
        "status": str(data.get("status", "Active")),
        "grades": list(data.get("grades", [])),
        "attendance": list(data.get("attendance", [])),
        "parents": list(data.get("parents", [])),
    }

    if student_type == "HonorStudent":
        return HonorStudent(
            **common_kwargs,
            scholarship_level=str(data.get("scholarship_level", "Merit")),
        )
    return Student(**common_kwargs)


def attendance_label(record: dict[str, object]) -> str:
    """Return a display label for an attendance record."""
    return ATTENDANCE_PRESENT if record["present"] else ATTENDANCE_ABSENT
