#!/usr/bin/env python
from os import environ
from py2neo import Graph, Node, Relationship
import google_survey


class MadpyHabitsSurvey:
    def __init__(self):
        self.responses = google_survey.get('madpy-habits-survey.yaml')
        self.responses.set_index('question_id', inplace=True)

    def graph_survey(self):
        screen_names = self.responses.ix['q0', ['person_id', 'response']]
        self.pythonistas = {person_id: Node('Pythonista', screen_name=name)
                            for _, (person_id, name) in
                            screen_names.iterrows()}

        self.graph = Graph(password=environ['NEO4J_PASSWORD'])
        for node in self.pythonistas.values():
            self.graph.merge(node, label='Pythonista')

        self._graph_responses_to_question('q1', 'Editor', 'TYPES_IN')
        self._graph_responses_to_question('q2', 'Package', 'LIKES')
        self._graph_responses_to_question('q3', 'VersionControl', 'USES')
        self._graph_responses_to_question('q4', 'Language', 'KNOWS')

    def _graph_responses_to_question(self, question_id, node_label,
                                     relationship_label):

        def Response(node_value):
            return Node(node_label, name=node_value)

        responses = self.responses.ix[question_id, ['person_id', 'response']]
        response_nodes = {}  # nodes for unique responses
        relationships = []   # relationships between people and responses
        for _, (person_id, node_value) in responses.iterrows():
            pythonista = self.pythonistas[person_id]
            node = response_nodes.setdefault(node_value, Response(node_value))
            response = Relationship(pythonista, relationship_label, node)
            relationships.append(response)

        for node in response_nodes.values():
            self.graph.merge(node, label=node_label)

        for relationship in relationships:
            self.graph.merge(relationship, label=node_label)

if __name__ == '__main__':
    survey = MadpyHabitsSurvey()
    survey.graph_survey()
