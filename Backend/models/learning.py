from models.trackable_node import TrackableNode
from models.subjects import Subject
from exceptions import NotFoundError, DuplicateError
from datetime import date

class Learning(TrackableNode):

    def __init__(self, name, description=""):
        super().__init__(name)
        self._day_started = date.today()
        self._description = description
        self._subjects = []

    @property
    def description(self):
        return self._description

    @property
    def progress(self):
        if len(self._subjects) == 0:
            return 0
        else:
            return sum(s.progress for s in self._subjects) / len(self._subjects)

    @property
    def status(self):
        if self.progress == 0:
            return "Not Started"
        elif self.progress == 100:
            return "Completed"
        else:
            return "In Progress"

    @property
    def day_started(self):
        return self._day_started

    def add_subject(self, subject):
        if isinstance(subject, Subject) == False:
            raise TypeError
        elif subject in self._subjects:
            raise DuplicateError("Duplicates not allowed")
        else:
            self._subjects.append(subject)

    def get_subject(self, name):
        for s in self._subjects:
            if s.name == name:
                return s
        raise NotFoundError(f"Subject '{name}' not found")
   
    def remove_subject(self, name):
        subject = self.get_subject(name)
        self._subjects.remove(subject)


    # def reorder_subjects(self, new_order):
    #     new_list = []
    #     for name in new_order:
    #         found = self.get_subject(name)
    #         new_list.append(found)
    #     self._subjects = new_list

    def __len__(self):
        return len(self._subjects)

    def __iter__(self):
        return iter(self._subjects)

    def __repr__(self):
        return f"Learning name = {self.name} progress = {self.progress} subjects = {len(self._subjects)}"

    def to_dict(self):
        return {
        "name": self.name,
        "description": self._description,
        "day_started": self._day_started.isoformat(),   # date -> string, e.g. "2026-07-31"
        "subjects": [s.to_dict() for s in self._subjects]
    }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["name"], data["description"])
        obj._day_started = date.fromisoformat(data["day_started"])   # string -> date, overwriting the auto-set today()
        for s_data in data["subjects"]:
            obj.add_subject(Subject.from_dict(s_data))
        return obj