from os import environ

import pywikibot
import pandas
import py2neo

def load_article(title):
    revisions = get_revisions(title)
    load_revisions(revisions)


def get_revisions(title):
    page = get_wiki_page(title)
    revisions = page.revisions(content=False)
    records = [revision.__dict__ for revision in revisions]
    table = pandas.DataFrame.from_records(records)
    table.insert(0, 'title', title)
    return table


def load_revisions(revisions):
    graph = py2neo.Graph(password=environ['NEO4J_PASSWORD'])

    # Create a dict of revids -> sha1s
    sha1s = (revision[['revid', '_sha1']]
                    .set_index('revid')
                    .squeeze()
                    .to_dict())

    for rev in revision.itertuples():
        transaction = graph.begin()

        child_sha1 = rev._sha1

        if rev._parent_id == 0:
            continue

        parent_sha1 = sha1s.get(rev._parent_id)

        if parent_sha1 is None:
            raise ParentRevisionNotFound

        py2neo.Relationship(parent_)




def get_wiki_page(title):
    site = pywikibot.Site('en', 'wikipedia')
    page = pywikibot.Page(site, title)
    return page


class ParentRevisionNotFound(Exception):
    """The parent revision was not found but it should have been."""
