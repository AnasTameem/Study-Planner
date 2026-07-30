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



# ==========
# TEST CASES
# ==========


# s1 = SubTopic("Vecotrs", "intro to vectors")
# print(s1.progress)
# print(s1.status)

# s1.mark_done()
# print(s1.progress)
# print(s1.status)

# print(s1.detail)

# s2 = SubTopic("", "x")