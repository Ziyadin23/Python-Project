# Project Requirements and Code Mapping

This document maps the project requirements and rubric to the specific implementation within the Student Database System.

## 1. Foundation and Logic
- **Requirement**: Use of user-friendly controls, numbered menus, conditionals,
  loops, and robust input handling.
- **Implementation**:
    - **Locations**: `student_database/webapp.py`, `student_database/cli.py`, and `main.py`
    - **Example**: `main.py` chooses between the browser GUI and CLI. The CLI
      uses a `while True` loop and `if/elif` menu navigation, while the browser
      GUI exposes the same operations through forms, buttons, dropdowns, and
      local API routes.
- **Snippet**:
```python
if args.gui:
    from student_database.webapp import run_web_app
    run_web_app(data_path=args.data_path, host=args.host, port=args.port)
else:
    from student_database.cli import run_cli
    run_cli(args.data_path)
```

## 2. Collections
- **Requirement**: Use of dictionaries, lists, sets, and tuples.
- **Implementation**:
    - **Dictionaries**: `StudentManager._students` maps student IDs to student objects (`student_database/manager.py`).
    - **Lists**: `Student._grades` and `Student._attendance` (`student_database/models.py`).
    - **Sets**: `StudentManager.unique_majors()` returns a set of unique major strings (`student_database/manager.py`).
    - **Tuples**: `ALLOWED_STATUSES` and `YEAR_LEVELS` constants are tuples used for validation (`student_database/constants.py`).

## 3. Object-Oriented Programming (OOP)
- **Requirement**: Inheritance, Encapsulation, Association, and Polymorphism.
- **Implementation**:
    - **Inheritance**: `Person` -> `Student` -> `HonorStudent` in `student_database/models.py`.
    - **Encapsulation**: Using private attributes (e.g., `self._name`) with `@property` getters and setters in `Person` and `Student` classes.
    - **Association**: `StudentManager` "has-a" collection of `Student` objects.
    - **Polymorphism**: `student_category()` is overridden in `HonorStudent` to provide different behavior than the base `Student` class.

## 4. Functional Programming
- **Requirement**: Use of `lambda`, `map`, and `filter`.
- **Implementation**:
    - **Location**: `student_database/manager.py`
    - **Example**: `search()` uses `filter` and a `lambda`. `student_gpa_map()` uses `map` and a `lambda`.
- **Snippet**:
```python
def search(self, query: str) -> list[Student]:
    return list(filter(lambda student: text in student.name.lower(), self._students.values()))
```

## 5. Decorators
- **Requirement**: Use of a custom decorator.
- **Implementation**:
    - **Location**: `student_database/decorators.py`
    - **Example**: The `@log_action` decorator is used in `StudentManager` to log every major database operation to a file.
- **Snippet**:
```python
@log_action("Added student")
def add_student(self, student: Student) -> Student:
    # ...
```

## 6. Iterators and Generators
- **Requirement**: Use of custom iterators or generators.
- **Implementation**:
    - **Location**: `student_database/manager.py`
    - **Example**: `iter_students_by_status()` and `students_at_risk()` are generator functions using the `yield` keyword.
- **Snippet**:
```python
def iter_students_by_status(self, status: str):
    for student in self.all_students():
        if student.status == normalized_status:
            yield student
```

## 7. Regular Expressions (Regex)
- **Requirement**: Use of the `re` module for validation.
- **Implementation**:
    - **Location**: `student_database/validation.py`
    - **Example**: `STUDENT_ID_RE`, `EMAIL_RE`, and `PHONE_RE` are compiled regex patterns used to validate user input.

## 8. Data Persistence
- **Requirement**: Save and load data using `json` and `csv`.
- **Implementation**:
    - **Location**: `student_database/storage.py`, `student_database/manager.py`, `student_database/cli.py`, and `student_database/webapp.py`
    - **Details**: `save_students_json` and `load_students_json` handle JSON
      serialization. `export_students_csv` creates CSV exports. `StudentManager`
      includes an `_auto_save()` method that automatically triggers a JSON save
      after any data modification (Add, Update, Delete, Grade, Attendance, and
      Parent updates). Both the CLI and browser GUI expose save, load, and CSV
      export actions.
- **Snippet**:
```python
def _auto_save(self) -> None:
    if self.data_path:
        self.save_json(self.data_path)
```

## 9. Testing
- **Requirement**: Include at least five `unittest` tests.
- **Implementation**:
    - **Location**: `tests/test_student_database.py`
    - **Details**: Contains 13 tests for `StudentManager`, validation logic,
      models, reports, JSON persistence, CSV export, parents, GPA, and
      attendance behavior.

## 10. User-Friendly Interface
- **Requirement**: Provide a user-friendly interface with the same commands and
  functionality as the CLI.
- **Implementation**:
    - **Location**: `student_database/webapp.py`
    - **Details**: The browser GUI runs locally with Python's standard
      `http.server` stack and calls the same `StudentManager` methods as the
      CLI. It supports viewing, searching, filtering, adding, updating,
      deleting, grades, attendance, parents, reports, JSON save/load, and CSV
      export.
