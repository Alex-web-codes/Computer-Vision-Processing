import json
import pandas as pd

timetable_data = {
    "header": {
        "institution": "IIIT BHAGALPUR",
        "title": "Class Time Table [AUG-DEC] 2026-27",
        "batch": "2024-28-MAE"
    },
    "schedule": [
        {
            "Day": "Monday",
            "9:00 - 9:55": "-",
            "10:00 - 10:55": "ME309 (Room C002, SKK)",
            "11:00 - 11:55": "ME302 (Room C002, AG)",
            "12:00 - 12:55": "EC301 (Room C104, BP)",
            "14:00 - 14:55": "-",
            "15:00 - 15:55": "EC304 (Room C004, SU)",
            "16:00 - 16:55": "ME359 (Room C202, VK)",
            "17:00 - 17:55": "ME359 (Room C202, VK)"
        },
        {
            "Day": "Tuesday",
            "9:00 - 9:55": "ME309 (Room C003, SKK)",
            "10:00 - 10:55": "ME302 (Room C002, AG)",
            "11:00 - 11:55": "-",
            "12:00 - 12:55": "-",
            "14:00 - 14:55": "ME302 Lab (Room L003, AG, G1)",
            "15:00 - 15:55": "ME302 Lab (Room L003, AG, G1)",
            "16:00 - 16:55": "-",
            "17:00 - 17:55": "-"
        },
        {
            "Day": "Wednesday",
            "9:00 - 9:55": "EC304 (Room C001, SU)",
            "10:00 - 10:55": "EC301 (Room C104, BP)",
            "11:00 - 11:55": "ME309 (Room C002, SKK)",
            "12:00 - 12:55": "ME359 (Room C202, VK)",
            "14:00 - 14:55": "EC304 Lab (CC Floor3, SU)",
            "15:00 - 15:55": "EC304 Lab (CC Floor3, SU)",
            "16:00 - 16:55": "EC304 Lab (CC Floor3, SU)",
            "17:00 - 17:55": "EC304 Lab (CC Floor3, SU)"
        },
        {
            "Day": "Thursday",
            "9:00 - 9:55": "EC304 (Room C104, SU)",
            "10:00 - 10:55": "EC301 (Room C104, BP)",
            "11:00 - 11:55": "-",
            "12:00 - 12:55": "-",
            "14:00 - 14:55": "EC301 Lab (CC Floor3, BP)",
            "15:00 - 15:55": "EC301 Lab (CC Floor3, BP)",
            "16:00 - 16:55": "EC301 Lab (CC Floor3, BP)",
            "17:00 - 17:55": "EC301 Lab (CC Floor3, BP)"
        },
        {
            "Day": "Friday",
            "9:00 - 9:55": "-",
            "10:00 - 10:55": "-",
            "11:00 - 11:55": "ME302 (Room C002, AG)",
            "12:00 - 12:55": "ME309 (Room C002, SKK)",
            "14:00 - 14:55": "ME302 Lab (Room L003, AG/BrS, G2)",
            "15:00 - 15:55": "ME302 Lab (Room L003, AG/BrS, G2)",
            "16:00 - 16:55": "-",
            "17:00 - 17:55": "ME359 (Room C202, VK)"
        }
    ],
    "courses": {
        "EC301": "Digital Signal Processing",
        "EC304": "IoT and Embedded Systems",
        "HS301": "Principles of Management",
        "ME302": "Sensor and Actuator",
        "ME309": "Mechanical Vibration",
        "ME359": "Industry 4.0"
    },
    "faculty": {
        "AG": "Dr. Abhinav Gautam",
        "BP": "Dr. Bhanu Priya",
        "BrS": "Dr. Brijendra Sangar",
        "SKK": "Dr. Sateeshkumar Kanakannavar",
        "SU": "Dr. Suraj",
        "VK": "Dr. Vinay Kumar",
        "mgf": "Management Guest fac"
    }
}

# Save JSON
with open("another_timetable_parsed.json", "w", encoding="utf-8") as f:
    json.dump(timetable_data, f, indent=2)

# Save CSV
df = pd.DataFrame(timetable_data["schedule"])
df.to_csv("another_timetable_parsed.csv", index=False)

print("Saved clean parsed files for another timetable.jpeg!")
