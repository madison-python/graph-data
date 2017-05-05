# Graph data in python with Neo4j and py2neo

Graphs are everywhere: social networks, recommender systems, even in fraud detection. But what's it like to actually use a graph database? I'll show you how to set up a Neo4j graph database and query it from python using the py2neo package. I'll cover some of the more interesting uses of graph databases in the news, such as how Neo4j was used in the investigation of the 11.5 million documents containing evidence of illegal offshore accounting leaked from the Panamanian law firm Mossack Fonseca (the Panama Papers), and more recently how Neo4j was used to visualize the TrumpWorld dataset of Trump's business ties collected by BuzzFeed. I'll also talk about how I'm using graph databases in my research on Wikipedia and on group problem solving. By the end, I hope you'll understand when to use graph databases like Neo4j and how to get started with python and the py2neo package.

# Outline

1. Totems game
2. Madpy habits
3. Wiki trees

# Totems game

The first time I had an actual use for a graph database was when a collaborator sent me the answer key to a simple game that I realized
was very clearly "a graph problem". My thought was that getting
the answer key into a graph would allow me to query it in more
intuitive ways.

# Madpy habits

Graph databases are often associated with social network applications
because it's easy to think about people as nodes and friendships 
as edges. Here I'll show how to load the results of the Madpy habits
survey into a graph database in order to identify groups of like-minded
individuals.

# Wiki trees

One of my research projects is investigating how Wikipedia articles
change as they accumulate edits, and in particular whether evolution
is a good model for understanding the changes to Wikipedia articles.
For this part I'll show how to read the revision history of a
Wikipedia article into a graph database.
