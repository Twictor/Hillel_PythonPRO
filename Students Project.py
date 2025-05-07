import re
import csv
from pathlib import Path
from typing import Dict, List, Optional, Union

STORAGE_FILE_NAME = "students.csv"


class Repository:
    def __init__(self, filename: str = STORAGE_FILE_NAME):
        self.filename = filename
        self._ensure_file_exists()
        self.students = self._load_students()

    def _ensure_file_exists(self) -> None:
        """Create CSV file with headers if it doesn't exist."""
        if not Path(self.filename).exists():
            with open(self.filename, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["id", "name", "marks", "info"])
                writer.writeheader()

    def _load_students(self) -> Dict[int, Dict[str, Union[str, List[int]]]]:
        """Load students from CSV file into dictionary."""
        students = {}
        with open(self.filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row['id']:  # Skip empty rows
                    continue
                student_id = int(row['id'])
                students[student_id] = {
                    'name': row['name'],
                    'marks': [int(mark) for mark in row['marks'].split(',') if mark],
                    'info': row.get('info', '')
                }
        return students

    def _save_students(self) -> None:
        """Save current students to CSV file."""
        with open(self.filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["id", "name", "marks", "info"])
            writer.writeheader()
            for student_id, student in self.students.items():
                writer.writerow({
                    'id': student_id,
                    'name': student['name'],
                    'marks': ','.join(map(str, student['marks'])),
                    'info': student.get('info', '')
                })

    def add_student(self, student: Dict[str, Union[str, List[int]]]) -> Optional[int]:
        """Add new student and return ID or None if failed."""
        if not student.get('name') or not student.get('marks'):
            return None

        new_id = max(self.students.keys()) + 1 if self.students else 1
        self.students[new_id] = student
        self._save_students()
        return new_id

    def get_student(self, id_: int) -> Optional[Dict[str, Union[str, List[int]]]]:
        """Get student by ID or None if not found."""
        return self.students.get(id_)

    def update_student(self, id_: int, data: Dict[str, Union[str, List[int]]]) -> bool:
        """Update student data and return success status."""
        if id_ not in self.students:
            return False

        student = self.students[id_]
        for key, value in data.items():
            if key == 'marks':
                student['marks'] = value
            elif key == 'info':
                # Smart update for info field
                old_info = student.get('info', '').strip()
                new_info = value.strip()
                if new_info.lower() not in old_info.lower():
                    student['info'] = f"{old_info} {new_info}".strip()
            else:
                student[key] = value

        self._save_students()
        return True

    def delete_student(self, id_: int) -> bool:
        """Delete student and return success status."""
        if id_ not in self.students:
            return False

        del self.students[id_]
        self._save_students()
        return True

    def add_mark(self, id_: int, mark: int) -> bool:
        """Add mark to student and return success status."""
        if id_ not in self.students:
            return False

        self.students[id_]['marks'].append(mark)
        self._save_students()
        return True


def is_valid_name(name: str) -> bool:
    """Check if the name contains only letters and spaces."""
    return bool(re.fullmatch(r"[A-Za-z ]+", name.strip()))


def is_valid_mark(mark: int) -> bool:
    """Check if the mark is a positive integer."""
    return isinstance(mark, int) and mark > 0


def parse_student_input(data: str) -> Optional[Dict[str, Union[str, List[int]]]]:
    """
    Parse student input string into a dictionary.

    Args:
        data: Input string in format "name; marks"

    Returns:
        Parsed student data or None if invalid
    """
    try:
        if ";" in data:
            name, marks_part = data.split(";")
            name = name.strip()
            if not name:
                return None
            marks = [int(m) for m in marks_part.replace(" ", "").split(",") if m]
            if not marks or not all(is_valid_mark(mark) for mark in marks):
                return None
            return {"name": name, "marks": marks}
        else:
            marks = [int(m) for m in data.replace(" ", "").split(",") if m]
            if not marks or not all(is_valid_mark(mark) for mark in marks):
                return None
            return {"name": "", "marks": marks}
    except (ValueError, AttributeError):
        return None


def student_management_command_handle(repo: Repository, command: str) -> None:
    """Handle different student management commands."""
    if command == "show":
        show_students(repo)
    elif command == "add":
        add_student_handler(repo)
    elif command == "addmark":
        add_mark_handler(repo)
    elif command == "search":
        search_student_handler(repo)
    elif command == "update":
        update_student_handler(repo)
    elif command == "delete":
        delete_student_handler(repo)


def show_students(repo: Repository) -> None:
    """Display all students in the storage."""
    students = repo.students
    print("=" * 25)
    if not students:
        print("No students found")
    else:
        for id_, student in students.items():
            print(f"{id_}. {student['name']} - Marks: {student['marks']} - Info: {student.get('info', '')}")
    print("=" * 25)


def show_student(repo: Repository, student_id: int) -> None:
    """Display detailed information about a specific student."""
    student = repo.get_student(student_id)
    if not student:
        print("Student not found")
        return

    print("=" * 25)
    print(f"ID: {student_id}")
    print(f"Name: {student['name']}")
    print(f"Marks: {student['marks']}")
    print(f"Info: {student.get('info', '')}")
    print("=" * 25)


def add_student_handler(repo: Repository) -> None:
    """Handle student addition."""
    data = input("Enter student (format: 'Name; marks'): ")
    student_data = parse_student_input(data)

    if not student_data:
        print("Invalid input format or marks must be positive integers")
        return

    if not student_data["name"]:
        while True:
            name = input("Enter student name: ").strip()
            if is_valid_name(name):
                student_data["name"] = name
                break
            print("Invalid name (letters and spaces only)")

    info = input("Enter additional info (optional): ").strip()
    student_data["info"] = info

    student_id = repo.add_student(student_data)
    if student_id:
        print(f"Student {student_data['name']} added successfully with ID {student_id}")
    else:
        print("Failed to add student (invalid data or marks)")


def add_mark_handler(repo: Repository) -> None:
    """Handle adding marks to student."""
    try:
        student_id = int(input("Enter student ID: "))
        student = repo.get_student(student_id)
        if not student:
            print("Student not found")
            return

        new_marks_input = input("Enter new mark(s) (comma separated): ")
        new_marks = [int(m) for m in new_marks_input.replace(" ", "").split(",") if m]

        if not new_marks or not all(is_valid_mark(mark) for mark in new_marks):
            print("No valid marks entered or marks must be positive integers")
            return

        for mark in new_marks:
            repo.add_mark(student_id, mark)

        updated_student = repo.get_student(student_id)
        print(f"Added marks {new_marks} to student {updated_student['name']}")
        print(f"Updated marks list: {updated_student['marks']}")
    except ValueError:
        print("Invalid input format for marks")


def search_student_handler(repo: Repository) -> None:
    """Handle student search."""
    try:
        student_id = int(input("Enter student ID: "))
        show_student(repo, student_id)
    except ValueError:
        print("Invalid ID format")


def update_student_handler(repo: Repository) -> None:
    """Handle student update."""
    try:
        student_id = int(input("Enter student ID: "))
        student = repo.get_student(student_id)
        if not student:
            print("Student not found")
            return

        new_name = input(f"Current name: {student['name']}\nNew name (leave empty to keep): ").strip()
        new_info = input(f"Current info: {student.get('info', '')}\nNew info (leave empty to keep): ").strip()

        if not new_name and not new_info:
            print("Nothing to update")
            return

        update_data = {}
        if new_name:
            update_data['name'] = new_name
        if new_info:
            update_data['info'] = new_info

        if repo.update_student(student_id, update_data):
            print("Updated successfully")
            show_student(repo, student_id)
        else:
            print("Update failed")
    except ValueError:
        print("Invalid ID format")


def delete_student_handler(repo: Repository) -> None:
    """Handle student deletion."""
    try:
        student_id = int(input("Enter student ID to delete: "))
        if repo.delete_student(student_id):
            print(f"Student with ID {student_id} deleted successfully")
        else:
            print("Student not found")
    except ValueError:
        print("Invalid ID format")


def display_help() -> None:
    """Display available commands and their descriptions."""
    commands = {
        "show": "List all students",
        "add": "Add new student",
        "addmark": "Add a new mark to a student",
        "search": "Find student by ID",
        "update": "Update student info",
        "delete": "Delete student",
        "help": "Show this help",
        "quit": "Exit program"
    }

    print("=" * 25)
    print("Student Management System")
    print("Available commands:")
    print('\n'.join(f"{cmd:8} - {desc}" for cmd, desc in commands.items()))
    print("=" * 25)


def main() -> None:
    """Main program loop."""
    repo = Repository()
    display_help()

    while True:
        command = input("\nEnter command: ").strip().lower()

        if command == "quit":
            print("Goodbye!")
            break
        elif command == "help":
            display_help()
        elif command in ("show", "add", "search", "update", "addmark", "delete"):
            student_management_command_handle(repo, command)
        else:
            print("Unknown command. Type 'help' for available commands")


if __name__ == "__main__":
    main()
