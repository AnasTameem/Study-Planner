from models.trackable_node import TrackableNode
from models.sub_topic import SubTopic
from exceptions import NotFoundError, DuplicateError

class Topic(TrackableNode):

    def __init__(self, name, description=""):
        super().__init__(name)
        self._description = description
        self._subtopics = []

    @property
    def description(self):
        return self._description

    @property
    def progress(self):
        if len(self._subtopics) == 0:
            return 0
        else:
            return sum(st.progress for st in self._subtopics) / len(self._subtopics)

    @property
    def status(self):
        if self.progress == 0:
            return "Not Started"
        elif self.progress == 100:
            return "Completed"
        else:
            return "In Progress"

    def add_subtopic(self, subtopic):
        if isinstance(subtopic, SubTopic) == False:
            raise TypeError
        elif subtopic in self._subtopics:
            raise DuplicateError("Duplicates not allowed")
        else:
            self._subtopics.append(subtopic)

    def get_subtopic(self, name):
        for st in self._subtopics:
            if st.name == name:
                return st
        raise NotFoundError(f"Subtopic '{name}' not found")

    def remove_subtopic(self, name):
        subtopic = self.get_subtopic(name)
        self._subtopics.remove(subtopic)


    def reorder_subtopics(self, new_order):
        new_list = []                          # start with an empty list
        for name in new_order:                  # go through each name, in the order given
            found = self.get_subtopic(name)     # find the actual object with that name
            new_list.append(found)              # add it to our new list, in this order
        self._subtopics = new_list
    
    def __len__(self):
        return len(self._subtopics)

    def __iter__(self):
        return iter(self._subtopics)

    def __repr__(self):
        return f"Topic name = {self.name} progress = {self.progress} subtopics = {len(self._subtopics)}"


