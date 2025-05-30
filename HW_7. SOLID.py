import enum


class Role(enum.StrEnum):
    STUDENT = enum.auto()
    TEACHER = enum.auto()


class User:
    def __init__(self, name: str, email: str, role: Role) -> None:
        self.name = name
        self.email = email
        self.role = role

    def send_notification(self, notification: "Notification") -> None:
        # Check that the notification and role match
        if self.role == Role.STUDENT and not isinstance(notification, (Notification, StudentNotification)):
            raise TypeError("Students can only receive general or student notifications.")
        if self.role == Role.TEACHER and not isinstance(notification, (Notification, TeacherNotification)):
            raise TypeError("Teachers can only receive general or teacher notifications.")

        # Print notification
        print(f"Sending notification to {self.name} ({self.email}) as {self.role}:")
        print(notification)
        print()  # Add empty line for better readability


class Notification:
    def __init__(self, subject: str, message: str, attachment: str = "") -> None:
        self.subject = subject
        self.message = message
        self.attachment = attachment  # Optional extra info

    def format(self) -> str:
        # Basic notification formatting
        formatted = f"Subject: {self.subject}\nMessage: {self.message}"
        if self.attachment:
            formatted += f"\nAttachment: {self.attachment}"
        return formatted

    def __str__(self) -> str:
        # Use format method for string representation
        return self.format()


class StudentNotification(Notification):
    def format(self) -> str:
        base_message = super().format()
        return f"{base_message}\nSent via Student Portal"


class TeacherNotification(Notification):
    def format(self) -> str:
        base_message = super().format()
        return f"{base_message}\nTeacher's Desk Notification"


def main():
    student = User("Alice", "alice@gmail.com", Role.STUDENT)
    teacher = User("Jack", "jack@gmail.com", Role.TEACHER)

    general_notification = Notification(
        "Important Announcement",
        "School will be closed tomorrow due to weather conditions."
    )

    student_notification = StudentNotification(
        "Homework Reminder",
        "Don't forget to submit your essay by Friday.",
        "essay_guidelines.pdf"
    )

    teacher_notification = TeacherNotification(
        "Staff Meeting",
        "There will be a staff meeting at 3pm in the conference room."
    )

    student.send_notification(general_notification)
    teacher.send_notification(general_notification)

    student.send_notification(student_notification)
    teacher.send_notification(teacher_notification)


if __name__ == "__main__":
    main()
