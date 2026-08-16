import re
import datetime

DAYS_MAP = {
    "monday": "Mon",
    "tuesday": "Tue",
    "wednesday": "Wed",
    "thursday": "Thu",
    "friday": "Fri",
    "saturday": "Sat",
    "sunday": "Sun",
    "mon": "Mon",
    "tue": "Tue",
    "wed": "Wed",
    "thu": "Thu",
    "fri": "Fri",
    "sat": "Sat",
    "sun": "Sun"
}

DAYS_OF_WEEK = list(DAYS_MAP.keys())

KNOWN_SUBJECT_PREFIXES = [
    "cloud comp", "sw engg", "dis sys", "dissys", "epq", "emc", "ml", "tw",
    "os lab", "dccn lab", "compiler des", "compiler design", "robotics", "wsm",
    "oe", "ice", "dccn", "os", "ai-nw", "java prog", "pe", "em-ii", "psee",
    "eptd", "cs", "ees", "c and i", "7th bt ml", "csea-1", "csea-2"
]

BATCH_PREFIX_RE = re.compile(
    r'^\s*(?:\d+(?:st|nd|rd|th)\s+)?(?:BT|BTECH|MTECH|BE|BSC|MSC|MCA|BCA)?\s*(?:CSEA-\d|ETC-\d|CSE-\d|IT-\d|ME-\d|CE-\d|EE-\d|EEE-\d)?\s*$',
    re.IGNORECASE
)

def combine_split_cells(cells_list):
    non_empty = [c for c in cells_list if c and isinstance(c, str) and c.strip()]
    if not non_empty:
        return ""
    if len(non_empty) == 1:
        return non_empty[0]

    cell_lines_list = [c.split("\n") for c in non_empty]
    max_lines = max(len(cl) for cl in cell_lines_list)

    combined_lines = []
    for line_idx in range(max_lines):
        line_parts = []
        for cl in cell_lines_list:
            if line_idx < len(cl) and cl[line_idx].strip():
                line_parts.append(cl[line_idx].strip())
        if line_parts:
            combined_lines.append(" ".join(line_parts))

    res = "\n".join(combined_lines)
    # Fix split word tokens across adjacent cell columns
    res = re.sub(r'\bBY\s+OD\b', 'BYOD', res, flags=re.IGNORECASE)
    res = re.sub(r'\bDe\s+epak\b', 'Deepak', res, flags=re.IGNORECASE)
    res = re.sub(r'\bR\s+ajat\b', 'Rajat', res, flags=re.IGNORECASE)
    res = re.sub(r'\bD\s+SP\b', 'DSP', res, flags=re.IGNORECASE)
    res = re.sub(r'\bC1\s+11\b', 'C111', res, flags=re.IGNORECASE)
    res = re.sub(r'\bAc\s+ad\b', 'Acad', res, flags=re.IGNORECASE)
    res = re.sub(r'\bF\s+aculty\b', 'Faculty', res, flags=re.IGNORECASE)
    return res

def normalize_cell_content(cell_str):
    if not cell_str or not cell_str.strip():
        return {"subject": "", "room": "", "faculty": "", "raw": ""}

    lines = [l.strip() for l in cell_str.split('\n') if l.strip()]
    raw_content = " ".join(lines)

    cleaned_lines = []
    for line in lines:
        if BATCH_PREFIX_RE.match(line):
            continue
        l = BATCH_PREFIX_RE.sub('', line).strip()
        if l:
            cleaned_lines.append(l)

    if not cleaned_lines:
        cleaned_lines = lines

    full_text = " ".join(cleaned_lines)

    # 1. Extract Room Code (e.g. AG02, AG06, C102, C111, C112, C112 DSP Lab, C202, A120, A120 BYOD Lab, SP Lab, OD Lab, Room 101)
    room = ""
    room_match = re.search(r'\b[A-Z]{1,3}[-]?\d{2,4}(?:\s+(?:DSP|BYOD|SP)?\s*Lab)?\b|\b(?:SP|OD|DSP|BYOD)\s+Lab\b|\b[A-Z]\d{3}\b', full_text, re.IGNORECASE)
    if room_match:
        room = room_match.group(0).strip()

    # Clean room residue from lines
    lines_no_room = []
    for line in cleaned_lines:
        rem_line = line
        if room:
            rem_line = rem_line.replace(room, "").strip(" -(),")
        if rem_line:
            lines_no_room.append(rem_line)

    # 2. Subject & Faculty separation
    subject = ""
    faculty = ""

    if len(lines_no_room) >= 2:
        subject = lines_no_room[0]
        faculty = " ".join(lines_no_room[1:])
    elif len(lines_no_room) == 1:
        subject = lines_no_room[0]
    else:
        tokens = full_text.split()
        if len(tokens) >= 3:
            if tokens[1].lower() in ["comp", "engg", "sys", "lab", "prog", "des", "design", "ii", "nw", "proj", "check"]:
                subject = f"{tokens[0]} {tokens[1]}"
                faculty = " ".join(tokens[2:])
            else:
                subject = tokens[0]
                faculty = " ".join(tokens[1:])
        elif len(tokens) == 2:
            subject = tokens[0]
            faculty = tokens[1]
        elif len(tokens) == 1:
            subject = tokens[0]

    # Clean room residue from subject if present
    if room and room.lower() in subject.lower():
        subject = subject.replace(room, "").strip(" -(),")

    return {
        "subject": subject.strip(),
        "room": room.strip(),
        "faculty": faculty.strip(),
        "raw": raw_content
    }


