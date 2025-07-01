# repair_utils.py

import random
from datetime import datetime, timedelta

def generate_dtr_codes(timetable_data):
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


    def repair_individual_advanced(individual, timetable, dtr_map, reverse_dtr_map, max_evaluations=5000):
        # your repair code...
        # at the end before returning:
        print("Repair function output:", individual)
        return individual

    pass
