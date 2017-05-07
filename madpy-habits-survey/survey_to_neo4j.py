import py2neo
import google_survey


def get_survey_responses():
    responses = google_survey.get('madpy-habits-survey.yaml')
    return responses


def connect_to_neo4j():
    neo4j_password = open('neo4j-password.txt').read().strip()
    graph = py2neo.Graph(password=neo4j_password)
    return graph


if __name__ == '__main__':
    responses = get_survey_responses()
    responses.to_csv('madpy-habits-responses.csv', index=False)
