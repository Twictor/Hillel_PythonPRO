import enum


class Role(enum.StrEnum):
    STUDENT = enum.auto()
    TEACHER = enum.auto()


class User:
    def __init__(self, name: str, email: str, role: Role) -> None:
        self.name = name
        self.email = email
        self.role = role

    def send_notification(self, notification):
        # Print out the notification with user info
        print(f"Sending notification to {self.name} ({self.email}) as {self.role}:")
        print(notification.format())
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
        # Add "Sent via Student Portal" to the message
        base_message = super().format()
        return f"{base_message}\nSent via Student Portal"


class TeacherNotification(Notification):
    def format(self) -> str:
        # Add "Teacher's Desk Notification" to the message
        base_message = super().format()
        return f"{base_message}\nTeacher's Desk Notification"


def main():
    # Create users of both types
    student = User("Alice", "alice@gmail.com", Role.STUDENT)
    teacher = User("Jack", "jack@gmail.com", Role.TEACHER)

    # Create notifications
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

    # Have users print (aka send) their notifications
    student.send_notification(general_notification)
    teacher.send_notification(general_notification)

    student.send_notification(student_notification)
    teacher.send_notification(teacher_notification)


if __name__ == "__main__":
    main()
