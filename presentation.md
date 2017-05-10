---
title: Getting started with graph databases
author: |
  Pierce Edmiston  
  @pedmistor  
  github.com/pedmiston
theme: metropolis
---

# What's a graph problem?

> Graphs are everywhere, they’re eating the world, and there’s no going back.

![](refs/graph_databases/social_graph.png)

# Uses of graph databases

- Social networks
- Search engines
- Geospatial data
- Meta management
- [Fraud detection](https://neo4j.com/graphgist/9d627127-003b-411a-b3ce-f8d3970c2afa)
- **Investigative journalism**
- **Research**
- **Recommendation systems**

# Graph databases

![](refs/graph_databases/cover.png)

# Why use a graph database?

- Performance (index free adjacency)
- Flexibility (schema-free)
- Intuitiveness (Cypher query language)

# Graph modeling

![](refs/graph_databases/twitter_graph.png)

# Kinds of graph databases

![](refs/graph_databases/graph_db_space.png)

# Neo4j + Cypher

`(emil)<-[:KNOWS]-(jim)-[:KNOWS]->(ian)-[:KNOWS]->(emil)`

![](refs/graph_databases/mutual_friends.png)

# Cypher variables

```
(emil)<-[:KNOWS]-(jim)-[:KNOWS]->(ian)-[:KNOWS]->(emil)

(emil:Person)
  <-[:KNOWS]-(jim:Person)
  -[:KNOWS]->(ian:Person)
  -[:KNOWS]->(emil)

()<-[:KNOWS]-(jim)-[:KNOWS]->()-[:KNOWS]->()

(emil:Person {name: 'Emil'})
  <-[:KNOWS]-(jim:Person {name: 'Jim'})
  -[:KNOWS]->(ian:Person {name: 'Ian'})
  -[:KNOWS]->(emil)
```

# Cypher queries

> Find all of Jim's friends who know each other.

```
MATCH (a:Person {name:'Jim'}),
  (a)-[:KNOWS]->(b)-[:KNOWS]->(c),
  (a)-[:KNOWS]->(c)
RETURN b, c
```

# Neo4j

```bash
$ brew install neo4j
$ neo4j start
# open browser to localhost:7474
# login and set password
# record password somewhere
$ export NEO4J_PASSWORD=gefilte-fish
$ echo $NEO4J_PASSWORD > neo4j-password.txt
```

# Getting data into Neo4j

1. Enter data manually with the [`CREATE`](https://neo4j.com/docs/developer-manual/current/cypher/clauses/create/) clause.
2. Load plaintext data with [`LOAD CSV`](https://neo4j.com/developer/guide-importing-data-and-etl/) or `neo4j-import`.
3. Build the data in python with [`py2neo`](http://py2neo.org/v3/).

# py2neo.Node

```python
from os import environ
from py2neo import Graph, Node

graph = Graph(password=environ['NEO4J_PASSWORD'])
me = Node('Person', first_name='Pierce')
graph.create(me)
```

# py2neo.Relationship

```python
from py2neo import Relationship

parker = Node('Person', first_name='Parker')
father_of = Relationship(me, 'FATHER_OF', parker)
graph.create(father_of)  # creates parker node too
```

# Graph queries

```python
import pandas

q_children = """
MATCH (:Person {first_name: 'Pierce'}) -[:FATHER_OF]-> (child)
RETURN child.first_name AS first_name
"""
children = pandas.DataFrame(graph.data(q_children))
assert len(children) == 1, 'whoops!'
```

# Wikipedia

# Totems

![](totems-game/gameplay.png)

# Recipes

![](totems-game/recipes.png)

# The Panama papers

# TrumpWorld

# You might also like...

# Getting the survey responses

```yaml
---
# contents of madpy-survey-info.yaml
sheet_name: madpy-habits-responses
creds_file: madpy-service-account-key.json
survey_url: https://docs.google.com/forms/d/e/1FAIpQLScnwwfdLN_iUNaZEyks62Y_2DO8qADWGZU0ykVoWSRcnDSkfA/viewform
```

```python
import google_survey
responses = google_survey.get('madpy-habits-survey.yaml')
# Set question_id as index to allow queries like: responses.ix['q0']
responses.set_index('question_id', inplace=True)
```

# Create nodes for all Madpy Pythonistas

```python
pythonistas = {}
screen_names = responses.ix['q0', ['person_id', 'response']]
for _, (person_id, screen_name) in screen_names.iterrows():
    pythonistas[person_id] = Node('Pythonista', screen_name=screen_name)
```

# Behold: dict comprehension

```python
pythonistas = {person_id: Node('Pythonista', screen_name=screen_name)
               for _, (person_id, screen_name) in
               responses.ix['q0', ['person_id', 'response']].iterrows()}
```

# Create nodes for editors and relationships for editor preferences

```python
editors = {}
editor_prefs = []
editor_responses = responses.ix['q1', ['person', 'response']]
for _, (person_id, editor) in editor_responses.iterrows():
    pythonista = pythonistas[person_id]
    editor = editors.setdefault(editor, Node('Editor', name=editor))
    editor_prefs.append(Relationship(pythonista, 'TYPES_IN', editor))
```
