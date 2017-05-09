from os import environ

from py2neo import Graph, Node, Relationship
import google_survey


responses = google_survey.get('madpy-habits-survey.yaml')

screen_names = (responses[['person', 'response']]
                         .ix[responses.question_id == 'q0']
                         .set_index('person')
                         .squeeze()
                         .to_dict())

people = {person: Node('Person', id=person, screen_name=screen_name)
          for person, screen_name in screen_names.items()}

likes = {response: Node('Habit', name=response)
         for response in responses.response.unique()}

habits = []
for resp in responses.itertuples():
    person = people[resp.person]
    like = likes[resp.response]
    habit = Relationship(person, 'LIKES', like)
    habits.append(habit)


graph = Graph(password=environ['NEO4J_PASSWORD'])

for person in people.values():
    graph.merge(person, label='Person')

for like in likes.values():
    graph.merge(like, label='Habit')

for relationship in habits:
    graph.merge(relationship, label='Person')
