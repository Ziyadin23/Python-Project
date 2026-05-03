# Project Requirements and Code Mapping

This document maps the project requirements and rubric to the specific implementation within the Student Database System.

## 1. Foundation and Logic
- **Requirement**: Use of numbered menus, conditionals, loops, and robust input handling.
- **Implementation**:
    - **Location**: `student_database/cli.py`
    - **Example**: The `run_cli()` function contains the main `while True` loop and `if/elif` blocks for menu navigation. `Prompt.ask` and `Confirm.ask` from the `rich` library ensure robust input.
- **Snippet**:
```python
while True:
    print_header()
    # ... menu printing ...
    choice = Prompt.ask("Choose an option", choices=[str(i) for i in range(1, 10)])
    if choice == "1":
        add_student_flow(manager)
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
    - **Location**: `student_database/storage.py` and `student_database/manager.py`
    - **Details**: `save_students_json` and `load_students_json` handle JSON serialization. `StudentManager` now includes an `_auto_save()` method that automatically triggers a JSON save after any data modification (Add, Update, Delete, Grade, Attendance).
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
    - **Details**: Contains a suite of tests for `StudentManager`, validation logic, and models, ensuring system reliability.
