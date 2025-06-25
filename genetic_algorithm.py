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

    course_ids = sorted(parent1.keys())
    p1_list = [parent1[course] for course in course_ids]
    p2_list = [parent2[course] for course in course_ids]

    if operator == "ox":
        child_list = order_crossover(p1_list, p2_list)
    elif operator == "pmx":
        child_list = pmx_crossover(p1_list, p2_list)
    else:
        raise ValueError(f"Unknown crossover operator: {operator}")

    # Rebuild dictionary using course_ids
    child = {course: dtr for course, dtr in zip(course_ids, child_list)}
    return child

def uniform_crossover(parent1, parent2):
    child = {}
    for key in parent1:
        child[key] = random.choice([parent1[key], parent2[key]])
    return child

def order_crossover(p1, p2):
    size = len(p1)
    start, end = sorted(random.sample(range(size), 2))

    child = [None] * size
    child[start:end + 1] = p1[start:end + 1]

    p2_idx = (end + 1) % size
    child_idx = (end + 1) % size

    while None in child:
        gene = p2[p2_idx]
        if gene not in child:
            child[child_idx] = gene
            child_idx = (child_idx + 1) % size
        p2_idx = (p2_idx + 1) % size

    return child

def pmx_crossover(p1, p2):
    size = len(p1)
    start, end = sorted(random.sample(range(size), 2))

    child = [None] * size
    child[start:end + 1] = p1[start:end + 1]

    for i in range(start, end + 1):
        gene = p2[i]
        if gene not in child:
            pos = i
            while True:
                mapped_gene = p1[pos]
                pos = p2.index(mapped_gene)
                if child[pos] is None:
                    child[pos] = gene
                    break

    for i in range(size):
        if child[i] is None:
            child[i] = p2[i]

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

def genetic_algorithm(timetable, max_evaluations=5000, pop_size=50, mutation_rate=0.01,
                      crossover_rate=0.6,
                      crossover_operator="uniform",
                      use_repair=False,
                      dtr_map=None,
                      reverse_dtr_map=None,
                      repair_fn=None
                      ):
    dtr_map, _ = generate_dtr_codes()
    dtr_codes = list(dtr_map.keys())
    population = initialize_population(timetable, dtr_codes, pop_size)

    evaluations = 0
    best_fitness = float('-inf')
    best_individual = None

    while evaluations < max_evaluations:
        scored_population = [
            (ind, evaluate_fitness(timetable, convert_solution(ind, dtr_map)))
            for ind in population
        ]
        evaluations += len(scored_population)

        scored_population.sort(key=lambda x: x[1], reverse=True)
        if scored_population[0][1] > best_fitness:
            best_fitness = scored_population[0][1]
            best_individual = scored_population[0][0]

        print(f"Evaluations: {evaluations}, Best Fitness = {scored_population[0][1]}")

        next_gen = [scored_population[0][0]]  # elitism

        while len(next_gen) < pop_size:
            parents = random.sample(scored_population[:10], 2)

            if random.random() < crossover_rate:
                child = crossover(parents[0][0], parents[1][0], operator=crossover_operator)
            else:
                child = random.choice([parents[0][0], parents[1][0]])  # no crossover

            child = mutate(child, dtr_codes, mutation_rate=mutation_rate)

            if use_repair and repair_fn and dtr_map and reverse_dtr_map:
                child = repair_fn(child, timetable, dtr_map, reverse_dtr_map)

            next_gen.append(child)

    population = next_gen

    best_solution = convert_solution(best_individual, dtr_map)
    return best_solution

# === Main Test Runner ===
if __name__ == "__main__":
    with open("files/instance_10_hard.json") as f:
        data = json.load(f)

    timetable = TimetableData(data)
    best_schedule = genetic_algorithm(timetable, max_evaluations=10000, pop_size=50, mutation_rate=0.01, crossover_rate=0.8)

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
