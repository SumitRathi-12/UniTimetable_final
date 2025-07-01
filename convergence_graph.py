import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("convergence_no_repair.csv")

# Plot settings
plt.figure(figsize=(12, 6))

# Plot for each instance
for instance in df['Instance'].unique():
    instance_data = df[df['Instance'] == instance]
    plt.plot(instance_data['Evaluations'], instance_data['Best Fitness'], label=instance)

# Graph labels and title
plt.xlabel("Evaluations")
plt.ylabel("Best Fitness")
plt.title("Convergence Graph: Evaluations vs Best Fitness")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save and show the plot
plt.savefig("convergence_plot.png", dpi=300)
plt.show()
