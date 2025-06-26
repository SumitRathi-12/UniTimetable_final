import random
import json
from datetime import datetime, timedelta
from typing import Dict, Tuple, List, Set, Optional

from timetable_parser import TimetableData, Course, Room
from genetic_algorithm import genetic_algorithm  # ✅ Make sure this version only has uniform and single_point crossover


def generate_dtr_codes(timetable_data: TimetableData):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    start_time = datetime.strptime("08:00", "%H:%M")
    time_slots = [(start_time + timedelta(hours=i)).strftime("%H:%M") for i in range(11)]
    rooms = [room.id for room in timetable_data.rooms]

    dtr_map = {}
    reverse_map = {}
    index = 1

    for room in rooms:
        for day in days:
            for time in time_slots:
                dtr_code = f"DTR{index}"
                dtr_map[dtr_code] = (day, time, room)
                reverse_map[(day, time, room)] = dtr_code
                index += 1

    return dtr_map, reverse_map


def repair_individual_advanced(individual, timetable_data, dtr_map, reverse_dtr_map, max_evaluations=5000):
    repaired_individual = individual.copy()

    all_rooms = [room.id for room in timetable_data.rooms]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = [(datetime.strptime("08:00", "%H:%M") + timedelta(hours=i)).strftime("%H:%M") for i in range(11)]

    def find_suitable_slot(course_id, current_state, excluded_slot=None):
        course = timetable_data.get_course_by_id(course_id)
        if not course:
            return None

        course_students = course.students
        lecturer = course.lecturer
        lecturer_unavailable = {
            tuple(x.split()) for x in timetable_data.lecturer_availability.get(lecturer, [])
        }

        occupied_slots = set()
        lecturer_slots = set()
        student_schedules = {}

        for cid, dtr in current_state.items():
            day, time, room = dtr_map[dtr]
            occupied_slots.add((day, time, room))
            c = timetable_data.get_course_by_id(cid)
            if c:
                lecturer_slots.add((day, time, c.lecturer))
                for s in c.students:
                    student_schedules.setdefault(s, set()).add((day, time))

        rooms_to_try = list(course.preferred_rooms) + [r for r in all_rooms if r not in course.preferred_rooms]
        random.shuffle(rooms_to_try)

        for room in rooms_to_try:
            room_obj = timetable_data.get_room_by_id(room)
            if not room_obj or room_obj.capacity < len(course_students):
                continue

            for day in random.sample(days, len(days)):
                for time in random.sample(time_slots, len(time_slots)):
                    slot = (day, time, room)
                    time_key = (day, time)

                    if excluded_slot == slot:
                        continue
                    if slot in occupied_slots:
                        continue
                    if (day, time, lecturer) in lecturer_slots:
                        continue
                    if time_key in lecturer_unavailable:
                        continue
                    if any(time_key in student_schedules.get(s, set()) for s in course_students):
                        continue
                    if slot in reverse_dtr_map:
                        return reverse_dtr_map[slot]

        return None

    def room_conflicts(indiv):
        occupancy = {}
        conflicts = []
        for cid, dtr in indiv.items():
            key = dtr_map[dtr]
            occupancy.setdefault(key, []).append(cid)
        for k, v in occupancy.items():
            if len(v) > 1:
                print(f"❗ Room conflict at {k}: {v}")
                conflicts.extend(v[1:])
        return conflicts

    def lecturer_conflicts(indiv):
        schedule = {}
        conflicts = []
        for cid, dtr in indiv.items():
            c = timetable_data.get_course_by_id(cid)
            if not c:
                continue
            day, time, _ = dtr_map[dtr]
            k = (day, time, c.lecturer)
            schedule.setdefault(k, []).append(cid)
        for k, v in schedule.items():
            if len(v) > 1:
                print(f"❗ Lecturer conflict at {k}: {v}")
                conflicts.extend(v[1:])
        return conflicts

    def student_conflicts(indiv):
        schedule = {}
        conflicts = []
        for cid, dtr in indiv.items():
            c = timetable_data.get_course_by_id(cid)
            if not c:
                continue
            day, time, _ = dtr_map[dtr]
            key = (day, time)
            for s in c.students:
                schedule.setdefault((s, key), []).append(cid)
        for (s, key), v in schedule.items():
            if len(v) > 1:
                print(f"❗ Student conflict for student {s} at {key}: {v}")
                conflicts.extend(v[1:])
        return list(set(conflicts))

    def capacity_or_unavailable(indiv):
        conflicts = []
        for cid, dtr in indiv.items():
            c = timetable_data.get_course_by_id(cid)
            if not c:
                continue
            day, time, room = dtr_map[dtr]
            room_obj = timetable_data.get_room_by_id(room)
            if room_obj and room_obj.capacity < len(c.students):
                print(f"❗ Capacity conflict: {cid} in {room} (capacity {room_obj.capacity}) with {len(c.students)} students")
                conflicts.append(cid)
            if (day, time) in {
                tuple(x.split()) for x in timetable_data.lecturer_availability.get(c.lecturer, [])
            }:
                print(f"❗ Unavailability conflict: {c.lecturer} unavailable at {day} {time} for {cid}")
                conflicts.append(cid)
        return conflicts

    checks = [room_conflicts, lecturer_conflicts, student_conflicts, capacity_or_unavailable]

    evaluation_count = 0
    while evaluation_count < max_evaluations:
        all_resolved = True
        for check_fn in checks:
            to_reassign = check_fn(repaired_individual)
            evaluation_count += 1
            if to_reassign:
                all_resolved = False
                print(f"🛠️ Eval {evaluation_count}: Reassigning {len(to_reassign)} due to {check_fn.__name__}")
                for cid in to_reassign:
                    new_dtr = find_suitable_slot(cid, repaired_individual, excluded_slot=dtr_map[repaired_individual[cid]])
                    repaired_individual[cid] = new_dtr or random.choice(list(dtr_map.keys()))
            if evaluation_count >= max_evaluations:
                print("⚠️ Max evaluations reached.")
                break
        if all_resolved:
            print("✅ All conflicts resolved before max evaluations.")
            break

    return repaired_individual


if __name__ == "__main__":
    with open("files/instance_10_hard.json") as f:
        data = json.load(f)
    timetable = TimetableData(data)

    dtr_map, reverse_dtr_map = generate_dtr_codes(timetable)

    print("\n🚀 Running Genetic Algorithm with Repair Function...\n")

    # Run the GA with selected crossover operator
    best_solution = genetic_algorithm(
        timetable,
        max_evaluations=10000,
        pop_size=50,
        mutation_rate=0.01,
        crossover_rate=0.7,
        crossover_operator="uniform",  # ✅ Only "uniform" or "single_point" supported
        use_repair=True,
        dtr_map=dtr_map,
        reverse_dtr_map=reverse_dtr_map,
        repair_fn=repair_individual_advanced
    )

    # Display best schedule
    print("\n✅ Best Schedule:")
    for course_id, assignment in best_solution.items():
        day, time = assignment['time_slot'].split()
        room = assignment['room_id']
        print(f"{course_id}: {day} {time} in {room}")

    # Export to CSV
    import csv
    with open("result_GADK.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Student ID", "Day", "Time", "Course ID", "Room"])
        for student_id, enrolled in timetable.student_enrollments.items():
            for cid in enrolled:
                if cid in best_solution:
                    ts = best_solution[cid]["time_slot"]
                    room = best_solution[cid]["room_id"]
                    day, time = ts.split()
                    writer.writerow([student_id, day, time, cid, room])

    print("\n📄 Exported schedule to 'result_GADK.csv'")
