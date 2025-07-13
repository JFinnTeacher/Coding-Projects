import json
import os
from openpyxl import Workbook

def read_json(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def export_feedback_to_excel(feedback_list, output_path):
    # feedback_list: list of dicts with keys: name, gender, grades (dict), feedback (str)
    wb = Workbook()
    ws = wb.active
    ws.title = 'Feedback'
    # Header
    headers = ['Name', 'Gender', 'Feedback']
    # Add dynamic grade columns
    if feedback_list:
        grade_keys = list(feedback_list[0]['grades'].keys())
        headers[2:2] = grade_keys
    ws.append(headers)
    for entry in feedback_list:
        row = [entry['name'], entry['gender']]
        for key in grade_keys:
            row.append(entry['grades'].get(key, ''))
        row.append(entry['feedback'])
        ws.append(row)
    wb.save(output_path) 