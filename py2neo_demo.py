from os import environ
from py2neo import Graph, Node, Relationship
import pandas

# Connect to the Neo4j graph database
graph = Graph(password=environ['NEO4J_PASSWORD'])

# Create a Node for me
me = Node('Person', first_name='Pierce', birthday='June 2')
graph.create(me)

# Create a Node for Parker
parker = Node('Person', first_name='Parker', birthday='July 6')
father_of = Relationship(me, 'FATHER_OF', parker)
graph.create(father_of)

# Query the db to get my children
children = pandas.DataFrame(graph.data("""
MATCH (:Person {first_name: 'Pierce'}) -[:FATHER_OF]-> (child)
RETURN child.first_name AS name, child.birthday AS birthday
"""))
assert len(children) == 1, 'whoops!'
