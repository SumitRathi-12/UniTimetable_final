from datetime import datetime, timedelta

# Define time slots
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
start_time = datetime.strptime("08:00", "%H:%M")
time_slots = [(start_time + timedelta(hours=i)).strftime("%H:%M") for i in range(11)]  # 08:00 to 18:00
rooms = ["R1", "R2", "R3", "R4", "R5"]

# Total combinations: day × time × room = 5 × 11 × 5 = 275
def decode_dtr(dtr_code: str) -> str:
    index = int(dtr_code.replace("DTR", "")) - 1  # Convert to 0-based index

    total_per_room = len(days) * len(time_slots)  # 5 × 11 = 55
    room_index = index // total_per_room
    remainder = index % total_per_room

    day_index = remainder // len(time_slots)
    time_index = remainder % len(time_slots)

    try:
        return f"{days[day_index]} {time_slots[time_index]}, {rooms[room_index]}"
    except IndexError:
        return "Invalid DTR code"

# Example usage
for i in [4, 2, 55, 56, 110, 275]:
    print(f"DTR{i} ➜ {decode_dtr(f'DTR{i}')}")
