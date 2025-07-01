import os
import time
import json
import csv
from timetable_parser import TimetableData
from genetic_algorithm import genetic_algorithm
from fitnessfunction import evaluate_fitness

# Import repair utilities
from repair_utils import generate_dtr_codes

# === CONFIGURABLE PARAMETERS ===
CONFIG = {
    "pop_size": 30,
    "mutation_rate": 0.01,
    "crossover_rate": 0.6,
    "crossover_operator": "single_point",
    "max_evaluations": 10000,
    "use_repair": False  # Will be set in the loop
}
RUNS_PER_INSTANCE = 10
INSTANCE_FOLDER = "files"
OUTPUT_CSV = "final_experiment_results.csv"
LOG_FOLDER = "logs"

# Ensure log folder exists
os.makedirs(LOG_FOLDER, exist_ok=True)

# === Prepare Instances ===
instance_files = sorted([
    f for f in os.listdir(INSTANCE_FOLDER) if f.endswith(".json")
])

# === Output Header ===
results = [(
    "Instance", "Run", "Pop Size", "Mutation Rate", "Crossover Rate",
    "Crossover Op", "Use Repair", "Fitness", "Time (s)"
)]

# === Loop over repair modes ===
for use_repair_mode in [False, True]:
    CONFIG["use_repair"] = use_repair_mode
    print(f"\n=== Running experiments with use_repair = {use_repair_mode} ===")

    for filename in instance_files:
        instance_path = os.path.join(INSTANCE_FOLDER, filename)
        print(f"\n📄 Instance: {filename}")

        with open(instance_path) as f:
            data = json.load(f)

        timetable = TimetableData(data)

        # Generate repair mappings only if needed
        if CONFIG["use_repair"]:
            dtr_map, reverse_dtr_map = generate_dtr_codes(timetable)
        else:
            dtr_map, reverse_dtr_map = None, None

        # === Run GA multiple times ===
        for run in range(1, RUNS_PER_INSTANCE + 1):
            print(f"  🔁 Run {run}...", end=" ")

            log_filename = f"{filename.replace('.json', '')}_repair_{use_repair_mode}_run{run}.csv"
            log_path = os.path.join(LOG_FOLDER, log_filename)

            start_time = time.time()

            # Run GA
            best_solution = genetic_algorithm(
                timetable=timetable,
                max_evaluations=CONFIG["max_evaluations"],
                pop_size=CONFIG["pop_size"],
                mutation_rate=CONFIG["mutation_rate"],
                crossover_rate=CONFIG["crossover_rate"],
                crossover_operator=CONFIG["crossover_operator"],
                use_repair=CONFIG["use_repair"],
                dtr_map=dtr_map,
                reverse_dtr_map=reverse_dtr_map,
                log_progress_file=log_path
            )

            duration = round(time.time() - start_time, 2)
            fitness = evaluate_fitness(timetable, best_solution)

            results.append((
                filename, run,
                CONFIG["pop_size"], CONFIG["mutation_rate"],
                CONFIG["crossover_rate"], CONFIG["crossover_operator"],
                CONFIG["use_repair"], fitness, duration
            ))

            print(f"✅ Fitness: {fitness}, Time: {duration}s")

# === Save to summary CSV ===
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(results)

print(f"\n✅ All experiments complete. Summary saved to '{OUTPUT_CSV}'")
