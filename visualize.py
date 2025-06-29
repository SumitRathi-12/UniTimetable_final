import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the result file
with open("result.GA_readable.json") as f:
    schedule = json.load(f)

# Prepare a list of tuples: (Course, Day, Time, Room)
entries = []
for course_id, details in schedule.items():
    day, time = details["time_slot"].split()
    room = details["room_id"]
    entries.append((day, time, room, course_id))

# Create a DataFrame
df = pd.DataFrame(entries, columns=["Day", "Time", "Room", "Course"])

# Pivot table to create a timetable grid
pivot = df.pivot_table(index=["Time"], columns=["Day", "Room"], values="Course", aggfunc=lambda x: ' / '.join(x))

# Sort time index for display
pivot = pivot.sort_index(key=lambda times: pd.to_datetime(times, format="%H:%M"))

# === Text display version ===
print("\n🗓 Weekly Timetable (Course IDs):")
print(pivot.fillna("-"))

# === Optional: Heatmap-style plot (rooms per time/day) ===
plt.figure(figsize=(15, 8))
sns.heatmap(pivot.notnull(), cmap="Purples", cbar=False, linewidths=.5, linecolor='gray', annot=pivot.fillna(""), fmt="", annot_kws={"size": 8})
plt.title("Room Usage Timetable (Course IDs)", fontsize=14)
plt.xlabel("Day / Room")
plt.ylabel("Time")
plt.tight_layout()
plt.show()
