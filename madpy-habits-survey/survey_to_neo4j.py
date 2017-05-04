import py2neo
import google_survey


def get_survey_responses():
    google_sheet_name = 'madpy-habits-responses'
    creds_file = 'madpy-service-account-key.json'
    wide_responses = google_survey.get_responses(google_sheet_name, creds_file)
    responses = google_survey.tidy_responses(wide_responses)
    return responses

    
def connect_to_neo4j():
    neo4j_password = open('neo4j-password.txt').read().strip()
    graph = py2neo.Graph(password=neo4j_password)
    return graph


if __name__ == '__main__':
    responses = get_survey_responses()
    responses.to_csv('madpy-habits-responses.csv', index=False)
