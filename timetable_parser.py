import json
from typing import List, Dict

class Course:
    def __init__(self, course_id: str, lecturer: str, students: List[int], preferred_rooms: List[str]):
        self.id = course_id
        self.lecturer = lecturer
        self.students = students
        self.preferred_rooms = preferred_rooms

class Room:
    def __init__(self, room_id: str, capacity: int):
        self.id = room_id
        self.capacity = capacity

class TimetableData:
    def __init__(self, json_data: dict):
        self.courses: List[Course] = [
            Course(course['id'], course['lecturer'], course['students'], course['preferred_rooms'])
            for course in json_data['courses']
        ]
        self.rooms: List[Room] = [
            Room(room['id'], room['capacity']) for room in json_data['rooms']
        ]
        self.time_slots: List[str] = json_data['time_slots']
        self.lecturer_availability: Dict[str, List[str]] = json_data['lecturer_availability']
        self.student_enrollments: Dict[int, List[str]] = {
            int(student_id): enrolled_courses for student_id, enrolled_courses in json_data['student_enrollments'].items()
        }

    def get_course_by_id(self, course_id: str) -> Course:
        return next((c for c in self.courses if c.id == course_id), None)

    def get_room_by_id(self, room_id: str) -> Room:
        return next((r for r in self.rooms if r.id == room_id), None)

    def get_student_courses(self, student_id: int) -> List[str]:
        return self.student_enrollments.get(student_id, [])

if __name__ == "__main__":
    with open('files/instance_10_hard.json', 'r') as f:
        data = json.load(f)

    timetable = TimetableData(data)

    for course in timetable.courses:
        print(f"{course.id} taught by {course.lecturer} with preferred rooms {course.preferred_rooms}")
