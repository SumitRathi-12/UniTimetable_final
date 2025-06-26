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
    elif operator == "single_point":
        course_ids = sorted(parent1.keys())
        p1_list = [parent1[course] for course in course_ids]
        p2_list = [parent2[course] for course in course_ids]
        child_list = single_point_crossover(p1_list, p2_list)
        return {course: dtr for course, dtr in zip(course_ids, child_list)}
    else:
        raise ValueError(f"Unknown crossover operator: {operator}")

def uniform_crossover(parent1, parent2):
    child = {}
    for key in parent1:
        child[key] = random.choice([parent1[key], parent2[key]])
    return child

def single_point_crossover(parent1, parent2):
    """Single-point crossover for list-based chromosomes."""
    if len(parent1) != len(parent2):
        raise ValueError("Parents must be the same length.")

    point = random.randint(1, len(parent1) - 1)
    child = parent1[:point] + parent2[point:]
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
                      repair_fn=None):
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
    best_schedule = genetic_algorithm(
        timetable,
        max_evaluations=5000,
        pop_size=50,
        mutation_rate=0.01,
        crossover_rate=0.8,
        crossover_operator="uniform"  # Change to "single_point" to test single-point crossover
    )

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

    with open("result.GA.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print("\n📁 Student schedules exported to 'result_GA.csv'")
