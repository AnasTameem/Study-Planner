from models.learning import Learning
from exceptions import NotFoundError, DuplicateError


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

    def reorder_learnings(self, new_order):
        new_list = []
        for name in new_order:
            found = self.get_learning(name)
            new_list.append(found)
        self._learnings = new_list

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


if __name__ == "__main__":

    from tracker import StudyTracker
    from models.learning import Learning
    from models.subjects import Subject
    from models.topic import Topic
    from models.sub_topic import SubTopic
    from exceptions import NotFoundError, DuplicateError

    # ===============
    # BUILD TWO LEARNINGS
    # ===============

    # Learning 1: "Gen AI" — fully complete (1 subject, 1 topic, 1 subtopic, all done)
    learning1 = Learning("Gen AI", "path to gen ai job readiness")
    subj1 = Subject("NLP", "natural language processing")
    topic1 = Topic("Embeddings", "text to vectors")
    st1 = SubTopic("Word2Vec", "shallow embedding model")
    st1.mark_done()
    topic1.add_subtopic(st1)
    subj1.add_topic(topic1)
    learning1.add_subject(subj1)

    # Learning 2: "SQL Basics" — completely untouched, 0% everywhere
    learning2 = Learning("SQL Basics", "database fundamentals")
    subj2 = Subject("Queries", "select/insert/update/delete")
    topic2 = Topic("Joins", "combining tables")
    st2 = SubTopic("Inner Join", "matching rows only")
    topic2.add_subtopic(st2)
    subj2.add_topic(topic2)
    learning2.add_subject(subj2)

    tracker = StudyTracker()

    # ===============
    # TEST 1 — empty tracker
    # ===============
    print(len(tracker))               # expect: 0
    print(tracker.overall_progress)   # expect: 0

    # ===============
    # TEST 2 — add both learnings
    # ===============
    tracker.add_learning(learning1)
    tracker.add_learning(learning2)
    print(len(tracker))               # expect: 2

    # ===============
    # TEST 3 — overall_progress averages across learnings
    # ===============
    print(learning1.progress)          # expect: 100.0
    print(learning2.progress)          # expect: 0.0
    print(tracker.overall_progress)    # expect: 50.0   (average of 100.0 and 0.0)

    # ===============
    # TEST 4 — the .learnings property returns the raw list
    # ===============
    print([l.name for l in tracker.learnings])   # expect: ['Gen AI', 'SQL Basics']

    # ===============
    # TEST 5 — get / duplicate / not found
    # ===============
    found = tracker.get_learning("SQL Basics")
    print(found)                        # expect: repr of the SQL Basics Learning

    try:
        tracker.add_learning(Learning("Gen AI", "duplicate"))
        print("BUG: should have raised DuplicateError")
    except DuplicateError:
        print("Test 5a passed: DuplicateError raised correctly")

    try:
        tracker.get_learning("Nonexistent")
        print("BUG: should have raised NotFoundError")
    except NotFoundError:
        print("Test 5b passed: NotFoundError raised correctly")

    # ===============
    # TEST 6 — remove, reorder, iteration, repr
    # ===============
    print([l.name for l in tracker])              # expect: ['Gen AI', 'SQL Basics']
    tracker.reorder_learnings(["SQL Basics", "Gen AI"])
    print([l.name for l in tracker])              # expect: ['SQL Basics', 'Gen AI']

    tracker.remove_learning("SQL Basics")
    print(len(tracker))                # expect: 1
    print(tracker.overall_progress)    # expect: 100.0  (only Gen AI left)

    print(tracker)                      # expect: repr showing remaining learnings