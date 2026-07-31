from tracker import StudyTracker
from models.learning import Learning
from models.subjects import Subject
from models.topic import Topic
from models.sub_topic import SubTopic

tracker = StudyTracker()
learning = Learning("Gen AI", "path to gen ai job readiness")
subj = Subject("NLP", "natural language processing")
topic = Topic("Embeddings", "text to vectors")
st = SubTopic("Word2Vec", "shallow embedding model")
st.mark_done()
topic.add_subtopic(st)
subj.add_topic(topic)
learning.add_subject(subj)
tracker.add_learning(learning)

print(tracker.overall_progress)   # expect: 100.0

tracker.save_to_file("test_data.json")     # writes a real file to disk

loaded_tracker = StudyTracker.load_from_file("test_data.json")   # reads it back
print(loaded_tracker.overall_progress)   # expect: 100.0
print(len(loaded_tracker))                  # expect: 1
print([l.name for l in loaded_tracker])       # expect: ['Gen AI']