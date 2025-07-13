import json
from utils.pronoun_utils import substitute_pronouns

TEMPLATE_PATH = "data/feedback_templates.json"

class FeedbackGenerator:
    def __init__(self):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            self.templates = json.load(f)

    def generate(self, student_name, gender, grades):
        feedback_parts = []
        for category, grade in grades.items():
            template = self.templates.get(category, {}).get(grade)
            if template:
                feedback = substitute_pronouns(template, student_name, gender)
                feedback_parts.append(feedback)
        return " " .join(feedback_parts) 