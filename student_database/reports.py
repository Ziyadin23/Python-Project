"""Polymorphic report classes for student records."""

from __future__ import annotations

from student_database.models import Student, attendance_label


class StudentReport:
    """Base report interface."""

    title = "Student Report"

    def generate(self, student: Student) -> str:
        """Generate a report for one student."""
        raise NotImplementedError("Subclasses must implement generate().")


class BasicReport(StudentReport):
    """Short report for quick scanning."""

    title = "Basic Student Report"

    def generate(self, student: Student) -> str:
        """Generate a compact student report."""
        return (
            f"{self.title}\n"
            f"ID: {student.student_id}\n"
            f"Name: {student.name}\n"
            f"Major: {student.major}\n"
            f"GPA: {student.gpa():.2f}\n"
            f"Status: {student.status}\n"
            f"Category: {student.student_category()}"
        )


class DetailedReport(StudentReport):
    """Detailed report for academic review."""

    title = "Detailed Student Report"

    def generate(self, student: Student) -> str:
        """Generate a detailed student report."""
        grade_text = ", ".join(map(lambda grade: f"{grade:.1f}", student.grades))
        if not grade_text:
            grade_text = "No grades recorded"

        attendance_lines = []
        for record in student.attendance:
            attendance_lines.append(
                f"{record['date']}: {attendance_label(record)}"
            )
        attendance_text = "\n".join(attendance_lines) or "No attendance recorded"

        return (
            f"{self.title}\n"
            f"ID: {student.student_id}\n"
            f"Name: {student.name}\n"
            f"Age: {student.age}\n"
            f"Email: {student.email}\n"
            f"Phone: {student.phone}\n"
            f"Major: {student.major}\n"
            f"Year Level: {student.year_level}\n"
            f"Status: {student.status}\n"
            f"Category: {student.student_category()}\n"
            f"Grades: {grade_text}\n"
            f"Average Grade: {student.average_grade():.2f}\n"
            f"GPA: {student.gpa():.2f}\n"
            f"Attendance: {student.attendance_percentage():.2f}%\n"
            f"Attendance Records:\n{attendance_text}"
        )
