class Record:
    def __init__(self):
        self.scores = []

    def add_score(self, score):
        self.scores.append(score)

    def display_records(self):
        if not self.scores:
            return "No records available."
        records = "Game Records:\n"
        for index, score in enumerate(self.scores, start=1):
            records += f"{index}. Score: {score}\n"
        return records

    def clear_records(self):
        self.scores.clear()