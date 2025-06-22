from collections import defaultdict
from datetime import datetime
from typing import Dict
from timetable_parser import TimetableData  # Ensure this matches your actual file name

# Penalties for constraints (H for Hard/S for Soft)
PENALTIES = {
    'H1': 100,  # Student course conflict
    'H2': 80,   # Room overcapacity
    'H3': 90,   # Lecturer time conflict
    'H5': 100,  # Room time conflict
    'H6': 70,   # Lecturer too many classes/day
    'H7': 90,   # Student too many classes/day
    'S1': 5,    # Gaps in student schedule
    'S2': 3,    # Early classes
    'S3': 3,    # Late classes
    'S4': 5     # Too many classes in a day
}
BONUSES = {
    'S5': 5     # Balanced week
}

def parse_time_slot(slot: str):
    """Split 'Monday 08:00' into ('Monday', datetime.time)"""
    day, time_str = slot.split()
    return day, datetime.strptime(time_str, "%H:%M").time()

def evaluate_fitness(timetable: TimetableData, solution: Dict[str, Dict[str, str]]) -> int:
    hard_penalty = 0
    soft_penalty = 0
    soft_bonus = 0

    student_schedule = defaultdict(lambda: defaultdict(list))  # student_id -> day -> [times]
    lecturer_schedule = defaultdict(set)  # lecturer -> set(time_slots)
    room_schedule = defaultdict(lambda: defaultdict(str))  # day -> time_str -> room_id

    for course_id, assignment in solution.items():
        course = timetable.get_course_by_id(course_id)
        if not course:
            continue

        slot = assignment["time_slot"]
        room_id = assignment["room_id"]
        room = timetable.get_room_by_id(room_id)
        day, time = parse_time_slot(slot)

        # Hard Constraint H2: Room capacity exceeded
        if room and len(course.students) > room.capacity:
            hard_penalty += PENALTIES['H2']

        # Hard Constraint H3: Lecturer teaching multiple courses at same time
        if slot in lecturer_schedule[course.lecturer]:
            hard_penalty += PENALTIES['H3']
        lecturer_schedule[course.lecturer].add(slot)

        # Hard Constraint H5: Room used for multiple courses at same time
        if room_schedule[day].get(time.strftime('%H:%M')) == room_id:
            hard_penalty += PENALTIES['H5']
        else:
            room_schedule[day][time.strftime('%H:%M')] = room_id

        # Track student schedules for H1 and soft constraints
        for student_id in course.students:
            student_schedule[student_id][day].append(time)

    # Hard Constraint H1: Student enrolled in overlapping courses
    for student_id, days in student_schedule.items():
        for times in days.values():
            if len(times) != len(set(times)):
                hard_penalty += PENALTIES['H1']

    # Soft Constraint evaluation
    for student_id, days in student_schedule.items():
        class_days = 0
        for day, times in days.items():
            class_days += 1
            times.sort()

            # S1: Gaps in schedule
            for i in range(len(times) - 1):
                diff = (datetime.combine(datetime.today(), times[i + 1]) - datetime.combine(datetime.today(), times[i])).seconds / 3600
                if diff > 1:
                    soft_penalty += PENALTIES['S1']

            # S2 and S3: Early and Late classes
            for time in times:
                if time < datetime.strptime("09:00", "%H:%M").time():
                    soft_penalty += PENALTIES['S2']
                elif time >= datetime.strptime("18:00", "%H:%M").time():
                    soft_penalty += PENALTIES['S3']

            # S4: More than 4 classes in one day
            if len(times) > 4:
                soft_penalty += (len(times) - 4) * PENALTIES['S4']

        # S5: Balanced week (3–5 days of class)
        if 3 <= class_days <= 5:
            soft_bonus += BONUSES['S5']

    # Final fitness score
    fitness = 200 - hard_penalty - soft_penalty + soft_bonus
    return max(fitness, 0)
