from os import environ

from flask import Flask, request, render_template, flash
from py2neo import Graph
import pandas

app = Flask(__name__)
app.secret_key = 'juniper-tree'
graph = Graph(password=environ['NEO4J_PASSWORD'])

pythonistas = pandas.DataFrame(graph.data("""
MATCH (member:Pythonista) RETURN member.screen_name AS screen_name
"""))['screen_name'].tolist()


@app.route('/', methods=['GET', 'POST'])
def madpy_habits():
    screen_name = None
    recommendations = None
    if request.method == 'POST':
        screen_name = request.form['screen_name']
        try:
            recommendations = get_recommendations(screen_name)
        except ScreenNameNotFound:
            flash(('No one with screen name "{}" was found. '
                   'Did you take the survey? '
                   '<a href="bit.ly/madpy-habits-survey">'
                   'bit.ly/madpy-habits-survey</a>')
                   .format(screen_name))
    return render_template('you_might_like.html',
                           screen_name=screen_name,
                           recommendations=recommendations)


def get_recommendations(screen_name):
    if screen_name not in pythonistas:
        raise ScreenNameNotFound()

    recommendations = pandas.DataFrame(graph.data("""
    MATCH (member:Pythonista {screen_name: {screen_name}}),
          (member) -[:LIKES]-> (known_package),
          (known_package) <-[:LIKES]- (similar_person),
          (similar_person) -[:LIKES]-> (other_package)
    WHERE NOT (member) -[:LIKES]-> (other_package)
    RETURN known_package.name AS known_package,
           similar_person.screen_name AS similar_person,
           other_package.name AS recommendation
    """, screen_name=screen_name))

    # Set column order
    out_col_order = ['known_package', 'similar_person', 'recommendation']
    return recommendations[out_col_order].to_html()


class ScreenNameNotFound(Exception):
    pass
