"""import random
import json
from timetable_parser import TimetableData
from fitnessfunction import evaluate_fitness
from datetime import datetime, timedelta

# === DTR Code Mapping ===
def generate_dtr_codes():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    start_time = datetime.strptime("08:00", "%H:%M")
    time_slots = [(start_time + timedelta(hours=i)).strftime("%H:%M") for i in range(11)]  # 08:00 to 18:00
    rooms = ["R1", "R2", "R3", "R4", "R5"]

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

# === GA Core Functions ===
def generate_random_individual(courses, dtr_codes):
    return {course.id: random.choice(dtr_codes) for course in courses}

def initialize_population(timetable, dtr_codes, size=50):
    return [generate_random_individual(timetable.courses, dtr_codes) for _ in range(size)]

def crossover(parent1, parent2):
    return {
        course: random.choice([parent1[course], parent2[course]])
        for course in parent1
    }

def mutate(individual, dtr_codes, mutation_rate=0.05):
    new_ind = individual.copy()
    for course in new_ind:
        if random.random() < mutation_rate:
            new_ind[course] = random.choice(dtr_codes)
    return new_ind

def convert_solution(encoded_solution, dtr_map):
    return {
        course_id: {
            "time_slot": f"{dtr_map[dtr][0]} {dtr_map[dtr][1]}",
            "room_id": dtr_map[dtr][2]
        }
        for course_id, dtr in encoded_solution.items()
    }

def genetic_algorithm(timetable, generations=100, pop_size=50):
    dtr_map, _ = generate_dtr_codes()
    dtr_codes = list(dtr_map.keys())
    population = initialize_population(timetable, dtr_codes, pop_size)

    for gen in range(generations):
        scored_population = [
            (ind, evaluate_fitness(timetable, convert_solution(ind, dtr_map)))
            for ind in population
        ]
        scored_population.sort(key=lambda x: x[1], reverse=True)

        print(f"Generation {gen}: Best Fitness = {scored_population[0][1]}")

        next_gen = [scored_population[0][0]]  # elitism

        while len(next_gen) < pop_size:
            parents = random.sample(scored_population[:10], 2)
            child = crossover(parents[0][0], parents[1][0])
            child = mutate(child, dtr_codes)
            next_gen.append(child)

        population = next_gen

    best_individual = scored_population[0][0]
    best_solution = convert_solution(best_individual, dtr_map)
    return best_solution

# === Main Runner ===
if __name__ == "__main__":
    with open("files/instance_10_hard.json") as f:
        data = json.load(f)

    timetable = TimetableData(data)
    best_schedule = genetic_algorithm(timetable, generations=100, pop_size=50)

    print("\nStudent schedules:")
    for student_id, enrolled_courses in timetable.student_enrollments.items():
        print(f"\n🧑‍🎓 Student {student_id}")
        schedule = []
        for course_id in enrolled_courses:
            if course_id in best_schedule:
                slot = best_schedule[course_id]
                schedule.append((slot["time_slot"], course_id, slot["room_id"]))
        # Sort by day/time for readability
        schedule.sort()
        for entry in schedule:
            print(f"  {entry[0]} - {entry[1]} in {entry[2]}")

    print("\nBest schedule found:")
    for course_id, assignment in best_schedule.items():
        print(f"{course_id}: {assignment['time_slot']}, {assignment['room_id']}")



import csv

# Prepare rows for CSV
rows = [("Student ID", "Day", "Time", "Course ID", "Room")]

for student_id, enrolled_courses in timetable.student_enrollments.items():
    for course_id in enrolled_courses:
        if course_id in best_schedule:
            time_slot = best_schedule[course_id]["time_slot"]
            room = best_schedule[course_id]["room_id"]
            day, time = time_slot.split()
            rows.append((student_id, day, time, course_id, room))

# Export to CSV
with open("student_schedules.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(rows)

print("\n📁 Student schedules exported to 'student_schedules.csv'")"""

import random
import json
from timetable_parser import TimetableData
from fitnessfunction import evaluate_fitness
from datetime import datetime, timedelta

# === DTR Code Mapping ===
def generate_dtr_codes():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    start_time = datetime.strptime("08:00", "%H:%M")
    time_slots = [(start_time + timedelta(hours=i)).strftime("%H:%M") for i in range(11)]  # 08:00 to 18:00
    rooms = ["R1", "R2", "R3", "R4", "R5"]

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

# === GA Core Functions ===
def generate_random_individual(courses, dtr_codes):
    return {course.id: random.choice(dtr_codes) for course in courses}

def initialize_population(timetable, dtr_codes, size=50):
    return [generate_random_individual(timetable.courses, dtr_codes) for _ in range(size)]