def is_day_string(text):
    if not text:
        return False
    clean = text.strip().lower()
    return any(clean.startswith(day) or day in clean for day in DAYS_MAP.keys())

def map_day_short(text):
    if not text:
        return "Mon"
    clean = text.strip().lower()
    for key, val in DAYS_MAP.items():
        if key in clean:
            return val
    return text[:3].capitalize()

def format_time_slot_12h(slot_str):
    if not slot_str:
        return ""
    m = re.match(r'(\d{1,2}:\d{2}|\d{1,2})\s*[-–—to]\s*(\d{1,2}:\d{2}|\d{1,2})', slot_str.strip(), re.IGNORECASE)
    if not m:
        return slot_str

    def to_12h(t_str):
        t_clean = t_str.strip()
        if ":" not in t_clean:
            h = int(t_clean)
            m = 0
        else:
            parts = t_clean.split(":")
            h = int(parts[0])
            m = int(parts[1])
        
        ampm = "AM"
        if h >= 12:
            ampm = "PM"
            if h > 12:
                h -= 12
        elif h == 0:
            h = 12
        elif h >= 1 and h <= 7:
            ampm = "PM"
        
        return f"{h}:{m:02d} {ampm}"

    try:
        start_12 = to_12h(m.group(1))
        end_12 = to_12h(m.group(2))
        return f"{start_12} - {end_12}"
    except Exception:
        return slot_str

