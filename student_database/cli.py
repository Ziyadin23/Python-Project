"""Command-line interface for the student database system."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from student_database.constants import (
    ALLOWED_STATUSES,
    ALLOWED_PARENT_RELATIONSHIPS,
    DEFAULT_DATA_PATH,
    DEFAULT_EXPORT_PATH,
    YEAR_LEVELS,
)
from student_database.manager import StudentManager
from student_database.models import Parent, Student
from student_database.reports import BasicReport, DetailedReport

console = Console()


def print_header(title: str = "STUDENT DATABASE SYSTEM") -> None:
    console.print(Panel(title.center(60), style="bold blue"))


def pause() -> None:
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def prompt_required(label: str) -> str:
    return Prompt.ask(f"[bold]{label}[/bold]")


def prompt_int(label: str) -> int:
    while True:
        value = Prompt.ask(f"[bold]{label}[/bold]")
        try:
            return int(value)
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")


def prompt_float(label: str) -> float:
    while True:
        value = Prompt.ask(f"[bold]{label}[/bold]")
        try:
            return float(value)
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")


def prompt_choice(label: str, choices: tuple[str, ...]) -> str:
    return Prompt.ask(f"[bold]{label}[/bold]", choices=choices)


def prompt_yes_no(label: str) -> bool:
    return Confirm.ask(f"[bold]{label}[/bold]")


def display_students(students: list[Student]) -> None:
    if not students:
        console.print("[yellow]No students found.[/yellow]")
        return

    table = Table(title="Student Records")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Major", style="green")
    table.add_column("Year", justify="right")
    table.add_column("GPA", justify="right", style="bold")
    table.add_column("Status", style="yellow")

    for student in students:
        student_id, name, major, year, gpa, status = student.summary_row()
        table.add_row(
            student_id,
            name,
            major,
            str(year),
            f"{gpa:.2f}",
            status,
        )

    console.print(table)


def display_parents(parents: list[Parent] | tuple[Parent, ...]) -> None:
    if not parents:
        console.print("[yellow]No parents found.[/yellow]")
        return

    table = Table(title="Parent Contacts")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Relationship", style="green")
    table.add_column("Email", style="blue")
    table.add_column("Phone", style="yellow")

    for index, parent in enumerate(parents, start=1):
        name, relationship, email, phone = parent.summary_row()
        table.add_row(str(index), name, relationship, email, phone)

    console.print(table)


def add_student_flow(manager: StudentManager) -> None:
    print_header("ADD NEW STUDENT")
    try:
        student = Student(
            student_id=prompt_required("Student ID"),
            name=prompt_required("Name"),
            age=prompt_int("Age"),
            email=prompt_required("Email"),
            phone=prompt_required("Phone"),
            major=prompt_required("Major"),
            year_level=int(
                prompt_choice(
                    "Year level",
                    tuple(map(str, YEAR_LEVELS)),
                )
            ),
            status=prompt_choice("Status", ALLOWED_STATUSES),
        )
        while prompt_yes_no("Add a parent or guardian"):
            student.add_parent(
                name=prompt_required("Parent Name"),
                relationship=prompt_choice(
                    "Relationship",
                    ALLOWED_PARENT_RELATIONSHIPS,
                ),
                email=prompt_required("Parent Email"),
                phone=prompt_required("Parent Phone"),
            )
        manager.add_student(student)
        console.print("[green]Student added successfully.[/green]")
    except (KeyError, ValueError, RuntimeError) as error:
        console.print(f"[red]Could not add student: {error}[/red]")


def view_all_flow(manager: StudentManager) -> None:
    print_header("ALL STUDENTS")
    console.print("1. [bold]No Filter (View All)[/bold]")
    console.print("2. [bold]Filter by Major[/bold]")
    console.print("3. [bold]Filter by Year Level[/bold]")
    console.print("4. [bold]Filter by Status[/bold]")
    choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"])

    if choice == "1":
        display_students(manager.all_students())
        majors = sorted(manager.unique_majors())
        if majors:
            console.print(f"\n[bold]Unique majors:[/bold] {', '.join(majors)}")
    elif choice == "2":
        majors = sorted(manager.unique_majors())
        if not majors:
            console.print("[yellow]No majors found.[/yellow]")
            return
        console.print(f"[dim]Available majors: {', '.join(majors)}[/dim]")
        major = prompt_required("Major")
        display_students(manager.filter_by_major(major))
    elif choice == "3":
        year = prompt_int("Year Level")
        display_students(manager.filter_by_year_level(year))
    elif choice == "4":
        status = prompt_choice("Status", ALLOWED_STATUSES)
        display_students(manager.filter_by_status(status))


def search_flow(manager: StudentManager) -> None:
    print_header("SEARCH STUDENT")
    query = prompt_required("Search by ID, name, or major")
    display_students(manager.search(query))


def update_student_flow(manager: StudentManager) -> None:
    print_header("UPDATE STUDENT")
    student_id = prompt_required("Student ID")
    try:
        student = manager.get_student(student_id)
        fields_to_update = {}
        while True:
            console.print("\n[bold]Select a field to update:[/bold]")
            console.print("1. Name")
            console.print("2. Age")
            console.print("3. Email")
            console.print("4. Phone")
            console.print("5. Major")
            console.print("6. Year level")
            console.print("7. Status")
            console.print("8. Apply Updates")
            console.print("9. Cancel")
            choice = Prompt.ask("Choose an option", choices=[str(i) for i in range(1, 10)])
            
            if choice == "1":
                fields_to_update["name"] = Prompt.ask("New Name", default=student.name).strip()
            elif choice == "2":
                fields_to_update["age"] = Prompt.ask("New Age", default=str(student.age)).strip()
            elif choice == "3":
                fields_to_update["email"] = Prompt.ask("New Email", default=student.email).strip()
            elif choice == "4":
                fields_to_update["phone"] = Prompt.ask("New Phone", default=student.phone).strip()
            elif choice == "5":
                fields_to_update["major"] = Prompt.ask("New Major", default=student.major).strip()
            elif choice == "6":
                fields_to_update["year_level"] = Prompt.ask(
                    "New Year level",
                    default=str(student.year_level),
                    choices=tuple(map(str, YEAR_LEVELS)),
                ).strip()
            elif choice == "7":
                fields_to_update["status"] = Prompt.ask(
                    "New Status",
                    default=student.status,
                    choices=ALLOWED_STATUSES,
                ).strip()
            elif choice == "8":
                if fields_to_update:
                    manager.update_student(student_id, **fields_to_update)
                    console.print("[green]Student updated successfully.[/green]")
                else:
                    console.print("[yellow]No changes made.[/yellow]")
                break
            elif choice == "9":
                console.print("[yellow]Update cancelled.[/yellow]")
                break
    except (KeyError, ValueError, RuntimeError) as error:
        console.print(f"[red]Could not update student: {error}[/red]")


def delete_student_flow(manager: StudentManager) -> None:
    print_header("DELETE STUDENT")
    student_id = prompt_required("Student ID")
    try:
        student = manager.get_student(student_id)
        if prompt_yes_no(f"Delete {student.name}?"):
            manager.delete_student(student_id)
            console.print("[green]Student deleted successfully.[/green]")
    except (KeyError, ValueError, RuntimeError) as error:
        console.print(f"[red]Could not delete student: {error}[/red]")


def grades_attendance_flow(manager: StudentManager) -> None:
    while True:
        print_header("GRADES & ATTENDANCE")
        console.print("1. [bold]Add Grade[/bold]")
        console.print("2. [bold]Record Attendance[/bold]")
        console.print("3. [bold]Back[/bold]")
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3"])
        try:
            if choice == "1":
                student_id = prompt_required("Student ID")
                grade = prompt_float("Grade (0-100)")
                manager.add_grade(student_id, grade)
                console.print("[green]Grade added successfully.[/green]")
                pause()
            elif choice == "2":
                student_id = prompt_required("Student ID")
                present = prompt_yes_no("Was the student present")
                record_date = Prompt.ask(
                    "Date YYYY-MM-DD (blank for today)", default=""
                ).strip()
                manager.add_attendance(student_id, present, record_date or None)
                console.print("[green]Attendance recorded successfully.[/green]")
                pause()
            elif choice == "3":
                return
        except (KeyError, ValueError, RuntimeError) as error:
            console.print(f"[red]Operation failed: {error}[/red]")
            pause()


def parents_flow(manager: StudentManager) -> None:
    student_id: str | None = None
    student: Student | None = None
    while True:
        title = "PARENTS / GUARDIANS"
        if student:
            title = f"PARENTS FOR {student.name} ({student.student_id})"
        print_header(title)
        console.print("1. [bold]Find Student by ID[/bold]")
        console.print("2. [bold]View Parents[/bold]")
        console.print("3. [bold]Add Parent[/bold]")
        console.print("4. [bold]Remove Parent[/bold]")
        console.print("5. [bold]Back[/bold]")
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"])
        try:
            if choice == "1":
                student_id = prompt_required("Student ID")
                student = manager.get_student(student_id)
                console.print(f"[green]Selected {student.name}.[/green]")
                display_parents(list(student.parents))
                pause()
            elif choice == "2":
                if not student:
                    console.print("[yellow]Select a student first.[/yellow]")
                    pause()
                    continue
                display_parents(list(student.parents))
                pause()
            elif choice == "3":
                if not student or not student_id:
                    console.print("[yellow]Select a student first.[/yellow]")
                    pause()
                    continue
                manager.add_parent(
                    student_id=student_id,
                    name=prompt_required("Parent Name"),
                    relationship=prompt_choice(
                        "Relationship",
                        ALLOWED_PARENT_RELATIONSHIPS,
                    ),
                    email=prompt_required("Parent Email"),
                    phone=prompt_required("Parent Phone"),
                )
                student = manager.get_student(student_id)
                console.print("[green]Parent added successfully.[/green]")
                pause()
            elif choice == "4":
                if not student or not student_id:
                    console.print("[yellow]Select a student first.[/yellow]")
                    pause()
                    continue
                parents = list(student.parents)
                if not parents:
                    console.print("[yellow]No parents to remove.[/yellow]")
                    pause()
                    continue
                display_parents(parents)
                selection = Prompt.ask(
                    "Select parent number",
                    choices=[str(i) for i in range(1, len(parents) + 1)],
                )
                removed = manager.remove_parent(student_id, int(selection) - 1)
                student = manager.get_student(student_id)
                console.print(f"[green]Removed {removed.name}.[/green]")
                pause()
            elif choice == "5":
                return
        except (KeyError, ValueError, RuntimeError) as error:
            console.print(f"[red]Parent operation failed: {error}[/red]")
            pause()


def reports_flow(manager: StudentManager) -> None:
    while True:
        print_header("REPORTS")
        console.print("1. [bold]Basic Student Report[/bold]")
        console.print("2. [bold]Detailed Student Report[/bold]")
        console.print("3. [bold]Students at Attendance Risk[/bold]")
        console.print("4. [bold]GPA Summary[/bold]")
        console.print("5. [bold]Back[/bold]")
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"])
        if choice in {"1", "2"}:
            student_id = prompt_required("Student ID")
            report = BasicReport() if choice == "1" else DetailedReport()
            try:
                console.print()
                console.print(
                    Panel(report.generate(manager.get_student(student_id)), expand=False)
                )
            except (KeyError, ValueError) as error:
                console.print(f"[red]Report failed: {error}[/red]")
            pause()
        elif choice == "3":
            display_students(list(manager.students_at_risk()))
            pause()
        elif choice == "4":
            console.print(f"\n[bold]Class GPA average:[/bold] {manager.average_class_gpa():.2f}")
            console.print(f"[bold]GPA map:[/bold] {manager.student_gpa_map()}")
            pause()
        elif choice == "5":
            return


def save_export_flow(manager: StudentManager) -> None:
    while True:
        print_header("SAVE / EXPORT DATA")
        console.print("1. [bold]Save JSON[/bold]")
        console.print("2. [bold]Load JSON[/bold]")
        console.print("3. [bold]Export CSV[/bold]")
        console.print("4. [bold]Back[/bold]")
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"])
        try:
            if choice == "1":
                path = Prompt.ask("JSON path", default=DEFAULT_DATA_PATH).strip()
                manager.save_json(path or DEFAULT_DATA_PATH)
                console.print("[green]Data saved successfully.[/green]")
                pause()
            elif choice == "2":
                path = Prompt.ask("JSON path", default=DEFAULT_DATA_PATH).strip()
                count = manager.load_json(path or DEFAULT_DATA_PATH)
                console.print(f"[green]Loaded {count} student(s).[/green]")
                pause()
            elif choice == "3":
                path = Prompt.ask("CSV path", default=DEFAULT_EXPORT_PATH).strip()
                manager.export_csv(path or DEFAULT_EXPORT_PATH)
                console.print("[green]CSV exported successfully.[/green]")
                pause()
            elif choice == "4":
                return
        except (OSError, ValueError) as error:
            console.print(f"[red]File operation failed: {error}[/red]")
            pause()


def run_cli(data_path: str = DEFAULT_DATA_PATH) -> None:
    """Run the interactive command-line application."""
    manager = StudentManager(data_path=data_path)
    try:
        loaded_count = manager.load_json(data_path)
        if loaded_count:
            console.print(f"[green]Loaded {loaded_count} student(s) from {data_path}.[/green]")
    except (OSError, ValueError) as error:
        console.print(f"[yellow]Starting with an empty database: {error}[/yellow]")

    while True:
        print_header()
        console.print("1. [bold]Add New Student[/bold]")
        console.print("2. [bold]View All Students[/bold]")
        console.print("3. [bold]Search Student[/bold]")
        console.print("4. [bold]Update Student[/bold]")
        console.print("5. [bold]Delete Student[/bold]")
        console.print("6. [bold]Grades & Attendance[/bold]")
        console.print("7. [bold]Parents / Guardians[/bold]")
        console.print("8. [bold]Reports[/bold]")
        console.print("9. [bold]Save / Export Data[/bold]")
        console.print("10. [bold]Exit[/bold]")
        choice = Prompt.ask("Choose an option", choices=[str(i) for i in range(1, 11)])

        if choice == "1":
            add_student_flow(manager)
            pause()
        elif choice == "2":
            view_all_flow(manager)
            pause()
        elif choice == "3":
            search_flow(manager)
            pause()
        elif choice == "4":
            update_student_flow(manager)
            pause()
        elif choice == "5":
            delete_student_flow(manager)
            pause()
        elif choice == "6":
            grades_attendance_flow(manager)
        elif choice == "7":
            parents_flow(manager)
        elif choice == "8":
            reports_flow(manager)
        elif choice == "9":
            save_export_flow(manager)
        elif choice == "10":
            console.print("[bold blue]Goodbye![/bold blue]")
            return
