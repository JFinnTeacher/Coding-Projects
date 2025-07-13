def get_pronouns(gender):
    # Returns a dict of pronoun placeholders based on gender
    if gender.lower() == "male":
        return {
            "pronoun_subject": "he",
            "pronoun_object": "him",
            "pronoun_possessive": "his",
            "pronoun_possessive_cap": "His"
        }
    elif gender.lower() == "female":
        return {
            "pronoun_subject": "she",
            "pronoun_object": "her",
            "pronoun_possessive": "her",
            "pronoun_possessive_cap": "Her"
        }
    else:
        return {
            "pronoun_subject": "they",
            "pronoun_object": "them",
            "pronoun_possessive": "their",
            "pronoun_possessive_cap": "Their"
        }

def substitute_pronouns(text, student_name, gender):
    pronouns = get_pronouns(gender)
    text = text.replace("{student_name}", student_name)
    for key, value in pronouns.items():
        text = text.replace(f"{{{key}}}", value)
    return text 