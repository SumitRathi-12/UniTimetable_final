import json
from timetable_parser import TimetableData
from fitnessfunction import evaluate_fitness


with open('files/instance_10_hard.json') as f:
    data = json.load(f)
timetable = TimetableData(data)

# Example solution
solution = {
    "C1": {"time_slot": "Monday 09:00", "room_id": "R5"},
    "C2": {"time_slot": "Monday 10:00", "room_id": "R5"},
    "C3": {"time_slot": "Monday 11:00", "room_id": "R5"},
    "C4": {"time_slot": "Tuesday 09:00", "room_id": "R2"},
    "C5": {"time_slot": "Tuesday 10:00", "room_id": "R2"},
    "C6": {"time_slot": "Tuesday 11:00", "room_id": "R4"},
    "C7": {"time_slot": "Wednesday 09:00", "room_id": "R2"},
    "C8": {"time_slot": "Wednesday 10:00", "room_id": "R1"},
    "C9": {"time_slot": "Thursday 09:00", "room_id": "R2"},
    "C10": {"time_slot": "Thursday 10:00", "room_id": "R3"}
}


score = evaluate_fitness(timetable, solution)
print(f"Fitness Score: {score}")
