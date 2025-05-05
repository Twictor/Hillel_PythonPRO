import re

storage = {}


def is_valid_name(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z ]+", name.strip()))


def add_student(student: dict) -> dict | None:
    if (
            not student.get("name")
            or not student["name"].strip()
            or not student.get("marks")
            or not isinstance(student["marks"], list)
            or len(student["marks"]) == 0
    ):
        return None

    next_id = max(storage.keys()) + 1 if storage else 1
    storage[next_id] = student
    return student


def show_students() -> None:
    print("=" * 25)
    if not storage:
        print("No students found")
    else:
        for id_, student in storage.items():
            print(f"{id_}. {student['name']} - Marks: {student['marks']} - Info: {student.get('info', '')}")
    print("=" * 25)


def show_student(student_id: int) -> None:
    student = storage.get(student_id)
    if not student:
        print("Student not found")
        return

    print("=" * 25)
    print(f"ID: {student_id}")
    print(f"Name: {student['name']}")
    print(f"Marks: {student['marks']}")
    print(f"Info: {student.get('info', '')}")
    print("=" * 25)


def update_student(student_id: int, name: str = None, info: str = None):
    student = storage.get(student_id)
    if not student:
        return None

    if name:
        student["name"] = name

    if info:
        old_info = student.get("info", "")
        if info in old_info:
            student["info"] = info  # replace
        elif old_info and info != old_info:
            student["info"] = old_info + " " + info  # augment
        else:
            student["info"] = info

    return student


def parse_student_input(data: str):
    try:
        if ";" in data:
            name, marks_part = data.split(";")
            name = name.strip()
            if not name:
                return None
            marks = [int(m) for m in marks_part.replace(" ", "").split(",") if m]
            if not marks:
                return None
            return {"name": name, "marks": marks}
        else:
            marks = [int(m) for m in data.replace(" ", "", ).split(",") if m]
            if not marks:
                return None
            return {"name": "", "marks": marks}
    except (ValueError, AttributeError):
        return None


def student_management_command_handle(command: str) -> None:
    if command == "show":
        show_students()
    elif command == "add":
        data = input("Enter student: ")
        student_data = parse_student_input(data)

        if not student_data:
            print("Invalid input format")
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

        result = add_student(student_data)
        if result:
            print(f"Student {result['name']} added successfully")
        else:
            print("Failed to add student")


    elif command == "addmark":
        try:
            student_id = int(input("Enter student ID: "))
            student = storage.get(student_id)
            if not student:
                print("Student not found")
                return

            new_marks_input = input("Enter new mark(s): ")
            new_marks = [int(m) for m in new_marks_input.replace(" ", "").split(",") if m]

            if not new_marks:
                print("No valid marks entered")
                return

            student["marks"].extend(new_marks)
            print(f"Added marks {new_marks} to student {student['name']}")
        except ValueError:
            print("Invalid input format for marks")


    elif command == "search":
        try:
            student_id = int(input("Enter student ID: "))
            show_student(student_id)
        except ValueError:
            print("Invalid ID format")

    elif command == "update":
        try:
            student_id = int(input("Enter student ID: "))
            student = storage.get(student_id)
            if not student:
                print("Student not found")
                return

            new_name = input(f"Current name: {student['name']}\nNew name (leave empty to keep): ")
            new_info = input(f"Current info: {student.get('info', '')}\nNew info (leave empty to keep): ")

            if not new_name and not new_info:
                print("Nothing to update")
                return

            update_data = {
                "name": new_name if new_name else student['name'],
                "info": new_info if new_info else student.get('info', '')
            }

            if update_student(student_id, **update_data):
                print("Updated successfully")
            else:
                print("Update failed")
        except ValueError:
            print("Invalid ID format")


def display_help() -> None:
    commands = {
        "show": "List all students",
        "add": "Add new student",
        "addmark": "Add a new mark to a student",
        "search": "Find student by ID",
        "update": "Update student info",
        "help": "Show this help",
        "quit": "Exit program"
    }

    print("=" * 25)
    print("Student Management System")
    print("Available commands:")
    print('\n'.join(map(lambda item: f"{item[0]:8} - {item[1]}", commands.items())))
    print("=" * 25)


def main() -> None:
    display_help()

    while True:
        command = input("\nEnter command: ").strip().lower()

        if command == "quit":
            print("Goodbye!")
            break
        elif command == "help":
            display_help()
        elif command in ("show", "add", "search", "update", "addmark"):
            student_management_command_handle(command)
        else:
            print("Unknown command. Type 'help' for available commands")


if __name__ == "__main__":
    main()
