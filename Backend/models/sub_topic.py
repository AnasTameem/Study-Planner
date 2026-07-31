from models.trackable_node import TrackableNode

class SubTopic(TrackableNode):

    def __init__(self, name, detail=""):
        super().__init__(name)
        self._detail = detail
        self._done = False

    @property
    def progress(self):
        if self._done:
            return 100
        else:
            return 0

    @property
    def status(self):
        if self._done:
            return "Completed"
        else:
            return "Not Started"

    @property
    def detail(self):
        return self._detail
    
    @property
    def done(self):
        return self._done

    def mark_done(self):
        self._done = True

    def mark_undone(self):
        self._done = False
    
    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}' done={self._done}>"


    def to_dict(self):
        return {
            "name": self.name,
            "detail": self._detail,
            "done": self._done
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["name"], data["detail"])
        if data["done"]:
            obj.mark_done()
        return obj