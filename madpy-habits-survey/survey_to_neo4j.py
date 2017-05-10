from os import environ

from py2neo import Graph, Node, Relationship
import google_survey


def create_nodes_and_relationships(question_id, node_label, relationship_label):
    responses = 
    nodes = {}


responses = google_survey.get('madpy-habits-survey.yaml')
# Set question_id as index to allow queries like: responses.ix['q0']
responses.set_index('question_id', inplace=True)

# Create nodes for all Madpy Pythonistas
pythonistas = {}
screen_names = responses.ix['q0', ['person_id', 'response']]
for _, (person_id, screen_name) in screen_names.iterrows():
    pythonistas[person_id] = Node('Pythonista', screen_name=screen_name)

# Create nodes for editors and relationships for editor preferences
editors = {}
editor_prefs = []
editor_responses = responses.ix['q1', ['person', 'response']]
for _, (person_id, editor) in editor_responses.iterrows():
    pythonista = pythonistas[person_id]
    editor = editors.setdefault(editor, Node('Editor', name=editor))
    editor_prefs.append(Relationship(pythonista, 'TYPES_IN', editor))

# Create nodes for python packages and relationships for favorites
packages = {}
favorites = []
package_responses = responses.ix['q2', ['person', 'response']]
for _, (person_id, package) in package_responses.iterrows():
    pythonista = pythonistas[person_id]
    package = packages.setdefault(package, Node('Package', name=package))
    favorites.append(Relationship(pythonista, 'LOVES', package))


graph = Graph(password=environ['NEO4J_PASSWORD'])

for person in people.values():
    graph.merge(person, label='Person')

for like in likes.values():
    graph.merge(like, label='Habit')

for relationship in habits:
    graph.merge(relationship, label='Person')
