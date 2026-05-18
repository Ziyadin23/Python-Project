# Student Database System - Presentation Script

Here is a simpler version of the script with less text and direct code examples you can point to during the presentation!

---

## Speaker 1: Data Models & OOP
*(Focuses on `models.py`)*

**What to say:**
"I worked on the data models. To keep the code clean, I used Object-Oriented Programming (OOP) and Inheritance. I built a `Person` class for basic info, and a `Student` class that inherits from it to add grades and IDs."

**Code Example to show:** *(Location: `student_database/models.py`)*
```python
class Person:
    def __init__(self, name: str, age: int, email: str, phone: str):
        self._name = validate_name(name)
        # ...

class Student(Person):
    def __init__(self, student_id: str, name: str, age: int, ...):
        super().__init__(name=name, age=age, email=email, phone=phone)
        self._student_id = validate_student_id(student_id)
```

**What to say:**
"We also used Polymorphism. We made an `HonorStudent` class that acts like a Student but has special methods, like calculating if they made the Dean's List."

**Code Example to show:** *(Location: `student_database/models.py`)*
```python
class HonorStudent(Student):
    def honor_status(self) -> str:
        if self.gpa() >= 3.8:
            return "President's List"
        if self.gpa() >= 3.5:
            return "Dean's List"
```

---

## Speaker 2: Backend Logic & Functional Programming
*(Focuses on `manager.py`)*

**What to say:**
"I worked on the backend logic that manages all the students. Instead of using standard `for` loops, I used functional programming like `filter` and `lambda` to make searching faster."

**Code Example to show:** *(Location: `student_database/manager.py`)*
```python
def filter_by_major(self, major: str) -> list[Student]:
    text = str(major).strip().lower()
    return list(
        filter(
            lambda student: student.major.lower() == text,
            self._students.values()
        )
    )
```

**What to say:**
"I also used a Generator with the `yield` keyword. When looking for students with bad attendance, it yields them one-by-one instead of loading a massive list into memory."

**Code Example to show:** *(Location: `student_database/manager.py`)*
```python
def students_at_risk(self, minimum_attendance: float = 75.0):
    for student in self.all_students():
        if student.attendance and student.attendance_percentage() < minimum_attendance:
            yield student
```

---

## Speaker 3: User Interface, Validation & Saving Data
*(Focuses on `webapp.py`, `validation.py`, `storage.py`, and `manager.py`)*

**What to say:**
"I worked on making the system easier to use. The original terminal menu still
works, but I also added a local browser interface. It has the same features as
the CLI: students, search, update, grades, attendance, parents, reports, JSON
save/load, and CSV export."

**Code Example to show:** *(Location: `main.py`)*
```python
if args.gui:
    from student_database.webapp import run_web_app
    run_web_app(args.data_path)
else:
    from student_database.cli import run_cli
    run_cli(args.data_path)
```

**What to say:**
"I focused on user input and saving the data. To make sure users don't type bad data, I used Regular Expressions (Regex) to strictly check emails and phone numbers."

**Code Example to show:** *(Location: `student_database/validation.py`)*
```python
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def validate_email(email: str) -> str:
    if not EMAIL_RE.fullmatch(email):
        raise ValueError("Email address is not valid.")
    return email
```

**What to say:**
"For data persistence, I built an Auto-Save system using JSON. If saving fails for any reason, it uses a `try-except` block to catch the error and safely undo the changes."

**Code Example to show:** *(Location: `student_database/manager.py`)*
```python
def _auto_save(self) -> None:
    if self.data_path:
        try:
            self.save_json(self.data_path)
        except OSError as error:
            self.load_json(self.data_path)
            raise RuntimeError(f"Auto-save failed. Changes reverted. ({error})")
```

**What to say:**
"For sharing data outside the app, the Save / Export screen can export all
student summaries to CSV, so the file can be opened in Excel, Google Sheets, or
LibreOffice."