def normalize_timetable_matrix(matrix, filename="timetable"):
    if not matrix or len(matrix) == 0:
        return {
            "semester": 6,
            "columnTimeHeaders": [],
            "classes": [],
            "metadata": {
                "file_name": filename,
                "generated_at": datetime.datetime.now().isoformat(),
                "total_days": 0,
                "total_time_slots": 0,
                "total_entries": 0
            },
            "schedule": [],
            "raw_matrix": []
        }

    # Header identification
    header_row_idx = 0
    
    for r_idx, row in enumerate(matrix[:3]):
        joined = " ".join(row).lower()
        if any(char in joined for char in [":", "-", "am", "pm", "slot", "period", "time"]):
            header_row_idx = r_idx
            break

    header_row = matrix[header_row_idx]
    
    start_col = 1
    if is_day_string(header_row[0]):
        start_col = 1
    elif any(is_day_string(row[0]) for row in matrix[header_row_idx+1:]):
        start_col = 1
    else:
        start_col = 0

    time_slots = [col.strip() if col.strip() else f"Slot_{i+1}" for i, col in enumerate(header_row[start_col:])]
    
    days = []
    schedule = []
    
    # Store subjects for consolidation into CoSpace classes
    subject_map = {}

    current_day_label = "Monday"

    for row_idx in range(header_row_idx + 1, len(matrix)):
        row = matrix[row_idx]
        if not row or not any(row):
            continue

        raw_day_label = row[0].strip() if start_col == 1 and len(row) > 0 else ""
        if raw_day_label and is_day_string(raw_day_label):
            current_day_label = raw_day_label
        else:
            raw_day_label = current_day_label

        day_short = map_day_short(raw_day_label)
        if raw_day_label not in days:
            days.append(raw_day_label)

        cells = row[start_col:]
        c_idx = 0
        while c_idx < len(cells):
            cell_value = cells[c_idx]
            
            # Check if adjacent 2 or 3 cells form a merged block
            next_cell_1 = cells[c_idx + 1] if c_idx + 1 < len(cells) else ""
            next_cell_2 = cells[c_idx + 2] if c_idx + 2 < len(cells) else ""

            span = 1
            combined_value = cell_value

            # Check if adjacent 2 or 3 cells form a merged block
            next_cell_1 = cells[c_idx + 1] if c_idx + 1 < len(cells) else ""
            next_cell_2 = cells[c_idx + 2] if c_idx + 2 < len(cells) else ""

            # 3-column span check (e.g. 9:00-12:00 project blocks)
            if cell_value and next_cell_1 and next_cell_2 and any(k in cell_value.lower() for k in ["proj", "lab", "byod", "7th"]) and any(k in f"{next_cell_1} {next_cell_2}".lower() for k in ["proj", "lab"]):
                combined_value = combine_split_cells([cell_value, next_cell_1, next_cell_2])
                span = 3
            # 2-column span check (e.g. 11:00-13:00 or 9:00-11:00 2-hour labs/projects)
            elif cell_value and next_cell_1 and any(k in f"{cell_value} {next_cell_1}".lower() for k in ["lab", "byod", "proj", "dsp", "sp"]) and (any(k in cell_value.lower() for k in ["lab", "proj", "byod", "7th", "bt", "etc"]) or cell_value.strip().endswith(("-", "Ac", "ETC-Ac"))) and any(k in next_cell_1.lower() for k in ["proj", "lab", "etc-1", "etc-2", "csea-1", "csea-2", "byod", "dsp", "sp", "aculty", "ad"]):
                combined_value = combine_split_cells([cell_value, next_cell_1])
                span = 2

            if span > 1 and c_idx + span - 1 < len(time_slots):
                start_hdr = time_slots[c_idx]
                end_hdr = time_slots[c_idx + span - 1]
                start_part = start_hdr.split('-')[0] if '-' in start_hdr else start_hdr
                end_part = end_hdr.split('-')[1] if '-' in end_hdr else end_hdr
                time_slot = f"{start_part}-{end_part}"
            else:
                time_slot = time_slots[c_idx] if c_idx < len(time_slots) else f"Slot_{c_idx+1}"
                span = 1

            parsed_cell = normalize_cell_content(combined_value)
            
            if parsed_cell["subject"]:
                schedule.append({
                    "day": raw_day_label,
                    "time_slot": time_slot,
                    "subject": parsed_cell["subject"],
                    "room": parsed_cell["room"],
                    "faculty": parsed_cell["faculty"],
                    "raw_content": parsed_cell["raw"]
                })

                subj_name = parsed_cell["subject"].strip()
                if subj_name and len(subj_name) >= 2:
                    formatted_slot_range = format_time_slot_12h(time_slot)
                    timing_slot = f"{day_short} {formatted_slot_range}"
                    norm_key = subj_name.lower().replace(" ", "")

                    if norm_key not in subject_map:
                        subject_map[norm_key] = {
                            "name": subj_name,
                            "day": day_short,
                            "startColumnHeader": time_slot,
                            "endColumnHeader": time_slot,
                            "timings_list": [timing_slot],
                            "faculty": parsed_cell["faculty"],
                            "room": parsed_cell["room"],
                            "building": ""
                        }
                    else:
                        existing = subject_map[norm_key]
                        if timing_slot not in existing["timings_list"]:
                            existing["timings_list"].append(timing_slot)
                        if not existing["faculty"] and parsed_cell["faculty"]:
                            existing["faculty"] = parsed_cell["faculty"]
                        if not existing["room"] and parsed_cell["room"]:
                            existing["room"] = parsed_cell["room"]

            c_idx += span

    # Build final consolidated classes list for CoSpace
    cospace_classes = []
    for item in subject_map.values():
        item["timings"] = ", ".join(item["timings_list"])
        del item["timings_list"]
        cospace_classes.append(item)

    normalized = {
        "semester": 6,
        "columnTimeHeaders": time_slots,
        "classes": cospace_classes,
        "metadata": {
            "file_name": filename,
            "generated_at": datetime.datetime.now().isoformat(),
            "total_days": len(days),
            "total_time_slots": len(time_slots),
            "total_entries": len(schedule)
        },
        "days": days,
        "time_slots": time_slots,
        "schedule": schedule,
        "raw_matrix": matrix
    }

    return normalized
