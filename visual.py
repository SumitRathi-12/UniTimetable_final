import json
from timetable_parser import TimetableData
from collections import defaultdict
import pprint

# Load timetable input (for metadata)
with open("files/instance_10_hard.json") as f:
    timetable_data = json.load(f)
timetable = TimetableData(timetable_data)

# Load solution
with open("result.GA_readable.json") as f:
    solution = json.load(f)

# Helper: course -> time, room
course_slots = {
    course_id: (slot_info["time_slot"], slot_info["room_id"])
    for course_id, slot_info in solution.items()
}

# === 1. Per Student Schedule ===
student_view = defaultdict(list)
for student_id, courses in timetable.student_enrollments.items():
    for cid in courses:
        if cid in course_slots:
            time, room = course_slots[cid]
            student_view[student_id].append((time, cid, room))
    student_view[student_id].sort()

print("\n🧑 Per Student View:")
for sid, entries in student_view.items():
    print(f"\nStudent {sid}:")
    for time, cid, room in entries:
        print(f"  {time} - {cid} in {room}")

# === 2. Per Lecturer View ===
lecturer_view = defaultdict(list)
for course in timetable.courses:
    if course.id in course_slots:
        time, room = course_slots[course.id]
        lecturer_view[course.lecturer].append((time, course.id, room))
for lec in lecturer_view:
    lecturer_view[lec].sort()

print("\n🧑‍🏫 Per Lecturer View:")
for lec, entries in lecturer_view.items():
    print(f"\nLecturer {lec}:")
    for time, cid, room in entries:
        print(f"  {time} - {cid} in {room}")

# === 3. Per Room View ===
room_view = defaultdict(list)
for cid, (time, room) in course_slots.items():
    room_view[room].append((time, cid))
for r in room_view:
    room_view[r].sort()

print("\n🏫 Per Room View:")
for room, entries in room_view.items():
    print(f"\nRoom {room}:")
    for time, cid in entries:
        print(f"  {time} - {cid}")
