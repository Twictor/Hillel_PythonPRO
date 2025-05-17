import time
from typing import Dict, Union, List, Optional


class TimerContext:
    def __enter__(self):
        self.start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.monotonic() - self.start
        print(f"Elapsed: {elapsed:.6f} seconds")  # Changed to 6 decimal places for more precise measurement


class StudentManager:
    def __init__(self):
        self.students = {}

    def add_student(self, student: Dict[str, Union[str, List[int]]]) -> Optional[int]:
        """Add a new student and return ID or None if failed."""
        if not student.get('name') or not student.get('marks'):
            return None

        new_id = max(self.students.keys()) + 1 if self.students else 1
        self.students[new_id] = student
        # self._save_students()  # Commented out as the method is not implemented
        return new_id


# Create a student manager
manager = StudentManager()

# Test 1: Measuring single student addition
print("=== Test 1: Adding single student ===")
with TimerContext():
    result = manager.add_student({'name': 'Ivan', 'marks': [5, 4, 3]})
print(f"Added student with ID: {result}")

# Test 2: Measuring addition of 1000 students
print("\n=== Test 2: Adding 1000 students ===")
with TimerContext():
    for i in range(1000):
        manager.add_student({'name': f'Student {i}', 'marks': [i % 5 + 1]})
print(f"Total students: {len(manager.students)}")

# Test 3: Measuring attempt to add invalid a student
print("\n=== Test 3: Attempt to add invalid student ===")
with TimerContext():
    result = manager.add_student({'name': '', 'marks': []})
print(f"Addition result: {result}")

# Test 4: Measurement with error
print("\n=== Test 4: Measurement with error ===")
try:
    with TimerContext():
        manager.add_student({'name': 'Erroneous', 'marks': [1, 2, 3]})
        raise ValueError("Artificial error")
except ValueError as e:
    print(f"Caught error: {e}")