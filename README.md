# Student Database System

## Project Overview

This project is a terminal-based Student Database System for the Introduction
to Programming 2 final project. It manages rich student profiles, including
contact information, academic status, grades, attendance, JSON storage, CSV
exports, and reports.

The project is intentionally modular so each group member can own a clear part
of the system while the final application still runs as one integrated program.

## How to Run

```bash
python main.py
```

Run the unit tests with:

```bash
python -m unittest discover
```

## Main Features

- Add, view, search, update, and delete student records.
- Store numeric student ID, name, age, email, phone, major, 3-year bachelor
  year level, and status.
- Record grades and attendance.
- Calculate average grade, GPA, and attendance percentage.
- Filter students by status, major, year level, GPA range, and attendance risk.
- Save and load records with JSON.
- Export student summaries to CSV.
- Generate basic and detailed reports.
- Validate numeric student ID, email, phone, age, status, year level, and
  grades.
- Add regular student records directly from the CLI without asking for honor
  student status.
- Log important manager actions with a custom decorator.

## Architecture and Class Hierarchy

```text
main.py
  -> student_database.cli
      -> StudentManager
          -> Student / HonorStudent
          -> JSON and CSV storage
          -> BasicReport / DetailedReport
```

Class hierarchy:

```text
Person
  -> Student
      -> HonorStudent

StudentReport
  -> BasicReport
  -> DetailedReport
```

Important modules:

- `student_database.models`: `Person`, `Student`, `HonorStudent`, and object
  conversion helpers.
- `student_database.manager`: `StudentManager`, which associates and manages
  all students.
- `student_database.storage`: JSON and CSV file input/output.
- `student_database.validation`: regex and value validation.
- `student_database.reports`: polymorphic report classes.
- `student_database.decorators`: custom `@log_action` decorator.
- `student_database.cli`: menu system and user input/output.

## Logic Flow

1. `main.py` starts the CLI.
2. The CLI creates a `StudentManager`.
3. Existing JSON data is loaded if available.
4. The user chooses actions from the numbered menu.
5. The manager validates numeric IDs and 1-3 bachelor year levels.
6. Reports, CSV exports, and JSON saves are generated from manager data.
7. Unit tests verify the most important system behavior.

## Rubric Coverage

- **Foundation and Logic:** numbered menus, conditionals, loops, and robust
  input handling.
- **Collections:** dictionaries for students, lists for grades and attendance,
  sets for unique majors, and tuples for allowed statuses/year levels.
- **Data Persistence:** `os`, `json`, and `csv` modules are used.
- **OOP:** inheritance, encapsulation, association, and polymorphism.
- **Functions:** clear reusable functions with positional and keyword
  arguments.
- **Functional Programming:** `lambda`, `map`, and `filter` are used in manager
  and report logic.
- **Modules and Packages:** organized package with `__init__.py` and imports.
- **Testing:** more than five `unittest` tests are included.
- **Decorators:** `@log_action` records manager activity.
- **Iterators/Generators:** `iter_students_by_status()` and
  `students_at_risk()` generate student records.
- **Regex:** validation uses the `re` module.

## Team Contributions

- **Member 1:** models, validation, and class hierarchy.
- **Member 2:** student manager, storage, decorators, and generators.
- **Member 3:** CLI, reports, tests, README, and final integration.

## Quality Assurance

The code uses docstrings, clear module boundaries, validation, exception
handling, and unit tests. It uses only the Python standard library, so no
external dependencies are required.
