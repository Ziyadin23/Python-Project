# Student Database System

## Project Overview

This project is a modern Student Database System for the Introduction to
Programming 2 final project. It includes two user-friendly interfaces: a local
browser GUI for everyday use and an original terminal CLI powered by the `rich`
library. Both interfaces manage comprehensive student profiles, including
contact information, academic status, grades, attendance, parent contacts, and
reporting.

The project is intentionally modular so each group member can own a clear part
of the system while the final application still runs as one integrated program.

## How to Run

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the browser interface:
   ```bash
   python main.py --gui
   ```

   Then open the local URL printed in the terminal, usually:
   ```text
   http://127.0.0.1:8000
   ```

   You can also open the browser automatically:
   ```bash
   python main.py --gui --open-browser
   ```

   Or start the original terminal interface:
   ```bash
   python main.py
   ```

3. Run the unit tests:
   ```bash
   python -m unittest discover
   ```

## Main Features

- **Modern Terminal UI**: Colorful and intuitive menus, panels, and tables using the `rich` library.
- **Browser GUI**: A local web interface with the same student, parent, grade,
  attendance, report, save, load, and export operations as the CLI.
- **Robust Auto-Save**: Every change is automatically saved to JSON, with fail-safes to prevent data corruption.
- **Full Student Management**: Add, view, search, and selectively update specific student records.
- **Rich Student Profiles**: Store IDs, contact info, academic status, grades, and attendance.
- **Analytics**: Calculate average grade, GPA, and attendance percentage.
- **Advanced Filtering**: Filter by status, major, year level, GPA, and attendance risk.
- **Data Export**: Export student summaries to CSV for external use.
- **Polymorphic Reports**: Generate basic and detailed reports for any student.
- **Robust Validation**: Regex-based validation for IDs, emails, and phone numbers.
- **Activity Logging**: Custom `@log_action` decorator records all manager operations.

## Architecture and Class Hierarchy

```text
main.py
  -> student_database.webapp (Browser GUI + local HTTP API)
  -> student_database.cli (Rich terminal UI)
      -> StudentManager (Logic layer with Auto-Save)
          -> Student / HonorStudent (Model layer)
          -> JSON and CSV storage (Data layer)
          -> BasicReport / DetailedReport (Reporting layer)
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

## Logic Flow

1. `main.py` parses launch options.
2. `python main.py --gui` starts the local browser interface; `python main.py`
   starts the original CLI.
3. The selected interface creates a `StudentManager` and enables **Auto-Save**.
4. Existing JSON data is loaded automatically from `data/students.json`.
5. The user manages students, grades, attendance, parents, reports, and files
   through either the browser controls or the numbered `rich` menu.
6. All database modifications trigger an immediate `_auto_save()` to JSON.
7. Reports and CSV exports can be generated on demand.
8. Unit tests verify the most important system behavior.

## Project Requirements Mapping

For a detailed mapping of where specific rubric requirements (OOP, Functional Programming, Regex, etc.) are implemented in the code, please refer to the [REQUIREMENTS.md](./REQUIREMENTS.md) file.

## Rubric Coverage

- **Foundation and Logic:** browser controls, numbered menus, conditionals, loops, and robust input handling.
- **Collections:** dictionaries for storage, lists for grades, sets for unique majors, and tuples for validation.
- **Data Persistence:** `json` (automated) and `csv` (manual export) modules.
- **OOP:** inheritance, encapsulation, association, and polymorphism.
- **Functional Programming:** `lambda`, `map`, and `filter` used for searching and statistics.
- **Modules and Packages:** cleanly organized package structure with `__init__.py`.
- **Testing:** 13 comprehensive unit tests included.
- **Decorators:** `@log_action` records manager activity.
- **Iterators/Generators:** Generator functions for filtering students.
- **Regex:** `re` module used for input validation.

## Quality Assurance

The code uses docstrings, clear module boundaries, strict validation, and automated unit tests to ensure high-quality software standards.
