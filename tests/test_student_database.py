"""Unit tests for the student database system."""

from __future__ import annotations

import csv
import os
import tempfile
import unittest

from student_database.manager import StudentManager
from student_database.models import HonorStudent, Student
from student_database.reports import BasicReport, DetailedReport


def make_student(student_id: str = "1001") -> Student:
    """Create a valid regular student for tests."""
    return Student(
        student_id=student_id,
        name="Aisha Khan",
        age=19,
        email="aisha@example.com",
        phone="+1 555 123 4567",
        major="Computer Science",
        year_level=2,
    )


class TestStudentDatabase(unittest.TestCase):
    """Student database behavior tests."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.manager = StudentManager(
            log_path=os.path.join(self.temp_dir.name, "actions.log"),
        )

    def test_add_valid_student(self) -> None:
        student = make_student()
        self.manager.add_student(student)
        self.assertEqual(len(self.manager), 1)
        self.assertEqual(self.manager.get_student("1001").name, "Aisha Khan")

    def test_reject_duplicate_student_id(self) -> None:
        self.manager.add_student(make_student())
        with self.assertRaises(ValueError):
            self.manager.add_student(make_student())

    def test_reject_invalid_email_phone_id_and_year_level(self) -> None:
        with self.assertRaises(ValueError):
            make_student("BAD001")
        with self.assertRaises(ValueError):
            Student(
                student_id="1002",
                name="Bad Email",
                age=20,
                email="not-email",
                phone="+1 555 000 0000",
                major="Math",
                year_level=1,
            )
        with self.assertRaises(ValueError):
            Student(
                student_id="1003",
                name="Bad Phone",
                age=20,
                email="phone@example.com",
                phone="12",
                major="Math",
                year_level=1,
            )
        with self.assertRaises(ValueError):
            Student(
                student_id="1004",
                name="Fourth Year",
                age=20,
                email="year@example.com",
                phone="+1 555 000 4444",
                major="Math",
                year_level=4,
            )

    def test_update_student_contact_and_academic_info(self) -> None:
        self.manager.add_student(make_student())
        updated = self.manager.update_student(
            "1001",
            email="new.aisha@example.com",
            phone="+1 555 999 0000",
            major="Data Science",
            year_level=3,
            status="Inactive",
        )
        self.assertEqual(updated.email, "new.aisha@example.com")
        self.assertEqual(updated.major, "Data Science")
        self.assertEqual(updated.year_level, 3)
        self.assertEqual(updated.status, "Inactive")

    def test_calculate_gpa_correctly(self) -> None:
        student = make_student()
        student.add_grade(90)
        student.add_grade(80)
        self.assertEqual(student.average_grade(), 85.0)
        self.assertEqual(student.gpa(), 3.4)

    def test_calculate_attendance_percentage_correctly(self) -> None:
        student = make_student()
        student.add_attendance(True, "2026-05-01")
        student.add_attendance(False, "2026-05-02")
        student.add_attendance("present", "2026-05-03")
        self.assertEqual(student.attendance_percentage(), 66.67)

    def test_filter_students_by_status_and_gpa(self) -> None:
        first = make_student("1001")
        first.add_grade(95)
        second = make_student("1002")
        second.name = "Dana Lee"
        second.email = "dana@example.com"
        second.add_grade(50)
        second.status = "Inactive"
        self.manager.add_student(first)
        self.manager.add_student(second)

        inactive = self.manager.filter_by_status("inactive")
        high_gpa = self.manager.filter_by_gpa(minimum=3.5)

        self.assertEqual([student.student_id for student in inactive], ["1002"])
        self.assertEqual([student.student_id for student in high_gpa], ["1001"])

    def test_json_save_load_round_trip(self) -> None:
        json_path = os.path.join(self.temp_dir.name, "students.json")
        honor_student = HonorStudent(
            student_id="1010",
            name="Mina Park",
            age=21,
            email="mina@example.com",
            phone="+1 555 010 1111",
            major="Physics",
            year_level=3,
        )
        honor_student.add_grade(98)
        self.manager.add_student(honor_student)
        self.manager.save_json(json_path)

        loaded_manager = StudentManager(log_path=None)
        loaded_count = loaded_manager.load_json(json_path)
        loaded_student = loaded_manager.get_student("1010")

        self.assertEqual(loaded_count, 1)
        self.assertIsInstance(loaded_student, HonorStudent)
        self.assertEqual(loaded_student.gpa(), 3.92)

    def test_csv_export_creates_expected_rows(self) -> None:
        csv_path = os.path.join(self.temp_dir.name, "students.csv")
        student = make_student()
        student.add_grade(100)
        self.manager.add_student(student)
        self.manager.export_csv(csv_path)

        with open(csv_path, newline="", encoding="utf-8") as csv_file:
            rows = list(csv.DictReader(csv_file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["student_id"], "1001")
        self.assertEqual(rows[0]["gpa"], "4.00")

    def test_parent_round_trip_and_csv_export(self) -> None:
        json_path = os.path.join(self.temp_dir.name, "students.json")
        csv_path = os.path.join(self.temp_dir.name, "students.csv")
        student = make_student()
        student.add_parent(
            name="Salma Khan",
            email="salma@example.com",
            phone="+1 555 111 2222",
            relationship="Mother",
        )
        self.manager.add_student(student)
        self.manager.save_json(json_path)

        loaded_manager = StudentManager(log_path=None)
        loaded_manager.load_json(json_path)
        loaded_student = loaded_manager.get_student("1001")
        self.assertEqual(len(loaded_student.parents), 1)
        self.assertEqual(loaded_student.parents[0].relationship, "Mother")

        self.manager.export_csv(csv_path)
        with open(csv_path, newline="", encoding="utf-8") as csv_file:
            rows = list(csv.DictReader(csv_file))

        self.assertEqual(rows[0]["parent_names"], "Salma Khan")
        self.assertEqual(rows[0]["parent_relationships"], "Mother")

    def test_parent_collection_helpers(self) -> None:
        student = make_student()
        student.add_parent(
            name="Salma Khan",
            email="salma@example.com",
            phone="+1 555 111 2222",
            relationship="Mother",
        )
        student.add_parent(
            name="Omar Khan",
            email="omar@example.com",
            phone="+1 555 111 3333",
            relationship="Guardian",
        )
        self.manager.add_student(student)

        parents = list(self.manager.iter_parents())
        self.assertEqual(len(parents), 2)

        relationships = self.manager.unique_parent_relationships()
        self.assertEqual(relationships, {"Mother", "Guardian"})

        summary = self.manager.parent_summary_tuple("1001")
        self.assertIsInstance(summary, tuple)
        self.assertEqual(summary[0][0], "Salma Khan")

        phone_map = self.manager.parent_phone_map()
        self.assertEqual(phone_map["Omar Khan"], "+1 555 111 3333")

        guardians = self.manager.filter_parents_by_relationship("guardian")
        self.assertEqual([parent.relationship for parent in guardians], ["Guardian"])

    def test_report_generation_returns_expected_text(self) -> None:
        student = make_student()
        student.add_grade(90)
        student.add_attendance(True, "2026-05-01")

        basic_report = BasicReport().generate(student)
        detailed_report = DetailedReport().generate(student)

        self.assertIn("Basic Student Report", basic_report)
        self.assertIn("1001", basic_report)
        self.assertIn("Detailed Student Report", detailed_report)
        self.assertIn("2026-05-01: Present", detailed_report)

    def test_students_at_risk_generator(self) -> None:
        first = make_student("1001")
        first.add_attendance(False, "2026-05-01")
        second = make_student("1002")
        second.name = "Dana Lee"
        second.email = "dana@example.com"
        second.add_attendance(True, "2026-05-01")
        self.manager.add_student(first)
        self.manager.add_student(second)

        risky_students = list(self.manager.students_at_risk())

        self.assertEqual([student.student_id for student in risky_students], ["1001"])


if __name__ == "__main__":
    unittest.main()
