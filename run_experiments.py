import time
import json
import csv
import itertools
from timetable_parser import TimetableData
from genetic_algorithm import genetic_algorithm, generate_dtr_codes
from fitnessfunction import evaluate_fitness

# Define instances
instances = {
    "easy": "files/instance_1_easy.json",
    "medium": "files/instance_5_moderate.json",
    "hard": "files/instance_10_hard.json"
}

# Define parameter sets from your provided table
population_sizes = [30, 50, 100]
mutation_rates = [0.01, 0.05, 0.10]
generations_list = [50, 100, 200]
crossover_operators = ['uniform', 'ox', 'pmx']

# Prepare combinations of parameters
parameter_combinations = list(itertools.product(population_sizes, mutation_rates, generations_list, crossover_operators))

# Store results
results = [("Instance", "Pop Size", "Mutation Rate", "Generations", "Crossover Operator", "Best Fitness", "Time (s)")]

# Experiment
for instance_name, instance_path in instances.items():
    with open(instance_path) as f:
        data = json.load(f)

    timetable = TimetableData(data)

    for params in parameter_combinations:
        pop_size, mutation_rate, generations, crossover_op = params

        print(f"\n🔁 Instance: {instance_name}, PopSize: {pop_size}, Mutation: {mutation_rate}, Generations: {generations}, Crossover: {crossover_op}")

        start_time = time.time()

        best_solution = genetic_algorithm(
            timetable,
            generations=generations,
            pop_size=pop_size,
            mutation_rate=mutation_rate,
            crossover_operator=crossover_op
        )

        duration = time.time() - start_time

        # Evaluate best fitness
        fitness = evaluate_fitness(timetable, best_solution)

        # Log result
        results.append((
            instance_name,
            pop_size,
            mutation_rate,
            generations,
            crossover_op,
            fitness,
            round(duration, 2)
        ))

# Save to CSV
with open("experiment_full_results.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(results)

print("\n✅ All experiments complete. Results saved to 'experiment_full_results.csv'.")
