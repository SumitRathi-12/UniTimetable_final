import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV
df = pd.read_csv("student_schedules.csv")

# Define grid
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
hours = [f"{h:02}:00" for h in range(8, 19)]  # 08:00 to 18:00

def plot_student_schedule(student_id):
    student_df = df[df["Student ID"] == student_id]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xticks(range(len(hours)))
    ax.set_xticklabels(hours)
    ax.set_yticks(range(len(days)))
    ax.set_yticklabels(days)
    ax.set_xlim(-0.5, len(hours) - 0.5)
    ax.set_ylim(-0.5, len(days) - 0.5)
    ax.grid(True)

    for _, row in student_df.iterrows():
        day = row["Day"]
        time = row["Time"]
        course = row["Course ID"]
        room = row["Room"]

        x = hours.index(time)
        y = days.index(day)
        label = f"{course}\n{room}"

        ax.add_patch(plt.Rectangle((x - 0.4, y - 0.4), 0.8, 0.8, color="skyblue"))
        ax.text(x, y, label, ha="center", va="center", fontsize=8)

    plt.title(f"Timetable for Student {student_id}")
    plt.tight_layout()
    plt.show()

# Example: Plot timetable for student ID 1
plot_student_schedule(1)
