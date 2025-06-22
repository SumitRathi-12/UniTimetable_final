import time
import json
import csv
from timetable_parser import TimetableData
from genetic_algorithm import genetic_algorithm, generate_dtr_codes, convert_solution

# Define experiment configurations
instances = {
    "easy": "files/instance_1_easy.json",
    "medium": "files/instance_5_easy.json",
    "hard": "files/instance_10_hard.json"
}

# Example parameter sets for tuning
parameter_sets = [
    {"generations": 50, "pop_size": 30},
    {"generations": 100, "pop_size": 30},
    {"generations": 100, "pop_size": 50},
    {"generations": 150, "pop_size": 50},
    {"generations": 200, "pop_size": 60}
]

# Store results
results = [("Instance", "Run", "Generations", "Pop Size", "Best Fitness", "Time (s)")]

for instance_name, instance_path in instances.items():
    with open(instance_path) as f:
        data = json.load(f)

    timetable = TimetableData(data)

    for run_id, params in enumerate(parameter_sets, start=1):
        print(f"\n🔁 Running {instance_name} - Run {run_id} with {params}")
        start_time = time.time()

        best_solution = genetic_algorithm(
            timetable,
            generations=params["generations"],
            pop_size=params["pop_size"]
        )

        duration = time.time() - start_time

        # Evaluate best fitness
        from fitnessfunction import evaluate_fitness
       # from genetic_algorithm import generate_dtr_codes, convert_solution

        dtr_map, _ = generate_dtr_codes()
        fitness = evaluate_fitness(timetable, best_solution)

        # Log result
        results.append((
            instance_name,
            run_id,
            params["generations"],
            params["pop_size"],
            fitness,
            round(duration, 2)
        ))

# Save to CSV
with open("experiment_results.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(results)

print("\n✅ All experiments complete. Results saved to 'experiment_results.csv'.")
