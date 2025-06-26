import time
import json
import csv
import itertools
from timetable_parser import TimetableData
from genetic_algorithm import genetic_algorithm
from fitnessfunction import evaluate_fitness
from repair_function import generate_dtr_codes, repair_individual_advanced

# Define instances
instances = {
    "easy": "files/instance_1_easy.json",
    "medium": "files/instance_5_moderate.json",
    "hard": "files/instance_10_hard.json"
}

# Define parameter sets from your provided table
population_sizes = [30, 50, 100]
mutation_rates = [0.01, 0.05, 0.10]
crossover_rates = [0.6, 0.8, 0.95]
max_evaluations_list = [500]
crossover_operators = ['uniform', 'single_point']

# Prepare combinations of parameters
parameter_combinations = list(itertools.product(population_sizes, mutation_rates, max_evaluations_list, crossover_operators))

# Store results
results = [("Instance", "Pop Size", "Mutation Rate", "Max Evaluations", "Crossover Operator", "Best Fitness", "Time (s)")]

# Experiment
for instance_name, instance_path in instances.items():
    with open(instance_path) as f:
        data = json.load(f)

    timetable = TimetableData(data)
    dtr_map, reverse_dtr_map = generate_dtr_codes(timetable)

    for params in parameter_combinations:
        pop_size, mutation_rate, max_evaluations, crossover_op = params

        print(f"\n🔁 Instance: {instance_name}, PopSize: {pop_size}, Mutation: {mutation_rate}, MaxEvaluations: {max_evaluations}, Crossover: {crossover_op}")

        start_time = time.time()

        best_solution = genetic_algorithm(
            timetable,
            max_evaluations=max_evaluations,
            pop_size=pop_size,
            mutation_rate=mutation_rate,
            crossover_rate=0.7,  # Default crossover rate (can be parameterized if needed)
            crossover_operator=crossover_op,
            use_repair=True,
            dtr_map=dtr_map,
            reverse_dtr_map=reverse_dtr_map,
            repair_fn=repair_individual_advanced
        )

        duration = time.time() - start_time

        fitness = evaluate_fitness(timetable, best_solution)

        results.append((
            instance_name,
            pop_size,
            mutation_rate,
            max_evaluations,
            crossover_op,
            fitness,
            round(duration, 2)
        ))

# Save to CSV
with open("parameter_tuning.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(results)

print("\n✅ All experiments complete. Results saved to 'parameter_tuning.csv'.")
