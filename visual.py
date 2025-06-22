import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from timetable_parser import TimetableData
import json

# Sample time order
time_order = ["09:00", "10:00", "11:00", "13:00", "14:00"]
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def parse_slot(slot):
    day, time = slot.split()
    return day, time


def plot_timetable(solution, timetable: TimetableData, title="Timetable Visualization"):
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot grid
    ax.set_xticks(range(len(time_order)))
    ax.set_xticklabels(time_order)
    ax.set_yticks(range(len(day_order)))
    ax.set_yticklabels(day_order)
    ax.set_xlim(-0.5, len(time_order) - 0.5)
    ax.set_ylim(-0.5, len(day_order) - 0.5)
    ax.grid(True)

    colors = plt.cm.tab10.colors  # 10 unique colors
    legend_items = {}

    for i, (course_id, assignment) in enumerate(solution.items()):
        day, time = parse_slot(assignment["time_slot"])
        if day not in day_order or time not in time_order:
            continue
        y = day_order.index(day)
        x = time_order.index(time)
        lecturer = timetable.get_course_by_id(course_id).lecturer
        label = f"{course_id} ({assignment['room_id']})"

        color_index = hash(lecturer) % len(colors)
        color = colors[color_index]
        ax.add_patch(mpatches.Rectangle((x - 0.4, y - 0.4), 0.8, 0.8, color=color, alpha=0.7))
        ax.text(x, y, label, ha='center', va='center', fontsize=8, color='black')

        if lecturer not in legend_items:
            legend_items[lecturer] = mpatches.Patch(color=color, label=lecturer)

    plt.title(title)
    plt.legend(handles=list(legend_items.values()), bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


# === Example usage ===
if __name__ == "__main__":
    with open("files/instance_10_hard.json") as f:
        data = json.load(f)
    timetable = TimetableData(data)

    # Sample solution with "Monday 09:00" format
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

    plot_timetable(solution, timetable)
