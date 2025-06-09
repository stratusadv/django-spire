from abc import ABC


class BasePerson(ABC):
    def __init__(self, name):
        self.name = name

    class Meta:
        abstract = True


class BaseStudent(BasePerson, ABC):
    def __init__(self, name, student_id):
        super().__init__(name)
        self.student_id = student_id

    class Meta:
        abstract = True


class Student(BaseStudent):
    def __init__(self, name, student_id, gpa):
        super().__init__(name, student_id)
        self.gpa = gpa


new_student = Student("Nathan", 12345, 3.5)

print(new_student.__ba)