class Section:
    def __init__(self, title, lectures):
        self.title = title
        self.lectures = lectures

    def add_lecture(self, lecture):
        self.lectures += lecture

    def get_lectures_amount(self):
        return len(self.lectures)
