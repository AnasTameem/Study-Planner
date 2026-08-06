from models.learning import Learning
from exceptions import NotFoundError, DuplicateError
import json

class StudyTracker:

    def __init__(self):
        self._learnings = []

    @property
    def learnings(self):
        return self._learnings

    def add_learning(self, learning):
        if isinstance(learning, Learning) == False:
            raise TypeError
        elif learning in self. _learnings:
            raise DuplicateError("Duplicates not allowed")
        else:
            self._learnings.append(learning)

    def get_learning(self, name):
        for l in self._learnings:
            if l.name == name:
                return l
        raise NotFoundError(f"Learning '{name}' not found")

    def remove_learning(self, name):
        learning = self.get_learning(name)
        self._learnings.remove(learning)

    # def reorder_learnings(self, new_order):
    #     new_list = []
    #     for name in new_order:
    #         found = self.get_learning(name)
    #         new_list.append(found)
    #     self._learnings = new_list

    def __len__(self):
        return len(self._learnings)

    def __iter__(self):
        return iter(self._learnings)

    def __repr__(self):
        return f"StudyTracker learnings = {self._learnings}"

    @property
    def overall_progress(self):
        if len(self._learnings) == 0:
            return 0
        else:
            return sum(l.progress for l in self._learnings) / len(self._learnings)

    def to_dict(self):
        return {
            "learnings": [l.to_dict() for l in self._learnings]
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        for l_data in data["learnings"]:
            obj.add_learning(Learning.from_dict(l_data))
        return obj

    def save_to_file(self, path):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, path):
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)