def crossover(parent1, parent2, operator="uniform"):
    if operator == "uniform":
        return uniform_crossover(parent1, parent2)
    elif operator == "ox":
        return order_crossover(parent1, parent2)
    elif operator == "pmx":
        return pmx_crossover(parent1, parent2)
    else:
        raise ValueError(f"Unknown crossover operator: {operator}")

def uniform_crossover(parent1, parent2):
    child = {}
    for key in parent1:
        child[key] = random.choice([parent1[key], parent2[key]])
    return child

def order_crossover(parent1, parent2):
    keys = list(parent1.keys())
    size = len(keys)
    start, end = sorted(random.sample(range(size), 2))

    child = {k: None for k in keys}

    # Copy the slice from parent1
    for i in range(start, end + 1):
        child[keys[i]] = parent1[keys[i]]

    # Fill remaining from parent2
    p2_values = [parent2[k] for k in keys if parent2[k] not in child.values()]
    for k in keys:
        if child[k] is None:
            child[k] = p2_values.pop(0)
    return child

def pmx_crossover(parent1, parent2):
    keys = list(parent1.keys())
    size = len(keys)
    start, end = sorted(random.sample(range(size), 2))

    child = parent1.copy()
    for i in range(start, end + 1):
        key = keys[i]
        val_from_p2 = parent2[key]

        if val_from_p2 not in child.values():
            for k in keys:
                if child[k] == val_from_p2:
                    child[k] = parent2[k]
                    break
            child[key] = val_from_p2
    return child

def mutate(individual, dtr_codes, mutation_rate=0.05):
    new_ind = individual.copy()
    for course in new_ind:
        if random.random() < mutation_rate:
            new_ind[course] = random.choice(dtr_codes)
    return new_ind

def convert_solution(encoded_solution, dtr_map):
    return {
        course_id: {
            "time_slot": f"{dtr_map[dtr][0]} {dtr_map[dtr][1]}",
            "room_id": dtr_map[dtr][2]
        }
        for course_id, dtr in encoded_solution.items()
    }

def genetic_algorithm(timetable, generations=100, pop_size=50, mutation_rate=0.01, crossover_operator="uniform"):
    dtr_map, _ = generate_dtr_codes()
    dtr_codes = list(dtr_map.keys())
    population = initialize_population(timetable, dtr_codes, pop_size)

    for gen in range(generations):
        scored_population = [
            (ind, evaluate_fitness(timetable, convert_solution(ind, dtr_map)))
            for ind in population
        ]
        scored_population.sort(key=lambda x: x[1], reverse=True)

        print(f"Generation {gen}: Best Fitness = {scored_population[0][1]}")

        next_gen = [scored_population[0][0]]  # elitism

        while len(next_gen) < pop_size:
            parents = random.sample(scored_population[:10], 2)
            child = crossover(parents[0][0], parents[1][0], operator=crossover_operator)
            child = mutate(child, dtr_codes, mutation_rate=mutation_rate)
            next_gen.append(child)

        population = next_gen

    best_individual = scored_population[0][0]
    best_solution = convert_solution(best_individual, dtr_map)
    return best_solution


# === Main Test Runner ===
if __name__ == "__main__":
    with open("files/instance_10_hard.json") as f:
        data = json.load(f)

    timetable = TimetableData(data)
    best_schedule = genetic_algorithm(timetable, generations=100, pop_size=50)

    print("\nStudent schedules:")
    for student_id, enrolled_courses in timetable.student_enrollments.items():
        print(f"\n🧑‍🎓 Student {student_id}")
        schedule = []
        for course_id in enrolled_courses:
            if course_id in best_schedule:
                slot = best_schedule[course_id]
                schedule.append((slot["time_slot"], course_id, slot["room_id"]))
        schedule.sort()
        for entry in schedule:
            print(f"  {entry[0]} - {entry[1]} in {entry[2]}")

    print("\nBest schedule found:")
    for course_id, assignment in best_schedule.items():
        print(f"{course_id}: {assignment['time_slot']}, {assignment['room_id']}")

    # === CSV Export ===
    import csv
    rows = [("Student ID", "Day", "Time", "Course ID", "Room")]
    for student_id, enrolled_courses in timetable.student_enrollments.items():
        for course_id in enrolled_courses:
            if course_id in best_schedule:
                time_slot = best_schedule[course_id]["time_slot"]
                room = best_schedule[course_id]["room_id"]
                day, time = time_slot.split()
                rows.append((student_id, day, time, course_id, room))

    with open("student_schedules.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print("\n📁 Student schedules exported to 'student_schedules.csv'")