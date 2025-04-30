import re

students = []

def add_student(name: str, marks: list[int], details: str | None):
    student_id = len(students) + 1
    students.append({
        "id": student_id,
        "name": name,
        "marks": marks,
        "info": details if details else ""
    })
def is_valid_name(name: str):
    return bool(re.fullmatch(r"[A-Za-z ]+", name.strip()))

def show_students():
    if not students:
        print("Student list is empty.")
        return
    for student in students:
        print(f"ID: {student['id']}, Name: {student['name']}, Marks: {student['marks']}, Info: {student['info']}")


def show_student(student_id: int):
    for student in students:
        if student['id'] == student_id:
            print(f"ID: {student['id']}\nName: {student['name']}\nMarks: {student['marks']}\nInfo: {student['info']}")
            return
    print("Student with this ID not found.")


def main():
    while True:
        print("\nMenu:")
        print("1. Add student")
        print("2. Show all students")
        print("3. Show student by ID")
        print("4. Exit")
        choice = input("Choose an option (1-4): ")

        if choice == "1":
            while True:
                name = input("Enter student name: ").strip()
                if not name:
                    print("Name is required. Please enter a valid name.")
                    continue
                if not is_valid_name(name):
                    print("Name must contain only letters and spaces.")
                    continue
                break

            marks_input = input("Enter marks: ")
            try:
                marks = [int(mark.strip()) for mark in marks_input.split(",") if mark.strip()]
            except ValueError:
                print("Invalid marks format.")
                continue

            details = input("Enter additional info: ")
            add_student(name, marks, details if details else None)
            print("Student added.")

        elif choice == "2":
            show_students()

        elif choice == "3":
            try:
                student_id = int(input("Enter student ID: "))
                show_student(student_id)
            except ValueError:
                print("Invalid input. ID must be a number.")

        elif choice == "4":
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please try again.")


main()
