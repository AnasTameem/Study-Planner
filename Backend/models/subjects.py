from models.trackable_node import TrackableNode
from models.topic import Topic
from exceptions import NotFoundError, DuplicateError

class Subject(TrackableNode):

    def __init__(self, name, description=""):
        super().__init__(name)
        self._description = description
        self._topics = []

    @property
    def description(self):
        return self._description

    @property
    def progress(self):
        if len(self._topics) == 0:
            return 0
        else:
            return sum(t.progress for t in self._topics) / len(self._topics)


    @property
    def status(self):
        if self.progress == 0:
            return "Not Started"
        elif self.progress == 100:
            return "Completed"
        else:
            return "In Progress"       

    def add_topic(self, topic):
        if isinstance(topic, Topic) == False:
            raise TypeError
        elif topic in self._topics:
            raise DuplicateError("Duplicates not allowed")
        else:
            self._topics.append(topic)

    def get_topic(self, name):
        for t in self._topics:
            if t.name == name:
                return t
        raise NotFoundError(f"Topic '{name}' not found") 

    def remove_topic(self, name):
        topic = self.get_topic(name)
        self._topics.remove(topic)


    def reorder_topics(self, new_order):
        new_list = []
        for name in new_order:
            found = self.get_topic(name)
            new_list.append(found)
        self._topics = new_list

    def __len__(self):
        return len(self._topics)

    def __iter__(self):
        return iter(self._topics)

    def __repr__(self):
        return f"Subject name = {self.name} progress = {self.progress} topics = {len(self._topics)}"

    def to_dict(self):
        return {
            "name": self.name,
            "description": self._description,
            "topics": [t.to_dict() for t in self._topics]
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["name"], data["description"])
        for t_data in data["topics"]:
            obj.add_topic(Topic.from_dict(t_data))
        return obj